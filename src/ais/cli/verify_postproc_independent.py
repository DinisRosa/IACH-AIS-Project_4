"""Verificação INDEPENDENTE do pós-processamento (REV-057).

Escrito pela Abacus.AI (delegate-terminal) só a partir da descrição do filtro e das métricas, sem ver o código
nem os dados do projeto; revisto e corrido localmente. Serve para confirmar, por uma segunda implementação, os
números de `ais.cli.postproc_validation`. Lê o CSV das previsões e imprime JSON; não escreve ficheiros.

A janela da média pesada gaussiana é configurável: `--size N` (inteiro ímpar, por omissão 13), com k de -h a +h,
h = N//2 e sigma = N/6.

Execução:
    iach-ais-venv-4/bin/python -m ais.cli.verify_postproc_independent results/final_validation/predictions_validation.csv
    iach-ais-venv-4/bin/python -m ais.cli.verify_postproc_independent previsoes.csv --size 301
"""
import argparse
import sys
import json
import numpy as np
import pandas as pd


def carregar(caminho):
    df = pd.read_csv(caminho)
    df["_t"] = pd.to_datetime(df["t"])
    ordem = {}
    for tid in df["id"].tolist():
        if tid not in ordem:
            ordem[tid] = len(ordem)
    df["_ordem"] = df["id"].map(ordem)
    df = df.sort_values(["_ordem", "_t", "point_id"], kind="mergesort")
    return df.reset_index(drop=True)


def filtrar(p, size=13):
    p = np.asarray(p, dtype=float)
    n = len(p)
    if n == 0:
        return np.empty(0, dtype=float)

    raio = size // 2
    sigma = size / 6.0
    k = np.arange(-raio, raio + 1)
    w = np.exp(-(k ** 2) / (2.0 * sigma * sigma))

    # Numerador: convolução completa e deslocamento de `raio` para alinhar o centro do kernel.
    # O comprimento é sempre n, mesmo quando a viagem é mais curta do que a janela.
    num = np.convolve(p, w, mode="full")[raio:raio + n]

    # Denominador: soma dos pesos efectivamente usados em cada índice (só pontos existentes).
    den = np.convolve(np.ones(n, dtype=float), w, mode="full")[raio:raio + n]

    return num / den


def metricas(y_real, y_prev):
    y_real = np.asarray(y_real)
    y_prev = np.asarray(y_prev)
    n = len(y_real)
    acc = float(np.mean(y_real == y_prev)) if n else 0.0
    por_classe = {}
    for c in (0, 1):
        tp = int(np.sum((y_real == c) & (y_prev == c)))
        fp = int(np.sum((y_real != c) & (y_prev == c)))
        fn = int(np.sum((y_real == c) & (y_prev != c)))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2.0 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        por_classe[str(c)] = {
            "precisao": float(prec),
            "sensibilidade": float(rec),
            "f1": float(f1),
        }
    return {"exatidao": acc, "por_classe": por_classe}


def segmentos(tempos, classes):
    n = len(classes)
    blocos = []
    i = 0
    while i < n:
        j = i
        while j + 1 < n and classes[j + 1] == classes[i]:
            j += 1
        blocos.append((int(classes[i]), i, j))
        i = j + 1
    saida = []
    for c, i, j in blocos:
        inicio = float(tempos[i])
        fim = float(tempos[j + 1]) if (j + 1 < n) else float(tempos[j])
        saida.append((c, inicio, fim))
    return saida


def iou_temporal(a, b):
    s1, e1 = a
    s2, e2 = b
    inter = max(0.0, min(e1, e2) - max(s1, s2))
    uniao = max(e1, e2) - min(s1, s2)
    if uniao <= 0.0:
        return 1.0 if s1 == s2 else 0.0
    return inter / uniao


def emparelhar(ref, prev):
    candidatos = []
    for i, r in enumerate(ref):
        for j, p in enumerate(prev):
            v = iou_temporal((r[1], r[2]), (p[1], p[2]))
            if v >= 0.5:
                candidatos.append((v, i, j))
    candidatos.sort(key=lambda x: (-x[0], x[1], x[2]))
    usados_r = set()
    usados_p = set()
    pares = 0
    for v, i, j in candidatos:
        if i in usados_r or j in usados_p:
            continue
        usados_r.add(i)
        usados_p.add(j)
        pares += 1
    return pares


def avaliar_segmentos(viagens, chave_classe):
    totais = {0: {"n_ref": 0, "n_pred": 0, "n_pares": 0},
              1: {"n_ref": 0, "n_pred": 0, "n_pares": 0}}
    for v in viagens:
        ref = segmentos(v["tempos"], v["target"])
        prev = segmentos(v["tempos"], v[chave_classe])
        for c in (0, 1):
            r = [s for s in ref if s[0] == c]
            p = [s for s in prev if s[0] == c]
            totais[c]["n_ref"] += len(r)
            totais[c]["n_pred"] += len(p)
            totais[c]["n_pares"] += emparelhar(r, p)
    saida = {}
    for c in (0, 1):
        t = totais[c]
        den = t["n_pred"] + t["n_ref"]
        f1 = 2.0 * t["n_pares"] / den if den else 0.0
        saida[str(c)] = {
            "n_ref": int(t["n_ref"]),
            "n_pred": int(t["n_pred"]),
            "n_pares": int(t["n_pares"]),
            "f1": float(f1),
        }
    return saida


def main():
    parser = argparse.ArgumentParser(
        description="Verificação independente do pós-processamento (REV-057)."
    )
    parser.add_argument("csv", help="CSV das previsões")
    parser.add_argument(
        "--size",
        type=int,
        default=13,
        help="tamanho da janela gaussiana (inteiro ímpar, por omissão 13)",
    )
    args = parser.parse_args()

    if args.size < 1 or args.size % 2 == 0:
        parser.error("--size tem de ser um inteiro ímpar positivo")

    df = carregar(args.csv)

    ids = df["id"].to_numpy()
    p = df["p_fishing"].to_numpy(dtype=float)
    target = df["target"].to_numpy(dtype=int)
    antes = df["predicted"].to_numpy(dtype=int)

    depois = np.empty(len(df), dtype=int)
    limites = [0] + list(np.flatnonzero(ids[1:] != ids[:-1]) + 1) + [len(df)]
    for a, b in zip(limites[:-1], limites[1:]):
        if b <= a:
            continue
        pf = filtrar(p[a:b], args.size)
        depois[a:b] = (pf >= 0.65).astype(int)

    viagens = []
    for a, b in zip(limites[:-1], limites[1:]):
        if b <= a:
            continue
        delta = df["_t"].to_numpy()[a:b] - df["_t"].to_numpy()[a]
        seg = delta.astype("int64").astype(float) / 1e9
        viagens.append({
            "tempos": seg,
            "target": target[a:b],
            "antes": antes[a:b],
            "depois": depois[a:b],
        })

    alterados = antes != depois
    n_alterados = int(np.sum(alterados))
    n_corrigidos = int(np.sum(alterados & (depois == target)))

    resultado = {
        "antes": {
            "metricas": metricas(target, antes),
            "segmentos": avaliar_segmentos(viagens, "antes"),
        },
        "depois": {
            "metricas": metricas(target, depois),
            "segmentos": avaliar_segmentos(viagens, "depois"),
        },
        "mudancas": {
            "n_alterados": n_alterados,
            "n_corrigidos": n_corrigidos,
        },
    }
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
