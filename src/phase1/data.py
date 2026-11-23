"""Preparação comum dos dados da fase 1: leitura segura do treino, validação,
sequências completas por viagem, normalização e carregamento (batch_size=1).

Regras: só treino ou dados sintéticos; sem janelas, sem padding, sem truncar,
sem reamostrar. O scaler só é ajustado com sequências de treino.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

FEATURE_COLS = ["speed_calc_mps", "signed_turn_calc_deg", "time_gap_calc_s", "distanceToShore"]
# Características com máscara (as que podem faltar nos dois primeiros pontos).
MASK_FEATURES = ["speed_calc_mps", "signed_turn_calc_deg", "time_gap_calc_s"]
INPUT_CHANNELS = [
    "speed_calc_mps", "signed_turn_calc_deg", "time_gap_calc_s", "distanceToShore",
    "mask_speed_calc_mps", "mask_signed_turn_calc_deg", "mask_time_gap_calc_s",
]
N_INPUT_CHANNELS = 7

TARGET_COL = "target"
META_COLS = ["id", "point_id", "t"]

# Posições (0 = 1.º ponto de cada id) onde um NaN é esperado, por característica.
EXPECTED_NAN_POSITIONS = {
    "speed_calc_mps": (0,),
    "time_gap_calc_s": (0,),
    "signed_turn_calc_deg": (0, 1),
}


# --------------------------------------------------------------------------
# 1. Leitura segura do treino
# --------------------------------------------------------------------------
def load_training_data(data_path, split_manifest_path) -> pd.DataFrame:
    """Lê o parquet de treino, recusando validação/teste e ids não-train.

    A política olha só para o NOME do ficheiro (antes de qualquer leitura).
    O manifesto serve apenas para confirmar que todos os ids são 'train'.
    """
    name = Path(data_path).name.lower()
    if "validation" in name or "test" in name:
        raise ValueError(f"Política de acesso: '{Path(data_path).name}' parece validação/teste; recusado.")
    if "train" not in name:
        raise ValueError(f"Política de acesso: '{Path(data_path).name}' não é um ficheiro de treino; recusado.")

    manifest = pd.read_csv(split_manifest_path)
    if not {"id", "split"}.issubset(manifest.columns):
        raise ValueError("Manifesto sem colunas 'id' e 'split'.")
    split_of = dict(zip(manifest["id"].astype(str), manifest["split"].astype(str)))

    df = pd.read_parquet(data_path)
    if "split" in df.columns:
        bad = sorted(set(df["split"].astype(str)) - {"train"})
        if bad:
            raise ValueError(f"Política de acesso: coluna 'split' com valores não-train: {bad}.")
    ids = df["id"].astype(str).unique()
    not_train = [i for i in ids if split_of.get(i) != "train"]
    if not_train:
        raise ValueError(
            f"Política de acesso: {len(not_train)} id(s) não constam como train no manifesto "
            f"(ex.: {not_train[:3]})."
        )
    return df


# --------------------------------------------------------------------------
# 2. Validação
# --------------------------------------------------------------------------
def validate_training_data(df: pd.DataFrame, feature_cols=FEATURE_COLS) -> dict:
    """Valida estrutura, ordenação (id, t, point_id) e padrão de NaN esperado.

    Levanta ValueError com todas as falhas; devolve um relatório se estiver tudo bem.
    """
    errors: list[str] = []
    feature_cols = list(feature_cols)
    required = META_COLS + [TARGET_COL] + feature_cols
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas em falta: {missing}")

    for c in ["point_id", TARGET_COL] + feature_cols:
        if not pd.api.types.is_numeric_dtype(df[c]):
            errors.append(f"Coluna '{c}' não é numérica ({df[c].dtype}).")
    if errors:
        raise ValueError("; ".join(errors))

    if df["id"].isna().any() or df["t"].isna().any() or df["point_id"].isna().any():
        errors.append("NaN em id, t ou point_id.")
    if df["point_id"].duplicated().any():
        errors.append(f"point_id duplicado ({int(df['point_id'].duplicated().sum())} repetições).")

    target = df[TARGET_COL]
    if target.isna().any() or not target.isin([0, 1]).all():
        errors.append("target não binário (só 0/1, sem NaN).")

    # Ordenação: ids contíguos, e dentro de cada id (t, point_id) não decrescente.
    ids = df["id"].to_numpy()
    changes = np.flatnonzero(ids[1:] != ids[:-1]) + 1
    starts = np.concatenate([[0], changes]) if len(df) else np.array([], dtype=int)
    block_ids = ids[starts]
    if len(set(block_ids)) != len(block_ids):
        errors.append("Linhas de um mesmo id não são contíguas (base não ordenada por id).")
    elif len(block_ids) > 1 and not all(block_ids[i] < block_ids[i + 1] for i in range(len(block_ids) - 1)):
        errors.append("ids não estão por ordem crescente (ordenação por id violada).")
    same = np.zeros(len(df), dtype=bool)
    same[1:] = ids[1:] == ids[:-1]
    t = df["t"].to_numpy()
    pid = df["point_id"].to_numpy()
    t_dec = same[1:] & (t[1:] < t[:-1])
    if t_dec.any():
        errors.append(f"t decrescente dentro de um id ({int(t_dec.sum())} casos).")
    tie_bad = same[1:] & (t[1:] == t[:-1]) & (pid[1:] < pid[:-1])
    if tie_bad.any():
        errors.append(f"Empates de t sem point_id crescente ({int(tie_bad.sum())} casos).")

    # Padrão de NaN / infinitos.
    pos = df.groupby("id", sort=False).cumcount().to_numpy()
    nan_report = {}
    for c in feature_cols:
        v = df[c].to_numpy(dtype="float64")
        if np.isinf(v).any():
            errors.append(f"Valores infinitos em '{c}'.")
        isnan = np.isnan(v)
        allowed = np.isin(pos, EXPECTED_NAN_POSITIONS.get(c, ()))
        unexpected = isnan & ~allowed
        if unexpected.any():
            errors.append(f"NaN inesperado em '{c}' ({int(unexpected.sum())} linhas).")
        nan_report[c] = int(isnan.sum())

    if errors:
        raise ValueError("Validação falhou: " + " | ".join(errors))
    return {
        "n_rows": int(len(df)),
        "n_ids": int(len(block_ids)),
        "n_nan_per_feature": nan_report,
        "target_mean": float(target.mean()) if len(df) else float("nan"),
        "feature_cols": feature_cols,
    }


# --------------------------------------------------------------------------
# 3. Sequências completas
# --------------------------------------------------------------------------
def build_full_sequences(df: pd.DataFrame, feature_cols=FEATURE_COLS) -> list[dict]:
    """Um registo por id (viagem completa), pela ordem de 1.ª aparição na base.

    Dentro de cada id mantém a ordem das linhas. Não normaliza; NaN originais mantidos.
    """
    feature_cols = list(feature_cols)
    seqs = []
    for tid, g in df.groupby("id", sort=False):
        seqs.append({
            "id": tid,
            "point_ids": g["point_id"].to_numpy(dtype=np.int64),
            "t": g["t"].to_numpy(),
            "features_raw": g[feature_cols].to_numpy(dtype=np.float64).T.astype(np.float32),
            "y": g[TARGET_COL].to_numpy(dtype=np.float32)[None, :],
        })
    return seqs


# --------------------------------------------------------------------------
# 4. Scaler
# --------------------------------------------------------------------------
def fit_scaler(sequences) -> dict:
    """Média e desvio-padrão populacional (ddof=0) por característica, só valores observados.

    Acumula por sequência (contagem, média, soma dos desvios quadrados em float64)
    e junta-as (método de Chan), sem concatenar tudo: equivalente à soma e soma de
    quadrados mas numericamente mais estável. Se std == 0, usa 1.0 e regista.
    """
    n = np.zeros(len(FEATURE_COLS))
    mean = np.zeros(len(FEATURE_COLS))
    m2 = np.zeros(len(FEATURE_COLS))
    for s in sequences:
        raw = np.asarray(s["features_raw"], dtype=np.float64)
        for k in range(raw.shape[0]):
            v = raw[k][~np.isnan(raw[k])]
            nb = v.size
            if nb == 0:
                continue
            mb = v.mean()
            m2b = ((v - mb) ** 2).sum()
            tot = n[k] + nb
            delta = mb - mean[k]
            mean[k] += delta * nb / tot
            m2[k] += m2b + delta ** 2 * n[k] * nb / tot
            n[k] = tot
    if (n == 0).any():
        raise ValueError("Característica sem valores observados; scaler impossível.")
    std = np.sqrt(m2 / n)
    protected = [FEATURE_COLS[k] for k in range(len(std)) if std[k] == 0]
    std = np.where(std == 0, 1.0, std)
    return {
        "feature_cols": list(FEATURE_COLS),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "n_observed": [int(x) for x in n],
        "std_protected": protected,
        "ddof": 0,
    }


def save_scaler(scaler: dict, path) -> None:
    """Grava o scaler em JSON."""
    Path(path).write_text(json.dumps(scaler, indent=2, ensure_ascii=False), encoding="utf-8")


def load_scaler(path) -> dict:
    """Lê o scaler de JSON."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# 5. Aplicar scaler
