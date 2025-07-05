![CI](https://github.com/notLeoz/bandiradar/actions/workflows/build.yml/badge.svg)
# BandiRadar · Web-scraping demo 

> Non è un prodotto commerciale.  
> Dataset rilasciato solo per uso personale o di studio (CC BY-NC 4.0).

---

## Descrizione progetto
* Scarica il CSV open-data di **incentivi.gov.it**  
* Normalizza i campi, arricchisce **settore · tipologia · importi**  
* Esporta:
  * `bandi.csv`  – dataset completo (separator `;`)
  * `bandi.json` – version machine-readable
  * `bandi.ics`  – calendario scadenze
  * `slices/`    – sub-CSV regione × settore
* GitHub Action (`.github/workflows/build.yml`)  
  genera gli artefatti on-demand (trigger **workflow-dispatch**).

---

## Quick-start (locale)

```bash
git clone https://github.com/notLeoz/bandiradar-data.git
cd bandiradar-data
pip install -r requirements.txt
python -m scraper.main          
```

## Dataset di esempio
La cartella `data_sample/` contiene 50 righe estratte dal CSV completo

## Schema colonne principali

| campo          | descrizione                                                                      |
|----------------|----------------------------------------------------------------------------------|
| **titolo**     | nome del bando / incentivo                                                       |
| **ente**       | ministero, regione, comune, CCIAA…                                               |
| **regione**    | regione di validità (<i>Nazionale</i> se multi-regione)                          |
| **settore**    | <code>digitale</code> - <code>turismo</code> - <code>green</code> - <code>agro</code> - <code>vario</code> |
| **tipologia**  | <code>fondo_perduto</code> - <code>credito_imposta</code> - <code>garanzia</code> ...|
| **importo_min**| importo minimo rilevato (€, intero)                                              |
| **importo_max**| importo massimo rilevato (€, intero)                                             |
| **importo_flag** | <code>manual</code> \| <code>regex</code> \| <code>none</code> — origine del dato importo |
| **scadenza**   | formato <kbd>AAAA-MM-GG</kbd>  (vuoto = bando a sportello)                       |

> Le colonne numeriche originali (es. <code>Importo_massimo</code>)  
> sono conservate **tali e quali** nel CSV / JSON completo per analisi avanzate.

---

## Licenze

| componente | licenza | uso consentito |
|------------|---------|----------------|
| **Codice** | MIT ([`LICENSE_CODE`](./LICENSE_CODE)) | uso libero, anche commerciale |
| **Dati**   | CC BY-NC 4.0 ([`LICENSE_DATA`](./LICENSE_DATA)) | uso non commerciale; vietata rivendita |
