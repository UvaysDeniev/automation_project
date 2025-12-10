# utils.py
from datetime import datetime
from statistics import median

def get_last_order_date(dates):
    """Return the most recent order date as YYYY-MM-DD string."""
    if not dates:
        return ""
    return max(dates).strftime("%Y-%m-%d")


def order_frequency_median(dates, badge=None, today=None):
    """
    ✅  -> 'every N days'  (median gap of UNIQUE order dates)
    non-✅ & >1 -> 'last ordered X days ago'
    exactly 1   -> 'Once — X days ago'
    """
    if not dates:
        return ""

    today = today or datetime.now().date()
    uds = sorted({(d.date() if isinstance(d, datetime) else d) for d in dates})
    last = uds[-1]
    days_ago = max(0, (today - last).days)

    if len(uds) == 1:
        return f"Once — {days_ago} days ago"

    if badge == "✅":
        gaps = [(uds[i+1] - uds[i]).days for i in range(len(uds)-1)]
        if not gaps:
            return f"Once — {days_ago} days ago"
        med_gap = int(median(gaps))
        return f"lasts {med_gap} days" if med_gap > 0 else f"Once — {days_ago} days ago"

    return f"last ordered {days_ago} days ago"
