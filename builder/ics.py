from __future__ import annotations
from typing import Sequence, Dict
from datetime import datetime, timezone
from pathlib import Path

ICS_HEADER = """BEGIN:VCALENDAR
VERSION:2.0
METHOD:PUBLISH
PRODID:-//BandiRadar//IT
CALSCALE:GREGORIAN
X-WR-CALNAME:BandiRadar
X-WR-CALDESC:Scadenze bandi e incentivi italiani
"""

ICS_FOOTER = "END:VCALENDAR\n"


def _mk_uid(idx: int) -> str:
    """UID univoco per evento (richiesto dallo standard iCal)."""
    return f"bandiradar-{idx}@bandiradar.local"


def save_ics(records: Sequence[Dict], dst: str | Path = "bandi.ics") -> None:
    """
    Crea un file ICS con un VEVENT per ciascun record che possiede la chiave 'scadenza'.
    Ogni evento è 'all-day' (DTSTART value-date) per semplificare l'import.
    summary -> titolo
    description -> fonte_url
    """
    lines: list[str] = [ICS_HEADER]

    utc_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for idx, rec in enumerate(records):
        date = rec.get("scadenza")
        if not date:
            continue  

        date_compact = date.replace("-", "")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{_mk_uid(idx)}",
                f"DTSTAMP:{utc_now}",
                f"DTSTART;VALUE=DATE:{date_compact}",
                f"SUMMARY:{rec['titolo']}",
                f"DESCRIPTION:{rec['fonte_url']}",
                "END:VEVENT",
            ]
        )

    lines.append(ICS_FOOTER)
    Path(dst).write_text("\n".join(lines), encoding="utf-8")
    n_events = (len(lines) - 2) // 7  
    print(f"Salvato {dst} con {n_events} eventi")