# --------------------------------------------------------------------------
def apply_scaler(sequence: dict, scaler: dict) -> dict:
    """Devolve cópia do registo com `X` [7,N] float32: normaliza, máscara, depois NaN -> 0.

    Não reajusta o scaler nem toca em y. NaN em característica sem máscara é erro.
    """
    if list(scaler["feature_cols"]) != FEATURE_COLS:
        raise ValueError("feature_cols do scaler diferem de FEATURE_COLS.")
    raw = np.asarray(sequence["features_raw"], dtype=np.float64)
    mean = np.asarray(scaler["mean"], dtype=np.float64)[:, None]
    std = np.asarray(scaler["std"], dtype=np.float64)[:, None]
    nan = np.isnan(raw)
    for k, name in enumerate(FEATURE_COLS):
        if name not in MASK_FEATURES and nan[k].any():
            raise ValueError(f"NaN inesperado em '{name}' (sem máscara).")
    norm = (raw - mean) / std
    masks = nan[: len(MASK_FEATURES)].astype(np.float64)
    norm[nan] = 0.0  # preenchimento no espaço normalizado
    out = dict(sequence)
    out["X"] = np.concatenate([norm, masks], axis=0).astype(np.float32)
    return out


# --------------------------------------------------------------------------
# 6. Separação interna treino/monitorização
# --------------------------------------------------------------------------
def create_internal_training_split(sequences, fraction: float, seed: int):
    """Separa por id completo em treino interno e monitorização interna.

    `fraction` é a proporção de ids para MONITORIZAÇÃO (obrigatória; sem valor por omissão).
    IMPORTANTE: para independência interna, o scaler deve ser ajustado só com
    `train_seqs`, depois desta separação. Devolve (train_seqs, monitor_seqs, manifesto
    {id: "train_internal"|"monitor_internal"}); a ordem original é preservada.
    """
    if not (0.0 < fraction < 1.0):
        raise ValueError(f"fraction tem de estar em (0,1); recebido {fraction}.")
    n = len(sequences)
    if n < 2:
        raise ValueError("São precisas pelo menos 2 sequências para separar.")
    n_mon = min(max(int(round(fraction * n)), 1), n - 1)
    perm = np.random.default_rng(seed).permutation(n)
    mon_idx = set(perm[:n_mon].tolist())
    train_seqs = [s for i, s in enumerate(sequences) if i not in mon_idx]
    monitor_seqs = [s for i, s in enumerate(sequences) if i in mon_idx]
    manifest = {s["id"]: "train_internal" for s in train_seqs}
    manifest.update({s["id"]: "monitor_internal" for s in monitor_seqs})
    return train_seqs, monitor_seqs, manifest


