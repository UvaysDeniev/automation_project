from __future__ import annotations
from typing import Any, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, re
from bs4 import BeautifulSoup

from . import config
from . import mappings
from .browser import get_driver
from .sheets_io import open_sheet, clear_range, auto_stamp_gsheet

# --------------------------------------------------
# Upcoming Order Helper
# --------------------------------------------------

def get_item_median_delivery():
    """Returns {item_id: median_days} from ITEM SUMMARY tab (B11:D)"""
    ws_summary = open_sheet("ITEM SUMMARY")
    rows = ws_summary.get("B11:D1000")
    med_map = {}
    for row in rows:
        if len(row) < 3:
            continue
        # Extract item_id from HYPERLINK formula (or fallback to plain)
        match = re.search(r'HYPERLINK\("[^"]+","([^"]+)"\)', str(row[0]))
        item_id = match.group(1) if match else str(row[0])
        med_days = row[2].strip() if row[2].strip() else "No Data"
        med_map[item_id] = med_days
    return med_map


# --------------------------------------------------
# Upcoming Order
# --------------------------------------------------

#Scrape open purchase orders and write outstanding item lines
#    into the WAITING ON sheet.
def process_upcoming_orders():
    
    driver = get_driver()
    wait = WebDriverWait(driver, 15)
    el = wait.until(EC.element_to_be_clickable((By.ID, "linkpitmenu_section_20")))
    el.click()
    el = wait.until(EC.element_to_be_clickable((By.ID, "linkpitmenu_item_280")))
    el.click()

    links = driver.find_elements(
    By.XPATH,
    f"//td/a[contains(text(),'{config.SITE_CODE}')]"
    )


    rows = []

    for idx, link in enumerate(links, 1):
        po_num = link.text.strip()
        po_url = link.get_attribute("href")

        driver.execute_script("window.open(arguments[0]);", po_url)
        driver.switch_to.window(driver.window_handles[1])
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "PODatePlaced_DISP")))

        try:
            po_date = driver.find_element(By.ID, "PODatePlaced_DISP").text.strip()
        except:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            date_txt = re.search(r"\b\d{2}/\d{2}/\d{4}\b", soup.get_text())
            po_date = date_txt.group() if date_txt else "Unknown"

        soup = BeautifulSoup(driver.page_source, "html.parser")
        tables = soup.find_all('table')
        header_row = None
        for table in tables:
            tr_list = table.find_all('tr')
            for tr in tr_list:
                ths = tr.find_all('th')
                tds = tr.find_all('td')
                if ths and len(ths) >= 6:
                    header_row = tr
                    break
                elif tds and len(tds) >= 6 and any('SecHeader' in cls for td in tds for cls in (td.get('class', []) if td.get('class', []) else [])):
                    header_row = tr
                    break
            if header_row:
                break

        if not header_row:
            print(f"[{po_num}] ⚠️ No header row found in PO detail. Skipping.")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

        header_cells = header_row.find_all(['th', 'td'])
        # Build a map of (col_name, id_suffix) for key columns
        col_suffix_map = {}
        for i, cell in enumerate(header_cells):
            text = cell.get_text(strip=True).lower()
            m = re.search(r'col-(\d+)$', cell.get('id',''))
            if not m: continue
            idx = m.group(1)
            if 'item' in text and 'id' in text: col_suffix_map['item no (id)'] = idx
            elif 'description' in text: col_suffix_map['description'] = idx
            elif 'quantity' in text: col_suffix_map['quantity'] = idx
            elif 'received' in text: col_suffix_map['received'] = idx

        data_rows = list(header_row.find_next_siblings('tr'))

        for data_row in data_rows:
            cells = data_row.find_all('td')
            if len(cells) < 1:
                continue

            # Build a dict of col_suffix->cell for this data row
            cell_map = {}
            for cell in cells:
                cid = cell.get('id', '')
                m = re.search(r'_(\d+)$', cid)
                if m:
                    cell_map[m.group(1)] = cell

            try:
                qty_cell = cell_map.get(col_suffix_map['quantity'])
                rec_cell = cell_map.get(col_suffix_map['received'])
                if not qty_cell or not rec_cell:
                    continue
                qty_ord_raw = qty_cell.get_text(strip=True).replace(",", "")
                qty_rec_raw = rec_cell.get_text(strip=True).replace(",", "")
                qty_ord = int(float(qty_ord_raw)) if qty_ord_raw.replace('.', '', 1).isdigit() else 0
                qty_rec = int(float(qty_rec_raw)) if qty_rec_raw.replace('.', '', 1).isdigit() else 0
            except Exception:
                continue

            remaining = qty_ord - qty_rec
            if remaining == 0:
                continue

            item_cell = cell_map.get(col_suffix_map.get('item no (id)', '1'), None)
            if not item_cell:
                continue
            a_tag = item_cell.find('a')
            item_id = a_tag.get_text(strip=True) if a_tag else item_cell.get_text(strip=True)
            item_url = ("https://example-procurement.com" + a_tag['href']) if a_tag else ""

            desc_cell = cell_map.get(col_suffix_map.get('description', '2'), None)
            desc = desc_cell.get_text(strip=True) if desc_cell else ""
            desc_trunc = mappings.truncate_desc(desc)
            clean = mappings.normalize_name(desc_trunc, item_id)


            rows.append((po_num, po_url, po_date, item_id, item_url, clean, remaining))

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(.5)

    driver.quit()

    item_to_meddays = get_item_median_delivery()

    ws_g = open_sheet("WAITING ON")
    clear_range(ws_g, "B11:L1000")  
    auto_stamp_gsheet(ws_g)


    headers = [
        "PO #", "Order\nDate", "Item ID", "Description", "Quantity in\n reorder", "Median Delivery (Days)"
    ]
    ws_g.update(range_name="B10:G10", values=[headers], value_input_option="USER_ENTERED")

    data = [
        [
            f'=HYPERLINK("{url}","{po}")',
            date,
            f'=HYPERLINK("{iurl}","{iid}")',
            desc,
            qty,
            item_to_meddays.get(iid, "NA")
        ]
        for po, url, date, iid, iurl, desc, qty in rows
    ]
    if data:
        ws_g.update(range_name="B11", values=data, value_input_option="USER_ENTERED")
        print(f"✅ WAITING ON updated ({len(data)} rows).")
    else:
        print("⚠️ No outstanding items to update in WAITING ON.")



