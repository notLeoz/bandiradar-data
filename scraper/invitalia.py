import requests, logging
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://www.invitalia.it"
LIST_PAGE = "https://www.invitalia.it/bandi-di-gara-e-contratti"

def fetch_invitalia() -> list[dict]:
    """Wrapper usato dal main orchestrator."""
    html = fetch_list_html()
    return parse_rows(html)


def fetch_list_html() -> str | None:
    """Scarica la pagina; se 4xx/5xx ritorna None invece di lanciare."""
    try:
        r = requests.get(LIST_PAGE, timeout=15)
        r.raise_for_status()
        return r.text
    except requests.HTTPError as exc:
        logging.warning("Invitalia: HTTP %s – scraper skip", exc.response.status_code)
        return None


def parse_rows(html: str) -> list[dict]:
    """Estrae record base {titolo, url, scadenza_str}."""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    
    table = soup.find("table")
    if not table:
        return []

    records: list[dict] = []
    for row in table.select("tr")[1:]:         
        cells = row.select("td")
        if len(cells) < 3:
            continue
        
        title = cells[0].get_text(strip=True)
        url = BASE_URL + cells[0].find("a")["href"]
        deadline_raw = cells[2].get_text(strip=True)

        records.append(
            {
                "titolo": title,
                "fonte_url": url,
                "ente": "Invitalia",
                "regione": "Nazionale",
                "scadenza": deadline_raw,
                "estrazione": datetime.utcnow().isoformat(timespec="seconds"),
            }
        )
    return records
