"""
Scraping logic for fully received purchase orders.

Exposes:
    process_received_orders(driver) -> list[list[Any]]
"""
from __future__ import annotations
from typing import Any, List
import time, re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from . import config, mappings
from .browser import go_home

from datetime import datetime, timedelta

from selenium.common.exceptions import NoSuchElementException

from .browser import get_driver
from .sheets_io import open_sheet, auto_stamp_gsheet


# --------------------------------------------------
# PRECESS RECEIVED ORDERS W/ HELPER
# --------------------------------------------------

def get_existing_pos_and_latest_date():
    ws_g = open_sheet("CAME IN")
    data = ws_g.get("B11:L1000")

    existing_pos = set()
    latest_date = None
    for row in data:
        if len(row) >= 1 and row[0]:
            # Try to extract from HYPERLINK formula
            m = re.search(r'HYPERLINK\(".*?","([^"]+)"\)', str(row[0]))
            if m:
                po = m.group(1).strip()
            else:
                # Fallback: strip whitespace, just in case
                po = str(row[0]).strip()
            existing_pos.add(po)
        if len(row) >= 3 and row[2]:
            try:
                dt = datetime.strptime(str(row[2]), "%m/%d/%Y")
                if not latest_date or dt > latest_date:
                    latest_date = dt
            except Exception:
                pass

    return existing_pos, latest_date

