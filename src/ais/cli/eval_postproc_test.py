"""Efeito do pós-processamento nas previsões já guardadas da referência no `test` (REV-058).

Aplica o filtro gaussiano (sigma = tamanho/6, limiar 0,65) às previsões da referência congelada no `test`
(conjunto de seleção) e mede antes e depois, por ponto e por segmento, com as mesmas funções da aplicação ao
`validation`. Tamanho escolhido pelo utilizador: 301; 13, 201 e 401 só como contexto. Não abre parquets, não
corre a CNN e recusa o `validation`. Exige `configs/authorizations/test_postproc_eval.json` e regista a leitura.

Execução (a partir da raiz do projeto):
    iach-ais-venv-4/bin/python -m ais.cli.eval_postproc_test
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from ais.cli.postproc_validation import THRESHOLD, apply_filter, measure, order_points
from ais.phase1.postprocessing import gaussian_kernel
from ais.phase1.reserved import log_access, sha256_of

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "results/baseline_frozen/predictions_test_baseline.csv"
AUTH = "configs/authorizations/test_postproc_eval.json"
SIZES = (13, 201, 301, 401)
CHOSEN = 301


def summary_row(size: int | None, res: dict, key: str) -> dict:
    g = res[key]["ponto"]["global"]
    sp, sn = res[key]["segmento"]["pesca"], res[key]["segmento"]["navegacao"]
    return {"janela": size, "exatidao": g["accuracy"], "erros": g["n_errors"],
            "f1_pesca": g["por_classe"]["pesca"]["f1"], "f1_navegacao": g["por_classe"]["navegação"]["f1"],
            "seg_pesca_previstos": sp["n_pred_segments"], "seg_pesca_reais": sp["n_ref_segments"],
            "seg_pesca_pares": sp["n_matched"], "seg_pesca_f1": sp["f1"],
            "seg_nav_previstos": sn["n_pred_segments"], "seg_nav_reais": sn["n_ref_segments"],
            "seg_nav_pares": sn["n_matched"], "seg_nav_f1": sn["f1"],
            "erro_inicio_pesca_mediana_s": sp["median_abs_start_error_s"],
            "erro_fim_pesca_mediana_s": sp["median_abs_end_error_s"]}


def evaluate(df: pd.DataFrame, sizes=SIZES) -> dict:
    df = order_points(df)
    if not np.array_equal((df["p_fishing"] >= THRESHOLD).astype(int), df["predicted"]):
        raise ValueError("As previsões guardadas não correspondem ao limiar 0,65.")
    out, rows, trips = {}, [], {}
    for w in sizes:
        res = measure(apply_filter(df, THRESHOLD, gaussian_kernel(w, w / 6)))
        if not rows:
            rows.append(summary_row(None, res, "antes"))
            trips["antes"] = {i: m["accuracy"] for i, m in res["antes"]["ponto"]["por_viagem"].items()}
        rows.append(summary_row(w, res, "depois"))
        trips[str(w)] = {i: m["accuracy"] for i, m in res["depois"]["ponto"]["por_viagem"].items()}
        out[str(w)] = {"mudancas": res["mudancas"]}
    return {"resumo": rows, "exatidao_por_viagem": trips, "mudancas": out}


def main() -> None:
    auth = json.loads((ROOT / AUTH).read_text(encoding="utf-8"))
    if "test" not in auth["conjuntos_autorizados"] or auth.get("validation_autorizado"):
        raise PermissionError("Autorização inválida.")
    src = ROOT / SOURCE
    log_access(ROOT / "results" / "access_log.jsonl",
               {"event": "postproc_test_eval", "split": "test", "authorization": auth["id"], "file": SOURCE,
                "file_sha256": sha256_of(src), "janelas": list(SIZES)})
    res = evaluate(pd.read_csv(src))
    res.update({"fonte": SOURCE, "fonte_sha256": sha256_of(src), "janela_escolhida": CHOSEN, "limiar": THRESHOLD,
                "sigma": "tamanho/6", "criado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    out = ROOT / "results" / "postproc_window_analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / "test_eval.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    pd.DataFrame(res["resumo"]).to_csv(out / "test_eval_resumo.csv", index=False)
    print(pd.DataFrame(res["resumo"]).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
