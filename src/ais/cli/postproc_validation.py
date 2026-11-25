"""Pós-processamento da referência sobre as previsões já guardadas do `validation` (Marco 5, REV-057/REV-059).

Duas versões de protocolo, cada uma declarada e commitada antes de medir:
  - `posproc_validation_v1`: `configs/postproc_protocol.json`, janela gaussiana de 13 pontos (REV-057);
  - `posproc_validation_v2`: `configs/postproc_protocol_v2.json`, janela gaussiana de 301 pontos (REV-059).

NÃO abre o parquet do `validation` e NÃO volta a correr a CNN: lê
`results/final_validation/predictions_validation.csv`, gerado na medição final (REV-053), filtra `p_fishing`
com a janela gaussiana da versão, aplica o limiar 0,65 e compara com `target` antes e depois. Uma só execução
por versão, registada em `results/access_log.jsonl`.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.postproc_validation --version posproc_validation_v2
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

from ais.cli.select_windows_on_test import segment_report
from ais.phase1.inference import tables_for
from ais.phase1.postprocessing import gaussian_kernel, smooth_probabilities
from ais.phase1.reserved import log_access, read_log, sha256_of

ROOT = Path(__file__).resolve().parents[3]

# Lista fechada de versões: o caminho do protocolo, o tamanho da janela e a pasta de saída de cada uma.
# Sigma é sempre size / 6 e o limiar é sempre THRESHOLD; nada disto se lê de fora desta tabela.
PROTOCOLS = {
    "posproc_validation_v1": {"path": "configs/postproc_protocol.json", "size": 13,
                              "out": "results/postproc_validation"},
    "posproc_validation_v2": {"path": "configs/postproc_protocol_v2.json", "size": 301,
                              "out": "results/postproc_validation_v2"},
}
REQUIRED = ["id", "point_id", "t", "target", "p_fishing", "predicted"]
SOURCE = "results/final_validation/predictions_validation.csv"
# Hash do ficheiro de previsões da medição final (REV-053), fixado no código: o protocolo não o pode trocar.
# Os testes sintéticos põem-no a None (só então vale o hash declarado no protocolo).
SOURCE_SHA256 = "d4d8cd91cb2a552793afab379ea874d323b43e3f68a6b37756b5307c997c1d0e"
THRESHOLD = 0.65  # limiar congelado da referência; o protocolo não o pode mudar
EVENTS = ("postproc_start", "postproc_done")


def load_protocol(root: Path, version: str) -> dict:
    """Lê o protocolo da versão e confirma que é o decidido para essa versão."""
    spec = PROTOCOLS[version]
    proto = json.loads((root / spec["path"]).read_text(encoding="utf-8"))
    f = proto["filtro"]
    size, sigma = int(f["tamanho_pontos"]), Fraction(f["sigma_pontos"])
    if (proto.get("id") != version or proto.get("execucoes") != 1 or size != spec["size"]
            or sigma != Fraction(spec["size"], 6)
            or float(f["limiar_depois_do_filtro"]) != THRESHOLD or proto["fonte"]["ficheiro"] != SOURCE):
        raise ValueError(f"O protocolo não corresponde ao decidido para {version} ({spec['size']} pontos, "
                         f"sigma {spec['size']}/6, limiar 0,65, previsões da medição final, uma execução).")
    return proto


def check_preconditions(root: Path, version: str, proto: dict, log_path: Path) -> None:
    """Falha antes de ler qualquer linha se algo não estiver conforme o protocolo da versão."""
    spec = PROTOCOLS[version]
    rel = spec["path"]
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=root, capture_output=True)
    changed = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=root)
    if tracked.returncode != 0 or changed.returncode != 0:
        raise PermissionError("O protocolo tem de estar commitado e sem alterações antes de medir.")
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "src", "configs"], cwd=root,
                           capture_output=True, text=True)
    if dirty.returncode != 0 or dirty.stdout.strip():
        raise PermissionError("O código (src/) e os protocolos (configs/) têm de estar commitados antes de medir.")
    events = read_log(log_path)
    # Eventos antigos sem o campo `protocol` não contam para nenhuma versão; um protocolo fora da lista
    # é sinal de registo adulterado e bloqueia qualquer execução.
    unknown = [e for e in events
               if str(e.get("event", "")).startswith("postproc_")
               and "protocol" in e and e["protocol"] not in PROTOCOLS]
    if unknown:
        raise PermissionError("O registo de acessos tem eventos postproc_* com um protocolo fora da lista; "
                              "é preciso resolver isso antes de medir.")
    if any(e.get("event") in EVENTS and e.get("protocol") == version for e in events) or (root / spec["out"]).exists():
        raise PermissionError(f"O pós-processamento {version} já foi executado; o protocolo só permite "
                              "uma execução por versão.")
    src = root / proto["fonte"]["ficheiro"]
    if SOURCE_SHA256 is not None and proto["fonte"]["sha256"] != SOURCE_SHA256:
        raise ValueError("O protocolo declara um ficheiro de previsões diferente do da medição final (hash).")
    if sha256_of(src) != proto["fonte"]["sha256"]:
        raise ValueError("O ficheiro de previsões não é o da medição final (hash diferente).")


def order_points(df: pd.DataFrame) -> pd.DataFrame:
    """Viagens pela ordem de aparição; dentro de cada viagem, por t e depois point_id."""
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas em falta: {missing}")
    if not df["point_id"].is_unique:
        raise ValueError("point_id repetido")
    out = df.copy()
    out["_trip"] = pd.Categorical(out["id"], categories=pd.unique(out["id"]), ordered=True)
    out["_t"] = pd.to_datetime(out["t"])
    out = out.sort_values(["_trip", "_t", "point_id"], kind="mergesort")
    return out.drop(columns=["_trip", "_t"]).reset_index(drop=True)


def apply_filter(df: pd.DataFrame, threshold: float, kernel: np.ndarray) -> pd.DataFrame:
    """Acrescenta p_fishing_filtrada e predicted_filtrado; não altera as colunas originais."""
    out = df.copy()
    out["p_fishing_filtrada"] = smooth_probabilities(out["p_fishing"].to_numpy(), out["id"].to_numpy(), kernel)
    out["predicted_filtrado"] = (out["p_fishing_filtrada"] >= threshold).astype(int)
    return out


def change_summary(df: pd.DataFrame) -> dict:
    """Pontos que mudam de classe com o filtro, por sentido, e se a mudança corrige ou estraga."""
    before, after, tgt = (df[c].to_numpy() for c in ("predicted", "predicted_filtrado", "target"))
    ch = before != after
    return {
        "n_pontos": int(len(df)),
        "n_mudam": int(ch.sum()),
        "navegacao_para_pesca": int((ch & (after == 1)).sum()),
        "pesca_para_navegacao": int((ch & (after == 0)).sum()),
        "corrigidos": int((ch & (after == tgt)).sum()),
        "estragados": int((ch & (before == tgt)).sum()),
    }


def measure(df: pd.DataFrame) -> dict:
    """Tabelas por ponto e por segmento, antes e depois do filtro."""
    after = df.drop(columns=["predicted"]).rename(columns={"predicted_filtrado": "predicted"})
    if "label" not in df.columns:  # tables_for usa a etiqueta original, se existir
        df = df.assign(label=df["target"])
        after = after.assign(label=after["target"])
    return {"antes": {"ponto": tables_for(df), "segmento": segment_report(df)},
            "depois": {"ponto": tables_for(after), "segmento": segment_report(after)},
            "mudancas": change_summary(df)}


def _git_commit(root: Path) -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError("Não foi possível ler o commit atual (git rev-parse).")
    return r.stdout.strip()


def run(root: Path = ROOT, version: str = "posproc_validation_v2") -> dict:
    if version not in PROTOCOLS:
        raise ValueError(f"Versão de protocolo desconhecida: {version!r}; escolha uma de {sorted(PROTOCOLS)}.")
    root = Path(root)
    spec = PROTOCOLS[version]
    log_path = root / "results" / "access_log.jsonl"
    proto = load_protocol(root, version)
    check_preconditions(root, version, proto, log_path)
    threshold = THRESHOLD
    size = int(proto["filtro"]["tamanho_pontos"])
    sigma = Fraction(proto["filtro"]["sigma_pontos"])
    kernel = gaussian_kernel(size, float(sigma))

    # Tudo é calculado em memória antes de registar ou gravar: uma falha técnica a meio não mostra
    # resultados nem gasta a execução única. Só no fim se regista e grava.
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    df = order_points(pd.read_csv(root / proto["fonte"]["ficheiro"]))
    if not np.array_equal((df["p_fishing"] >= threshold).astype(int), df["predicted"]):
        raise ValueError("As previsões guardadas não correspondem ao limiar do protocolo.")
    df = apply_filter(df, threshold, kernel)
    res = measure(df)

    # Escrita atómica: tudo vai para uma pasta temporária, que só no fim passa a definitiva; só depois se
    # regista a execução. Uma falha na escrita não gasta a execução (a pasta temporária é apagada).
    out = root / spec["out"]
    tmp = out.with_name(out.name + ".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    try:
        _write_outputs(tmp, df, res, root, version, spec, proto, kernel, sigma, threshold)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    tmp.rename(out)
    log_access(log_path, {"event": "postproc_start", "split": "validation", "protocol": proto["id"],
                          "file": proto["fonte"]["ficheiro"], "file_sha256": proto["fonte"]["sha256"],
                          "calculo_iniciado_utc": started})
    log_access(log_path, {"event": "postproc_done", "split": "validation", "protocol": proto["id"]})
    return json.loads((out / "postproc_validation.json").read_text(encoding="utf-8"))


def _write_outputs(out, df, res, root, version, spec, proto, kernel, sigma, threshold) -> None:
    df.rename(columns={"predicted": "predicted_antes", "predicted_filtrado": "predicted_depois",
                       "p_fishing_filtrada": "p_fishing_depois"}).to_csv(
        out / "predictions_validation_postproc.csv", index=False)
    result = {
        "versao": version,
        "protocolo": proto["id"], "hash_do_protocolo": sha256_of(root / spec["path"]),
        "fonte": proto["fonte"]["ficheiro"], "fonte_sha256": proto["fonte"]["sha256"],
        "filtro": {"tamanho_pontos": int(len(kernel)), "sigma_pontos": float(sigma),
                   "pesos": kernel.tolist(), "limiar": threshold},
        "n_viagens": int(df["id"].nunique()), **res,
        "git_commit": _git_commit(root),
        "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aviso": "Uma só aplicação por versão, com o filtro fixado antes. Sem nova passagem pela CNN nem "
                 "leitura do parquet do validation; as anotações já usadas na medição final servem de novo, só para medir.",
    }
    (out / "postproc_validation.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str),
                                                 encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Pós-processamento da referência sobre as previsões já guardadas do validation.")
    parser.add_argument("--version", default="posproc_validation_v2", choices=sorted(PROTOCOLS),
                        help="versão do protocolo a aplicar (por omissão: posproc_validation_v2)")
    args = parser.parse_args(argv)
    r = run(version=args.version)
    a, d = r["antes"]["ponto"]["global"], r["depois"]["ponto"]["global"]
    sa, sd = r["antes"]["segmento"]["pesca"], r["depois"]["segmento"]["pesca"]
    print(f"{r['versao']}: exatidão {a['accuracy']:.4f} -> {d['accuracy']:.4f}; segmentos de pesca previstos "
          f"{sa['n_pred_segments']} -> {sd['n_pred_segments']} (reais {sa['n_ref_segments']}); "
          f"mudanças: {r['mudancas']}")


if __name__ == "__main__":
    sys.exit(main())
