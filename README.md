# automation-project

# Purchase Order Automation Suite

A modular Python tool that:
- Logs into a procurement portal (sanitized for public repo)
- Scrapes purchase order data with Selenium
- Normalizes item descriptions
- Writes summaries into Google Sheets
- Computes trends and item-level stats

## Tech Stack

- Python 3.10+
- Selenium + webdriver-manager
- BeautifulSoup4
- Google Sheets API via `gspread` + `oauth2client`
- openpyxl for Excel-style formatting

## Module Overview

- `browser.py` – WebDriver setup and login
- `config.py` – URLs, site codes, sheet IDs (placeholders)
- `mappings.py` – Item name and ID normalization
- `sheets_io.py` – Google Sheets helpers and timestamps
- `scrape_upcoming.py` – "WAITING ON" sheet (open POs)
- `scrape_received.py` – "CAME IN" sheet (received POs)
- `scrape_item_summary.py` – Per-item summary & metrics
- `scrape_history.py` – 2-year history & trend table
- `utils.py` – Shared date/median helpers
- `main.py` – Simple Tkinter menu to run workflows

## Running

```bash
pip install -r requirements.txt
python -m automation-project.main
