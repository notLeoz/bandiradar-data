from .invitalia import fetch_invitalia
from .incentivi_gov import fetch_incentivi
from builder.export import save_csv, save_json
from builder.ics import save_ics
from builder.enrich import enrich
from tools.slice import slice_dataset  

def run() -> None:
    records = fetch_invitalia() + fetch_incentivi()
    records = enrich(records)

    print("Totale record:", len(records))
    if not records or len(records) < 2000:
        raise SystemExit(f"{len(records)} records rilevati, open-data forse down")

    save_csv(records, "bandi.csv")
    save_json(records, "bandi.json")
    save_ics(records, "bandi.ics")

    slice_dataset(src="bandi.csv", out="slices")

if __name__ == "__main__":
    run()




