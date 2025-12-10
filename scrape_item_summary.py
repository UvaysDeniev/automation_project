from datetime import datetime, timedelta
from math import ceil
from statistics import median
import re

from .sheets_io import open_sheet, auto_stamp_gsheet, clear_range
from . import mappings
from .utils import get_last_order_date, order_frequency_median


def process_item_summary():
    """
    Compute per-item stats from CAME IN and WAITING ON and push
    a consolidated summary into ITEM SUMMARY (B11:J).
    """

    link_re = re.compile(
        r'=HYPERLINK\("(?P<url>[^"]+)"\s*,\s*"(?P<text>[^"]+)"\)',
        re.IGNORECASE
    )

    def _pending_order_dates_from_waiting_on():
        """Returns {item_id: [datetime,...]} from WAITING ON."""
        ws = open_sheet("WAITING ON")
        rows = ws.get("B11:D1000", value_render_option="FORMULA")
        pending = {}
        for r in rows:
            if len(r) < 3:
                continue
            order_cell   = r[1]      # C
            link_formula = r[2]      # D
            m = link_re.match(link_formula or "")
            if not m:
                continue
            item_id = m.group("text")

            if isinstance(order_cell, (int, float)):
                dt = datetime(1899, 12, 30) + timedelta(days=int(order_cell))
            else:
                try:
                    dt = datetime.strptime(str(order_cell), "%m/%d/%Y")
                except ValueError:
                    continue

            pending.setdefault(item_id, []).append(dt)
        return pending

    # 1) Open sheets
    came    = open_sheet("CAME IN")
    summary = open_sheet("ITEM SUMMARY")

    # 2) Clear old output
    clear_range(summary, "B11:J1000")

    # 3) Fetch B→I with formulas from CAME IN (keeps HYPERLINKs)
    raw = came.get("B11:I1000", value_render_option="FORMULA")
    print(f"⚙️  Fetched {len(raw)} rows from CAME IN")

    stats = {}
    for row in raw:
        if len(row) < 8:
            row += [""] * (8 - len(row))

        # B→I: PO#, Order Date, Received Date, Arrived In,
        #      Item ID (HYPERLINK), Description, Qty, Price Per Unit
        order_cell, _, ai_cell, link_formula, raw_desc, qty_cell, price_cell = (
            row[1], row[2], row[3], row[4], row[5], row[6], row[7]
        )

        m = link_re.match(link_formula or "")
        if not m:
            continue
        url, item_id = m.group("url"), m.group("text")

        try:
            qty = int(float(qty_cell))
        except Exception:
            qty = 0

        try:
            price_per_unit = float(price_cell)
        except Exception:
            price_per_unit = None

        if isinstance(order_cell, (int, float)):
            dt = datetime(1899, 12, 30) + timedelta(days=int(order_cell))
        else:
            try:
                dt = datetime.strptime(str(order_cell), "%m/%d/%Y")
            except ValueError:
                continue

        days = None
        if ai_cell:
            m2 = re.match(r"(\d+)", str(ai_cell))
            if m2:
                days = int(m2.group(1))

        desc_trunc = mappings.truncate_desc(raw_desc or "")
        name = mappings.normalize_name(desc_trunc, item_id)

        rec = stats.setdefault(item_id, {
            "url":           url,
            "name":          name,
            "sum_qty":       0,
            "count":         0,
            "qtys":          [],
            "dates":         [],
            "months":        set(),
            "min_dt":        dt,
            "max_dt":        dt,
            "delivery_days": [],
            "prices":        [],
        })

        rec["sum_qty"] += qty
        rec["count"]   += 1
        rec["qtys"].append(qty)
        rec["dates"].append(dt)
        rec["months"].add((dt.year, dt.month))
        rec["min_dt"]  = min(rec["min_dt"], dt)
        rec["max_dt"]  = max(rec["max_dt"], dt)
        if days is not None:
            rec["delivery_days"].append(days)
        if price_per_unit is not None:
            rec["prices"].append(price_per_unit)

    print(f"⚙️  Aggregated stats for {len(stats)} unique items")

    pending_map = _pending_order_dates_from_waiting_on()
    for item_id, pend_dates in pending_map.items():
        if item_id not in stats:
            continue
        rec = stats[item_id]
        for dt in pend_dates:
            if dt not in rec["dates"]:
                rec["dates"].append(dt)
                rec["months"].add((dt.year, dt.month))

    out = []
    for item_id, info in stats.items():
        med_days_str = f"{median(info['delivery_days']):.0f}" if info["delivery_days"] else ""
        med_qty      = median(info["qtys"]) if info["qtys"] else 0

        span_months = (
            (info["max_dt"].year  - info["min_dt"].year) * 12
          + (info["max_dt"].month - info["min_dt"].month)
          + 1
        )
        avg_per_month = info["sum_qty"] / span_months if span_months else 0
        avg_per_month = int(ceil(avg_per_month))

        price_per_unit      = median(info["prices"]) if info["prices"] else 0.0
        mdn_cost_per_month  = price_per_unit * avg_per_month

        dates_sorted = sorted(info["dates"])
        gaps = [(dates_sorted[i+1] - dates_sorted[i]).days for i in range(len(dates_sorted)-1)]
        med_gap    = median(gaps) if gaps else float("inf")
        freq_ratio = len(info["months"]) / span_months if span_months else 0
        badge = ""
        if info["count"] > 1 and span_months > 2:
            if freq_ratio >= 0.80 or med_gap <= 45:
                badge = "✅"

        last_order = get_last_order_date(info["dates"])
        order_freq = order_frequency_median(info["dates"], badge)

        out.append([
            f'=HYPERLINK("{info["url"]}","{item_id}")',
            info["name"],
            med_days_str,
            str(int(med_qty) if isinstance(med_qty, (int, float)) else med_qty),
            order_freq,
            str(avg_per_month),
            f"{mdn_cost_per_month:.2f}",
            badge,
            last_order,
        ])

    # sort: ✅ first, then Monthly Cost desc (col 6)
    out.sort(key=lambda row: (row[7] == "✅", float(row[6] or 0.0)), reverse=True)

    headers = [
        "Item ID",
        "Description",
        "Delivery\nDays",
        "Qty Per Order",
        "Lasts For",
        "Avg\nQty Monthly",
        "Monthly Cost",
        "Ordered Often?",
        "Last Ordered",
    ]
    summary.update(
        range_name="B10:J10",
        values=[headers],
        value_input_option="USER_ENTERED",
    )
    auto_stamp_gsheet(summary)

    if out:
        summary.update(
            range_name="B11",
            values=out,
            value_input_option="USER_ENTERED",
        )
        print(f"✅ ITEM SUMMARY updated ({len(out)} items).")
    else:
        print("⚠️ No valid rows found to populate ITEM SUMMARY.")
