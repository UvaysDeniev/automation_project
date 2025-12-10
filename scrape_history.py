"""
History scraping + trend statistics for the last 2 years.
"""
from datetime import datetime, date
from calendar import month_name
from collections import defaultdict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from .browser import get_driver
from .sheets_io import open_sheet, auto_stamp_gsheet, clear_range
from . import config

# --------------------------------------------------
# MONTHLY EXPENSE BUCKETER
# --------------------------------------------------

def process_data_from_2024():
    driver = get_driver()
    wait   = WebDriverWait(driver, 15)

    wait = WebDriverWait(driver, 15)
    el = wait.until(EC.element_to_be_clickable((By.ID, "linkpitmenu_section_15")))
    el.click()
    wait = WebDriverWait(driver, 15)
    el = wait.until(EC.element_to_be_clickable((By.ID, "linkpitmenu_item_160")))
    el.click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.GridDetail")))

    expense_rows = []
    done = False

    while True:
        all_rows = driver.find_elements(By.XPATH, "//tr")
        for tr in all_rows:
            tds = tr.find_elements(By.CSS_SELECTOR, "td.GridDetail")
            if len(tds) < 6:
                continue

            # a) parse date and stop if before 2023
            full_dt = tds[2].text.strip()
            if not full_dt:
                continue
            date_only = full_dt.split()[0]
            try:
                dt = datetime.strptime(date_only, "%m/%d/%Y").date()
            except Exception:
                continue
            if dt.year < 2024:
                done = True
                break

            # b) only “Fully Received”
            if tds[3].text.strip() != "Fully Received":
                continue

            # c) extract Request # link
            link_els = tds[1].find_elements(By.TAG_NAME, "a")
            if not link_els:
                continue
            req_num = link_els[0].text.strip()
            req_url = link_els[0].get_attribute("href")

            # d) extract total, strip "$" and commas
            raw_cost = tds[5].text.strip()
            cost     = raw_cost.replace("$", "").replace(",", "")

            # e) extract Request Title and check for Exception
            req_title = tds[4].text.strip()
            is_main = (
                "Main Location GM (Store 001)" in req_title or
                "Main Location Support (Store 001)" in req_title
            )
            exception = "—" 
            if not is_main:
                exception = "✅"

            expense_rows.append((req_num, req_url, date_only, cost, exception))

        if done:
            break

        # e) click Next, or break if no more pages
        try:
            nxt = driver.find_element(By.CSS_SELECTOR, "input.GridDetailSubmit[name='next']")
            if not nxt.is_enabled():
                break
            nxt.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.GridDetail")))
        except NoSuchElementException:
            break

    driver.quit()

    # 4) Push into Google Sheets
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(config.CREDS_FILE, scope)
    gc    = gspread.authorize(creds)
    sh    = gc.open_by_key(config.SHEET_ID)

    ws_name = "LATEST 2 YEARS"
    try:
        ws = sh.worksheet(ws_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(ws_name, rows="1000", cols="5")
        ws.append_row(["Request #", "Date", "Total", "Exception"], value_input_option="USER_ENTERED")

    clear_range(ws, "B11:H1000")

    data = [
        [f'=HYPERLINK("{url}","{req}")', date, cost, exception]
        for req, url, date, cost, exception in expense_rows
    ]
    if data:
        ws.update(values=data, range_name="B11", value_input_option="USER_ENTERED")
        print(f"✅ {ws_name} updated ({len(data)} rows).")
    else:
        print("⚠️ No fully‐received requisitions from 2024 onward found.")
    auto_stamp_gsheet(ws)

def write_weekly_by_month_table():
    # 1) Auth & open
    ws_exp = open_sheet("LATEST 2 YEARS")
    raw    = ws_exp.get("C11:E1000")  # Now includes exception column

    # 2) Sum daily totals, split into normal vs exception
    daily_normal = defaultdict(float)
    daily_exception = defaultdict(float)
    for row in raw:
        if len(row) < 2:
            continue
        date_str, cost_str = row[0], row[1]
        exception = row[2] if len(row) > 2 else ""
        if not date_str or not cost_str:
            continue
        try:
            dt = datetime.strptime(date_str, "%m/%d/%Y").date()
            amt = float(cost_str)
        except Exception:
            continue

        if exception == "✅":
            daily_exception[dt] += amt
        else:
            daily_normal[dt] += amt

    if not (daily_normal or daily_exception):
        print("⚠️ No expense data to plot.")
        return

    # 3) Bucket into weeks-of-month 1–5 for normal, and sum exceptions by month
    mw_normal = defaultdict(lambda: defaultdict(float))
    mw_exception = defaultdict(float)

    for dt, total in daily_normal.items():
        week_num = (dt.day - 1) // 7 + 1
        key = (dt.year, dt.month)
        mw_normal[key][week_num] += total

    for dt, total in daily_exception.items():
        key = (dt.year, dt.month)
        mw_exception[key] += total

    # 4) Prepare header & data rows
    weeks = [1, 2, 3, 4, 5]
    header = [""] + [f"W{w}" for w in weeks] + ["Exception"]

    rows = []
    for year, month in sorted(set(mw_normal.keys()) | set(mw_exception.keys())):
        label = f"{month_name[month]} {year}"
        row = [label]
        for w in weeks:
            amt = mw_normal[(year, month)].get(w, 0.0)
            row.append(round(amt, 2) if amt else "")
        exception_amt = mw_exception.get((year, month), 0.0)
        row.append(round(exception_amt, 2) if exception_amt else "")
        rows.append(row)

    # 5) Write to TREND GRAPH at B11
    ws = open_sheet("TREND GRAPH")
    clear_range(ws, "B11:H1000")
    ws.update(values=[header], range_name="B11")
    ws.update(values=rows, range_name="B12")
    auto_stamp_gsheet(ws)

    print("✅ TREND GRAPH updated with weekly-by-month table and one exception column per month.")