# --------------------------------------------------------------------------
# 7. DataLoader
# --------------------------------------------------------------------------
class _SequenceDataset(Dataset):
    def __init__(self, sequences):
        self.sequences = sequences

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, i):
        s = self.sequences[i]
        meta = {"id": s["id"], "point_ids": s["point_ids"], "t": s["t"]}
        return torch.from_numpy(np.ascontiguousarray(s["X"])), torch.from_numpy(np.ascontiguousarray(s["y"])), meta


def _collate_single(batch):
    (x, y, meta), = batch  # batch_size=1
    return x.unsqueeze(0), y.unsqueeze(0), meta


def build_sequence_loader(sequences, shuffle: bool, seed: int) -> DataLoader:
    """DataLoader com batch_size=1: X [1,7,N], y [1,1,N], meta (id, point_ids, t).

    Exige `X` em cada sequência (use apply_scaler antes). Sem truncar nem padding.
    """
    for s in sequences:
        if "X" not in s:
            raise ValueError(f"Sequência '{s.get('id')}' sem 'X'; aplicar apply_scaler primeiro.")
    gen = torch.Generator()
    gen.manual_seed(seed)
    return DataLoader(_SequenceDataset(list(sequences)), batch_size=1, shuffle=shuffle,
                      generator=gen, collate_fn=_collate_single)
