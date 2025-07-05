"""
Scarica il CSV open-data di incentivi.gov.it e restituisce record normalizzati.
Ogni record contiene almeno:
  titolo, ente, regione, fonte_url, scadenza, estrazione
Più TUTTE le colonne numeriche originali, che serviranno a enrich.py
"""

from __future__ import annotations
import csv, io, datetime as _dt, requests

OPEN_CSV = (
    "https://www.incentivi.gov.it/sites/default/files/open-data/"
    "2025-4-5_opendata-export.csv"
)

#   I campi "di base" li rimappiamo a nomi più brevi.
#   Le colonne NUMERICHE le lasciamo con il loro nome originale (chiave identica)
#   così non perdiamo informazioni (enrich.py le leggerà tutte).
FIELD_MAP = {
    "Titolo": "titolo",
    "Soggetto_Concedente": "ente",
    "Regioni": "regione",
    "Link_istituzionale": "fonte_url",
    "Data_chiusura": "scadenza",
    "Importo_minimo": "Importo_minimo",
    "Importo_massimo": "Importo_massimo",
    "Spesa_Ammessa_min": "Spesa_Ammessa_min",
    "Spesa_Ammessa_max": "Spesa_Ammessa_max",
    "Agevolazione_Concedibile_min": "Agevolazione_Concedibile_min",
    "Agevolazione_Concedibile_max": "Agevolazione_Concedibile_max",
    "Stanziamento_incentivo": "Stanziamento_incentivo",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36 BandiRadar/1.0"
    )
}


_BASE_KEYS = {
    "titolo", "ente", "regione", "fonte_url", "scadenza", "estrazione"
}
_INTERNAL_KEYS = _BASE_KEYS | set(v for v in FIELD_MAP.values() if v not in _BASE_KEYS)


def _detect_delim(sample: str) -> str:
    return ";" if sample.count(";") > sample.count(",") else ","

def _normalize_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    if "T" in date_str and date_str[4] == "-":
        return date_str.split("T")[0]
    if date_str[4:5] == "-" and len(date_str) >= 10:
        return date_str[:10]
    if "/" in date_str:
        d, m, y = date_str.split("/")
        if len(y) == 4:
            return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    return None


def fetch_incentivi() -> list[dict]:
    resp = requests.get(OPEN_CSV, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    reader = csv.DictReader(
        io.StringIO(resp.text),
        delimiter=_detect_delim(resp.text[:1000]),
    )

    # header chiave interna (solo se presente in FIELD_MAP)
    keymap = {h: FIELD_MAP[h] for h in reader.fieldnames if h in FIELD_MAP}

    records: list[dict] = []
    for row in reader:
        rec = {k: None for k in _INTERNAL_KEYS}
        for col, internal in keymap.items():
            raw = (row.get(col) or "").strip()
            if raw:                     
                rec[internal] = raw
        rec["scadenza"] = _normalize_date(rec["scadenza"])
        if rec["titolo"] and rec["fonte_url"]:
            rec["estrazione"] = _dt.datetime.utcnow().isoformat(timespec="seconds")
            records.append(rec)

    print(f"Incentivi.gov record estratti: {len(records)}")
    return records
