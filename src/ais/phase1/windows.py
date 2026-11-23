"""Janelamento com sobreposição da CNN 1D (Marco 4, REV-046).

A mesma CNN da baseline é treinada e usada sobre janelas de L pontos. Contratos fixados:

* Cada viagem (`id` completo) é uma sequência; as janelas começam no ponto 0 e avançam pelo passo
  `L * (1 - sobreposição)`. Pára-se na primeira janela que alcança o fim da viagem. A **última
  janela pode ter menos de L pontos** (sem pontos falsos); uma viagem com N <= L dá uma só janela.
* Nenhuma janela atravessa viagens. Dentro de uma viagem as janelas atravessam os intervalos de
  tempo, tal como a baseline trata a viagem inteira como uma sequência.
* Um lote de janelas de comprimentos diferentes é empilhado com enchimento só para empilhar: a
  máscara tira o enchimento da perda e da média, e o modelo põe a zero as posições de enchimento
  depois de cada camada (`FullTripCNN.forward(x, mask)`), pelo que cada janela tem a previsão que
  teria sozinha.
* A perda é `BCEWithLogits` mascarada: soma das posições reais dividida pelo seu número. Cada
  ocorrência de um ponto conta (um ponto repetido em duas janelas pesa duas vezes no treino).
* Reconstrução: a probabilidade de cada ponto original é a **média simples das probabilidades**
  (sigmoide aplicada uma só vez, em float64) das janelas que o cobrem. Não é suavização temporal.
* Só treino ou sintéticos em desenvolvimento; este módulo não decide acessos reservados.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

PROB_EPS = 1e-12  # recorte da probabilidade média só ao calcular a perda (float64)

WINDOW_CONFIG_REQUIRED = {
    "stage": str, "variant": str, "seed": int, "train_path": str, "split_manifest_path": str,
    "output_dir": str, "window_length": int, "overlap": float, "batch_size": int, "lr": float,
    "max_epochs": int, "time_budget_seconds": float, "device": str,
}


# --------------------------------------------------------------------------
# 1. Configuração
# --------------------------------------------------------------------------
def load_window_config(path) -> dict:
    """Lê e valida a configuração de treino com janelas (só treino, só desenvolvimento)."""
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = sorted(set(WINDOW_CONFIG_REQUIRED) - set(cfg))
    unknown = sorted(set(cfg) - set(WINDOW_CONFIG_REQUIRED))
    if missing or unknown:
        raise ValueError(f"Configuração inválida; em falta: {missing}; desconhecidas: {unknown}")
    for k, t in WINDOW_CONFIG_REQUIRED.items():
        v = cfg[k]
        if isinstance(v, bool) or not (isinstance(v, t) or (t is float and isinstance(v, int))):
            raise ValueError(f"Tipo inválido em '{k}': esperado {t.__name__}, recebido {type(v).__name__}")
    if cfg["stage"] != "development":
        raise ValueError("Só stage='development' é permitido (teste/validação exigem autorização externa).")
    name = Path(cfg["train_path"]).name.lower()
    if "validation" in name or "test" in name or "train" not in name:
        raise ValueError("Política de acesso: train_path tem de ser o ficheiro de treino.")
    if not (cfg["lr"] > 0 and cfg["max_epochs"] >= 1 and cfg["batch_size"] >= 1
            and cfg["time_budget_seconds"] > 0 and cfg["window_length"] >= 1):
        raise ValueError("Valores fora do intervalo (lr, épocas, lote, orçamento, L).")
    calculate_stride(cfg["window_length"], cfg["overlap"])  # valida a sobreposição
    if cfg["device"] not in ("cpu", "auto", "cuda"):
        raise ValueError("device tem de ser cpu, auto ou cuda.")
    return cfg


# --------------------------------------------------------------------------
# 2. Índice das janelas
# --------------------------------------------------------------------------
def calculate_stride(window_length: int, overlap: float) -> int:
    """Passo inteiro `L * (1 - sobreposição)`; recusa sobreposições sem passo inteiro ou fora de [0, 1)."""
    if int(window_length) != window_length or window_length < 1:
        raise ValueError(f"L tem de ser um inteiro positivo; recebido {window_length}.")
    if not 0.0 <= overlap < 1.0:
        raise ValueError(f"A sobreposição tem de estar em [0, 1); recebida {overlap}.")
    raw = window_length * (1.0 - overlap)
    stride = int(round(raw))
    if stride < 1 or abs(raw - stride) > 1e-9:
        raise ValueError(f"Sobreposição {overlap} com L={window_length} não dá um passo inteiro.")
    return stride


def window_starts(n_points: int, window_length: int, stride: int) -> list[int]:
    """Inícios (a partir de 0) das janelas de uma viagem com `n_points` pontos.

    Pára na primeira janela que alcança o fim (`início + L >= N`). N <= L dá `[0]`.
    """
    if n_points < 1:
        raise ValueError("Uma viagem tem de ter pelo menos 1 ponto.")
    if not 1 <= stride <= window_length:
        raise ValueError("O passo tem de estar entre 1 e L (senão há pontos por cobrir).")
    starts = [0]
    while starts[-1] + window_length < n_points:
        starts.append(starts[-1] + stride)
    return starts


class WindowSet:
    """Janelas de um conjunto de viagens, extraídas sob pedido a partir de arrays contíguos.

    Recebe sequências com `X` [C, N] já normalizado (`apply_scaler`), `y` [1, N], `id`,
    `point_ids` [N] e `t` [N]. Guarda as viagens concatenadas e uma tabela de janelas
    (`win_start` global, `win_len`, `win_seq`); não materializa os tensores de todas as janelas.
    """

    def __init__(self, sequences, window_length: int, overlap: float):
        if not sequences:
            raise ValueError("Sem sequências.")
        for s in sequences:
            if "X" not in s:
                raise ValueError(f"Sequência '{s.get('id')}' sem 'X'; aplicar apply_scaler primeiro.")
            n = s["X"].shape[1]
            if not (s["y"].shape == (1, n) and len(s["point_ids"]) == n and len(s["t"]) == n):
                raise ValueError(f"Sequência '{s['id']}': X, y, point_ids e t têm comprimentos diferentes.")
        if len({s["id"] for s in sequences}) != len(sequences):
            raise ValueError("Há viagens com o mesmo id; cada viagem tem de ser uma só sequência.")
        self.window_length = int(window_length)
        self.overlap = float(overlap)
        self.stride = calculate_stride(window_length, overlap)
        lengths = np.array([s["X"].shape[1] for s in sequences], dtype=np.int64)
        self.n_channels = int(sequences[0]["X"].shape[0])
        self.offsets = np.concatenate([[0], np.cumsum(lengths)]).astype(np.int64)
        self.X = np.ascontiguousarray(np.concatenate([s["X"] for s in sequences], axis=1), dtype=np.float32)
        self.y = np.ascontiguousarray(np.concatenate([s["y"] for s in sequences], axis=1), dtype=np.float32)
        self.point_ids = np.concatenate([s["point_ids"] for s in sequences]).astype(np.int64)
        self.t = np.concatenate([np.asarray(s["t"]) for s in sequences])
        self.ids = np.concatenate([np.full(n, s["id"], dtype=object) for s, n in zip(sequences, lengths)])
        self.trip_ids = [s["id"] for s in sequences]
        self.n_points = int(self.offsets[-1])
        seq, start, length = [], [], []
        for i, n in enumerate(lengths):
            for st in window_starts(int(n), self.window_length, self.stride):
                seq.append(i)
                start.append(int(self.offsets[i]) + st)
                length.append(min(self.window_length, int(n) - st))
        self.win_seq = np.array(seq, dtype=np.int64)
        self.win_start = np.array(start, dtype=np.int64)
        self.win_len = np.array(length, dtype=np.int64)

    def __len__(self) -> int:
        return int(self.win_start.size)

    def get_batch(self, window_idx):
        """Tensores `X [B,C,Lmax]`, `y [B,1,Lmax]`, `mask [B,1,Lmax]` (1 = ponto real)."""
        idx = np.asarray(window_idx, dtype=np.int64)
        lmax = int(self.win_len[idx].max())
        b = len(idx)
        X = np.zeros((b, self.n_channels, lmax), np.float32)
        Y = np.zeros((b, 1, lmax), np.float32)
        M = np.zeros((b, 1, lmax), np.float32)
        for k, w in enumerate(idx):
            s, n = int(self.win_start[w]), int(self.win_len[w])
            X[k, :, :n] = self.X[:, s:s + n]
            Y[k, 0, :n] = self.y[0, s:s + n]
            M[k, 0, :n] = 1.0
        return torch.from_numpy(X), torch.from_numpy(Y), torch.from_numpy(M)

    def window_table(self) -> pd.DataFrame:
        """Correspondência janela -> ponto (auditoria): window_id, id, point_id, position_in_window."""
        rows = []
        for w in range(len(self)):
            s, n = int(self.win_start[w]), int(self.win_len[w])
            rows.append(pd.DataFrame({
                "window_id": w, "id": self.ids[s:s + n], "point_id": self.point_ids[s:s + n],
                "position_in_window": np.arange(n)}))
        return pd.concat(rows, ignore_index=True)

    def coverage(self) -> np.ndarray:
        """Nº de janelas que cobrem cada ponto (deve ser >= 1 em todos)."""
        cnt = np.zeros(self.n_points, dtype=np.int64)
        for s, n in zip(self.win_start, self.win_len):
            cnt[s:s + n] += 1
        return cnt


def validate_window_coverage(ws: WindowSet) -> dict:
    """Verifica cobertura total, nenhuma janela a atravessar viagens e (sem sobreposição) cobertura 1."""
    cnt = ws.coverage()
    if (cnt < 1).any():
        raise ValueError(f"{int((cnt < 1).sum())} pontos sem nenhuma janela.")
    for w in range(len(ws)):
        s, n = int(ws.win_start[w]), int(ws.win_len[w])
        if len(set(ws.ids[s:s + n])) != 1:
            raise ValueError(f"A janela {w} atravessa viagens.")
        if not 1 <= n <= ws.window_length:
            raise ValueError(f"A janela {w} tem comprimento inválido {n}.")
    if ws.overlap == 0.0 and not (cnt == 1).all():
        raise ValueError("Com 0 % de sobreposição cada ponto devia estar em exactamente uma janela.")
    return {"n_windows": len(ws), "n_points": ws.n_points, "min_coverage": int(cnt.min()),
            "max_coverage": int(cnt.max()), "n_short_windows": int((ws.win_len < ws.window_length).sum())}


# --------------------------------------------------------------------------
# 3. Perda e treino
# --------------------------------------------------------------------------
def masked_bce(logits: torch.Tensor, y: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """BCEWithLogits só nas posições reais: soma / número de posições reais. Recusa lote sem posições."""
    n = mask.sum()
    if float(n) == 0.0:
        raise ValueError("Lote sem posições válidas.")
    per = F.binary_cross_entropy_with_logits(logits, y, reduction="none")
    return (per * mask).sum() / n


def train_window_epoch(model, ws: WindowSet, optimizer, batch_size: int, seed: int, device) -> dict:
    """Uma passagem por todas as janelas (ordem baralhada por `seed`), um passo de Adam por lote."""
    model.train()
    perm = np.random.default_rng(seed).permutation(len(ws))
    n_steps, n_valid, sum_loss = 0, 0.0, 0.0
    t0 = time.perf_counter()
    for i in range(0, len(perm), batch_size):
        X, Y, M = (t.to(device) for t in ws.get_batch(perm[i:i + batch_size]))
        optimizer.zero_grad()
        loss = masked_bce(model(X, mask=M), Y, M)
        if not torch.isfinite(loss):
            raise FloatingPointError(f"Perda não finita no passo {n_steps}: {loss.item()}")
        loss.backward()
        optimizer.step()
        m = float(M.sum())
        n_steps += 1
        n_valid += m
        sum_loss += float(loss.item()) * m
    return {"mean_loss_per_occurrence": sum_loss / n_valid, "n_steps": n_steps,
            "n_valid_occurrences": int(n_valid), "n_windows": len(ws),
            "seconds": time.perf_counter() - t0}


# --------------------------------------------------------------------------
# 4. Inferência e reconstrução
# --------------------------------------------------------------------------
@torch.no_grad()
def predict_window_probabilities(model, ws: WindowSet, device, batch_size: int = 256):
    """Probabilidade média por ponto original e número de janelas que o cobrem.

    Sigmoide aplicada uma só vez (float64) a cada logit; a média é das probabilidades.
    Janelas de comprimento igual ficam juntas nos lotes para gastar menos enchimento.
    """
    model.eval()
    psum = np.zeros(ws.n_points, dtype=np.float64)
    cnt = np.zeros(ws.n_points, dtype=np.int64)
    order = np.argsort(ws.win_len, kind="stable")
    for i in range(0, len(order), batch_size):
        idx = order[i:i + batch_size]
        X, _, M = ws.get_batch(idx)
        p = torch.sigmoid(model(X.to(device), mask=M.to(device)).double()).cpu().numpy()
        for k, w in enumerate(idx):
            s, n = int(ws.win_start[w]), int(ws.win_len[w])
            psum[s:s + n] += p[k, 0, :n]
            cnt[s:s + n] += 1
    if (cnt < 1).any():
        raise ValueError("Há pontos sem previsão depois da reconstrução.")
    return psum / cnt, cnt


def reconstructed_loss_per_point(prob: np.ndarray, target: np.ndarray) -> float:
    """Entropia cruzada binária por ponto original sobre a probabilidade reconstruída (float64)."""
    p = np.clip(np.asarray(prob, dtype=np.float64), PROB_EPS, 1.0 - PROB_EPS)
    t = np.asarray(target, dtype=np.float64)
    return float(-(t * np.log(p) + (1.0 - t) * np.log1p(-p)).mean())


def predict_window_table(model, ws: WindowSet, labels: pd.DataFrame, device, threshold: float,
                         batch_size: int = 256) -> pd.DataFrame:
    """Tabela por ponto original (mesmas colunas que `inference.predict`, mais `n_windows`)."""
    prob, cnt = predict_window_probabilities(model, ws, device, batch_size)
    pred = pd.DataFrame({"id": ws.ids, "point_id": ws.point_ids, "t": ws.t,
                         "target": ws.y[0].astype(int), "p_fishing": prob, "n_windows": cnt})
    pred["predicted"] = (pred["p_fishing"] >= threshold).astype(int)
    pred = pred.merge(labels, on="point_id", how="left")
    assert pred["point_id"].is_unique and pred["label"].notna().all()
    return pred


def expected_steps_per_epoch(n_windows: int, batch_size: int) -> int:
    return math.ceil(n_windows / batch_size)
