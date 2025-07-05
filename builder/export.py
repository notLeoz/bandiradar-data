"""
Esporta i record in
• CSV (bandi.csv)
• JSON (bandi.json)
Il CSV include tutte le colonne, mettendo per prime quelle di base.
"""

from __future__ import annotations
import csv, json, pathlib
from typing import List, Dict
from collections import OrderedDict

BASE_FIELDS = [
    "titolo", "ente", "regione", "fonte_url", "scadenza",
    "settore", "tipologia",
    "importo_min", "importo_max", "importo_flag",
    "estrazione",
]
def _all_fields(records):
    """BASE_FIELDS + extra (senza duplicati, ordine stabile)."""
    extra_ordered = OrderedDict()
    for rec in records:
        for k in rec:
            if k not in BASE_FIELDS:
                extra_ordered.setdefault(k, None)
    return BASE_FIELDS + list(extra_ordered.keys())

def save_csv(records: List[Dict], path: str | pathlib.Path = "bandi.csv") -> None:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=_all_fields(records))
        writer.writeheader()
        writer.writerows(records)

    print(f"CSV salvato: {path} ({len(records)} record)")


def save_json(records: List[Dict], path: str | pathlib.Path = "bandi.json") -> None:
    path = pathlib.Path(path)
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"JSON salvato: {path}")
