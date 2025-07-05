"""
Aggiunge ai record:
- settore (digitale, turismo, green, agro, ...)
- tipologia (fondo_perduto, credito_imposta, garanzia, ...)
- importo_min/max in euro (int), calcolati:
     1. dalle colonne numeriche originali del CSV
     2. in fallback, con regex su tutto il testo
- importo_flag  ("auto" se ottenuto dal CSV, "regex" se dal testo, "none" se mancante)
"""

from __future__ import annotations
import re, decimal
from typing import List, Dict

SECTORS = {
    "digitale":  ["digit", "ict", "software", "innovazione tecnologica"],
    "turismo":   ["turism", "hotel", "ricettiv"],
    "green":     ["energie rinnovabili", "sostenibil", "fotovoltaic", "ecolog"],
    "agro":      ["agricolt", "agro", "rural", "impresa agric"],
}

TYPES = {
    "fondo_perduto":          ["contributo a fondo perduto", "fondo perduto"],
    "credito_imposta":        ["credito d'imposta", "tax credit"],
    "garanzia":               ["garanzia", "fondo di garanzia"],
    "finanziamento_agevolato": ["finanziamento agevolato", "tasso agevolato"],
}

NUMERIC_COLUMNS = [
    "Importo_minimo", "Importo_massimo",
    "Spesa_Ammessa_min", "Spesa_Ammessa_max",
    "Agevolazione_Concedibile_min", "Agevolazione_Concedibile_max",
    "Stanziamento_incentivo",
]

EURO_RE = re.compile(r"(?:€|\bEUR?\b)\s*([0-9][0-9\.\'\s]*[0-9])", re.I)
SEP_RE  = re.compile(r"[ \.\']")

def _coerce(x) -> int | None:
    try:
        return int(float(str(x).replace(",", ".")))
    except (ValueError, TypeError):
        return None

def _parse_euro(text: str) -> list[int]:
    out = []
    for raw in EURO_RE.findall(text):
        num = SEP_RE.sub("", raw)
        try:
            n = int(decimal.Decimal(num))
            if n > 2300:          
                out.append(n)
        except decimal.InvalidOperation:
            pass
    return out

def enrich(records: List[Dict]) -> List[Dict]:
    for rec in records:
        lc = rec["titolo"].lower()
        rec["settore"]   = next((s for s,w in SECTORS.items() if any(k in lc for k in w)), "vario")
        rec["tipologia"] = next((t for t,w in TYPES.items()   if any(k in lc for k in w)), "altro")
        numeric = [
            _coerce(rec.get(col))
            for col in NUMERIC_COLUMNS + ["importo_min", "importo_max"]
            if rec.get(col) not in (None, "")
        ]
        numeric = [n for n in numeric if n is not None]

        flag = "none"
        if numeric:
            rec["importo_min"], rec["importo_max"] = min(numeric), max(numeric)
            flag = "auto"
        else:
            amounts = _parse_euro(" ".join(str(v) for v in rec.values() if isinstance(v,str)))
            if amounts:
                rec["importo_min"], rec["importo_max"] = min(amounts), max(amounts)
                flag = "regex"
            else:
                rec["importo_min"] = rec["importo_max"] = None

        rec["importo_flag"] = flag

    return records
