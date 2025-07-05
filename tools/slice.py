"""
Genera CSV filtrati regione × settore
    python tools/slice.py --src bandi.csv --out slices
"""

import csv, argparse, pathlib, re, hashlib
from typing import List, Dict

MAX_LEN = 40



def _slug(s: str) -> str:
    base = re.sub(r"[^a-z0-9_]", "", s.replace(" ", "_").lower())
    base = re.sub(r"(_)\1+", r"\1", base)
    if len(base) <= MAX_LEN:
        return base
    digest = hashlib.md5(base.encode()).hexdigest()[:6]
    return f"{base[:MAX_LEN]}_{digest}"


def _normalize_region(raw: str) -> str:
    """
    Converte le varianti strane del dataset in un nome pulito.
    - Liste separate da virgola -> 'Nazionale'
    - Stringhe con slash -> parte prima dello slash
    - Qualunque cosa contenga 'valle' e 'aosta' -> 'Valle d'Aosta'
    - Gestisce anche 'Trentino-Alto Adige/Südtirol'
    """
    txt = raw.strip()
    if not txt:
        return "Nazionale"

    low = txt.lower()

    if "," in txt:
        return "Nazionale"

    if "valle" in low and "aosta" in low:
        return "Valle d'Aosta"

    if "trentino" in low and "alto" in low and "adige" in low:
        return "Trentino-Alto Adige/Südtirol"

    if "/" in txt:
        txt = txt.split("/")[0]

    return txt.title()



def slice_dataset(src: str, out: str) -> None:
    out_path = pathlib.Path(out)
    out_path.mkdir(parents=True, exist_ok=True)

    with open(src, newline="", encoding="utf-8") as fp:
        rows: List[Dict] = list(csv.DictReader(fp))

    by_key: dict[tuple[str, str], list[Dict]] = {}
    for r in rows:
        regione = _normalize_region(r.get("regione", ""))
        settore = (r.get("settore") or "vario").strip()
        by_key.setdefault((regione, settore), []).append(r)

    for (reg, sec), recs in by_key.items():
        dir_reg = out_path / _slug(reg)
        dir_reg.mkdir(exist_ok=True)
        dst = dir_reg / f"{_slug(sec)}.csv"

        with dst.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=recs[0].keys())
            w.writeheader()
            w.writerows(recs)

    print(f"Slice creati: {len(by_key)} (cartella '{out}')")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="bandi.csv")
    ap.add_argument("--out", default="slices")
    args = ap.parse_args()
    slice_dataset(src=args.src, out=args.out)
