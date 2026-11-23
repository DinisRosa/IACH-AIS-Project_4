"""Congela a CNN de referência depois da seleção no `test` (REV-038).

Copia o checkpoint escolhido para uma pasta própria e grava `baseline_frozen.json` com: época,
limiar, hashes do checkpoint, do scaler e da seleção, configuração do treino, ids do protocolo
e da autorização, commit do código e aviso de que o `validation` NÃO foi aberto. Não abre nenhum
conjunto reservado e não concede acesso a nenhum. `verify_frozen` volta a calcular os hashes.

Execução (a partir da raiz do projeto, depois de `select_on_test`):
    iach-ais-venv-4/bin/python -m ais.cli.freeze_baseline [results/phase1_select] [results/baseline_frozen]
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from ais.phase1.artifacts import load_checkpoint
from ais.phase1.reserved import read_log, sha256_of

ROOT = Path(__file__).resolve().parents[3]


def _git_commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()


def freeze_baseline(run_dir, out_dir, log_path=None) -> dict:
    run_dir, out_dir = Path(run_dir), Path(out_dir)
    sel = json.loads((run_dir / "selection_test.json").read_text(encoding="utf-8"))
    ck_name = sel["candidatos"][str(sel["epoca_escolhida"])]["ficheiro"]
    src = run_dir / "checkpoints" / ck_name
    if sha256_of(src) != sel["hashes"]["checkpoint_escolhido"]:
        raise ValueError("O checkpoint escolhido mudou desde a seleção (hash diferente).")
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "checkpoint_frozen.pt"
    shutil.copy2(src, dst)
    _, ck = load_checkpoint(dst)
    validation_opened = any(e.get("split") == "validation" and e.get("event") == "open"
                            for e in read_log(log_path)) if log_path else None
    manifest = {
        "congelado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(),
        "epoca": int(sel["epoca_escolhida"]), "limiar": float(sel["limiar_escolhido"]),
        "checkpoint": dst.name, "checkpoint_sha256": sha256_of(dst),
        "origem_do_checkpoint": str(src),
        "scaler_do_treino": ck["scaler"], "canais_de_entrada": ck["input_channels"],
        "config_do_treino": ck["config"],
        "selecao": {"ficheiro": "selection_test.json", "sha256": sha256_of(run_dir / "selection_test.json"),
                    "protocolo": sel["protocolo"], "autorizacao": sel["autorizacao"],
                    "possivelmente_nao_convergiu": sel["possivelmente_nao_convergiu"]},
        "validation_aberto_ate_agora": validation_opened,
        "aviso": "Baseline congelada. Nada muda a partir daqui (épocas, limiar, pesos). O conjunto "
                 "`validation` só se abre no fim do projeto, uma só vez, com todas as variantes e "
                 "autorização nova do utilizador. Esta congelação não concede acesso a nenhum conjunto.",
    }
    (out_dir / "baseline_frozen.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def verify_frozen(out_dir) -> dict:
    """Confirma que o checkpoint congelado ainda corresponde ao manifesto."""
    out_dir = Path(out_dir)
    m = json.loads((out_dir / "baseline_frozen.json").read_text(encoding="utf-8"))
    return {"checkpoint_confere": sha256_of(out_dir / m["checkpoint"]) == m["checkpoint_sha256"],
            "epoca": m["epoca"], "limiar": m["limiar"]}


def main(run: str | None = None, out: str | None = None) -> None:
    run_dir = ROOT / (run or "results/phase1_select")
    out_dir = ROOT / (out or "results/baseline_frozen")
    m = freeze_baseline(run_dir, out_dir, ROOT / "results" / "access_log.jsonl")
    print(f"baseline congelada: época {m['epoca']}, limiar {m['limiar']}, "
          f"checkpoint {m['checkpoint_sha256'][:12]}…; validation aberto: {m['validation_aberto_ate_agora']}")


if __name__ == "__main__":
    main(*(sys.argv[1:3]))
