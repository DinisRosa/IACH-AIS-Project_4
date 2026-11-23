"""Acesso controlado aos conjuntos reservados (`test` e `validation`) — REV-038.

Papéis decididos pelo utilizador (REV-036): `test` = seleção (épocas, limiar, variantes) e
`validation` = medição final, aberta UMA só vez com tudo congelado.

Nada aqui concede autorização. Uma abertura só é possível se existir um ficheiro de autorização
escrito pelo utilizador (conjuntos, finalidade, número de rondas), um protocolo declarado antes de
abrir e, no caso do `validation`, uma execução congelada. Cada abertura fica registada em
`results/access_log.jsonl`. O desenvolvimento normal (`load_training_data`) continua a recusar
qualquer ficheiro que não seja de treino.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

RESERVED = ("test", "validation")
PURPOSE_OF = {"test": "selecao", "validation": "medicao_final"}


def sha256_of(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_log(log_path) -> list[dict]:
    p = Path(log_path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def log_access(log_path, event: dict) -> None:
    """Acrescenta um evento ao registo de acessos (JSON por linha; nunca se reescreve)."""
    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), **event}
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def check_access(split: str, authorization: dict, protocol: dict, log_path,
                 frozen_manifest_path=None) -> None:
    """Levanta PermissionError se a abertura do conjunto `split` não estiver autorizada.

    Verifica, por esta ordem: é um conjunto reservado; consta da autorização; a finalidade
    corresponde ao papel do conjunto; o protocolo foi declarado antes de abrir e é para este
    conjunto; o número de rondas autorizado não foi excedido; e, no `validation`, existe uma
    execução congelada e o conjunto nunca foi aberto (medição única).
    """
    if split not in RESERVED:
        raise PermissionError(f"'{split}' não é um conjunto reservado; use o carregador de treino.")
    if split not in authorization.get("conjuntos_autorizados", []):
        raise PermissionError(f"Sem autorização para abrir '{split}' (autorizados: "
                              f"{authorization.get('conjuntos_autorizados')}).")
    purpose = PURPOSE_OF[split]
    if authorization.get("finalidade") != purpose:
        raise PermissionError(f"Finalidade autorizada '{authorization.get('finalidade')}' não "
                              f"corresponde ao papel de '{split}' ('{purpose}').")
    if split == "validation" and not authorization.get("validation_autorizado", False):
        raise PermissionError("A medição final no `validation` exige autorização própria.")
    if protocol.get("conjunto") != split or not protocol.get("declarado_antes_de_abrir_o_test"):
        raise PermissionError("Protocolo ausente, para outro conjunto ou não declarado antes de abrir.")
    opened = [e for e in read_log(log_path)
              if e.get("event") == "open" and e.get("authorization") == authorization.get("id")]
    if len(opened) >= int(authorization.get("max_rondas", 0)):
        raise PermissionError(f"Rondas autorizadas esgotadas ({len(opened)}/"
                              f"{authorization.get('max_rondas')}); é preciso nova autorização.")
    if split == "validation":
        if any(e.get("event") == "open" and e.get("split") == "validation" for e in read_log(log_path)):
            raise PermissionError("O `validation` só se abre uma vez; já há uma abertura registada.")
        if frozen_manifest_path is None or not Path(frozen_manifest_path).is_file():
            raise PermissionError("A medição final exige uma execução congelada (manifesto em falta).")


def load_reserved_data(split: str, data_path, manifest_path, authorization_path, protocol_path,
                       log_path, frozen_manifest_path=None) -> pd.DataFrame:
    """Abre um conjunto reservado depois de `check_access`; regista a abertura.

    O nome do ficheiro tem de conter o nome do conjunto (`..._clean_test.parquet`) e todos os ids
    têm de constar como `split` no manifesto. A abertura é registada ANTES da leitura.
    """
    auth = _read_json(authorization_path)
    proto = _read_json(protocol_path)
    check_access(split, auth, proto, log_path, frozen_manifest_path)
    name = Path(data_path).name.lower()
    if split not in name or ("test" in name and split == "validation") or (
            "validation" in name and split == "test") or "train" in name.replace("training", ""):
        raise PermissionError(f"O ficheiro '{Path(data_path).name}' não corresponde a '{split}'.")
    log_access(log_path, {"event": "open", "split": split, "authorization": auth["id"],
                          "protocol": proto["id"], "file": Path(data_path).name,
                          "file_sha256": sha256_of(data_path)})
    manifest = pd.read_csv(manifest_path)
    split_of = dict(zip(manifest["id"].astype(str), manifest["split"].astype(str)))
    df = pd.read_parquet(data_path)
    wrong = sorted({i for i in df["id"].astype(str).unique() if split_of.get(i) != split})
    if wrong:
        raise ValueError(f"{len(wrong)} id(s) não constam como '{split}' no manifesto (ex.: {wrong[:3]}).")
    return df
