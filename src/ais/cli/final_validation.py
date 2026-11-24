"""Medição final no conjunto `validation` do modelo escolhido (Marcos 6 e 7, REV-053). UMA só abertura.

Papéis (REV-036): `test` seleciona; `validation` é a medição final, aberta uma só vez com tudo congelado.
Só corre com `configs/authorizations/validation_final.json` (autorização própria, `validation_autorizado`),
o protocolo `configs/selection_protocol_validation.json` declarado antes e um manifesto de congelação do
modelo escolhido; a abertura fica em `results/access_log.jsonl` e uma segunda é recusada
(`ais.phase1.reserved`).

Fluxo, por esta ordem:
  1. verifica que os três modelos (referência, J0, J50) estão congelados e que o `validation` nunca foi aberto;
  2. **escolhe o modelo** pelo critério declarado no protocolo, usando só resultados do `test`, e grava
     `results/final_validation/model_choice.json` ANTES de abrir o `validation`;
  3. abre o `validation` (uma vez) e aplica o modelo escolhido, com a época e o limiar congelados;
  4. mede por ponto, por viagem e por segmento (IoU 0,5, sem suavizar) e grava
     `final_validation.json` e `predictions_validation.csv`.
Não mede os outros modelos, não escolhe nem ajusta nada com o `validation`.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.final_validation
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import torch

from ais.cli.freeze_baseline import verify_frozen
from ais.cli.select_windows_on_test import segment_report
from ais.phase1.artifacts import load_checkpoint
from ais.phase1.data import apply_scaler, build_full_sequences, validate_training_data
from ais.phase1.inference import predict, tables_for
from ais.phase1.reserved import load_reserved_data, log_access, read_log, sha256_of
from ais.phase1.windows import WindowSet, predict_window_table

ROOT = Path(__file__).resolve().parents[3]
ORDER = ["baseline", "J0", "J50"]  # ordem de desempate do protocolo
FROZEN = {"baseline": ("results/baseline_frozen", "baseline"),
          "J0": ("results/windows_j0_frozen", "j0"),
          "J50": ("results/windows_j50_frozen", "j50")}
TEST_TABLES = {"baseline": ("results/baseline_frozen/test_segment_results.json", "metricas_no_test"),
               "J0": ("results/windows_j0/selection_test.json", "metricas_no_test_com_limiar_escolhido"),
               "J50": ("results/windows_j50/selection_test.json", "metricas_no_test_com_limiar_escolhido")}


def macro_f1_of(tables: dict) -> float:
    c = tables["global"]["por_classe"]
    return (c["navegação"]["f1"] + c["pesca"]["f1"]) / 2


def choose_model(test_tables: dict[str, dict]) -> tuple[str, list[dict]]:
    """Critério do protocolo: maior F1 médio por ponto no `test`; empate: maior exatidão; depois a ordem."""
    rows = [{"modelo": m, "f1_medio_por_ponto_no_test": macro_f1_of(t),
             "exatidao_no_test": t["global"]["accuracy"]} for m, t in test_tables.items()]
    ranked = sorted(rows, key=lambda r: (-round(r["f1_medio_por_ponto_no_test"], 12),
                                         -round(r["exatidao_no_test"], 12), ORDER.index(r["modelo"])))
    return ranked[0]["modelo"], ranked


def _git_commit(root: Path) -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip()


def apply_frozen(model_name: str, ckpt_path: Path, threshold: float, seqs_raw, labels, device):
    """Previsões por ponto do modelo congelado (viagem completa ou janelas), com o limiar congelado."""
    model, ck = load_checkpoint(ckpt_path, device)
    seqs = [apply_scaler(s, ck["scaler"]) for s in seqs_raw]
    if model_name == "baseline":
        return predict(model, seqs, labels, device, threshold), ck
    cfg = ck["config"]
    ws = WindowSet(seqs, cfg["window_length"], cfg["overlap"])
    return predict_window_table(model, ws, labels, device, threshold), ck


def run_final_validation(root: Path = ROOT, device: str = "cpu") -> dict:
    root = Path(root)
    dev = torch.device(device)
    log_path = root / "results" / "access_log.jsonl"
    out = root / "results" / "final_validation"
    out.mkdir(parents=True, exist_ok=True)

    # ---- 1. pré-condições (sem abrir o validation) ----
    metas = {}
    for name, (d, label) in FROZEN.items():
        if not verify_frozen(root / d, label=label)["checkpoint_confere"]:
            raise ValueError(f"O modelo congelado '{name}' não confere com o seu manifesto (hash).")
        metas[name] = json.loads((root / d / f"{label}_frozen.json").read_text(encoding="utf-8"))
    if any(e.get("split") == "validation" for e in read_log(log_path)):
        raise PermissionError("O `validation` já foi aberto; a medição final é única.")

    # ---- 2. escolha do modelo, só com o test, gravada ANTES de abrir ----
    test_tables = {}
    for name, (rel, key) in TEST_TABLES.items():
        test_tables[name] = json.loads((root / rel).read_text(encoding="utf-8"))[key]
    chosen, ranking = choose_model(test_tables)
    proto_path = root / "configs" / "selection_protocol_validation.json"
    auth_path = root / "configs" / "authorizations" / "validation_final.json"
    choice = {"escolhido": chosen, "ranking_no_test": ranking, "protocolo": json.loads(
        proto_path.read_text(encoding="utf-8"))["id"], "hash_do_protocolo": sha256_of(proto_path),
        "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nota": "Escolha feita só com o test, antes de abrir o validation."}
    (out / "model_choice.json").write_text(json.dumps(choice, indent=2, ensure_ascii=False), encoding="utf-8")
    log_access(log_path, {"event": "model_chosen", "model": chosen, "protocol": choice["protocolo"]})

    # ---- 3. única abertura do validation ----
    d, label = FROZEN[chosen]
    frozen_manifest = root / d / f"{label}_frozen.json"
    data_path = root / "data" / "123_fishing_trajs_clean_validation.parquet"
    manifest_path = root / "manifests" / "split_manifest_seed42.csv"
    df = load_reserved_data("validation", data_path, manifest_path, auth_path, proto_path, log_path,
                            frozen_manifest_path=frozen_manifest)
    report = validate_training_data(df)
    labels = df[["point_id", "label"]]
    meta = metas[chosen]
    pred, ck = apply_frozen(chosen, root / d / meta["checkpoint"], meta["limiar"],
                            build_full_sequences(df), labels, dev)
    pred.to_csv(out / "predictions_validation.csv", index=False)

    tables = tables_for(pred)
    result = {
        "modelo": chosen, "epoca": meta["epoca"], "limiar": meta["limiar"],
        "n_pontos": report["n_rows"], "n_viagens": report["n_ids"],
        "validation": tables, "segmentos_validation": segment_report(pred),
        "test_do_mesmo_modelo": test_tables[chosen],
        "ranking_no_test": ranking,
        "hashes": {"checkpoint": meta["checkpoint_sha256"], "ficheiro_validation": sha256_of(data_path),
                   "manifesto": sha256_of(manifest_path), "protocolo": sha256_of(proto_path),
                   "autorizacao": sha256_of(auth_path)},
        "git_commit": _git_commit(root),
        "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aviso": "Medição final única no conjunto validation, só do modelo escolhido. Nada foi escolhido nem "
                 "ajustado com estes resultados. Os outros modelos não foram medidos no validation.",
    }
    (out / "final_validation.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str),
                                              encoding="utf-8")
    log_access(log_path, {"event": "final_measurement_done", "split": "validation", "model": chosen,
                          "protocol": choice["protocolo"]})
    return result


def main() -> None:
    r = run_final_validation()
    g = r["validation"]["global"]
    print(f"modelo escolhido: {r['modelo']} (época {r['epoca']}, limiar {r['limiar']}); "
          f"validation: {r['n_viagens']} viagens, {r['n_pontos']} pontos; exatidão {g['accuracy']:.4f} "
          f"(regra da maioritária {g['accuracy_maioritaria']:.4f})")


if __name__ == "__main__":
    sys.exit(main())