def process_received_orders() -> list[list[Any]]:
    print("📦 Scraping received orders via PO Search…")
    driver = get_driver()
    wait = WebDriverWait(driver, 15)

    # Rolling window: last 24 months for CAME IN (tiny patch)
    cutoff_date = datetime.now() - timedelta(days=730)

    # 1) Get existing PO numbers and latest date from the sheet
    ws_g = open_sheet("CAME IN")
    old_data = ws_g.get("B11:L1000")

    existing_pos, latest_date_in_sheet = get_existing_pos_and_latest_date()

    # 2) Navigate to received POs
    el = wait.until(EC.element_to_be_clickable((By.ID, "linkpitmenu_section_20")))
    el.click()
    el = wait.until(EC.element_to_be_clickable((By.ID, "linkpitmenu_item_230")))
    el.click()

    # Status dropdown
    status_span = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[starts-with(@id,'select2-POStatusID') and contains(@class,'selection__rendered')]")
    ))
    status_span.click()

    # Wait for dropdown option
    received_option = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//li[contains(@class,'select2-results__option') and normalize-space(.)='fully received, reconciled']")
    ))
    received_option.click()

    # Wait for and click the Search POs button
    search_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//input[@type='submit' and @value='Search POs']")
    ))
    search_btn.click()

    # Wait for results table to load
    wait.until(EC.presence_of_element_located(
        (By.XPATH, f"//td/a[contains(text(),'{config.SITE_CODE}')]")
    ))

    po_links = driver.find_elements(By.XPATH, f"//td/a[contains(text(),'{config.SITE_CODE}')]")
    new_rows = []
    seen = set()

    for link in po_links:
        td = link.find_element(By.XPATH, "./parent::td")
        po_full_text = td.text.strip()  # includes date
        po = link.text.strip()
        date_match = re.search(r'\((\d{2}/\d{2}/\d{4})\)', po_full_text)
        if not date_match:
            continue  # skip if no date

        try:
            po_date_obj = datetime.strptime(date_match.group(1), "%m/%d/%Y")
            # tiny patch: rolling window instead of year==2025
            if po_date_obj < cutoff_date:
                print(f"⏩ Reached older PO {po} ({po_date_obj.strftime('%Y-%m-%d')}); stopping scan.")
                break  # stop scanning older results
        except Exception:
            continue  # skip if date can't be parsed

        po = po_full_text.split()[0].strip()
        if po in seen or po in existing_pos:
            # tiny patch: explicit duplicate log
            print(f"⏩ Skipping duplicate PO {po} (already in sheet or this run)")
            continue
        seen.add(po)

        url = link.get_attribute("href")
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[1])

        # Wait for PO detail page to load
        wait.until(EC.visibility_of_element_located((By.ID, "PODatePlaced_DISP")))

        od_text = driver.find_element(By.ID, "PODatePlaced_DISP").text.strip()
        rd_text = driver.find_element(By.ID, "DateComplete_DISP").text.strip()
        fmt = "%m/%d/%Y"

        try:
            rd_date = datetime.strptime(rd_text, fmt)
            # tiny patch: rolling window instead of year==2025
            if rd_date < cutoff_date:
                print(f"⏩ Skipping PO {po} with received date {rd_date.strftime('%Y-%m-%d')} (older than window)")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
        except Exception:
            pass

        try:
            od_date = datetime.strptime(od_text, fmt)
            arrived_days = (rd_date - od_date).days
            ai_str = f"{arrived_days} days"
        except Exception:
            ai_str = ""

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # --- NEW: Grab Unit Cost from PO detail page ---
        unit_cost_div = soup.find(id="UnitCostStart_DISP")
        if unit_cost_div:
            try:
                price_per_unit = f"{float(unit_cost_div.text.strip()):.2f}"
            except ValueError:
                price_per_unit = ""
        else:
            price_per_unit = ""

        invoice_hdr = None
        for hdr in soup.find_all("td", class_="SecHeader"):
            if "CAD-Invoice" in hdr.get_text():
                invoice_hdr = hdr
                break
        received_col = 12 if invoice_hdr else 11

        idx = 1
        while True:
            idf = soup.find(id=f"{idx}_1")
            if not idf:
                break

            rf = soup.find(id=f"{idx}_{received_col}")
            if not rf:
                idx += 1
                continue

            # Extract quantity as before
            try:
                qty_rec = int(float(rf.get_text(strip=True).replace(",", "")))
            except ValueError:
                idx += 1
                continue

            iid      = idf.get_text(strip=True)
            iurl     = f"{config.BASE_PO_DOMAIN}" + idf.find("a")["href"]
            raw_desc = soup.find(id=f"{idx}_2").get_text(strip=True)
            desc_trunc = mappings.truncate_desc(raw_desc)
            clean = mappings.normalize_name(desc_trunc, iid)

            # --- Extract Price Per Unit for THIS row (if present) ---
            price_per_unit = ""
            cost_td = soup.find(id=f"{idx}_4")
            if cost_td:
                price_div = cost_td.find("div", id="InvoiceCostOC_DISP")
                if price_div:
                    try:
                        price_per_unit = f"{float(price_div.get_text(strip=True)):0.2f}"
                    except Exception:
                        price_per_unit = price_div.get_text(strip=True)
                else:
                    price_per_unit = ""
            else:
                price_per_unit = ""

            # --- New row ---
            new_rows.append((
                po, url,
                od_text, rd_text, ai_str,
                iid, iurl,
                clean, str(qty_rec), price_per_unit
            ))
            idx += 1

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    driver.quit()

    # 3) Append new rows only
    next_row = len(old_data) + 11 
    headers = [
        "PO #", "Order Date", "Received Date", "Arrived In",
        "Item ID", "Description", "Quantity Received", "Price Per Unit"
    ]
    ws_g.update(
        range_name="B10:I10", 
        values=[headers],
        value_input_option="USER_ENTERED"
    )
    auto_stamp_gsheet(ws_g)

    data = [[
        f'=HYPERLINK("{url}","{po}")',
        od_text, rd_text, ai_str,
        f'=HYPERLINK("{iurl}","{iid}")',
        clean, qty, price
    ] for po, url, od_text, rd_text, ai_str, iid, iurl, clean, qty, price in new_rows]

    if data:
        # tiny patch: write starting at B{next_row} (true append), not always B11
        ws_g.update(
            values=data,
            range_name=f"B{next_row}",
            value_input_option="USER_ENTERED"
        )
        print(f"✅ Appended {len(data)} new POs to CAME IN (starting at row {next_row})")
    else:
        print("No new POs to append.")