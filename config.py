"""
Central configuration for the Purchase Order Automation tool.
All credentials and environment-specific settings live here.
"""

# --- Portal / Authentication (sanitized placeholders) ---

LOGIN_URL = "https://example-portal.com/workflow"
USERNAME  = "YOUR_USERNAME_HERE"
PASSWORD  = "YOUR_PASSWORD_HERE"

# --- Google Sheets / OAuth ---

SHEET_ID   = "REDACTED_SHEET_ID"
CREDS_FILE = r"path/to/creds.json"

# --- Site / Domain configuration (sanitized) ---

SITE_CODE       = "001" 
BASE_PO_DOMAIN  = "https://example-procurement.com"

# --- Sheet names ---

SHEET_NAMES = {
    "item_summary":    "ITEM SUMMARY",
    "waiting_on":      "WAITING ON",
    "came_in":         "CAME IN",
    "latest_2_years":  "LATEST 2 YEARS",
    "trend_graph":     "TREND GRAPH",
}
