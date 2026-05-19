"""Seed script — carrega um lote de recebíveis a partir de um arquivo CSV.

Uso:
    python scripts/seed_receivables.py [--file caminho.csv] [--api http://localhost:8000]

Formato do CSV (com cabeçalho):
    assignor_document,product_code,face_value,currency,issue_date,due_date,external_reference

Exemplo de linha:
    36160198000118,DUPLICATA_MERCANTIL,15000.00,BRL,2026-05-19,2026-08-19,NF-2001

Códigos de produto aceitos (devem existir no banco):
    DUPLICATA_MERCANTIL
    CHEQUE_PRE_DATADO
    CONTRATO_USD
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_API = "http://localhost:8000"
DEFAULT_FILE = Path(__file__).parent / "receivables_sample.csv"


def post_receivable(api_base: str, row: dict[str, str]) -> tuple[int, dict]:
    payload = {
        "assignor_document": row["assignor_document"].strip(),
        "product_code": row["product_code"].strip().upper(),
        "face_value": {
            "amount": row["face_value"].strip(),
            "currency": row["currency"].strip().upper(),
        },
        "issue_date": row["issue_date"].strip(),
        "due_date": row["due_date"].strip(),
        "external_reference": row["external_reference"].strip(),
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{api_base}/api/v1/receivables",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed receivables from CSV")
    parser.add_argument("--file", default=str(DEFAULT_FILE), help="Caminho para o CSV")
    parser.add_argument("--api", default=DEFAULT_API, help="URL base da API")
    args = parser.parse_args()

    csv_path = Path(args.file)
    if not csv_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {csv_path}")
        sys.exit(1)

    ok = 0
    errors = 0

    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Carregando {len(rows)} recebíveis para {args.api} ...\n")

    for i, row in enumerate(rows, 1):
        status, body = post_receivable(args.api, row)
        ref = row.get("external_reference", f"linha {i}")
        if status == 201:
            print(f"  [{i:>3}] ✅  {ref}  →  id={body['id']}")
            ok += 1
        else:
            code = body.get("code", "?")
            msg = body.get("message", body)
            print(f"  [{i:>3}] ❌  {ref}  →  HTTP {status} {code}: {msg}")
            errors += 1

    print(f"\nConcluído: {ok} criados, {errors} erros.")
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
