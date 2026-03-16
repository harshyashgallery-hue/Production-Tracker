import streamlit as st
import pandas as pd
import json
from datetime import date, datetime, timedelta
import uuid

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Garment ERP v2",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #f5f6fa;
    color: #1c1c2e;
}
.stApp { background: #f5f6fa; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1c1c2e !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * { color: #e8e4dc !important; }
section[data-testid="stSidebar"] hr { border-color: #2e2e4a !important; }

/* Headers */
h1 { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 800 !important; color: #1c1c2e !important; letter-spacing: -0.5px; font-size: 28px !important; }
h2, h3, h4 { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; color: #1c1c2e !important; }

/* Cards */
.card {
    background: #ffffff;
    border: 1px solid #e2e5ef;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 8px 0;
    box-shadow: 0 1px 4px rgba(28,28,46,0.06);
}
.card-accent  { border-left: 3px solid #c8a96e; }
.card-left    { border-left: 4px solid #c8a96e; }
.card-left-blue  { border-left: 4px solid #3b82f6; }
.card-left-green { border-left: 4px solid #10b981; }
.card-left-red   { border-left: 4px solid #ef4444; }

/* Metric boxes */
.metric-box {
    background: #1c1c2e;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    color: #f5f6fa;
}
.metric-box.green { background: #064e3b; }
.metric-box.amber { background: #78350f; }
.metric-box.red   { background: #7f1d1d; }
.metric-value { font-size: 30px; font-weight: 800; color: #c8a96e; font-family: 'Plus Jakarta Sans', sans-serif; }
.metric-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #aaa; margin-top: 4px; }

/* KPI cards (SO module) */
.kpi-card { background: #1c1c2e; border-radius: 14px; padding: 20px 22px; color: #f5f6fa; }
.kpi-value { font-size: 32px; font-weight: 800; line-height: 1; }
.kpi-label { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; opacity: 0.6; margin-top: 5px; }
.kpi-accent { background: #c8a96e; }
.kpi-accent .kpi-value, .kpi-accent .kpi-label { color: #1c1c2e; opacity: 1; }
.kpi-warn   { background: #b91c1c; }
.kpi-green  { background: #065f46; }

/* Badges */
.badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; font-family:'JetBrains Mono',monospace; }
.badge-done      { background:#d1fae5; color:#065f46; }
.badge-pending   { background:#fee2e2; color:#991b1b; }
.badge-new       { background:#dbeafe; color:#1e40af; }
.badge-certified { background:#fef3c7; color:#92400e; }

/* SO status badges */
.status-badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; font-family:'JetBrains Mono',monospace; text-transform:uppercase; letter-spacing:0.5px; }
.s-draft      { background:#f1f5f9; color:#64748b; }
.s-submitted  { background:#dbeafe; color:#1e40af; }
.s-approved   { background:#d1fae5; color:#065f46; }
.s-production { background:#fef3c7; color:#92400e; }
.s-partial    { background:#ede9fe; color:#5b21b6; }
.s-received   { background:#d1fae5; color:#065f46; }
.s-closed     { background:#f1f5f9; color:#475569; }
.s-cancelled  { background:#fee2e2; color:#991b1b; }

/* Progress bar */
.prog-wrap  { background:#e2e8f0; border-radius:99px; height:7px; margin:6px 0; overflow:hidden; }
.prog-fill  { height:100%; border-radius:99px; background:#c8a96e; }
.prog-fill-red   { background:#ef4444; }
.prog-fill-green { background:#10b981; }

/* Tags */
.tag { display:inline-block; background:#f1f5f9; color:#475569; font-size:11px; padding:2px 8px; border-radius:4px; margin:2px; font-family:'JetBrains Mono',monospace; border:1px solid #e2e8f0; }
.tag-accent { background:#fef3c7; color:#92400e; border-color:#fde68a; }
.tag-gold   { background:#fef3c7; color:#92400e; border-color:#fde68a; }
.tag-blue   { background:#dbeafe; color:#1e40af; border-color:#bfdbfe; }
.tag-red    { background:#fee2e2; color:#991b1b; border-color:#fecaca; }

/* Section number circle */
.section-number { background:#c8a96e; color:#1c1c2e; width:22px; height:22px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:11px; font-weight:700; font-family:'JetBrains Mono',monospace; }

/* Info/warn boxes */
.info-box  { background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:10px 14px; font-size:13px; color:#1e40af; }
.warn-box  { background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:10px 14px; font-size:13px; color:#92400e; }
.ok-box    { background:#ecfdf5; border:1px solid #a7f3d0; border-radius:8px; padding:10px 14px; font-size:13px; color:#065f46; }
.danger-box{ background:#fef2f2; border:1px solid #fecaca; border-radius:8px; padding:10px 14px; font-size:13px; color:#991b1b; }

/* Sec label */
.sec-label { font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:2px; color:#c8a96e; margin-bottom:6px; }

/* Inputs */
.stTextInput>div>div>input,
.stSelectbox>div>div>div,
.stNumberInput>div>div>input,
.stDateInput>div>div>input,
.stTextArea>div>div>textarea {
    background: #ffffff !important;
    border: 1.5px solid #e2e5ef !important;
    color: #1c1c2e !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Buttons */
.stButton>button {
    background: #1c1c2e !important;
    color: #f5f6fa !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
}
.stButton>button:hover { background: #c8a96e !important; color: #1c1c2e !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #ffffff !important; border-bottom: 2px solid #e2e5ef !important; border-radius: 10px 10px 0 0; gap:0 !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#94a3b8 !important; font-family:'Plus Jakarta Sans',sans-serif !important; font-weight:600 !important; font-size:13px !important; border-bottom:2px solid transparent !important; padding:10px 18px !important; }
.stTabs [aria-selected="true"] { color:#1c1c2e !important; border-bottom-color:#c8a96e !important; }

/* Expander */
.streamlit-expanderHeader { background:#ffffff !important; border:1px solid #e2e5ef !important; border-radius:8px !important; color:#1c1c2e !important; font-weight:600 !important; }

/* Divider */
hr { border-color: #e2e5ef !important; }

/* Dataframe */
.stDataFrame { border-radius:8px; overflow:hidden; border:1px solid #e2e5ef; }
</style>
""", unsafe_allow_html=True)

# ─── Persistence Layer (Google Sheets) ─────────────────────────────────────────
import os
import gspread
from google.oauth2.service_account import Credentials

DEFAULT_DATA = {
    "items":          {},
    "boms":           {},
    "merchants":      {"MC001": "Amit Textiles", "MC002": "Ravi Exports", "MC003": "Sharma Trading Co."},
    "buyers":         ["Myntra", "Flipkart", "Amazon", "Reliance", "Direct"],
    "processes":      ["Cutting", "Printing", "Dyeing", "Stitching", "Finishing", "Packing", "Embroidery", "Washing"],
    "routings":       {},
    "so_list":        {},
    "demands":        {},
    "so_counter":     1,
    "demand_counter": 1,
    "warehouses":     ["Main Warehouse", "Finished Goods Store", "Export Warehouse"],
    "sales_teams":    ["Team Alpha", "Team Beta", "North Zone", "South Zone", "Export Desk"],
    "payment_terms":  ["Immediate", "Net 15", "Net 30", "Net 45", "Net 60", "Against LC"],
    "skus":           {},
    "mrp_result":     {},
    "mrp_so_list":    [],
    "mrp_run_time":   "",
    "reservations":   {},
    "soft_reservations": {},
    "tna_list": {},
    "tna_counter": 1,
    "tna_templates": {},
    "tna_activity_groups": ["Merchandising","Fabric","Sampling","CAD","Purchase","Printing","Dyeing","Cutting","Stitching","Finishing","Packing","Quality","Dispatch","Logistics"],
    "suppliers": {},
    "pr_list": {},
    "po_list": {},
    "jwo_list": {},
    "grn_list": {},
    "pr_counter": 1,
    "po_counter": 1,
    "jwo_counter": 1,
    "grn_counter": 1,
}

@st.cache_resource
def get_gsheet():
    """Connect to Google Sheet — cached so only connects once per session"""
    try:
        # Check if secrets are configured
        if "SHEET_ID" not in st.secrets or "gcp_service_account" not in st.secrets:
            return None
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(st.secrets["SHEET_ID"])
        return sheet
    except Exception:
        return None

def _get_or_create_ws(sheet, name):
    """Get worksheet by name, create if not exists"""
    try:
        return sheet.worksheet(name)
    except gspread.WorksheetNotFound:
        return sheet.add_worksheet(title=name, rows=10, cols=3)

def load_data():
    """Load all data from Google Sheets, fallback to local file"""
    sheet = get_gsheet()
    if sheet is None:
        # Try local file first
        import os
        if os.path.exists("erp_data.json"):
            try:
                with open("erp_data.json", "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for key, default_val in DEFAULT_DATA.items():
                    if key not in st.session_state:
                        st.session_state[key] = saved.get(key, default_val)
                for k, v in saved.get("_pkg_lines", {}).items():
                    if k not in st.session_state:
                        st.session_state[k] = v
                return
            except Exception:
                pass
        # Final fallback to defaults
        for key, val in DEFAULT_DATA.items():
            if key not in st.session_state:
                st.session_state[key] = val
        return

    try:
        ws = _get_or_create_ws(sheet, "erp_data")
        records = ws.get_all_values()
        if records and len(records) > 0:
            # Data stored as: row[0]=key, row[1]=json_value
            saved = {}
            for row in records:
                if len(row) >= 2 and row[0]:
                    try:
                        saved[row[0]] = json.loads(row[1])
                    except Exception:
                        pass
            for key, default_val in DEFAULT_DATA.items():
                if key not in st.session_state:
                    st.session_state[key] = saved.get(key, default_val)
            # Load pkg_lines
            for k, v in saved.items():
                if k.startswith("pkg_lines_") and k not in st.session_state:
                    st.session_state[k] = v
        else:
            for key, val in DEFAULT_DATA.items():
                if key not in st.session_state:
                    st.session_state[key] = val
    except Exception as e:
        for key, val in DEFAULT_DATA.items():
            if key not in st.session_state:
                st.session_state[key] = val

def save_data():
    """Save all data to Google Sheets, fallback to local file"""
    sheet = get_gsheet()
    if sheet is None:
        # Local file fallback
        try:
            to_save = {key: st.session_state.get(key, DEFAULT_DATA.get(key)) for key in DEFAULT_DATA}
            pkg_lines = {k: v for k, v in st.session_state.items() if k.startswith("pkg_lines_")}
            to_save["_pkg_lines"] = pkg_lines
            with open("erp_data.json", "w", encoding="utf-8") as f:
                json.dump(to_save, f, ensure_ascii=False, indent=2, default=str)
        except Exception:
            pass
        return

    try:
        ws = _get_or_create_ws(sheet, "erp_data")
        # Build data dict
        to_save = {key: st.session_state.get(key, DEFAULT_DATA.get(key)) for key in DEFAULT_DATA}
        pkg_lines = {k: v for k, v in st.session_state.items() if k.startswith("pkg_lines_")}
        to_save.update(pkg_lines)

        # Write as rows: [[key, json_value], ...]
        rows = [["key", "value"]]  # header
        for k, v in to_save.items():
            rows.append([k, json.dumps(v, ensure_ascii=False, default=str)])

        ws.clear()
        ws.update(rows, value_input_option="RAW")
    except Exception as e:
        st.warning(f"Save failed: {e}")

def load_pkg_lines():
    pass  # Already handled in load_data()

load_data()
load_pkg_lines()

ITEM_TYPES = ["Finished Goods (FG)", "Semi Finished Goods (SFG)", "Raw Material (RM)", 
              "Accessories", "Packing Materials", "Fuel & Lubricants"]
SEASONS = ["SS25", "AW25", "SS26", "AW26", "Resort 2025", "Holiday 2025"]
UNITS = ["Meter", "KG", "Gram", "Piece", "Set", "Box", "Roll", "Litre", "Dozen"]
SIZES_ALL = ["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "Free Size"]
HSN_CODES = ["6211", "6206", "6204", "6203", "6205", "6207", "6208", "6212", "5208", "5209"]


# ─── Page routing via session state ────────────────────────────────────────────────
ALL_PAGES = [
    ("IM", "📊 Item Master Dashboard"),
    ("IM", "➕ Create Item"),
    ("IM", "📋 Item Master List"),
    ("IM", "🔩 BOM Management"),
    ("IM", "🔄 Routing Master"),
    ("IM", "👤 Merchant Master"),
    ("IM", "📦 Buyer Packaging"),
    ("SO", "📊 SO Dashboard"),
    ("SO", "📋 Demand Management"),
    ("SO", "➕ Create Sales Order"),
    ("SO", "📂 SO List & Tracking"),
    ("SO", "📈 SO Reports"),
    ("SO", "⚙️ SO Settings"),
    ("MRP", "🏭 MRP Dashboard"),
    ("MRP", "▶ Run MRP"),
    ("MRP", "📦 Material Requirements"),
    ("MRP", "🔒 Reservations"),
    ("MRP", "📊 MRP Reports"),
    ("TNA", "📅 TNA Dashboard"),
    ("TNA", "➕ Create TNA"),
    ("TNA", "📋 TNA List"),
    ("TNA", "📁 TNA Templates"),
    ("TNA", "📊 TNA Reports"),
    ("PUR", "🛒 Purchase Dashboard"),
    ("PUR", "📋 Purchase Requisitions"),
    ("PUR", "📦 Purchase Orders"),
    ("PUR", "🔧 Job Work Orders"),
    ("PUR", "📥 GRN"),
    ("PUR", "👥 Supplier Master"),
    ("PUR", "📊 Purchase Reports"),
]
IM_PAGES  = [p for m, p in ALL_PAGES if m == "IM"]
SO_PAGES  = [p for m, p in ALL_PAGES if m == "SO"]
MRP_PAGES = [p for m, p in ALL_PAGES if m == "MRP"]
TNA_PAGES = [p for m, p in ALL_PAGES if m == "TNA"]
PUR_PAGES = [p for m, p in ALL_PAGES if m == "PUR"]

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "📊 Item Master Dashboard"

with st.sidebar:
    st.markdown('<div style="padding:16px 4px 8px;"><div style="font-size:22px;font-weight:800;color:#c8a96e;">🧵 Garment ERP</div><div style="font-size:10px;color:#888;letter-spacing:2px;text-transform:uppercase;margin-top:2px;">Production Management System</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<p style="font-size:10px;color:#666;letter-spacing:2px;text-transform:uppercase;margin:0 0 6px 0;">ITEM MASTER</p>', unsafe_allow_html=True)
    for _, pg in [(m,p) for m,p in ALL_PAGES if m=="IM"]:
        is_active = st.session_state["current_page"] == pg
        btn_style = "background:#c8a96e;color:#1c1c2e;font-weight:700;" if is_active else "background:transparent;color:#bbb;"
        st.markdown(f'<div style="margin:1px 0;">', unsafe_allow_html=True)
        if st.button(pg, key=f"btn_{pg}", use_container_width=True):
            st.session_state["current_page"] = pg
            st.rerun()

    st.markdown('<p style="font-size:10px;color:#666;letter-spacing:2px;text-transform:uppercase;margin:10px 0 6px 0;">SALES</p>', unsafe_allow_html=True)
    for _, pg in [(m,p) for m,p in ALL_PAGES if m=="SO"]:
        is_active = st.session_state["current_page"] == pg
        if st.button(pg, key=f"btn_{pg}", use_container_width=True):
            st.session_state["current_page"] = pg
            st.rerun()

    st.markdown('<p style="font-size:10px;color:#666;letter-spacing:2px;text-transform:uppercase;margin:10px 0 6px 0;">MRP</p>', unsafe_allow_html=True)
    for _, pg in [(m,p) for m,p in ALL_PAGES if m=="MRP"]:
        _active = st.session_state["current_page"] == pg
        if st.button(pg, key=f"btn_{pg}", use_container_width=True):
            st.session_state["current_page"] = pg
            st.rerun()

    st.markdown('<p style="font-size:10px;color:#666;letter-spacing:2px;text-transform:uppercase;margin:10px 0 6px 0;">TNA</p>', unsafe_allow_html=True)
    for _, pg in [(m,p) for m,p in ALL_PAGES if m=="TNA"]:
        _active = st.session_state["current_page"] == pg
        if st.button(pg, key=f"btn_{pg}", use_container_width=True):
            st.session_state["current_page"] = pg
            st.rerun()

    st.markdown('<p style="font-size:10px;color:#666;letter-spacing:2px;text-transform:uppercase;margin:10px 0 6px 0;">PURCHASE</p>', unsafe_allow_html=True)
    for _, pg in [(m,p) for m,p in ALL_PAGES if m=="PUR"]:
        _active = st.session_state["current_page"] == pg
        if st.button(pg, key=f"btn_{pg}", use_container_width=True):
            st.session_state["current_page"] = pg
            st.rerun()

    st.markdown("---")
    _ni = len(st.session_state.get("items", {}))
    _nb = len(st.session_state.get("boms", {}))
    _no = sum(1 for s in st.session_state.get("so_list", {}).values() if s.get("status") not in ["Closed","Cancelled","Fully Received"])
    st.caption(f"Items: {_ni} | BOMs: {_nb} | Open SO: {_no}")

# Route to correct page
_cp  = st.session_state["current_page"]
nav     = _cp if _cp in IM_PAGES  else None
nav_so  = _cp if _cp in SO_PAGES  else None
nav_mrp = _cp if _cp in MRP_PAGES else None
nav_tna = _cp if _cp in TNA_PAGES else None
nav_pur = _cp if _cp in PUR_PAGES else None

SS = st.session_state

# ─── Helpers ────────────────────────────────────────────────────────────────────
STATUS_LIST = ["Draft", "Submitted", "Approved", "In Production", "Partially Received", "Fully Received", "Closed", "Cancelled"]
STATUS_CLASS = {
    "Draft": "s-draft", "Submitted": "s-submitted", "Approved": "s-approved",
    "In Production": "s-production", "Partially Received": "s-partial",
    "Fully Received": "s-received", "Closed": "s-closed", "Cancelled": "s-cancelled",
}
ORDER_SOURCES = ["Sales Team Demand", "Buyer PO", "Offline Order"]
GST_RATES = [0, 5, 12, 18, 28]

def next_so():
    n = f"SO-{SS['so_counter']:04d}"
    SS["so_counter"] += 1
    return n

def next_demand():
    n = f"DEM-{SS['demand_counter']:04d}"
    SS["demand_counter"] += 1
    return n

def get_sku_info(sku):
    """Get SKU info from Item Master items, falling back to demo skus dict"""
    items = st.session_state.get("items", {})
    if sku in items:
        item = items[sku]
        return {
            "name": item.get("name", sku),
            "parent": item.get("parent", ""),
            "size": sku.split("-")[-1] if "-" in sku else "",
            "price": item.get("selling_price", 0),
            "stock": item.get("stock", 0),
            "reserved": item.get("reserved", 0),
            "in_production": item.get("in_production", 0),
        }
    # fallback demo data
    return SS["skus"].get(sku, {"name": sku, "parent": "", "size": "", "price": 0, "stock": 0, "reserved": 0, "in_production": 0})

def get_all_skus():
    """Return all SKUs from Item Master (size variants + standalone FG).
    Returns dict: sku_code -> item_name (simple, parent stored separately in item data)"""
    items = st.session_state.get("items", {})
    so_skus = {}
    for code, item in items.items():
        parent = item.get("parent", "")
        if parent or (item.get("item_type","") == "Finished Goods (FG)" and not item.get("sizes")):
            so_skus[code] = item.get("name", code)
    # Merge with demo skus for fallback
    for k, v in SS["skus"].items():
        if k not in so_skus:
            so_skus[k] = v.get("name", k)
    return so_skus

def avg_daily_sale(sku):
    info = get_sku_info(sku)
    stock = info.get("stock", 0)
    return round(stock * 0.08, 1)

def running_days(sku):
    info = get_sku_info(sku)
    ads  = avg_daily_sale(sku)
    avail = info.get("stock", 0) - info.get("reserved", 0)
    return round(avail / ads, 1) if ads > 0 else 999

def so_qty_for_sku(sku):
    total = 0
    for so in SS["so_list"].values():
        if so.get("status") not in ["Cancelled", "Closed"]:
            for line in so.get("lines", []):
                if line["sku"] == sku:
                    total += line["qty"]
    return total

def badge(status):
    cls = STATUS_CLASS.get(status, "s-draft")
    return f'<span class="status-badge {cls}">{status}</span>'


# ═══════════════════════════════════════════════════════════════════════
# ITEM MASTER MODULE
# ═══════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if nav == "📊 Item Master Dashboard":
    st.markdown('<h1>Item Master & BOM Dashboard</h1>', unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    items_by_type = {}
    for item in st.session_state["items"].values():
        t = item.get("item_type", "Unknown")
        items_by_type[t] = items_by_type.get(t, 0) + 1
    
    with col1:
        st.markdown(f'''<div class="metric-box">
            <div class="metric-value">{len(st.session_state["items"])}</div>
            <div class="metric-label">Total Items</div>
        </div>''', unsafe_allow_html=True)
    with col2:
        fg = items_by_type.get("Finished Goods (FG)", 0)
        st.markdown(f'''<div class="metric-box">
            <div class="metric-value">{fg}</div>
            <div class="metric-label">Finished Goods</div>
        </div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="metric-box">
            <div class="metric-value">{len(st.session_state["boms"])}</div>
            <div class="metric-label">BOMs Created</div>
        </div>''', unsafe_allow_html=True)
    with col4:
        certified = sum(1 for b in st.session_state["boms"].values() if b.get("status") == "Certified")
        st.markdown(f'''<div class="metric-box">
            <div class="metric-value">{certified}</div>
            <div class="metric-label">Certified BOMs</div>
        </div>''', unsafe_allow_html=True)
    


# ═══════════════════════════════════════════════════════════════════════════════
# CREATE ITEM
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "➕ Create Item":
    st.markdown('<h1>Create New Item</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Basic Details", "📐 Size Variants", "🔄 Routing", "📦 Buyer Packaging"])
    
    with tab1:
        st.markdown('''<div class="warn-box">ℹ️ Merchant Code field mein drop-down ke liye pehle Merchant Master mein merchant create karein.</div>''', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Basic Information")
            code_mode = st.radio("Item Code Mode", ["Auto Generate", "Manual"], horizontal=True)
            if code_mode == "Manual":
                item_code = st.text_input("Item Code *", placeholder="e.g. YG-KURTA-001")
            else:
                item_code = f"YG-{str(uuid.uuid4())[:6].upper()}"
                st.markdown(f'<div class="card"><span style="color:#888888; font-size:12px;">Auto Code:</span><br><span class="tag tag-accent">{item_code}</span></div>', unsafe_allow_html=True)
            
            item_name = st.text_input("Item Name / Style Name *", placeholder="e.g. Floral Printed Kurta Set")
            item_type = st.selectbox("Item Category *", ITEM_TYPES)
            st.session_state["_tmp_item_type"] = item_type
            
            # Parent item
            parent_items = {k: v["name"] for k, v in st.session_state["items"].items() if v.get("item_type") == item_type}
            parent_options = ["None"] + [f"{k} – {v}" for k, v in parent_items.items()]
            parent_item = st.selectbox("Parent Item", parent_options)
        
        with col2:
            st.markdown("#### Commercial Details")
            merchant_options = [f"{k} – {v}" for k, v in st.session_state["merchants"].items()]
            merchant = st.selectbox("Merchant Code", ["Select Merchant..."] + merchant_options)
            
            hsn = st.selectbox("HSN Code", HSN_CODES)
            season = st.selectbox("Season", SEASONS)
            launch_date = st.date_input("Launch Date", value=date.today())
            
            col_sp, col_pp = st.columns(2)
            with col_sp:
                selling_price = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0)
            with col_pp:
                purchase_price = st.number_input("Purchase Price (₹)", min_value=0.0, step=10.0)
        
        # Image upload placeholder
        st.markdown("---")
        st.markdown("#### 📸 Item Images *(Upload functionality – PENDING)*")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="card" style="text-align:center; min-height:100px; display:flex; align-items:center; justify-content:center; border-style:dashed;"><span style="color:var(--text-muted);">📷 Front Image</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card" style="text-align:center; min-height:100px; display:flex; align-items:center; justify-content:center; border-style:dashed;"><span style="color:var(--text-muted);">📷 Back Image</span></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="card" style="text-align:center; min-height:100px; display:flex; align-items:center; justify-content:center; border-style:dashed;"><span style="color:var(--text-muted);">📷 Detail Image</span></div>', unsafe_allow_html=True)
        
        # Attachment upload placeholder
        st.markdown("#### 📎 Attachments *(Upload functionality – PENDING)*")
        attachment_types = ["CAD File", "Design Sheet", "Tech Pack", "Artwork", "Reference Images"]
        for att in attachment_types:
            st.markdown(f'<span class="tag">📄 {att}</span>', unsafe_allow_html=True)
        st.caption("Multiple file upload support – to be implemented")
    
    with tab2:
        if item_type == "Finished Goods (FG)":
            st.markdown("#### 📐 Size Variant Generation")
            st.markdown('''<div class="info-box">✓ Size range select karein – ERP automatically size-wise SKUs generate kar dega (e.g. YG-001-S, YG-001-M...)</div>''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            selected_sizes = st.multiselect("Select Size Range *", SIZES_ALL, default=["S", "M", "L", "XL", "XXL"])
            
            if selected_sizes and item_code and item_name:
                st.markdown("#### Auto-Generated SKUs Preview")
                skus = []
                for sz in selected_sizes:
                    sku = f"{item_code}-{sz}"
                    skus.append({"SKU Code": sku, "Size": sz, "Parent Item": item_code, "Status": "Draft"})
                
                df_skus = pd.DataFrame(skus)
                st.dataframe(df_skus, use_container_width=True, hide_index=True)
                
                st.markdown(f'''<div class="info-box">✓ {len(skus)} SKUs will be auto-created as children of <strong>{item_code}</strong></div>''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">Size variants are only applicable for Finished Goods items.</div>', unsafe_allow_html=True)
    
    with tab3:
        _routing_types = ["Finished Goods (FG)", "Semi Finished Goods (SFG)"]
        _cur_type = st.session_state.get("_tmp_item_type", "Finished Goods (FG)")
        if _cur_type not in _routing_types:
            st.markdown(f'<div class="warn-box">⚠️ Routing sirf <strong>Finished Goods</strong> aur <strong>Semi Finished Goods</strong> ke liye hoti hai.<br>Is item type (<strong>{_cur_type}</strong>) ke liye routing applicable nahi hai.</div>', unsafe_allow_html=True)
        else:
            st.markdown("#### 🔄 Production Routing (Process Order)")
            st.markdown('''<div class="info-box">✓ Processes ko order wise arrange karein – alag SKU ke liye alag process order define kar sakte hain</div>''', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            available_processes = st.session_state["processes"].copy()
            selected_route = st.multiselect("Select Processes (in order)", available_processes,
                                             default=["Cutting", "Stitching", "Finishing", "Packing"])
            
            if selected_route:
                st.markdown("#### Process Sequence")
                for i, proc in enumerate(selected_route, 1):
                    st.markdown(f'''<div class="card card-accent" style="padding:10px 16px; margin:4px 0;">
                        <span class="section-number">{i}</span>
                        <span style="margin-left:10px; font-weight:500;">{proc}</span>
                    </div>''', unsafe_allow_html=True)
    
    with tab4:
        st.markdown("#### 📦 Buyer-wise Packaging")
        st.markdown('<div class="info-box">✓ Pehle <strong>Packing Materials</strong> type ke items Item Master mein banao (sticker, tag, polybag, carton etc.) — phir yahan buyer ke liye add karo.</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Get all packing material items from item master
        packing_items = {
            k: v for k, v in st.session_state["items"].items()
            if v.get("item_type") in ["Packing Materials", "Accessories"]
        }

        buyers_list = st.session_state["buyers"]
        if not buyers_list:
            st.markdown('<div class="warn-box">Koi buyer nahi mila. SO Settings mein buyers add karo.</div>', unsafe_allow_html=True)
        else:
            sel_buyer_pkg = st.selectbox("Buyer select karo", [""] + buyers_list, key="pkg_buyer_sel")

            if sel_buyer_pkg:
                pkg_key = f"pkg_lines_{sel_buyer_pkg}"
                if pkg_key not in st.session_state:
                    st.session_state[pkg_key] = []

                # Add packing item line
                with st.expander(f"➕ {sel_buyer_pkg} ke liye packing item add karo", expanded=len(st.session_state[pkg_key]) == 0):
                    if not packing_items:
                        st.markdown('<div class="warn-box">⚠️ Koi Packing Materials / Accessories item nahi mila. Pehle Item Master mein banao.</div>', unsafe_allow_html=True)
                    else:
                        pc1, pc2, pc3 = st.columns(3)
                        with pc1:
                            pkg_item = st.selectbox(
                                "Packing Item *",
                                [""] + list(packing_items.keys()),
                                format_func=lambda x: f"{x} – {packing_items.get(x,{}).get('name','')}" if x else "— Select Item —",
                                key="pkg_item_sel"
                            )
                        with pc2:
                            pkg_qty  = st.number_input("Qty per piece", min_value=0.0, step=1.0, value=1.0, key="pkg_qty")
                            pkg_uom  = st.selectbox("UOM", ["Piece", "Set", "Meter", "KG", "Gram", "Roll"], key="pkg_uom")
                        with pc3:
                            pkg_remarks = st.text_input("Remarks", key="pkg_remarks", placeholder="e.g. Inside polybag")

                        if st.button(f"➕ Add to {sel_buyer_pkg} Packaging"):
                            if pkg_item:
                                st.session_state[pkg_key].append({
                                    "item_code": pkg_item,
                                    "item_name": packing_items[pkg_item].get("name", pkg_item),
                                    "item_type": packing_items[pkg_item].get("item_type", ""),
                                    "qty":       pkg_qty,
                                    "uom":       pkg_uom,
                                    "remarks":   pkg_remarks,
                                })
                                save_data()
                                st.rerun()

                # Show current lines
                lines = st.session_state[pkg_key]
                if lines:
                    st.markdown(f"##### {sel_buyer_pkg} — Packaging Lines")
                    for idx, ln in enumerate(lines):
                        lc1, lc2, lc3, lc4, lc5 = st.columns([2, 2, 1, 1, 0.5])
                        with lc1: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>{ln["item_code"]}</strong></div>', unsafe_allow_html=True)
                        with lc2: st.markdown(f'<div style="padding-top:8px;font-size:13px;">{ln["item_name"]}</div>', unsafe_allow_html=True)
                        with lc3: st.markdown(f'<div style="padding-top:8px;font-size:13px;">{ln["qty"]} {ln["uom"]}</div>', unsafe_allow_html=True)
                        with lc4: st.markdown(f'<div style="padding-top:8px;font-size:13px;color:#64748b;">{ln.get("remarks","")}</div>', unsafe_allow_html=True)
                        with lc5:
                            if st.button("🗑", key=f"del_pkg_{sel_buyer_pkg}_{idx}"):
                                st.session_state[pkg_key].pop(idx)
                                save_data()
                                st.rerun()
                        st.markdown('<hr style="margin:2px 0;border-color:#e2e5ef;">', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warn-box">Koi packing item nahi add kiya abhi tak.</div>', unsafe_allow_html=True)

            # pkg_lines stored in session state — save_data() picks them up automatically
    
    # Save Button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("💾 Save Item", use_container_width=True):
            if not item_name:
                st.error("Item Name is required!")
            else:
                sizes = selected_sizes if item_type == "Finished Goods (FG)" else []
                route = selected_route if 'selected_route' in dir() else []
                
                item_data = {
                    "code": item_code,
                    "name": item_name,
                    "item_type": item_type,
                    "merchant": merchant,
                    "hsn": hsn,
                    "season": season,
                    "launch_date": str(launch_date),
                    "selling_price": selling_price,
                    "purchase_price": purchase_price,
                    "sizes": sizes,
                    "routing": route,
                    "buyer_packaging": {
                        b: st.session_state[f"pkg_lines_{b}"]
                        for b in st.session_state.get("buyers", [])
                        if st.session_state.get(f"pkg_lines_{b}")
                    },
                    "parent": parent_item if parent_item != "None" else None,
                    "created_at": datetime.now().isoformat(),
                }
                
                st.session_state["items"][item_code] = item_data
                save_data()
                
                # Auto-create size variant records
                for sz in sizes:
                    sku = f"{item_code}-{sz}"
                    st.session_state["items"][sku] = {
                        **item_data,
                        "code": sku,
                        "name": f"{item_name} – {sz}",
                        "parent": item_code,
                        "sizes": [],
                    }
                
                # Save routing — only for FG / SFG
                if route and item_type in ["Finished Goods (FG)", "Semi Finished Goods (SFG)"]:
                    st.session_state["routings"][item_code] = route
                    save_data()
                
                st.success(f"✅ Item '{item_name}' saved! {len(sizes)} size variants created.")
                st.balloons()

# ═══════════════════════════════════════════════════════════════════════════════
# ITEM MASTER LIST
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "📋 Item Master List":
    st.markdown('<h1>Item Master List</h1>', unsafe_allow_html=True)

    if "edit_item_code" not in st.session_state:
        st.session_state["edit_item_code"] = None

    if not st.session_state["items"]:
        st.markdown('<div class="warn-box">No items created yet. Go to "Create Item" to add items.</div>', unsafe_allow_html=True)
    else:
        # ── If edit mode ──────────────────────────────────────────────────────
        if st.session_state["edit_item_code"] and st.session_state["edit_item_code"] in st.session_state["items"]:
            ec   = st.session_state["edit_item_code"]
            item = st.session_state["items"][ec]

            bc1, bc2 = st.columns([1, 6])
            with bc1:
                if st.button("← Back"):
                    st.session_state["edit_item_code"] = None
                    st.rerun()
            with bc2:
                st.markdown(f'<h3 style="margin:0;">Edit Item — <span style="color:#c8a96e;">{ec}</span></h3>', unsafe_allow_html=True)

            st.markdown("---")
            e1, e2 = st.columns(2)
            with e1:
                e_name   = st.text_input("Item Name *", value=item.get("name",""), key="e_name")
                e_type   = st.selectbox("Item Category", ITEM_TYPES, index=ITEM_TYPES.index(item.get("item_type", ITEM_TYPES[0])), key="e_type")
                e_season = st.selectbox("Season", SEASONS, index=SEASONS.index(item.get("season", SEASONS[0])) if item.get("season") in SEASONS else 0, key="e_season")
            with e2:
                merchant_opts_e = ["Select Merchant..."] + [f"{k} – {v}" for k, v in st.session_state["merchants"].items()]
                cur_merch = item.get("merchant","")
                merch_idx = next((i for i, o in enumerate(merchant_opts_e) if o.startswith(cur_merch.split(" –")[0])), 0)
                e_merchant = st.selectbox("Merchant Code", merchant_opts_e, index=merch_idx, key="e_merchant")
                e_hsn      = st.selectbox("HSN Code", HSN_CODES, index=HSN_CODES.index(item.get("hsn", HSN_CODES[0])) if item.get("hsn") in HSN_CODES else 0, key="e_hsn")
                e_sp, e_pp = st.columns(2)
                with e_sp: e_selling  = st.number_input("Selling Price (₹)", value=float(item.get("selling_price",0)), step=10.0, key="e_sp")
                with e_pp: e_purchase = st.number_input("Purchase Price (₹)", value=float(item.get("purchase_price",0)), step=10.0, key="e_pp")

            e_desc    = st.text_area("Description", value=item.get("description",""), key="e_desc")

            st.markdown("---")
            sv1, sv2 = st.columns(2)
            with sv1:
                if st.button("💾 Save Changes", use_container_width=True):
                    st.session_state["items"][ec].update({
                        "name":           e_name,
                        "item_type":      e_type,
                        "season":         e_season,
                        "merchant":       e_merchant,
                        "hsn":            e_hsn,
                        "selling_price":  e_selling,
                        "purchase_price": e_purchase,
                        "description":    e_desc,
                    })
                    save_data()
                    st.success(f"✅ Item '{e_name}' updated!")
                    st.session_state["edit_item_code"] = None
                    st.rerun()
            with sv2:
                if st.button("✖ Cancel", use_container_width=True):
                    st.session_state["edit_item_code"] = None
                    st.rerun()

        # ── List mode ─────────────────────────────────────────────────────────
        else:
            # Filters
            fc1, fc2, fc3 = st.columns(3)
            with fc1: filter_type   = st.selectbox("Filter by Type", ["All"] + ITEM_TYPES)
            with fc2: filter_season = st.selectbox("Filter by Season", ["All"] + SEASONS)
            with fc3: search        = st.text_input("🔍 Search by Name/Code", placeholder="Type to filter...")

            filtered = {}
            for code, item in st.session_state["items"].items():
                if filter_type != "All" and item.get("item_type") != filter_type: continue
                if filter_season != "All" and item.get("season") != filter_season: continue
                if search and search.lower() not in code.lower() and search.lower() not in item.get("name","").lower(): continue
                filtered[code] = item

            st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px;">Showing <strong>{len(filtered)}</strong> of <strong>{len(st.session_state["items"])}</strong> items</div>', unsafe_allow_html=True)

            # Confirm delete state
            if "confirm_delete_item" not in st.session_state:
                st.session_state["confirm_delete_item"] = None

            for code, item in filtered.items():
                has_bom    = code in st.session_state["boms"]
                bom_status = st.session_state["boms"].get(code,{}).get("status","—") if has_bom else "—"
                child_count = sum(1 for d in st.session_state["items"].values() if d.get("parent") == code)

                r1, r2, r3, r4, r5, r6 = st.columns([1.5, 2.5, 1.2, 1, 0.8, 0.8])
                with r1:
                    st.markdown(f'<div style="padding-top:8px;font-family:JetBrains Mono,monospace;font-size:13px;font-weight:700;color:#c8a96e;">{code}</div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'<div style="padding-top:6px;"><div style="font-size:13px;font-weight:600;">{item.get("name","")}</div><div style="font-size:11px;color:#94a3b8;">{item.get("item_type","")}</div></div>', unsafe_allow_html=True)
                with r3:
                    st.markdown(f'<div style="padding-top:8px;font-size:12px;">{item.get("season","—")}</div>', unsafe_allow_html=True)
                with r4:
                    st.markdown(f'<div style="padding-top:8px;font-size:12px;">₹{item.get("selling_price",0):,.0f}</div>', unsafe_allow_html=True)
                with r5:
                    if st.button("✏️ Edit", key=f"edit_{code}", use_container_width=True):
                        st.session_state["edit_item_code"] = code
                        st.session_state["confirm_delete_item"] = None
                        st.rerun()
                with r6:
                    if st.session_state["confirm_delete_item"] == code:
                        if st.button("✅ Confirm", key=f"conf_del_{code}", use_container_width=True):
                            # Delete item and its children
                            children = [c for c, d in st.session_state["items"].items() if d.get("parent") == code]
                            for child in children:
                                del st.session_state["items"][child]
                            del st.session_state["items"][code]
                            if code in st.session_state["boms"]:
                                del st.session_state["boms"][code]
                            if code in st.session_state["routings"]:
                                del st.session_state["routings"][code]
                            save_data()
                            st.session_state["confirm_delete_item"] = None
                            st.success(f"'{code}' deleted!")
                            st.rerun()
                    else:
                        if st.button("🗑 Delete", key=f"del_{code}", use_container_width=True):
                            st.session_state["confirm_delete_item"] = code
                            st.rerun()

                # Confirm warning
                if st.session_state["confirm_delete_item"] == code:
                    _warn = f"⚠️ '{code}' delete hoga" + (f" + {child_count} child SKUs" if child_count else "") + ". Pakka?"
                    st.markdown(f'<div class="danger-box" style="margin:2px 0 4px 0;">{_warn}</div>', unsafe_allow_html=True)

                st.markdown('<hr style="margin:3px 0;border-color:#e2e5ef;">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BOM MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "🔩 BOM Management":
    st.markdown('<h1>BOM Management</h1>', unsafe_allow_html=True)
    
    bom_tab1, bom_tab2, bom_tab3 = st.tabs(["➕ Create / Edit BOM", "📋 BOM List", "💰 BOM Costing"])
    
    with bom_tab1:
        st.markdown('''<div class="warn-box">ℹ️ BOM mein components tab tab add honge jab vo pehle se Item Master mein create ho. Components existing items mein se select karein.</div>''', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            target_item = st.selectbox("Select Item for BOM *", [""] + list(st.session_state["items"].keys()))
        with col2:
            bom_number = st.selectbox("BOM Number", ["BOM-1 (Default)", "BOM-2 (Alt Fabric)", "BOM-3"])
            bom_desc = st.text_input("BOM Description", placeholder="e.g. 56 inch fabric width")

        if target_item:
            item_sizes = st.session_state["items"][target_item].get("sizes", [])
            has_existing_bom = target_item in st.session_state["boms"]

            if has_existing_bom:
                st.markdown(f'<div class="ok-box">✅ <strong>{target_item}</strong> ka BOM already exists — edit kar sakte ho neeche. Lines load ho gayi hain.</div>', unsafe_allow_html=True)

            # BOM Type
            bom_type = st.radio("BOM Type", ["Common BOM (applies to all sizes)", "Size-wise BOM (different per size)"], horizontal=True)

            if bom_type == "Size-wise BOM (different per size)" and item_sizes:
                size_group = st.selectbox("Define BOM for size group:", item_sizes)

            # Copy BOM feature
            existing_boms = list(st.session_state["boms"].keys())
            if existing_boms:
                st.markdown("#### 📋 Copy from Existing BOM")
                copy_from = st.selectbox("Copy BOM from item:", ["— Don't copy —"] + existing_boms)

            # ── Session state keys ──────────────────────────────────────────
            bom_key  = f"bom_lines_{target_item}"
            proc_key = f"proc_lines_{target_item}"

            if bom_key not in st.session_state:
                if has_existing_bom:
                    # Load existing BOM lines for editing
                    st.session_state[bom_key]  = st.session_state["boms"][target_item].get("lines", []).copy()
                    st.session_state[proc_key] = st.session_state["boms"][target_item].get("process_lines", []).copy()
                elif 'copy_from' in dir() and copy_from != "\u2014 Don't copy \u2014" and copy_from in st.session_state["boms"]:
                    st.session_state[bom_key]  = st.session_state["boms"][copy_from].get("lines", []).copy()
                    st.session_state[proc_key] = st.session_state["boms"][copy_from].get("process_lines", []).copy()
                else:
                    st.session_state[bom_key]  = []
                    st.session_state[proc_key] = []

            if proc_key not in st.session_state:
                st.session_state[proc_key] = []

            # Reload button — force reload from saved BOM
            if has_existing_bom:
                rb1, rb2 = st.columns(2)
                with rb1:
                    if st.button("🔄 Reload from Saved BOM", key="reload_bom"):
                        st.session_state[bom_key]  = st.session_state["boms"][target_item].get("lines", []).copy()
                        st.session_state[proc_key] = st.session_state["boms"][target_item].get("process_lines", []).copy()
                        st.rerun()
                with rb2:
                    if st.button("🗑 Delete Existing BOM & Fresh Start", key="del_bom"):
                        del st.session_state["boms"][target_item]
                        st.session_state[bom_key]  = []
                        st.session_state[proc_key] = []
                        save_data()
                        st.success(f"✅ {target_item} ka BOM delete ho gaya — ab fresh BOM banao!")
                        st.rerun()

            # ================================================================
            # SECTION 1 - MATERIAL / COMPONENT LINES
            # ================================================================
            st.markdown("#### 🧵 Material / Component Lines")
            st.caption("Item Master mein pehle se bane hue components yahan add karein")

            with st.expander("➕ Add Material Line", expanded=len(st.session_state[bom_key]) == 0):
                c1, c2, c3 = st.columns(3)
                with c1:
                    component_items = {k: v["name"] for k, v in st.session_state["items"].items() if k != target_item}
                    if component_items:
                        comp_code = st.selectbox("Component Item *",
                                                  [""] + [f"{k} – {v}" for k, v in component_items.items()],
                                                  key="new_comp")
                    else:
                        st.markdown('<div class="warn-box">No components in Item Master. Create Raw Materials first.</div>', unsafe_allow_html=True)
                        comp_code = ""
                    qty  = st.number_input("Quantity *", min_value=0.0, step=0.1, key="new_qty")
                    unit = st.selectbox("Unit", UNITS, key="new_unit")
                with c2:
                    rate      = st.number_input("Rate (₹/unit)", min_value=0.0, step=1.0, key="new_rate")
                    shrinkage = st.number_input("Shrinkage %", min_value=0.0, max_value=100.0, step=0.5, key="new_shrink")
                    wastage   = st.number_input("Wastage %",   min_value=0.0, max_value=100.0, step=0.5, key="new_waste")
                with c3:
                    process_used = st.selectbox("Used In Process", ["\u2014"] + st.session_state["processes"], key="new_process")
                    remarks      = st.text_input("Remarks", key="new_remarks")

                if st.button("➕ Add Material Line"):
                    if comp_code and qty > 0:
                        actual_qty = qty * (1 + shrinkage/100) * (1 + wastage/100)
                        amount     = actual_qty * rate
                        ck = comp_code.split(" – ")[0] if " – " in comp_code else comp_code
                        st.session_state[bom_key].append({
                            "line_type": "Material",
                            "item_code": ck,
                            "item_name": component_items.get(ck, ck),
                            "item_type": st.session_state["items"].get(ck, {}).get("item_type", ""),
                            "qty": qty, "unit": unit, "rate": rate,
                            "shrinkage": shrinkage, "wastage": wastage,
                            "actual_qty": round(actual_qty, 3),
                            "amount": round(amount, 2),
                            "process": process_used, "remarks": remarks,
                        })
                        st.rerun()

            mat_lines = st.session_state[bom_key]
            if mat_lines:
                df_mat = pd.DataFrame(mat_lines)
                sc = [x for x in ["item_code","item_name","item_type","qty","unit","rate","shrinkage","actual_qty","amount","process","remarks"] if x in df_mat.columns]
                st.dataframe(df_mat[sc].rename(columns={
                    "item_code":"Code","item_name":"Component","item_type":"Type",
                    "qty":"Qty","unit":"Unit","rate":"Rate(₹)","shrinkage":"Shrink%",
                    "actual_qty":"Net Qty","amount":"Amount(₹)","process":"Process","remarks":"Remarks"
                }), use_container_width=True, hide_index=True)
                del_mat = st.number_input("Delete material line # (1-based, 0=none)", min_value=0, max_value=len(mat_lines), step=1, key="del_mat")
                if st.button("🗑 Delete Material Line") and del_mat > 0:
                    st.session_state[bom_key].pop(del_mat - 1); st.rerun()

            mat_total = sum(l.get("amount", 0) for l in mat_lines)
            st.markdown(f'<div class="card" style="text-align:right;padding:10px 16px;">Material Total: <strong style="color:#c8a96e;">₹{mat_total:,.2f}</strong></div>', unsafe_allow_html=True)

            st.markdown("---")

            # ================================================================
            # SECTION 2 - PROCESS COST LINES
            # ================================================================
            st.markdown("#### ⚙️ Process Cost Lines")
            st.caption("Har process ki alag rate daalein — jaise Cutting ₹2/piece, Stitching ₹15/piece")

            with st.expander("➕ Add Process Cost Line", expanded=len(st.session_state[proc_key]) == 0):
                p1, p2, p3 = st.columns(3)
                with p1:
                    proc_name = st.selectbox("Process *", [""] + st.session_state["processes"], key="new_proc_name")
                    proc_qty  = st.number_input("Qty / Pieces", min_value=0.0, value=1.0, step=1.0, key="new_proc_qty")
                with p2:
                    proc_unit = st.selectbox("Unit", ["Per Piece","Per Meter","Per KG","Per Set","Lump Sum"], key="new_proc_unit")
                    proc_rate = st.number_input("Rate (₹)", min_value=0.0, step=0.5, key="new_proc_rate")
                with p3:
                    proc_vendor  = st.text_input("Vendor / Job Worker", key="new_proc_vendor", placeholder="e.g. Sharma Cutting Unit")
                    proc_remarks = st.text_input("Remarks", key="new_proc_remarks")

                if st.button("➕ Add Process Line"):
                    if proc_name:
                        st.session_state[proc_key].append({
                            "line_type": "Process",
                            "process":   proc_name,
                            "qty":       proc_qty,
                            "unit":      proc_unit,
                            "rate":      proc_rate,
                            "amount":    round(proc_qty * proc_rate, 2),
                            "vendor":    proc_vendor,
                            "remarks":   proc_remarks,
                        })
                        st.rerun()

            proc_lines = st.session_state[proc_key]
            if proc_lines:
                df_proc = pd.DataFrame(proc_lines)
                sp = [x for x in ["process","qty","unit","rate","amount","vendor","remarks"] if x in df_proc.columns]
                st.dataframe(df_proc[sp].rename(columns={
                    "process":"Process","qty":"Qty","unit":"Unit",
                    "rate":"Rate(₹)","amount":"Amount(₹)","vendor":"Vendor","remarks":"Remarks"
                }), use_container_width=True, hide_index=True)
                del_proc = st.number_input("Delete process line # (1-based, 0=none)", min_value=0, max_value=len(proc_lines), step=1, key="del_proc")
                if st.button("🗑 Delete Process Line") and del_proc > 0:
                    st.session_state[proc_key].pop(del_proc - 1); st.rerun()

            proc_total = sum(l.get("amount", 0) for l in proc_lines)
            st.markdown(f'<div class="card" style="text-align:right;padding:10px 16px;">Process Cost Total: <strong style="color:#c8a96e;">₹{proc_total:,.2f}</strong></div>', unsafe_allow_html=True)

            st.markdown("---")

            # ================================================================
            # SECTION 3 - CMT + OTHER COSTS
            # ================================================================
            st.markdown("#### 💼 CMT & Other Costs")
            cm1, cm2 = st.columns(2)
            with cm1:
                cmt_cost   = st.number_input("CMT Cost (₹)", min_value=0.0, step=5.0,
                                              help="Overall job work cost (agar process-wise nahi dalna)")
            with cm2:
                other_cost = st.number_input("Other Cost (₹)", min_value=0.0, step=5.0,
                                              help="Transport, overhead etc.")

            grand_total = mat_total + proc_total + cmt_cost + other_cost

            st.markdown(f"""
<div class="card" style="margin-top:12px;">
  <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-end;">
    <div>
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Material</div>
      <div style="font-size:20px;font-weight:600;">₹{mat_total:,.2f}</div>
    </div>
    <div style="color:#555;font-size:20px;align-self:center;">+</div>
    <div>
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Process</div>
      <div style="font-size:20px;font-weight:600;">₹{proc_total:,.2f}</div>
    </div>
    <div style="color:#555;font-size:20px;align-self:center;">+</div>
    <div>
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">CMT</div>
      <div style="font-size:20px;font-weight:600;">₹{cmt_cost:,.2f}</div>
    </div>
    <div style="color:#555;font-size:20px;align-self:center;">+</div>
    <div>
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Other</div>
      <div style="font-size:20px;font-weight:600;">₹{other_cost:,.2f}</div>
    </div>
    <div style="margin-left:auto;text-align:right;">
      <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Total Production Cost</div>
      <div style="font-size:30px;font-weight:700;color:#c8a96e;">₹{grand_total:,.2f}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

            # Save BOM
            st.markdown("---")

            # Show warning if BOM is certified
            _bom_status = st.session_state["boms"].get(target_item, {}).get("status", "")
            if _bom_status == "Certified":
                st.markdown('<div class="warn-box">⚠️ Yeh BOM "Certified" hai — save karne par status "Draft" ho jaayega. Lines add karo phir dobara Certify karo.</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save BOM (Draft)", use_container_width=True):
                    st.session_state["boms"][target_item] = {
                        "item_code":     target_item,
                        "bom_number":    bom_number,
                        "description":   bom_desc,
                        "bom_type":      bom_type,
                        "lines":         st.session_state.get(bom_key, []),
                        "process_lines": st.session_state.get(proc_key, []),
                        "cmt_cost":      cmt_cost,
                        "other_cost":    other_cost,
                        "mat_total":     mat_total,
                        "proc_total":    proc_total,
                        "total":         grand_total,
                        "status":        "Draft",
                        "created_at":    datetime.now().isoformat(),
                    }
                    save_data()
                    st.success("✅ BOM saved as Draft!")

            with col2:
                if st.button("✅ Certify BOM (Admin Only)", use_container_width=True):
                    # In real app, check admin role
                    admin_pass = st.session_state.get("admin_verified", False)
                    if target_item in st.session_state["boms"]:
                        st.session_state["boms"][target_item]["status"] = "Certified"
                        save_data()
                        st.success("✅ BOM Certified! Only Admin can now modify it.")
                    else:
                        st.warning("Save BOM first before certifying.")
            with col3:
                if st.button("🗑️ Clear BOM Lines", use_container_width=True):
                    st.session_state[bom_key] = []
                    st.rerun()
    
    with bom_tab2:
        st.markdown("#### All BOMs")
        if not st.session_state["boms"]:
            st.markdown('<div class="warn-box">No BOMs created yet.</div>', unsafe_allow_html=True)
        else:
            for item_code, bom in st.session_state["boms"].items():
                item_name = st.session_state["items"].get(item_code, {}).get("name", item_code)
                status = bom.get("status", "Draft")
                badge = f'<span class="badge {"badge-certified" if status == "Certified" else "badge-pending"}">{status}</span>'
                
                st.markdown(f'''<div class="card card-accent" style="margin:6px 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="tag tag-accent">{item_code}</span>
                            <span style="margin-left:8px; font-weight:500;">{item_name}</span>
                            <span style="margin-left:8px; color:var(--text-muted); font-size:12px;">{bom.get("bom_number","BOM-1")} | {len(bom.get("lines",[]))} components</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="color:var(--accent); font-weight:600;">₹{bom.get("total",0):,.2f}</span>
                            {badge}
                        </div>
                    </div>
                </div>''', unsafe_allow_html=True)
                
                with st.expander(f"View BOM Lines – {item_code}"):
                    lines = bom.get("lines", [])
                    if lines:
                        df = pd.DataFrame(lines)
                        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with bom_tab3:
        st.markdown("#### BOM Costing Summary")
        if not st.session_state["boms"]:
            st.markdown('<div class="warn-box">No BOMs available for costing.</div>', unsafe_allow_html=True)
        else:
            selected_bom_item = st.selectbox("Select Item", list(st.session_state["boms"].keys()))
            if selected_bom_item:
                bom = st.session_state["boms"][selected_bom_item]
                lines = bom.get("lines", [])
                
                # Categorize costs
                fabric_cost = sum(l["amount"] for l in lines if "fabric" in l.get("item_name","").lower() or "grey" in l.get("item_name","").lower())
                acc_cost = sum(l["amount"] for l in lines if l.get("item_type","") == "Accessories")
                pack_cost = sum(l["amount"] for l in lines if l.get("item_type","") == "Packing Materials")
                other_comp = sum(l["amount"] for l in lines) - fabric_cost - acc_cost - pack_cost
                
                cost_data = {
                    "Cost Head": ["Fabric Cost", "Accessory Cost", "Packing Cost", "Other Components", 
                                  "Process Cost", "CMT Cost", "Other Cost"],
                    "Amount (₹)": [fabric_cost, acc_cost, pack_cost, other_comp,
                                   bom.get("process_cost", 0), bom.get("cmt_cost", 0), bom.get("other_cost", 0)]
                }
                df_cost = pd.DataFrame(cost_data)
                df_cost = df_cost[df_cost["Amount (₹)"] > 0]
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.dataframe(df_cost, use_container_width=True, hide_index=True)
                    st.markdown(f'''<div class="card card-accent">
                        <div style="color:var(--text-muted); font-size:12px;">TOTAL PRODUCTION COST</div>
                        <div style="font-size:28px; color:var(--accent); font-family:'DM Serif Display',serif;">₹{bom.get("total",0):,.2f}</div>
                    </div>''', unsafe_allow_html=True)
                with col2:
                    if not df_cost.empty:
                        st.bar_chart(df_cost.set_index("Cost Head"))

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING MASTER
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "🔄 Routing Master":
    st.markdown('<h1>Routing Master</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### Add New Process")
        new_process = st.text_input("Process Name", placeholder="e.g. Washing, Embroidery")
        if st.button("➕ Add Process"):
            if new_process and new_process not in st.session_state["processes"]:
                st.session_state["processes"].append(new_process)
                save_data()
                st.success(f"Process '{new_process}' added!")
                st.rerun()
    
    with col2:
        st.markdown("#### Current Process Master")
        for i, p in enumerate(st.session_state["processes"], 1):
            st.markdown(f'<div class="card" style="padding:8px 14px; margin:3px 0;"><span class="section-number">{i}</span> <span style="margin-left:8px;">{p}</span></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Item-wise Routing View")
    for item_code, route in st.session_state["routings"].items():
        item_name = st.session_state["items"].get(item_code, {}).get("name", item_code)
        route_str = " → ".join(route)
        st.markdown(f'''<div class="card" style="margin:4px 0;">
            <span class="tag tag-accent">{item_code}</span>
            <span style="margin:0 8px; font-weight:500;">{item_name}</span>
            <span style="color:var(--text-muted); font-size:13px;">{route_str}</span>
        </div>''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MERCHANT MASTER
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "👤 Merchant Master":
    st.markdown('<h1>Merchant Master</h1>', unsafe_allow_html=True)
    st.markdown('''<div class="info-box">✓ Merchant codes pehle yahan create karein, tab Item Master mein drop-down mein dikhenge</div>''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### Add New Merchant")
        mc_code = st.text_input("Merchant Code *", placeholder="e.g. MC004")
        mc_name = st.text_input("Merchant Name *", placeholder="e.g. Jain Fabrics Pvt Ltd")
        mc_contact = st.text_input("Contact Person", placeholder="e.g. Rajesh Jain")
        mc_phone = st.text_input("Phone", placeholder="e.g. +91 98765 43210")
        
        if st.button("💾 Save Merchant", use_container_width=True):
            if mc_code and mc_name:
                st.session_state["merchants"][mc_code] = mc_name
                save_data()
                st.success(f"Merchant '{mc_name}' ({mc_code}) added!")
                st.rerun()
            else:
                st.error("Code and Name are required!")
    
    with col2:
        st.markdown("#### Merchant List")
        if st.session_state["merchants"]:
            df_merchants = pd.DataFrame([
                {"Code": k, "Name": v} for k, v in st.session_state["merchants"].items()
            ])
            st.dataframe(df_merchants, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No merchants added yet.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BUYER PACKAGING
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "📦 Buyer Packaging":
    st.markdown('<h1>Buyer Packaging Master</h1>', unsafe_allow_html=True)
    st.markdown('''<div class="info-box">✓ Item wise buyer-specific packaging define karein. Sales Order banate waqt system automatically sahi packaging identify karega.</div>''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add buyers
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### Buyer Master")
        new_buyer = st.text_input("Add Buyer", placeholder="e.g. H&M India")
        if st.button("➕ Add Buyer"):
            if new_buyer and new_buyer not in st.session_state["buyers"]:
                st.session_state["buyers"].append(new_buyer)
                save_data()
                st.success(f"Buyer '{new_buyer}' added!")
                st.rerun()
        
        st.markdown("**Current Buyers:**")
        for b in st.session_state["buyers"]:
            st.markdown(f'<span class="tag tag-accent">{b}</span>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### View Item Packaging Definitions")
        items_with_packaging = {k: v for k, v in st.session_state["items"].items() if v.get("buyer_packaging")}

        if items_with_packaging:
            for item_code, item in items_with_packaging.items():
                pkg = item.get("buyer_packaging", {})
                if pkg:
                    with st.expander(f"📦 {item_code} – {item.get('name', '')}"):
                        for buyer, lines in pkg.items():
                            if lines:
                                st.markdown(f"**{buyer}**")
                                for ln in lines:
                                    st.markdown(f'<div class="card" style="padding:8px 12px;margin:3px 0;display:flex;gap:16px;font-size:13px;"><span class="tag tag-gold">{ln.get("item_code","")}</span> <span>{ln.get("item_name","")}</span> <span style="color:#64748b;">{ln.get("qty","")} {ln.get("uom","")}</span> <span style="color:#94a3b8;">{ln.get("remarks","")}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">No buyer packaging defined yet. Item create karte waqt Buyer Packaging tab mein define karo.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# SALES ORDER MODULE
# ═══════════════════════════════════════════════════════════════════════
elif nav_so == "📊 SO Dashboard":
    st.markdown('<h1>Sales Order Dashboard</h1>', unsafe_allow_html=True)

    # KPI Cards
    total_open = sum(1 for s in SS["so_list"].values() if s.get("status") not in ["Closed","Cancelled","Fully Received"])
    today_so   = sum(1 for s in SS["so_list"].values() if s.get("so_date") == str(date.today()))
    overdue    = sum(1 for s in SS["so_list"].values()
                     if s.get("status") not in ["Closed","Cancelled","Fully Received"]
                     and s.get("delivery_date","9999") < str(date.today()))
    pending_qty = sum(
        line["qty"] - line.get("received_qty", 0)
        for s in SS["so_list"].values()
        if s.get("status") not in ["Closed","Cancelled"]
        for line in s.get("lines", [])
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_open}</div><div class="kpi-label">Total Open SOs</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card kpi-accent"><div class="kpi-value">{int(pending_qty)}</div><div class="kpi-label">Pending SO Qty</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card kpi-green"><div class="kpi-value">{today_so}</div><div class="kpi-label">Today Created SOs</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card kpi-warn"><div class="kpi-value">{overdue}</div><div class="kpi-label">Overdue Orders</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### Recent Sales Orders")
        if SS["so_list"]:
            rows = []
            for so_no, so in list(SS["so_list"].items())[-10:]:
                total_q = sum(l["qty"] for l in so.get("lines", []))
                rcvd_q  = sum(l.get("received_qty", 0) for l in so.get("lines", []))
                rows.append({
                    "SO #": so_no,
                    "Buyer": so.get("buyer", ""),
                    "Source": so.get("order_source", ""),
                    "Total Qty": total_q,
                    "Received": rcvd_q,
                    "Pending": total_q - rcvd_q,
                    "Delivery": so.get("delivery_date", ""),
                    "Status": so.get("status", "Draft"),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No Sales Orders yet. Create one from "Create Sales Order".</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### SKU Running Days Alert")
        alert_rows = []
        _all = get_all_skus()
        for sku in list(_all.keys())[:20]:
            _i = get_sku_info(sku)
            rd = running_days(sku)
            alert_rows.append({"SKU": sku, "Stock": _i.get("stock",0), "Running Days": rd})
        alert_rows.sort(key=lambda x: x["Running Days"])
        for row in alert_rows[:6]:
            rd = row["Running Days"]
            color = "#ef4444" if rd < 7 else "#d97706" if rd < 15 else "#059669"
            pct = min(rd / 30 * 100, 100)
            fill_cls = "prog-fill-red" if rd < 7 else ""
            st.markdown(f'''<div class="card" style="padding:12px 16px;margin:4px 0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-family:Inconsolata,monospace;font-size:13px;">{row["SKU"]}</span>
                    <span style="font-weight:700;color:{color};">{rd} days</span>
                </div>
                <div class="prog-wrap"><div class="{f"prog-fill {fill_cls}"}" style="width:{pct}%;"></div></div>
                <div style="font-size:11px;color:#888;">Stock: {row["Stock"]} pcs</div>
            </div>''', unsafe_allow_html=True)

    # Status distribution
    st.markdown("---")
    st.markdown("#### SO Status Distribution")
    status_counts = {}
    for so in SS["so_list"].values():
        s = so.get("status", "Draft")
        status_counts[s] = status_counts.get(s, 0) + 1

    if status_counts:
        c1, c2, c3, c4 = st.columns(4)
        cols = [c1, c2, c3, c4]
        for i, (status, count) in enumerate(status_counts.items()):
            with cols[i % 4]:
                st.markdown(f'<div class="card" style="text-align:center;padding:16px;">{badge(status)}<div style="font-size:24px;font-weight:700;margin-top:8px;font-family:Syne,sans-serif;">{count}</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DEMAND MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
elif nav_so == "📋 Demand Management":
    st.markdown('<h1>Demand Management</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Demand = Sales Team ya Forecasting se aane wali requirement. Demand ke against Sales Orders bante hain.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    dtab1, dtab2 = st.tabs(["➕ Create Demand", "📋 Demand List & Tracking"])

    with dtab1:
        col1, col2 = st.columns(2)
        with col1:
            dem_no = next_demand()
            st.markdown(f'<div class="card card-left" style="padding:10px 16px;"><span class="sec-label">Auto Demand Number</span><br><span style="font-family:Inconsolata,monospace;font-size:20px;font-weight:700;">{dem_no}</span></div>', unsafe_allow_html=True)
            dem_date   = st.date_input("Demand Date", value=date.today(), key="dem_date")
            dem_source = st.selectbox("Demand Source", ["Sales Team", "Forecasting System", "Buyer Indent", "Marketing Team"])
            dem_buyer  = st.selectbox("Buyer / Customer", ["All"] + SS["buyers"])
        with col2:
            dem_delivery = st.date_input("Required By Date", value=date.today() + timedelta(days=30), key="dem_delivery")
            dem_priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])
            dem_remarks  = st.text_area("Remarks", height=80, key="dem_remarks")

        st.markdown("---")
        st.markdown("#### Add SKU Lines to Demand")

        dem_lines_key = "dem_lines_new"
        if dem_lines_key not in st.session_state:
            st.session_state[dem_lines_key] = []

        with st.expander("➕ Add SKU to Demand", expanded=True):
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                _all_skus_d = get_all_skus()
                d_sku = st.selectbox("SKU / Style-Size *", [""] + list(_all_skus_d.keys()),
                                     format_func=lambda x: f"{x}  —  {_all_skus_d.get(x,'')}" if x else "— Select SKU —",
                                     key="d_sku")
                if d_sku:
                    _di = get_sku_info(d_sku)
                    st.markdown(f'<div class="ok-box">Stock: {_di.get("stock",0)} | Reserved: {_di.get("reserved",0)} | Running Days: {running_days(d_sku)}</div>', unsafe_allow_html=True)
            with dc2:
                d_qty     = st.number_input("Demand Qty *", min_value=0, step=10, key="d_qty")
                d_uom     = st.selectbox("UOM", ["Pieces", "Set", "Dozen"], key="d_uom")
            with dc3:
                d_remarks = st.text_input("Remarks", key="d_line_remarks")

            if st.button("➕ Add SKU Line to Demand"):
                if d_sku and d_qty > 0:
                    st.session_state[dem_lines_key].append({
                        "sku": d_sku,
                        "sku_name": get_sku_info(d_sku).get("name", d_sku),
                        "parent": get_sku_info(d_sku).get("parent", ""),
                        "size": d_sku.split("-")[-1] if "-" in d_sku else "",
                        "demand_qty": d_qty,
                        "so_qty": 0,
                        "pending_qty": d_qty,
                        "uom": d_uom,
                        "remarks": d_remarks,
                    })
                    st.rerun()

        dem_lines = st.session_state[dem_lines_key]
        if dem_lines:
            st.markdown(f"**{len(dem_lines)} lines added:**")
            for idx, ln in enumerate(dem_lines):
                dl1, dl2, dl3, dl4, dl5, dl6 = st.columns([1.5, 2, 1, 1, 1, 0.5])
                with dl1: st.markdown(f'<div style="padding-top:8px;font-size:12px;font-family:monospace;color:#c8a96e;">{ln.get("parent","")}</div>', unsafe_allow_html=True)
                with dl2: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>{ln.get("sku","")}</strong> <span style="color:#94a3b8;">({ln.get("size","")})</span><br><span style="font-size:11px;color:#64748b;">{ln.get("sku_name","")}</span></div>', unsafe_allow_html=True)
                with dl3: st.markdown(f'<div style="padding-top:8px;font-size:13px;">{ln.get("demand_qty",0)} {ln.get("uom","")}</div>', unsafe_allow_html=True)
                with dl4: st.markdown(f'<div style="padding-top:8px;font-size:12px;color:#64748b;">{ln.get("remarks","")}</div>', unsafe_allow_html=True)
                with dl5: st.markdown(f'<div style="padding-top:8px;"></div>', unsafe_allow_html=True)
                with dl6:
                    if st.button("🗑", key=f"del_dem_line_{idx}"):
                        st.session_state[dem_lines_key].pop(idx)
                        st.rerun()
                st.markdown('<hr style="margin:2px 0;border-color:#e2e5ef;">', unsafe_allow_html=True)

            if st.button("💾 Save Demand"):
                SS["demands"][dem_no] = {
                    "dem_no": dem_no,
                    "dem_date": str(dem_date),
                    "source": dem_source,
                    "buyer": dem_buyer,
                    "delivery_date": str(dem_delivery),
                    "priority": dem_priority,
                    "remarks": dem_remarks,
                    "lines": dem_lines.copy(),
                    "status": "Open",
                    "created_at": datetime.now().isoformat(),
                }
                st.session_state[dem_lines_key] = []
                # Increment counter properly
                SS["demand_counter"] = int(dem_no.split("-")[1]) + 1
                save_data()
                st.success(f"✅ Demand {dem_no} created successfully!")
                st.rerun()

    with dtab2:
        if not SS["demands"]:
            st.markdown('<div class="warn-box">No demands created yet.</div>', unsafe_allow_html=True)
        else:
            for dem_no, dem in SS["demands"].items():
                total_dem_qty = sum(l["demand_qty"] for l in dem.get("lines", []))
                # Count SO qty against this demand
                so_against = sum(
                    l["qty"] for so in SS["so_list"].values()
                    if so.get("ref_number") == dem_no
                    for l in so.get("lines", [])
                )
                pending = max(0, total_dem_qty - so_against)
                pct = int((so_against / total_dem_qty * 100)) if total_dem_qty > 0 else 0

                with st.expander(f"📋 {dem_no} | {dem.get('buyer','')} | {total_dem_qty} pcs | SO Coverage: {pct}%"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Date:** {dem.get('dem_date')}  \n**Source:** {dem.get('source')}  \n**Priority:** {dem.get('priority')}")
                    with col2:
                        st.markdown(f"**Total Demand:** {total_dem_qty} pcs  \n**SO Created:** {so_against} pcs  \n**Pending SO:** {pending} pcs")
                    with col3:
                        fill_cls = "prog-fill-red" if pct < 30 else ""
                        st.markdown(f'''<div style="padding-top:8px;">
                            <div style="font-size:11px;color:#888;">SO Coverage</div>
                            <div class="prog-wrap"><div class="prog-fill {fill_cls}" style="width:{pct}%;"></div></div>
                            <div style="font-size:13px;font-weight:700;color:#d4a853;">{pct}%</div>
                        </div>''', unsafe_allow_html=True)

                    # SKU-level tracking
                    if dem.get("lines"):
                        st.markdown("**SKU-wise Demand vs SO:**")
                        sku_rows = []
                        for line in dem["lines"]:
                            sku_so = sum(
                                l["qty"] for so in SS["so_list"].values()
                                if so.get("ref_number") == dem_no
                                for l in so.get("lines", []) if l["sku"] == line["sku"]
                            )
                            sku_rows.append({
                                "SKU": line["sku"], "Name": line["sku_name"],
                                "Demand Qty": line["demand_qty"],
                                "SO Created": sku_so,
                                "Pending": max(0, line["demand_qty"] - sku_so),
                            })
                        st.dataframe(pd.DataFrame(sku_rows), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CREATE SALES ORDER
# ═══════════════════════════════════════════════════════════════════════════════
elif nav_so == "➕ Create Sales Order":
    st.markdown('<h1>Create Sales Order</h1>', unsafe_allow_html=True)

    so_tab1, so_tab2, so_tab3 = st.tabs(["📝 SO Header", "🧵 SO Lines", "💰 Financials"])

    # -- shared state for SO being created
    if "new_so_lines" not in st.session_state:
        st.session_state["new_so_lines"] = []

    with so_tab1:
        st.markdown('<div class="sec-label">Header Information</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            so_number = f"SO-{SS['so_counter']:04d}"
            st.markdown(f'<div class="card card-left" style="padding:10px 16px;"><span class="sec-label">Auto SO Number</span><br><span style="font-family:Inconsolata,monospace;font-size:22px;font-weight:700;">{so_number}</span></div>', unsafe_allow_html=True)
            so_date      = st.date_input("SO Date", value=date.today(), key="_so_date")
            order_source = st.selectbox("Order Source *", ORDER_SOURCES, key="_so_src")
            warehouse    = st.selectbox("Warehouse", SS["warehouses"], key="_so_wh")

        with col2:
            buyer         = st.selectbox("Buyer / Customer *", [""] + SS["buyers"], key="_so_buyer")
            delivery_date = st.date_input("Delivery Date", value=date.today() + timedelta(days=21), key="_so_del")
            dispatch_date = st.date_input("Planned Dispatch Date", value=date.today() + timedelta(days=18), key="_so_disp")
            sales_team    = st.selectbox("Sales Team", SS["sales_teams"], key="_so_team")

        with col3:
            # Reference fields based on source
            ref_map = {
                "Sales Team Demand": ("Demand Number", list(SS["demands"].keys())),
                "Buyer PO": ("Buyer PO Number", []),
                "Offline Order": ("Offline Order Number", []),
            }
            ref_label, ref_options = ref_map.get(order_source, ("Reference Number", []))

            if ref_options:
                ref_number = st.selectbox(f"{ref_label} *", [""] + ref_options, key="_so_ref")
                # Auto-fill buyer from demand + auto-populate lines
                if ref_number and ref_number in SS["demands"]:
                    dem = SS["demands"][ref_number]
                    st.markdown(f'<div class="ok-box">Demand: {ref_number} | Source: {dem.get("source")} | Priority: {dem.get("priority")}</div>', unsafe_allow_html=True)
                    # Auto-populate SO lines from demand if not already done
                    if st.session_state.get("_last_demand_loaded") != ref_number:
                        new_lines = []
                        for dl in dem.get("lines", []):
                            _info   = get_sku_info(dl["sku"])
                            _price  = float(_info.get("price", 0))
                            _gst    = 12
                            _taxable = dl["demand_qty"] * _price
                            _gst_amt = _taxable * _gst / 100
                            # Auto-fill merchant from item master
                            _item_merch = st.session_state.get("items", {}).get(dl["sku"], {}).get("merchant", "")
                            new_lines.append({
                                "sku":          dl["sku"],
                                "sku_name":     dl.get("sku_name", dl["sku"]),
                                "parent":       _info.get("parent", ""),
                                "size":         dl["sku"].split("-")[-1] if "-" in dl["sku"] else "",
                                "qty":          dl["demand_qty"],
                                "uom":          "Pieces",
                                "rate":         _price,
                                "gst_pct":      _gst,
                                "hsn":          st.session_state.get("items", {}).get(dl["sku"], {}).get("hsn", ""),
                                "merchant":     _item_merch,
                                "priority":     dem.get("priority", "Normal"),
                                "taxable":      round(_taxable, 2),
                                "gst_amount":   round(_gst_amt, 2),
                                "total":        round(_taxable + _gst_amt, 2),
                                "delivery_date": str(date.today() + timedelta(days=21)),
                                "produced_qty": 0, "dispatch_qty": 0, "received_qty": 0,
                                "remarks":      f"From {ref_number}",
                            })
                        st.session_state["new_so_lines"] = new_lines
                        st.session_state["_last_demand_loaded"] = ref_number
                        st.rerun()
            else:
                ref_number = st.text_input(f"{ref_label} *", placeholder=f"Enter {ref_label}", key="_so_ref")

            ref_date       = st.date_input("Reference Date", value=date.today(), key="_so_refdate")
            payment_terms  = st.selectbox("Payment Terms", SS["payment_terms"], key="_so_pay")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            merchant = st.text_input("Merchant Name / Code", placeholder="e.g. MC001 – Amit Textiles", key="_so_merchant")
        with col2:
            so_remarks = st.text_area("Remarks", height=70, key="_so_remarks")

    with so_tab2:
        st.markdown('<div class="sec-label">SO Line Items</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">Live inventory visibility ke saath SKU select karein. Size-wise quantity define karein.</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Show demand info if lines were loaded from demand
        _loaded_dem = st.session_state.get("_last_demand_loaded", "")
        if _loaded_dem and _loaded_dem in SS["demands"]:
            dem_ref = SS["demands"][_loaded_dem]
            _total_dem_qty = sum(dl["demand_qty"] for dl in dem_ref.get("lines", []))
            st.markdown(f'<div class="ok-box">✅ <strong>{_loaded_dem}</strong> ki {len(dem_ref.get("lines",[]))} lines auto-load ho gayi hain ({_total_dem_qty} pcs) — neeche edit/delete kar sakte ho.</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # Build SKU list from Item Master
        all_skus = get_all_skus()
        im_merchants = st.session_state.get("merchants", {})
        merchant_opts = [""] + [f"{k} – {v}" for k, v in im_merchants.items()]

        with st.expander("➕ Add SKU Line", expanded=len(st.session_state["new_so_lines"]) == 0):
            if not all_skus:
                st.markdown('<div class="warn-box">⚠️ Item Master mein koi SKU nahi mila. Pehle Item Master mein Finished Goods items banao aur size variants generate karo.</div>', unsafe_allow_html=True)

            lc1, lc2, lc3 = st.columns(3)
            with lc1:
                line_sku = st.selectbox("SKU / Style-Size *", [""] + list(all_skus.keys()),
                                         format_func=lambda x: f"{x}  —  {all_skus.get(x,'')}" if x else "— Select SKU —",
                                         key="line_sku")
                if line_sku:
                    info = get_sku_info(line_sku)
                    rd = running_days(line_sku)
                    rd_color = "#ef4444" if rd < 7 else "#d97706" if rd < 15 else "#059669"
                    st.markdown(f'''<div class="card" style="padding:10px 12px;margin:4px 0;">
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;">
                            <div><span style="color:#94a3b8;">Current Stock</span><br><strong>{info.get("stock",0)}</strong></div>
                            <div><span style="color:#94a3b8;">Reserved</span><br><strong>{info.get("reserved",0)}</strong></div>
                            <div><span style="color:#94a3b8;">In Production</span><br><strong>{info.get("in_production",0)}</strong></div>
                            <div><span style="color:#94a3b8;">Running Days</span><br><strong style="color:{rd_color};">{rd}</strong></div>
                            <div><span style="color:#94a3b8;">Avg Daily Sale</span><br><strong>{avg_daily_sale(line_sku)}</strong></div>
                            <div><span style="color:#94a3b8;">Available</span><br><strong>{info.get("stock",0) - info.get("reserved",0)}</strong></div>
                        </div>
                    </div>''', unsafe_allow_html=True)
                line_qty = st.number_input("Quantity *", min_value=0, step=10, key="line_qty")
                line_priority = st.selectbox("Priority", ["Normal", "High", "Urgent"], key="line_priority")

            with lc2:
                line_uom   = st.selectbox("UOM", ["Pieces", "Set", "Dozen"], key="line_uom")
                _sku_price = float(get_sku_info(line_sku).get("price", 0)) if line_sku else 0.0
                line_rate  = st.number_input("Rate (₹)", min_value=0.0, step=10.0, value=_sku_price, key="line_rate")
                line_gst   = st.selectbox("GST %", GST_RATES, index=2, key="line_gst")

                # Auto-fill merchant from Item Master — editable
                _item_merchant_raw = st.session_state.get("items", {}).get(line_sku, {}).get("merchant", "") if line_sku else ""
                # Extract just the code part (e.g. "MC001 – Amit Textiles" → "MC001")
                _item_merchant_code = _item_merchant_raw.split(" – ")[0] if " – " in _item_merchant_raw else _item_merchant_raw
                # Find matching option index in dropdown
                _merchant_default_idx = 0
                for _mi, _mopt in enumerate(merchant_opts):
                    if _mopt.startswith(_item_merchant_code) and _item_merchant_code:
                        _merchant_default_idx = _mi
                        break
                line_merchant = st.selectbox("Merchant Code", merchant_opts,
                                              index=_merchant_default_idx,
                                              key="line_merchant",
                                              help="Item Master se auto-filled — zaroorat ho toh change kar sakte hain")

            with lc3:
                # Auto-fill HSN from item master
                _hsn_default = st.session_state.get("items", {}).get(line_sku, {}).get("hsn", "") if line_sku else ""
                line_hsn     = st.text_input("HSN Code", value=_hsn_default, key="line_hsn")
                line_del     = st.date_input("Line Delivery Date", value=date.today() + timedelta(days=21), key="line_del")
                line_remarks = st.text_input("Remarks", key="line_remarks")

            if st.button("➕ Add Line to SO"):
                if line_sku and line_qty > 0:
                    taxable  = line_qty * line_rate
                    gst_amt  = taxable * line_gst / 100
                    _info    = get_sku_info(line_sku)
                    st.session_state["new_so_lines"].append({
                        "sku":          line_sku,
                        "sku_name":     _info.get("name", line_sku),
                        "parent":       _info.get("parent", ""),
                        "size":         line_sku.split("-")[-1] if "-" in line_sku else "",
                        "qty":          line_qty,
                        "uom":          line_uom,
                        "rate":         line_rate,
                        "gst_pct":      line_gst,
                        "hsn":          line_hsn,
                        "merchant":     line_merchant,
                        "priority":     line_priority,
                        "taxable":      round(taxable, 2),
                        "gst_amount":   round(gst_amt, 2),
                        "total":        round(taxable + gst_amt, 2),
                        "delivery_date":str(line_del),
                        "produced_qty": 0, "dispatch_qty": 0, "received_qty": 0,
                        "remarks":      line_remarks,
                    })
                    st.rerun()

        so_lines = st.session_state["new_so_lines"]
        if so_lines:
            st.markdown("#### ✏️ Lines — directly edit karo (Qty, Rate, GST%, Delivery, Priority, Remarks)")

            im_merchants = st.session_state.get("merchants", {})
            merchant_opts_list = [""] + [f"{k} – {v}" for k, v in im_merchants.items()]

            # Build editable dataframe
            edit_df = pd.DataFrame([{
                "Style Code":   ln.get("parent", ln["sku"].rsplit("-",1)[0] if "-" in ln["sku"] else ln["sku"]),
                "SKU Code":     ln["sku"],
                "Description":  ln.get("sku_name",""),
                "Size":         ln.get("size", ln["sku"].rsplit("-",1)[-1] if "-" in ln["sku"] else ""),
                "Qty":          int(ln.get("qty", 0)),
                "Rate (₹)":     float(ln.get("rate", 0)),
                "GST %":        int(ln.get("gst_pct", 12)),
                "Merchant":     ln.get("merchant",""),
                "Priority":     ln.get("priority","Normal"),
                "Delivery":     ln.get("delivery_date", str(date.today() + timedelta(days=21))),
                "Remarks":      ln.get("remarks",""),
            } for ln in so_lines])

            edited = st.data_editor(
                edit_df,
                use_container_width=True,
                hide_index=False,
                num_rows="dynamic",
                column_config={
                    "Style Code":  st.column_config.TextColumn("Style Code", disabled=True, width="small"),
                    "SKU Code":    st.column_config.TextColumn("SKU Code", disabled=True, width="small"),
                    "Description": st.column_config.TextColumn("Description", disabled=True, width="medium"),
                    "Size":        st.column_config.TextColumn("Size", disabled=True, width="small"),
                    "Qty":      st.column_config.NumberColumn("Qty", min_value=0, step=1, width="small"),
                    "Rate (₹)": st.column_config.NumberColumn("Rate (₹)", min_value=0.0, step=1.0, width="small"),
                    "GST %":    st.column_config.SelectboxColumn("GST %", options=GST_RATES, width="small"),
                    "Merchant": st.column_config.SelectboxColumn("Merchant", options=merchant_opts_list, width="medium"),
                    "Priority": st.column_config.SelectboxColumn("Priority", options=["Normal","High","Urgent"], width="small"),
                    "Delivery": st.column_config.TextColumn("Delivery (YYYY-MM-DD)", width="small"),
                    "Remarks":  st.column_config.TextColumn("Remarks", width="medium"),
                },
                key="so_lines_editor"
            )

            # Apply edits back to session state
            if st.button("✅ Apply Edits", use_container_width=False):
                updated_lines = []
                for i, row in edited.iterrows():
                    # Skip deleted rows (SKU Code empty or NaN)
                    sku_val = row.get("SKU Code", "")
                    if not sku_val or (isinstance(sku_val, float) and pd.isna(sku_val)):
                        continue
                    qty     = int(row["Qty"]) if not pd.isna(row["Qty"]) else 0
                    rate    = float(row["Rate (₹)"]) if not pd.isna(row["Rate (₹)"]) else 0.0
                    gst_raw = row.get("GST %", 12)
                    gst     = int(gst_raw) if gst_raw and not (isinstance(gst_raw, float) and pd.isna(gst_raw)) else 12
                    taxable = qty * rate
                    gst_amt = taxable * gst / 100
                    # Find original line by SKU Code
                    orig = next((l for l in so_lines if l["sku"] == sku_val), {})
                    if not orig:
                        orig = so_lines[i] if i < len(so_lines) else {}
                    updated_lines.append({
                        **orig,
                        "qty":          qty,
                        "rate":         rate,
                        "gst_pct":      gst,
                        "merchant":     row.get("Merchant",""),
                        "priority":     row.get("Priority","Normal"),
                        "delivery_date":str(row.get("Delivery", "")),
                        "remarks":      row.get("Remarks",""),
                        "taxable":      round(taxable, 2),
                        "gst_amount":   round(gst_amt, 2),
                        "total":        round(taxable + gst_amt, 2),
                    })
                st.session_state["new_so_lines"] = updated_lines
                st.success(f"✅ {len(updated_lines)} lines updated!")
                st.rerun()

            # Summary
            _sub = sum(ln.get("taxable",0) for ln in so_lines)
            _gst = sum(ln.get("gst_amount",0) for ln in so_lines)
            st.markdown(f'<div class="info-box" style="margin-top:8px;">Lines: <strong>{len(so_lines)}</strong> &nbsp;|&nbsp; Subtotal: <strong>₹{_sub:,.0f}</strong> &nbsp;|&nbsp; GST: <strong>₹{_gst:,.0f}</strong> &nbsp;|&nbsp; Total: <strong>₹{_sub+_gst:,.0f}</strong></div>', unsafe_allow_html=True)

    with so_tab3:
        so_lines = st.session_state["new_so_lines"]
        subtotal   = sum(l["taxable"] for l in so_lines)
        total_gst  = sum(l["gst_amount"] for l in so_lines)

        col1, col2 = st.columns(2)
        with col1:
            disc_pct      = st.number_input("Discount %", min_value=0.0, max_value=100.0, step=0.5, key="_so_disc")
            shipping      = st.number_input("Shipping Charges (₹)", min_value=0.0, step=50.0, key="_so_ship")
            other_charges = st.number_input("Other Charges (₹)", min_value=0.0, step=10.0, key="_so_other")

        disc_amt    = subtotal * disc_pct / 100
        taxable_net = subtotal - disc_amt
        grand_total = taxable_net + total_gst + shipping + other_charges

        with col2:
            st.markdown(f'''<div class="card card-left" style="padding:20px;">
                <table style="width:100%;font-size:14px;border-collapse:collapse;">
                    <tr><td style="padding:4px 0;color:#888;">Subtotal</td><td style="text-align:right;">₹{subtotal:,.2f}</td></tr>
                    <tr><td style="padding:4px 0;color:#888;">Discount ({disc_pct}%)</td><td style="text-align:right;color:#c0392b;">- ₹{disc_amt:,.2f}</td></tr>
                    <tr><td style="padding:4px 0;color:#888;">Taxable Amount</td><td style="text-align:right;">₹{taxable_net:,.2f}</td></tr>
                    <tr><td style="padding:4px 0;color:#888;">GST Amount</td><td style="text-align:right;">₹{total_gst:,.2f}</td></tr>
                    <tr><td style="padding:4px 0;color:#888;">Shipping</td><td style="text-align:right;">₹{shipping:,.2f}</td></tr>
                    <tr><td style="padding:4px 0;color:#888;">Other Charges</td><td style="text-align:right;">₹{other_charges:,.2f}</td></tr>
                    <tr style="border-top:2px solid #e8e3da;">
                        <td style="padding:10px 0 4px;font-family:Syne,sans-serif;font-weight:800;font-size:16px;">Grand Total</td>
                        <td style="text-align:right;font-family:Syne,sans-serif;font-weight:800;font-size:22px;color:#d4a853;">₹{grand_total:,.2f}</td>
                    </tr>
                </table>
            </div>''', unsafe_allow_html=True)

    # ── Save SO ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    sc1, sc2, sc3 = st.columns(3)

    def do_save(status):
        so_no   = f"SO-{SS['so_counter']:04d}"
        sl      = st.session_state.get("new_so_lines", [])
        if not sl:
            st.error("Add at least one SKU line!")
            return
        sub     = sum(l["taxable"] for l in sl)
        tgst    = sum(l["gst_amount"] for l in sl)
        dp      = st.session_state.get("_so_disc", 0.0)
        sh      = st.session_state.get("_so_ship", 0.0)
        oc      = st.session_state.get("_so_other", 0.0)
        da      = sub * dp / 100
        gt      = (sub - da) + tgst + sh + oc
        SS["so_list"][so_no] = {
            "so_number":    so_no,
            "so_date":      str(st.session_state.get("_so_date", date.today())),
            "order_source": st.session_state.get("_so_src", ""),
            "buyer":        st.session_state.get("_so_buyer", ""),
            "delivery_date":str(st.session_state.get("_so_del", date.today())),
            "dispatch_date":str(st.session_state.get("_so_disp", date.today())),
            "sales_team":   st.session_state.get("_so_team", ""),
            "ref_number":   st.session_state.get("_so_ref", ""),
            "ref_date":     str(st.session_state.get("_so_refdate", date.today())),
            "priority":     st.session_state.get("_so_priority", "Normal"),
            "payment_terms":st.session_state.get("_so_pay", ""),
            "warehouse":    st.session_state.get("_so_wh", ""),
            "merchant":     st.session_state.get("_so_merchant", ""),
            "remarks":      st.session_state.get("_so_remarks", ""),
            "discount_pct": dp, "shipping": sh, "other_charges": oc,
            "subtotal": sub, "total_gst": tgst, "grand_total": gt,
            "lines": sl, "status": status,
            "created_at": datetime.now().isoformat(),
        }
        SS["so_counter"] += 1
        st.session_state["new_so_lines"] = []
        st.session_state["_last_demand_loaded"] = ""
        save_data()
        st.success(f"✅ {so_no} saved as {status}!")
        st.rerun()

    with sc1:
        if st.button("💾 Save as Draft", use_container_width=True):
            do_save("Draft")
    with sc2:
        if st.button("📤 Save & Submit", use_container_width=True):
            do_save("Submitted")
    with sc3:
        if st.button("🗑 Clear All Lines", use_container_width=True):
            st.session_state["new_so_lines"] = []
            st.session_state["_last_demand_loaded"] = ""
            st.rerun()



# ═══════════════════════════════════════════════════════════════════════════════
# SO LIST & TRACKING
# ═══════════════════════════════════════════════════════════════════════════════
elif nav_so == "📂 SO List & Tracking":

    # ── Init selected SO in session state ──────────────────────────────────────
    if "selected_so" not in st.session_state:
        st.session_state["selected_so"] = None

    # ── If a SO is open, show detail view ──────────────────────────────────────
    if st.session_state["selected_so"] and st.session_state["selected_so"] in SS["so_list"]:
        sel_so = st.session_state["selected_so"]
        so     = SS["so_list"][sel_so]

        # ── Top bar ────────────────────────────────────────────────────────────
        back_col, title_col, status_col, print_col = st.columns([1, 4, 1.5, 1.5])
        with back_col:
            if st.button("← Back to List"):
                st.session_state["selected_so"] = None
                st.rerun()
        with title_col:
            st.markdown(f'<h1 style="margin:0;">Sales Order — {sel_so}</h1>', unsafe_allow_html=True)
        with status_col:
            st.markdown(f'<div style="padding-top:12px;">{badge(so.get("status","Draft"))}</div>', unsafe_allow_html=True)
        with print_col:
            if st.button("🖨️ Print / PDF", use_container_width=True):
                st.session_state["print_so"] = sel_so

        # ── Print view ─────────────────────────────────────────────────────────
        if st.session_state.get("print_so") == sel_so:
            lines    = so.get("lines", [])
            disc_pct = so.get("discount_pct", 0)
            subtotal = so.get("subtotal", 0)
            disc_amt = subtotal * disc_pct / 100
            rows_html = ""
            for i, ln in enumerate(lines, 1):
                pri_color = {"Urgent":"#dc2626","High":"#d97706","Normal":"#16a34a"}.get(ln.get("priority","Normal"),"#16a34a")
                rows_html += f"""
                <tr>
                    <td>{i}</td>
                    <td style="font-family:monospace;">{ln.get('parent', ln.get('sku','').rsplit('-',1)[0] if '-' in ln.get('sku','') else ln.get('sku',''))}</td>
                    <td style="font-family:monospace;font-weight:700;">{ln.get('sku','')}</td>
                    <td>{ln.get('sku_name','')}</td>
                    <td>{ln.get('size', ln.get('sku','').rsplit('-',1)[-1] if '-' in ln.get('sku','') else '—')}</td>
                    <td style="color:{pri_color};font-weight:600;">{ln.get('priority','Normal')}</td>
                    <td>{ln.get('hsn','—')}</td>
                    <td style="text-align:center;">{ln.get('qty',0)}</td>
                    <td style="text-align:center;">{ln.get('uom','')}</td>
                    <td style="text-align:right;">₹{ln.get('rate',0):,.2f}</td>
                    <td style="text-align:center;">{ln.get('gst_pct',0)}%</td>
                    <td style="text-align:right;">₹{ln.get('taxable',0):,.2f}</td>
                    <td style="text-align:right;">₹{ln.get('gst_amount',0):,.2f}</td>
                    <td style="text-align:right;font-weight:600;">₹{ln.get('total',0):,.2f}</td>
                    <td>{ln.get('delivery_date','—')}</td>
                    <td style="color:#666;font-size:11px;">{ln.get('merchant','—')}</td>
                </tr>"""

            html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Sales Order {sel_so}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: Arial, sans-serif; font-size: 12px; color: #1a1a1a; padding: 20px; }}
  .header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px; padding-bottom:12px; border-bottom:2px solid #c8a96e; }}
  .company {{ font-size:22px; font-weight:800; color:#1a1a2e; }}
  .company-sub {{ font-size:10px; color:#888; letter-spacing:2px; text-transform:uppercase; }}
  .so-title {{ text-align:right; }}
  .so-num {{ font-size:24px; font-weight:800; color:#c8a96e; font-family:monospace; }}
  .so-status {{ display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; background:#fef3c7; color:#92400e; }}
  .info-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-bottom:16px; }}
  .info-box {{ border:1px solid #e2e5ef; border-radius:6px; padding:10px 12px; }}
  .info-box-title {{ font-size:9px; text-transform:uppercase; letter-spacing:1.5px; color:#c8a96e; font-weight:700; margin-bottom:6px; }}
  .info-row {{ font-size:11px; margin-bottom:3px; }}
  .info-row span {{ color:#666; }}
  table {{ width:100%; border-collapse:collapse; margin-bottom:16px; font-size:11px; }}
  thead tr {{ background:#1a1a2e; color:white; }}
  thead th {{ padding:7px 6px; text-align:left; font-weight:600; font-size:10px; text-transform:uppercase; letter-spacing:0.5px; }}
  tbody tr:nth-child(even) {{ background:#f8fafc; }}
  tbody td {{ padding:6px 6px; border-bottom:1px solid #e2e5ef; vertical-align:top; }}
  .totals {{ margin-left:auto; width:280px; border:1px solid #e2e5ef; border-radius:6px; overflow:hidden; }}
  .totals table {{ margin:0; }}
  .totals td {{ padding:5px 10px; font-size:12px; border-bottom:1px solid #f1f5f9; }}
  .totals .grand {{ background:#1a1a2e; color:white; font-size:14px; font-weight:800; }}
  .totals .grand td {{ border:none; padding:8px 10px; }}
  .footer {{ margin-top:24px; padding-top:10px; border-top:1px solid #e2e5ef; display:flex; justify-content:space-between; font-size:10px; color:#888; }}
  .sig-box {{ border-top:1px solid #888; width:160px; padding-top:4px; text-align:center; font-size:10px; color:#666; }}
  @media print {{
    body {{ padding: 10px; }}
    button {{ display:none !important; }}
  }}
</style>
</head>
<body>
<div class="header">
  <div>
    <div class="company">🧵 Garment ERP</div>
    <div class="company-sub">Sales Order Document</div>
  </div>
  <div class="so-title">
    <div class="so-num">{sel_so}</div>
    <div style="margin-top:4px;"><span class="so-status">{so.get('status','Draft')}</span></div>
    <div style="font-size:11px;color:#666;margin-top:4px;">Date: {so.get('so_date','—')}</div>
  </div>
</div>

<div class="info-grid">
  <div class="info-box">
    <div class="info-box-title">Buyer / Customer</div>
    <div class="info-row"><strong style="font-size:13px;">{so.get('buyer','—')}</strong></div>
    <div class="info-row"><span>Payment Terms:</span> {so.get('payment_terms','—')}</div>
    <div class="info-row"><span>Warehouse:</span> {so.get('warehouse','—')}</div>
  </div>
  <div class="info-box">
    <div class="info-box-title">Order Info</div>
    <div class="info-row"><span>Source:</span> {so.get('order_source','—')}</div>
    <div class="info-row"><span>Ref #:</span> {so.get('ref_number','—')}</div>
    <div class="info-row"><span>Sales Team:</span> {so.get('sales_team','—')}</div>
    <div class="info-row"><span>Merchant:</span> {so.get('merchant','—')}</div>
  </div>
  <div class="info-box">
    <div class="info-box-title">Delivery</div>
    <div class="info-row"><span>Delivery Date:</span> <strong>{so.get('delivery_date','—')}</strong></div>
    <div class="info-row"><span>Dispatch Date:</span> {so.get('dispatch_date','—')}</div>
    <div class="info-row"><span>Remarks:</span> {so.get('remarks','—')}</div>
  </div>
</div>

<table>
  <thead>
    <tr>
      <th>#</th><th>Style Code</th><th>SKU Code</th><th>Description</th><th>Size</th><th>Priority</th><th>HSN</th>
      <th>Qty</th><th>UOM</th><th>Rate</th><th>GST%</th>
      <th>Taxable</th><th>GST Amt</th><th>Line Total</th><th>Delivery</th><th>Merchant</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>

<div style="display:flex;justify-content:flex-end;">
  <div class="totals">
    <table>
      <tr><td>Subtotal</td><td style="text-align:right;">₹{subtotal:,.2f}</td></tr>
      <tr><td>Discount ({disc_pct}%)</td><td style="text-align:right;color:#dc2626;">- ₹{disc_amt:,.2f}</td></tr>
      <tr><td>Taxable Amount</td><td style="text-align:right;">₹{subtotal - disc_amt:,.2f}</td></tr>
      <tr><td>GST Amount</td><td style="text-align:right;">₹{so.get('total_gst',0):,.2f}</td></tr>
      <tr><td>Shipping</td><td style="text-align:right;">₹{so.get('shipping',0):,.2f}</td></tr>
      <tr><td>Other Charges</td><td style="text-align:right;">₹{so.get('other_charges',0):,.2f}</td></tr>
      <tr class="grand"><td>GRAND TOTAL</td><td style="text-align:right;">₹{so.get('grand_total',0):,.2f}</td></tr>
    </table>
  </div>
</div>

<div class="footer">
  <div>
    <div>Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}</div>
    <div style="margin-top:2px;">This is a computer generated document.</div>
  </div>
  <div style="display:flex;gap:40px;">
    <div class="sig-box">Prepared By</div>
    <div class="sig-box">Authorized Signatory</div>
  </div>
</div>

<script>window.onload = function() {{ window.print(); }}</script>
</body>
</html>"""

            # Encode and create download + auto-open
            import base64
            b64 = base64.b64encode(html_doc.encode()).decode()
            st.markdown(f'''
            <a href="data:text/html;base64,{b64}" download="{sel_so}.html" id="so_dl_{sel_so}">
                <button style="background:#1c1c2e;color:white;border:none;padding:8px 20px;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px;">
                    ⬇️ Download {sel_so}.html (Print/PDF)
                </button>
            </a>
            <script>document.getElementById("so_dl_{sel_so}").click();</script>
            ''', unsafe_allow_html=True)

            st.markdown('<div class="info-box">👆 File download ho rahi hai — open karke <strong>Ctrl+P</strong> dabao ya browser ka Print button use karo → "Save as PDF" select karo.</div>', unsafe_allow_html=True)

            if st.button("✖ Close Print View"):
                st.session_state["print_so"] = None
                st.rerun()

        st.markdown("---")

        # ── Header Cards ───────────────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        total_q = sum(l["qty"] for l in so.get("lines", []))
        rcvd_q  = sum(l.get("received_qty", 0) for l in so.get("lines", []))
        pct_rcv = int(rcvd_q / total_q * 100) if total_q > 0 else 0

        with col1:
            st.markdown(f'''<div class="card card-left">
                <div class="sec-label">Order Info</div>
                <div style="font-family:JetBrains Mono,monospace;font-size:18px;font-weight:700;color:#c8a96e;">{sel_so}</div>
                <div style="font-size:13px;margin-top:6px;">Date: <strong>{so.get("so_date","—")}</strong></div>
                <div style="font-size:13px;">Source: <strong>{so.get("order_source","—")}</strong></div>
                <div style="font-size:13px;">Ref #: <strong>{so.get("ref_number","—")}</strong></div>
                <div style="font-size:13px;">Ref Date: <strong>{so.get("ref_date","—")}</strong></div>
            </div>''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''<div class="card card-left-blue">
                <div class="sec-label">Buyer / Dispatch</div>
                <div style="font-size:14px;font-weight:700;margin-bottom:4px;">{so.get("buyer","—")}</div>
                <div style="font-size:13px;">Delivery: <strong>{so.get("delivery_date","—")}</strong></div>
                <div style="font-size:13px;">Dispatch: <strong>{so.get("dispatch_date","—")}</strong></div>
                <div style="font-size:13px;">Team: <strong>{so.get("sales_team","—")}</strong></div>
                <div style="font-size:13px;">Payment: <strong>{so.get("payment_terms","—")}</strong></div>
            </div>''', unsafe_allow_html=True)
        with col3:
            st.markdown(f'''<div class="card card-left-green">
                <div class="sec-label">Qty Summary</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:13px;margin-top:4px;">
                    <div>SO Qty<br><strong style="font-size:18px;">{total_q}</strong></div>
                    <div>Received<br><strong style="font-size:18px;color:#059669;">{rcvd_q}</strong></div>
                    <div>Pending<br><strong style="font-size:18px;color:#ef4444;">{total_q - rcvd_q}</strong></div>
                    <div>Progress<br><strong style="font-size:18px;color:#c8a96e;">{pct_rcv}%</strong></div>
                </div>
                <div class="prog-wrap" style="margin-top:8px;"><div class="prog-fill prog-fill-green" style="width:{pct_rcv}%;"></div></div>
            </div>''', unsafe_allow_html=True)
        with col4:
            disc = so.get("discount_pct", 0)
            st.markdown(f'''<div class="card card-left-red">
                <div class="sec-label">Financials</div>
                <div style="font-size:13px;margin-top:4px;">Subtotal: <strong>₹{so.get("subtotal",0):,.2f}</strong></div>
                <div style="font-size:13px;">Discount ({disc}%): <strong style="color:#ef4444;">- ₹{so.get("subtotal",0)*disc/100:,.2f}</strong></div>
                <div style="font-size:13px;">GST: <strong>₹{so.get("total_gst",0):,.2f}</strong></div>
                <div style="font-size:13px;">Shipping: <strong>₹{so.get("shipping",0):,.2f}</strong></div>
                <div style="border-top:1px solid #e2e5ef;margin-top:6px;padding-top:6px;">
                    Grand Total<br><strong style="font-size:20px;color:#c8a96e;">₹{so.get("grand_total",0):,.2f}</strong>
                </div>
            </div>''', unsafe_allow_html=True)

        st.markdown("---")

        # ── Status Update ──────────────────────────────────────────────────────
        stu1, stu2, stu3 = st.columns([2, 1, 3])
        with stu1:
            new_status = st.selectbox("Update Status", STATUS_LIST,
                                       index=STATUS_LIST.index(so.get("status","Draft")),
                                       key="so_status_update")
        with stu2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Update Status", use_container_width=True):
                SS["so_list"][sel_so]["status"] = new_status
                save_data()
                st.success(f"Status → {new_status}")
                st.rerun()
        with stu3:
            st.markdown(f'<div class="info-box" style="margin-top:8px;">Warehouse: <strong>{so.get("warehouse","—")}</strong> &nbsp;|&nbsp; Merchant: <strong>{so.get("merchant","—")}</strong> &nbsp;|&nbsp; Remarks: {so.get("remarks","—")}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── SO Lines Table (full detail) ───────────────────────────────────────
        st.markdown("#### 🧵 SO Line Items")
        lines = so.get("lines", [])
        if lines:
            # Full lines table
            line_rows = []
            for ln in lines:
                _sku = ln.get("sku","")
                _parent = ln.get("parent", _sku.rsplit("-",1)[0] if "-" in _sku else _sku)
                line_rows.append({
                    "Style Code":   _parent,
                    "SKU Code":     _sku,
                    "Description":  ln.get("sku_name",""),
                    "Size":         ln.get("size", _sku.rsplit("-",1)[-1] if "-" in _sku else ""),
                    "Priority":     ln.get("priority","Normal"),
                    "Merchant":     ln.get("merchant","—"),
                    "Qty":          ln.get("qty",0),
                    "UOM":          ln.get("uom",""),
                    "Rate (₹)":     ln.get("rate",0),
                    "GST %":        ln.get("gst_pct",0),
                    "Taxable (₹)":  ln.get("taxable",0),
                    "GST Amt (₹)":  ln.get("gst_amount",0),
                    "Line Total (₹)": ln.get("total",0),
                    "HSN":          ln.get("hsn",""),
                    "Delivery":     ln.get("delivery_date",""),
                    "Produced":     ln.get("produced_qty",0),
                    "Dispatched":   ln.get("dispatch_qty",0),
                    "Received":     ln.get("received_qty",0),
                    "Balance":      ln.get("qty",0) - ln.get("received_qty",0),
                    "Remarks":      ln.get("remarks",""),
                })
            st.dataframe(pd.DataFrame(line_rows), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("#### ✏️ Update Line Quantities (Produced / Dispatched / Received)")

            for i, line in enumerate(lines):
                pri_color = {"Urgent":"#ef4444","High":"#d97706","Normal":"#059669"}.get(line.get("priority","Normal"),"#059669")
                with st.expander(
                    f"📦  {line.get('sku','')}  —  {line.get('sku_name','')}  |  Ordered: {line.get('qty',0)}  |  Balance: {line.get('qty',0)-line.get('received_qty',0)}",
                    expanded=False
                ):
                    # Line detail strip
                    st.markdown(f'''<div style="display:flex;gap:12px;flex-wrap:wrap;font-size:12px;margin-bottom:12px;padding:10px 14px;background:#f8fafc;border-radius:8px;border:1px solid #e2e5ef;">
                        <span><span style="color:#94a3b8;">SKU</span> <strong>{line.get("sku","")}</strong></span>
                        <span><span style="color:#94a3b8;">Size</span> <strong>{line.get("size","")}</strong></span>
                        <span><span style="color:#94a3b8;">Rate</span> <strong>₹{line.get("rate",0)}</strong></span>
                        <span><span style="color:#94a3b8;">GST</span> <strong>{line.get("gst_pct",0)}%</strong></span>
                        <span><span style="color:#94a3b8;">Line Total</span> <strong>₹{line.get("total",0):,.2f}</strong></span>
                        <span><span style="color:#94a3b8;">Delivery</span> <strong>{line.get("delivery_date","—")}</strong></span>
                        <span><span style="color:#94a3b8;">Priority</span> <strong style="color:{pri_color};">{line.get("priority","Normal")}</strong></span>
                        <span><span style="color:#94a3b8;">Merchant</span> <strong>{line.get("merchant","—")}</strong></span>
                        <span><span style="color:#94a3b8;">HSN</span> <strong>{line.get("hsn","—")}</strong></span>
                    </div>''', unsafe_allow_html=True)

                    ql1, ql2, ql3, ql4 = st.columns(4)
                    with ql1:
                        st.markdown(f'<div class="card" style="text-align:center;padding:12px;"><div style="color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Ordered</div><div style="font-size:26px;font-weight:800;">{line.get("qty",0)}</div></div>', unsafe_allow_html=True)
                    with ql2:
                        prod = st.number_input("Produced Qty", min_value=0, max_value=line["qty"]*2,
                                               value=line.get("produced_qty",0), key=f"prod_{sel_so}_{i}")
                    with ql3:
                        disp = st.number_input("Dispatched Qty", min_value=0, max_value=line["qty"]*2,
                                               value=line.get("dispatch_qty",0), key=f"disp_{sel_so}_{i}")
                    with ql4:
                        rcvd = st.number_input("Received Qty", min_value=0, max_value=line["qty"]*2,
                                               value=line.get("received_qty",0), key=f"rcvd_{sel_so}_{i}")

                    balance = line["qty"] - rcvd
                    pct_r   = int(rcvd / line["qty"] * 100) if line["qty"] > 0 else 0
                    st.markdown(f'''<div style="margin-top:8px;">
                        <div class="prog-wrap"><div class="prog-fill prog-fill-green" style="width:{pct_r}%;"></div></div>
                        <div style="font-size:11px;color:#64748b;margin-top:2px;">Received {pct_r}% &nbsp;|&nbsp; Balance: <strong>{balance} pcs</strong></div>
                    </div>''', unsafe_allow_html=True)

                    if st.button("💾 Save", key=f"save_line_{sel_so}_{i}"):
                        SS["so_list"][sel_so]["lines"][i]["produced_qty"] = prod
                        SS["so_list"][sel_so]["lines"][i]["dispatch_qty"]  = disp
                        SS["so_list"][sel_so]["lines"][i]["received_qty"]  = rcvd
                        save_data()
                        # Auto-update SO status
                        all_rcvd = all(
                            l.get("received_qty",0) >= l.get("qty",0)
                            for l in SS["so_list"][sel_so]["lines"]
                        )
                        any_rcvd = any(
                            l.get("received_qty",0) > 0
                            for l in SS["so_list"][sel_so]["lines"]
                        )
                        if all_rcvd:
                            SS["so_list"][sel_so]["status"] = "Fully Received"
                        elif any_rcvd:
                            SS["so_list"][sel_so]["status"] = "Partially Received"
                        save_data()
                        st.success("✅ Line updated!")
                        st.rerun()
        else:
            st.markdown('<div class="warn-box">This SO has no line items.</div>', unsafe_allow_html=True)

    # ── LIST VIEW (no SO selected) ─────────────────────────────────────────────
    else:
        st.markdown('<h1>SO List & Tracking</h1>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">👆 Kisi bhi SO row ke saamne <strong>Open</strong> button click karo — poori detail khul jaayegi.</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Filters
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1: f_status = st.selectbox("Status", ["All"] + STATUS_LIST, key="fl_status")
        with fc2: f_source = st.selectbox("Source", ["All"] + ORDER_SOURCES, key="fl_source")
        with fc3: f_buyer  = st.selectbox("Buyer",  ["All"] + SS["buyers"], key="fl_buyer")
        with fc4: f_search = st.text_input("🔍 Search SO # / Buyer", "", key="fl_search")

        if not SS["so_list"]:
            st.markdown('<div class="warn-box">Koi Sales Order nahi bana abhi tak. "Create Sales Order" se banao.</div>', unsafe_allow_html=True)
        else:
            filtered_sos = {}
            for so_no, so in SS["so_list"].items():
                if f_status != "All" and so.get("status") != f_status: continue
                if f_source != "All" and so.get("order_source") != f_source: continue
                if f_buyer  != "All" and so.get("buyer") != f_buyer: continue
                if f_search and f_search.lower() not in so_no.lower() and f_search.lower() not in so.get("buyer","").lower(): continue
                filtered_sos[so_no] = so

            st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:8px;">Showing <strong>{len(filtered_sos)}</strong> of <strong>{len(SS["so_list"])}</strong> orders</div>', unsafe_allow_html=True)

            # Render each SO as a clickable card row
            for so_no, so in reversed(list(filtered_sos.items())):
                total_q = sum(l["qty"] for l in so.get("lines", []))
                rcvd_q  = sum(l.get("received_qty", 0) for l in so.get("lines", []))
                pct     = int(rcvd_q / total_q * 100) if total_q > 0 else 0
                status  = so.get("status", "Draft")
                is_over = so.get("delivery_date","9999") < str(date.today()) and status not in ["Fully Received","Closed","Cancelled"]
                border_color = "#ef4444" if is_over else "#e2e5ef"

                r1, r2, r3, r4, r5, r6, r7 = st.columns([1.2, 2, 1.5, 1, 1, 1.5, 0.8])
                with r1:
                    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-weight:700;font-size:14px;color:#c8a96e;padding-top:10px;">{so_no}</div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'<div style="padding-top:8px;"><div style="font-weight:600;font-size:13px;">{so.get("buyer","—")}</div><div style="font-size:11px;color:#94a3b8;">{so.get("order_source","")}</div></div>', unsafe_allow_html=True)
                with r3:
                    overdue_tag = '<span class="tag tag-red">OVERDUE</span>' if is_over else ''
                    st.markdown(f'<div style="padding-top:8px;font-size:12px;">📅 {so.get("delivery_date","—")}<br>{overdue_tag}</div>', unsafe_allow_html=True)
                with r4:
                    st.markdown(f'<div style="padding-top:8px;text-align:center;"><div style="font-size:11px;color:#94a3b8;">Qty</div><div style="font-weight:700;">{total_q}</div></div>', unsafe_allow_html=True)
                with r5:
                    st.markdown(f'<div style="padding-top:4px;"><div style="font-size:11px;color:#94a3b8;">Progress</div><div class="prog-wrap"><div class="prog-fill" style="width:{pct}%;"></div></div><div style="font-size:11px;">{pct}%</div></div>', unsafe_allow_html=True)
                with r6:
                    st.markdown(f'<div style="padding-top:8px;text-align:center;">{badge(status)}<br><div style="font-size:12px;font-weight:600;color:#c8a96e;margin-top:4px;">₹{so.get("grand_total",0):,.0f}</div></div>', unsafe_allow_html=True)
                with r7:
                    if st.button("Open →", key=f"open_{so_no}", use_container_width=True):
                        st.session_state["selected_so"] = so_no
                        st.rerun()

                st.markdown(f'<hr style="margin:4px 0;border-color:{border_color};">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════════════════════
elif nav_so == "📈 SO Reports":
    st.markdown('<h1>Reports</h1>', unsafe_allow_html=True)

    rep = st.selectbox("Select Report", [
        "1. Demand vs SO Report",
        "2. SO vs Received Report",
        "3. SKU Pending Report",
        "4. Delivery Due Report",
        "5. Buyer Order Report",
        "6. Source-wise Order Report",
    ])

    st.markdown("---")

    if rep.startswith("1"):
        st.markdown("### Demand vs SO Report")
        rows = []
        for dem_no, dem in SS["demands"].items():
            for line in dem.get("lines", []):
                so_q = sum(l["qty"] for so in SS["so_list"].values()
                           if so.get("ref_number") == dem_no
                           for l in so.get("lines", []) if l["sku"] == line["sku"])
                rows.append({
                    "Demand #": dem_no, "Buyer": dem.get("buyer",""), "SKU": line["sku"],
                    "SKU Name": line["sku_name"], "Demand Qty": line["demand_qty"],
                    "SO Created": so_q, "Pending SO": max(0, line["demand_qty"] - so_q),
                    "Coverage %": f"{int(so_q/line['demand_qty']*100) if line['demand_qty'] > 0 else 0}%",
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No demand data available.</div>', unsafe_allow_html=True)

    elif rep.startswith("2"):
        st.markdown("### SO vs Received Report")
        rows = []
        for so_no, so in SS["so_list"].items():
            for line in so.get("lines", []):
                rows.append({
                    "SO #": so_no, "Buyer": so.get("buyer",""), "SKU": line["sku"],
                    "SO Qty": line["qty"], "Produced": line.get("produced_qty",0),
                    "Dispatched": line.get("dispatch_qty",0), "Received": line.get("received_qty",0),
                    "Balance": line["qty"] - line.get("received_qty",0),
                    "Status": so.get("status",""),
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No SO data available.</div>', unsafe_allow_html=True)

    elif rep.startswith("3"):
        st.markdown("### SKU Pending Report")
        sku_summary = {}
        for so in SS["so_list"].values():
            if so.get("status") in ["Cancelled","Closed"]: continue
            for line in so.get("lines", []):
                sku = line["sku"]
                if sku not in sku_summary:
                    sku_summary[sku] = {"name": line["sku_name"], "total_ordered": 0, "total_received": 0}
                sku_summary[sku]["total_ordered"]  += line["qty"]
                sku_summary[sku]["total_received"] += line.get("received_qty", 0)

        rows = [{"SKU": k, "Name": v["name"], "Total Ordered": v["total_ordered"],
                 "Total Received": v["total_received"],
                 "Pending": v["total_ordered"] - v["total_received"],
                 "Current Stock": get_sku_info(k).get("stock", "—"),
                 "Running Days": running_days(k)}
                for k, v in sku_summary.items()]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No pending SKU data.</div>', unsafe_allow_html=True)

    elif rep.startswith("4"):
        st.markdown("### Delivery Due Report")
        today = str(date.today())
        rows = []
        for so_no, so in SS["so_list"].items():
            if so.get("status") in ["Cancelled","Fully Received","Closed"]: continue
            dd = so.get("delivery_date","")
            overdue = dd < today if dd else False
            days_left = (datetime.strptime(dd, "%Y-%m-%d").date() - date.today()).days if dd else 999
            rows.append({
                "SO #": so_no, "Buyer": so.get("buyer",""),
                "Delivery Date": dd, "Days Left": days_left,
                "Total Qty": sum(l["qty"] for l in so.get("lines",[])),
                "Pending Qty": sum(l["qty"]-l.get("received_qty",0) for l in so.get("lines",[])),
                "Status": so.get("status",""), "Overdue": "🔴 YES" if overdue else "✅ NO",
            })
        rows.sort(key=lambda x: x["Days Left"])
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No pending delivery data.</div>', unsafe_allow_html=True)

    elif rep.startswith("5"):
        st.markdown("### Buyer Order Report")
        buyer_summary = {}
        for so in SS["so_list"].values():
            b = so.get("buyer","Unknown")
            if b not in buyer_summary:
                buyer_summary[b] = {"so_count": 0, "total_qty": 0, "received_qty": 0, "grand_total": 0}
            buyer_summary[b]["so_count"]    += 1
            buyer_summary[b]["total_qty"]   += sum(l["qty"] for l in so.get("lines",[]))
            buyer_summary[b]["received_qty"]+= sum(l.get("received_qty",0) for l in so.get("lines",[]))
            buyer_summary[b]["grand_total"] += so.get("grand_total",0)

        rows = [{"Buyer": k, "SO Count": v["so_count"], "Total Qty": v["total_qty"],
                 "Received": v["received_qty"], "Pending": v["total_qty"]-v["received_qty"],
                 "Total Value": f"₹{v['grand_total']:,.0f}"} for k, v in buyer_summary.items()]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No buyer data.</div>', unsafe_allow_html=True)

    elif rep.startswith("6"):
        st.markdown("### Source-wise Order Report")
        source_summary = {}
        for so in SS["so_list"].values():
            src = so.get("order_source","Unknown")
            if src not in source_summary:
                source_summary[src] = {"so_count": 0, "total_qty": 0, "grand_total": 0}
            source_summary[src]["so_count"]  += 1
            source_summary[src]["total_qty"] += sum(l["qty"] for l in so.get("lines",[]))
            source_summary[src]["grand_total"]+= so.get("grand_total",0)

        rows = [{"Source": k, "SO Count": v["so_count"], "Total Qty": v["total_qty"],
                 "Total Value": f"₹{v['grand_total']:,.0f}"} for k, v in source_summary.items()]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="warn-box">No data.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif nav_so == "⚙️ SO Settings":
    st.markdown('<h1>Settings</h1>', unsafe_allow_html=True)

    stab1, stab2, stab3, stab4 = st.tabs(["👤 Buyers", "🏭 Warehouses", "👥 Sales Teams", "💾 Data Backup"])

    with stab1:
        col1, col2 = st.columns(2)
        with col1:
            new_buyer = st.text_input("Add Buyer")
            if st.button("➕ Add Buyer") and new_buyer:
                if new_buyer not in SS["buyers"]:
                    SS["buyers"].append(new_buyer)
                    save_data()
                    st.success(f"'{new_buyer}' added!")
                    st.rerun()
        with col2:
            for b in SS["buyers"]:
                st.markdown(f'<span class="tag tag-gold">{b}</span>', unsafe_allow_html=True)

    with stab2:
        col1, col2 = st.columns(2)
        with col1:
            new_wh = st.text_input("Add Warehouse")
            if st.button("➕ Add Warehouse") and new_wh:
                if new_wh not in SS["warehouses"]:
                    SS["warehouses"].append(new_wh)
                    save_data()
                    st.success(f"'{new_wh}' added!")
                    st.rerun()
        with col2:
            for w in SS["warehouses"]:
                st.markdown(f'<span class="tag tag-blue">{w}</span>', unsafe_allow_html=True)

    with stab3:
        col1, col2 = st.columns(2)
        with col1:
            new_team = st.text_input("Add Sales Team")
            if st.button("➕ Add Team") and new_team:
                if new_team not in SS["sales_teams"]:
                    SS["sales_teams"].append(new_team)
                    save_data()
                    st.success(f"'{new_team}' added!")
                    st.rerun()
        with col2:
            for t in SS["sales_teams"]:
                st.markdown(f'<span class="tag">{t}</span>', unsafe_allow_html=True)

    with stab4:
        st.markdown("#### 💾 Data Backup & Restore")
        st.markdown('<div class="warn-box">⚠️ Streamlit Cloud pe data restart hone pr reset ho jaata hai. <strong>Har session ke baad data export karke rakhein</strong> — aur next session mein import karein.</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📤 Export (Download Backup)")
            # Build full backup
            backup = {key: st.session_state.get(key, DEFAULT_DATA.get(key)) for key in DEFAULT_DATA}
            pkg_lines = {k: v for k, v in st.session_state.items() if k.startswith("pkg_lines_")}
            backup["_pkg_lines"] = pkg_lines
            backup_json = json.dumps(backup, ensure_ascii=False, indent=2, default=str)

            import base64
            b64_backup = base64.b64encode(backup_json.encode()).decode()
            today_str = datetime.now().strftime("%Y%m%d_%H%M")
            st.markdown(f'''
            <a href="data:application/json;base64,{b64_backup}" download="erp_backup_{today_str}.json">
                <button style="background:#1c1c2e;color:white;border:none;padding:10px 24px;border-radius:8px;font-weight:700;cursor:pointer;font-size:14px;width:100%;">
                    ⬇️ Download Backup (erp_backup_{today_str}.json)
                </button>
            </a>
            ''', unsafe_allow_html=True)

            n_items = len(st.session_state.get("items", {}))
            n_boms  = len(st.session_state.get("boms", {}))
            n_so    = len(st.session_state.get("so_list", {}))
            n_dem   = len(st.session_state.get("demands", {}))
            st.markdown(f'<div class="ok-box" style="margin-top:12px;">Backup mein: <strong>{n_items}</strong> Items, <strong>{n_boms}</strong> BOMs, <strong>{n_so}</strong> SOs, <strong>{n_dem}</strong> Demands</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("##### 📥 Import (Restore Backup)")
            uploaded = st.file_uploader("Backup JSON file upload karo", type=["json"], key="backup_upload")
            if uploaded:
                try:
                    restored = json.load(uploaded)
                    st.markdown(f'<div class="info-box">File ready: {len(restored.get("items",{}))} items, {len(restored.get("so_list",{}))} SOs found.</div>', unsafe_allow_html=True)
                    if st.button("✅ Restore Data", use_container_width=True):
                        for key in DEFAULT_DATA:
                            if key in restored:
                                st.session_state[key] = restored[key]
                        for k, v in restored.get("_pkg_lines", {}).items():
                            st.session_state[k] = v
                        save_data()
                        st.success("✅ Data restore ho gaya!")
                        st.rerun()
                except Exception as e:
                    st.error(f"File read error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MRP MODULE
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_mrp(selected_so_nos):
    """
    Core MRP engine:
    For each SO → each line → BOM → explode materials recursively
    + buyer-wise packaging from item's buyer_packaging
    Returns: dict of {material_code: {name, type, total_req, stock, net_req, unit, breakdown[]}}
    """
    items    = st.session_state.get("items", {})
    boms     = st.session_state.get("boms", {})
    so_list  = SS.get("so_list", {})
    result   = {}  # material_code -> aggregated requirement

    def get_bom_lines(item_code):
        """Get BOM lines for an item"""
        bom = boms.get(item_code, {})
        return bom.get("lines", [])

    def explode_bom(item_code, qty, so_no, sku, buyer, depth=0):
        """Recursively explode BOM — multi-level support"""
        if depth > 10:
            return  # prevent infinite loop
        lines = get_bom_lines(item_code)
        if not lines:
            return
        for line in lines:
            # Only process Material lines (not process cost lines)
            if line.get("line_type") == "Process":
                continue
            comp_code = line.get("item_code", "")
            if not comp_code:
                continue
            comp_item  = items.get(comp_code, {})
            comp_name  = comp_item.get("name", comp_code)
            comp_type  = comp_item.get("item_type", "Raw Material (RM)")
            line_qty   = float(line.get("qty", 0))
            shrinkage  = float(line.get("shrinkage", 0)) / 100
            wastage    = float(line.get("wastage", 0)) / 100
            adj_qty    = line_qty * (1 + shrinkage + wastage)
            total_qty  = round(adj_qty * qty, 3)
            unit       = line.get("unit", comp_item.get("unit", "Pcs"))

            # Use item_type from BOM line (more reliable than items dict lookup)
            comp_type_from_line = line.get("item_type", comp_type)
            final_type = comp_type_from_line if comp_type_from_line else comp_type

            # Check if this component has its own BOM
            sub_bom_lines = boms.get(comp_code, {}).get("lines", [])
            has_sub_bom   = len([l for l in sub_bom_lines if l.get("line_type") != "Process"]) > 0

            # ALWAYS add this component to result (P308 bhi chahiye, slub bhi)
            if comp_code not in result:
                result[comp_code] = {
                    "name": comp_name, "type": final_type,
                    "unit": unit, "total_req": 0,
                    "stock": float(comp_item.get("stock", 0)),
                    "reserved": float(comp_item.get("reserved", 0)),
                    "breakdown": [],
                    "level": depth,
                }
            result[comp_code]["total_req"] = round(result[comp_code]["total_req"] + total_qty, 3)
            result[comp_code]["breakdown"].append({
                "so_no": so_no, "sku": sku, "qty_req": total_qty,
                "source": f"BOM: {item_code} → Level {depth}"
            })

            if has_sub_bom:
                # Also go deeper to get raw materials of this component
                explode_bom(comp_code, total_qty, so_no, sku, buyer, depth+1)

    def add_packaging(item_code, qty, so_no, sku, buyer):
        """Add buyer-wise packaging requirements"""
        item = items.get(item_code, {})
        pkg  = item.get("buyer_packaging", {})
        # Use buyer-specific packaging, fallback to first available
        pkg_lines = pkg.get(buyer, [])
        if not pkg_lines and pkg:
            pkg_lines = list(pkg.values())[0]

        for ln in pkg_lines:
            comp_code = ln.get("item_code", "")
            if not comp_code:
                continue
            comp_item = items.get(comp_code, {})
            comp_name = comp_item.get("name", comp_code)
            comp_type = comp_item.get("item_type", "Packing Materials")
            line_qty  = float(ln.get("qty", 1))
            unit      = ln.get("uom", "Pcs")
            total_qty = round(line_qty * qty, 3)

            if comp_code not in result:
                result[comp_code] = {
                    "name": comp_name, "type": comp_type,
                    "unit": unit, "total_req": 0,
                    "stock": float(items.get(comp_code, {}).get("stock", 0)),
                    "reserved": float(items.get(comp_code, {}).get("reserved", 0)),
                    "breakdown": []
                }
            result[comp_code]["total_req"] += total_qty
            result[comp_code]["breakdown"].append({
                "so_no": so_no, "sku": sku, "qty_req": total_qty,
                "source": f"Packaging ({buyer})"
            })

    # Main loop
    for so_no in selected_so_nos:
        so = so_list.get(so_no, {})
        buyer = so.get("buyer", "")
        for line in so.get("lines", []):
            sku = line.get("sku", "")
            qty = line.get("qty", 0)
            # Get parent item for BOM (size variant may not have BOM, parent does)
            sku_item = items.get(sku, {})
            parent   = sku_item.get("parent", sku)
            bom_item = parent if parent in boms else sku

            explode_bom(bom_item, qty, so_no, sku, buyer)
            add_packaging(bom_item, qty, so_no, sku, buyer)

    # Calculate net requirement (considering soft reservations from previous MRP runs)
    soft_res = SS.get("soft_reservations", {})
    for code, mat in result.items():
        hard_reserved = mat["reserved"]  # actual stock reserved (post-PO)
        soft_reserved = sum(
            qty for so_data in soft_res.get(code, {}).values()
            for qty in so_data.values()
        )
        avail = mat["stock"] - hard_reserved
        mat["available"]      = max(0, avail)
        mat["soft_reserved"]  = soft_reserved
        mat["net_available"]  = max(0, avail - soft_reserved)
        mat["net_req"]        = max(0, round(mat["total_req"] - avail, 3))
        mat["net_req_with_soft"] = max(0, round(mat["total_req"] - mat["net_available"], 3))

    return result


# ── MRP DASHBOARD ─────────────────────────────────────────────────────────────
if nav_mrp == "🏭 MRP Dashboard":
    st.markdown('<h1>MRP Dashboard</h1>', unsafe_allow_html=True)

    so_list = SS.get("so_list", {})
    open_sos = {k: v for k, v in so_list.items() if v.get("status") not in ["Closed","Cancelled","Fully Received"]}
    total_items = len(st.session_state.get("items", {}))
    total_boms  = len(st.session_state.get("boms", {}))
    items_without_bom = sum(1 for code, item in st.session_state.get("items",{}).items()
                            if item.get("item_type") == "Finished Goods (FG)"
                            and not item.get("parent")
                            and code not in st.session_state.get("boms",{}))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''<div class="metric-box">
            <div class="metric-value">{len(open_sos)}</div>
            <div class="metric-label">Open Sales Orders</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        total_pending = sum(
            line["qty"] - line.get("produced_qty", 0)
            for so in open_sos.values()
            for line in so.get("lines", [])
        )
        st.markdown(f'''<div class="metric-box">
            <div class="metric-value">{total_pending:,}</div>
            <div class="metric-label">Pending Production Qty</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="metric-box">
            <div class="metric-value">{total_boms}</div>
            <div class="metric-label">BOMs Defined</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="metric-box {"red" if items_without_bom > 0 else ""}">
            <div class="metric-value">{items_without_bom}</div>
            <div class="metric-label">FG Items Without BOM</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("---")

    # Open SOs summary
    if open_sos:
        st.markdown("#### 📋 Open Sales Orders (MRP Eligible)")
        rows = []
        boms_data = st.session_state.get("boms", {})
        items_data = st.session_state.get("items", {})
        for so_no, so in open_sos.items():
            total_q = sum(l["qty"] for l in so.get("lines", []))
            prod_q  = sum(l.get("produced_qty", 0) for l in so.get("lines", []))
            # Check BOM availability for each line
            bom_ok = True
            for l in so.get("lines", []):
                sku = l.get("sku", "")
                parent = items_data.get(sku, {}).get("parent", "")
                bom_item = parent if parent and parent in boms_data else sku
                if bom_item not in boms_data:
                    bom_ok = False
                    break
            rows.append({
                "SO #": so_no, "Buyer": so.get("buyer",""), "Delivery": so.get("delivery_date",""),
                "Total Qty": total_q, "Produced": prod_q, "Pending": total_q - prod_q,
                "BOM Ready": "✅" if bom_ok else "⚠️ Missing",
                "Status": so.get("status",""), "Lines": len(so.get("lines",[]))
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="warn-box">Koi open Sales Order nahi hai. Pehle SO banao.</div>', unsafe_allow_html=True)

    if items_without_bom > 0:
        st.markdown("---")
        st.markdown("#### ⚠️ FG Items Without BOM")
        boms_data = st.session_state.get("boms", {})
        for code, item in st.session_state.get("items", {}).items():
            if item.get("item_type") == "Finished Goods (FG)" and not item.get("parent") and code not in boms_data:
                st.markdown(f'<span class="tag tag-red">⚠️ {code} – {item.get("name","")}</span>', unsafe_allow_html=True)


# ── RUN MRP ───────────────────────────────────────────────────────────────────
elif nav_mrp == "▶ Run MRP":
    st.markdown('<h1>Run Material Requirement Planning</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select karo kaunse Sales Orders ke liye MRP run karni hai — system automatically BOM aur Packaging se material requirement calculate karega.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    so_list   = SS.get("so_list", {})
    open_sos  = {k: v for k, v in so_list.items() if v.get("status") not in ["Closed","Cancelled","Fully Received"]}

    if not open_sos:
        st.markdown('<div class="warn-box">Koi open SO nahi hai. Pehle Sales Order banao.</div>', unsafe_allow_html=True)
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            filter_buyer = st.selectbox("Filter by Buyer", ["All"] + SS.get("buyers", []), key="mrp_buyer")
        with f2:
            date_from = st.date_input("Delivery From", value=date.today(), key="mrp_from")
        with f3:
            date_to   = st.date_input("Delivery To", value=date.today() + timedelta(days=90), key="mrp_to")

        # Filter SOs
        eligible = {}
        for so_no, so in open_sos.items():
            if filter_buyer != "All" and so.get("buyer") != filter_buyer:
                continue
            del_date = so.get("delivery_date", "9999-99-99")
            if str(date_from) <= del_date <= str(date_to):
                eligible[so_no] = so

        if not eligible:
            st.markdown('<div class="warn-box">Filter mein koi SO nahi aaya. Dates ya Buyer filter change karo.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"**{len(eligible)} SOs eligible hain:**")
            selected_sos = st.multiselect(
                "SOs select karo (sabhi by default selected hain)",
                options=list(eligible.keys()),
                default=list(eligible.keys()),
                format_func=lambda x: f"{x} – {eligible.get(x,{}).get('buyer','')} – Delivery: {eligible.get(x,{}).get('delivery_date','')}",
                key="mrp_selected_sos"
            )

            if selected_sos:
                # Show summary of selected
                total_lines = sum(len(eligible[s].get("lines",[])) for s in selected_sos)
                total_qty   = sum(l["qty"] for s in selected_sos for l in eligible[s].get("lines",[]))
                st.markdown(f'<div class="info-box">Selected: <strong>{len(selected_sos)}</strong> SOs | <strong>{total_lines}</strong> SKU lines | <strong>{total_qty:,}</strong> total pcs</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Debug: Show BOM structure
                with st.expander("🔍 BOM Structure Debug (check karo sahi hai ya nahi)"):
                    boms_data = st.session_state.get("boms", {})
                    items_data = st.session_state.get("items", {})
                    if not boms_data:
                        st.warning("Koi BOM nahi bana abhi tak!")
                    for bom_code, bom in boms_data.items():
                        mat_lines = [l for l in bom.get("lines",[]) if l.get("line_type") != "Process"]
                        st.markdown(f"**BOM: {bom_code}** — {len(mat_lines)} material lines")
                        for l in mat_lines:
                            comp = l.get("item_code","")
                            comp_type = items_data.get(comp,{}).get("item_type","?")
                            has_sub = comp in boms_data
                            st.markdown(f"&nbsp;&nbsp;&nbsp;→ `{comp}` ({comp_type}) | Qty: {l.get('qty',0)} {l.get('unit','')} | Has sub-BOM: {'✅' if has_sub else '❌'}")

                if st.button("🚀 Run MRP Now", use_container_width=False):
                    with st.spinner("MRP calculate ho rahi hai..."):
                        mrp_result = calculate_mrp(selected_sos)
                        SS["mrp_result"]   = mrp_result
                        SS["mrp_so_list"]  = selected_sos
                        SS["mrp_run_time"] = datetime.now().strftime("%d-%m-%Y %H:%M")
                        save_data()
                    st.success(f"✅ MRP complete! {len(mrp_result)} materials found.")
                    st.session_state["current_page"] = "📦 Material Requirements"
                    st.rerun()


# ── MATERIAL REQUIREMENTS ─────────────────────────────────────────────────────
elif nav_mrp == "📦 Material Requirements":
    st.markdown('<h1>Material Requirements</h1>', unsafe_allow_html=True)

    if not SS.get("mrp_result"):
        st.markdown('<div class="warn-box">MRP nahi chali abhi tak. Pehle "▶ Run MRP" se MRP run karo.</div>', unsafe_allow_html=True)
    else:
        mrp_result = SS["mrp_result"]
        run_time   = SS.get("mrp_run_time", "")
        so_list_used = SS.get("mrp_so_list", [])

        st.markdown(f'<div class="ok-box">Last MRP run: <strong>{run_time}</strong> | SOs: <strong>{", ".join(so_list_used)}</strong></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Filters
        mf1, mf2, mf3 = st.columns(3)
        with mf1:
            mat_types = list(set(m["type"] for m in mrp_result.values()))
            f_type = st.selectbox("Filter by Type", ["All"] + mat_types, key="mrp_mat_type")
        with mf2:
            f_shortage = st.checkbox("Only show shortage items", key="mrp_shortage")
        with mf3:
            f_search = st.text_input("🔍 Search material", key="mrp_search")

        # Summary table
        rows = []
        for code, mat in mrp_result.items():
            if f_type != "All" and mat["type"] != f_type:
                continue
            if f_shortage and mat["net_req"] <= 0:
                continue
            if f_search and f_search.lower() not in code.lower() and f_search.lower() not in mat["name"].lower():
                continue
            shortage = mat["net_req"] > 0
            level = mat.get("level", 0)
            level_label = "🔵 FG Component" if level == 0 else f"🟡 Level {level} (Sub-component)"
            soft_res = mat.get("soft_reserved", 0)
            rows.append({
                "Level":              level_label,
                "Material Code":      code,
                "Material Name":      mat["name"],
                "Type":               mat["type"],
                "Unit":               mat["unit"],
                "Total Required":     mat["total_req"],
                "In Stock":           mat["stock"],
                "Hard Reserved":      mat["reserved"],
                "Soft Reserved":      soft_res,
                "Available":          mat["available"],
                "Net Req (w/ Soft)":  mat.get("net_req_with_soft", mat["net_req"]),
                "Status":             "🔴 Shortage" if shortage else "🟢 OK",
            })

        if rows:
            df_mrp = pd.DataFrame(rows)
            st.dataframe(df_mrp, use_container_width=True, hide_index=True)

            # Summary KPIs
            shortage_count = sum(1 for r in rows if r["Net Req (w/ Soft)"] > 0)
            ok_count = len(rows) - shortage_count
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f'<div class="metric-box red"><div class="metric-value">{shortage_count}</div><div class="metric-label">Shortage Materials</div></div>', unsafe_allow_html=True)
            with k2: st.markdown(f'<div class="metric-box green"><div class="metric-value">{ok_count}</div><div class="metric-label">Stock OK Materials</div></div>', unsafe_allow_html=True)
            with k3: st.markdown(f'<div class="metric-box"><div class="metric-value">{len(rows)}</div><div class="metric-label">Total Materials</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            # Drill-down
            st.markdown("#### 🔍 Material Drill-Down (Breakup by SO / SKU)")
            drill_opts = {code: f"{code} – {mat['name']}" for code, mat in mrp_result.items()
                         if (f_type == "All" or mat["type"] == f_type)}
            drill_sel = st.selectbox("Material select karo detail dekhne ke liye", [""] + list(drill_opts.keys()),
                                      format_func=lambda x: drill_opts.get(x, x) if x else "— Select —",
                                      key="mrp_drill")
            if drill_sel and drill_sel in mrp_result:
                mat = mrp_result[drill_sel]
                st.markdown(f'''<div class="card card-left" style="margin-bottom:12px;">
                    <div style="display:flex;gap:24px;flex-wrap:wrap;font-size:13px;">
                        <div><span style="color:#94a3b8;">Material</span><br><strong>{drill_sel} – {mat["name"]}</strong></div>
                        <div><span style="color:#94a3b8;">Total Required</span><br><strong>{mat["total_req"]} {mat["unit"]}</strong></div>
                        <div><span style="color:#94a3b8;">Available Stock</span><br><strong>{mat["available"]} {mat["unit"]}</strong></div>
                        <div><span style="color:#94a3b8;">Net Requirement</span><br><strong style="color:{"#ef4444" if mat["net_req"]>0 else "#059669"};">{mat["net_req"]} {mat["unit"]}</strong></div>
                    </div>
                </div>''', unsafe_allow_html=True)

                bd_rows = []
                for bd in mat.get("breakdown", []):
                    so = SS["so_list"].get(bd["so_no"], {})
                    bd_rows.append({
                        "SO #":    bd["so_no"],
                        "Buyer":   so.get("buyer", "—"),
                        "SKU":     bd["sku"],
                        "Source":  bd["source"],
                        "Qty Required": bd["qty_req"],
                        "Unit":    mat["unit"],
                    })
                if bd_rows:
                    st.dataframe(pd.DataFrame(bd_rows), use_container_width=True, hide_index=True)

            st.markdown("---")

            # Excel Export
            st.markdown("#### 📥 Export")
            import base64
            csv_data = df_mrp.to_csv(index=False)
            b64_csv = base64.b64encode(csv_data.encode()).decode()
            st.markdown(f'''<a href="data:text/csv;base64,{b64_csv}" download="MRP_Requirements_{datetime.now().strftime("%Y%m%d")}.csv">
                <button style="background:#1c1c2e;color:white;border:none;padding:8px 20px;border-radius:8px;font-weight:700;cursor:pointer;">
                    ⬇️ Download CSV (Excel mein open karo)
                </button></a>''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">Filter ke hisaab se koi material nahi mila.</div>', unsafe_allow_html=True)


# ── RESERVATIONS ──────────────────────────────────────────────────────────────
elif nav_mrp == "🔒 Reservations":
    st.markdown('<h1>Material Reservations (Soft)</h1>', unsafe_allow_html=True)
    st.markdown('''<div class="info-box">
        <strong>Soft Reservation</strong> — MRP ke basis pe material SO ke against plan karo.<br>
        Soft Reserved material future MRP mein "Net Available" mein count nahi hoga.<br>
        <strong>Hard Reservation</strong> PO module ke baad hogi jab material physically aayega.
    </div>''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not SS.get("mrp_result"):
        st.markdown('<div class="warn-box">Pehle MRP run karo "▶ Run MRP" se.</div>', unsafe_allow_html=True)
    else:
        mrp_result = SS["mrp_result"]
        so_list_used = SS.get("mrp_so_list", [])

        # soft_reservations structure:
        # { material_code: { so_no: { sku: qty, ... }, ... } }
        if "soft_reservations" not in SS:
            SS["soft_reservations"] = {}

        # ── Soft Reserve All button ────────────────────────────────────────────
        if st.button("🔒 Soft Reserve All (MRP ke basis pe)", use_container_width=False):
            for code, mat in mrp_result.items():
                if code not in SS["soft_reservations"]:
                    SS["soft_reservations"][code] = {}
                # Distribute requirement SO-wise from breakdown
                for bd in mat.get("breakdown", []):
                    so_no   = bd["so_no"]
                    sku     = bd["sku"]
                    qty_req = bd["qty_req"]
                    if so_no not in SS["soft_reservations"][code]:
                        SS["soft_reservations"][code][so_no] = {}
                    prev = SS["soft_reservations"][code][so_no].get(sku, 0)
                    SS["soft_reservations"][code][so_no][sku] = round(prev + qty_req, 3)
            save_data()
            st.success("✅ Soft Reservation complete!")
            st.rerun()

        st.markdown("---")

        # ── Summary View ───────────────────────────────────────────────────────
        st.markdown("#### 📊 Reservation Summary")

        tab_sum, tab_detail, tab_so = st.tabs(["Material-wise Summary", "SO-wise Detail", "Release Reservation"])

        with tab_sum:
            sum_rows = []
            for code, mat in mrp_result.items():
                soft_res = SS["soft_reservations"].get(code, {})
                soft_total = sum(
                    qty for so_data in soft_res.values()
                    for qty in so_data.values()
                )
                in_stock  = mat.get("stock", 0)
                hard_res  = mat.get("reserved", 0)  # will be used post-PO
                available = max(0, in_stock - hard_res)
                net_after_soft = max(0, mat["total_req"] - available - soft_total)

                sum_rows.append({
                    "Material":        f"{code} – {mat['name']}",
                    "Type":            mat["type"],
                    "Total Required":  mat["total_req"],
                    "In Stock":        in_stock,
                    "Soft Reserved":   soft_total,
                    "Net Shortage":    net_after_soft,
                    "Unit":            mat["unit"],
                    "Status":          "🟡 Soft Reserved" if soft_total > 0 else ("🔴 Not Reserved" if mat["total_req"] > 0 else "🟢 OK"),
                })
            if sum_rows:
                st.dataframe(pd.DataFrame(sum_rows), use_container_width=True, hide_index=True)

        with tab_detail:
            st.markdown("##### SO / SKU wise Reservation Detail")
            for code, so_data in SS["soft_reservations"].items():
                if not so_data:
                    continue
                mat_name = mrp_result.get(code, {}).get("name", code)
                unit     = mrp_result.get(code, {}).get("unit", "")
                total_soft = sum(q for sd in so_data.values() for q in sd.values())
                with st.expander(f"📦 {code} – {mat_name} | Soft Reserved: {total_soft} {unit}"):
                    det_rows = []
                    for so_no, sku_data in so_data.items():
                        so = SS["so_list"].get(so_no, {})
                        for sku, qty in sku_data.items():
                            det_rows.append({
                                "SO #":   so_no,
                                "Buyer":  so.get("buyer","—"),
                                "SKU":    sku,
                                "Soft Reserved Qty": qty,
                                "Unit":   unit,
                                "Delivery": so.get("delivery_date","—"),
                            })
                    if det_rows:
                        st.dataframe(pd.DataFrame(det_rows), use_container_width=True, hide_index=True)

        with tab_so:
            st.markdown("##### Release / Clear Reservation")
            st.markdown('<div class="warn-box">SO complete hone ke baad ya cancel hone pe reservation release karo.</div>', unsafe_allow_html=True)

            rel_so = st.selectbox("SO select karo release ke liye",
                                   [""] + list(SS["so_list"].keys()),
                                   key="rel_so_sel")
            if rel_so:
                # Show what's reserved for this SO
                rel_rows = []
                for code, so_data in SS["soft_reservations"].items():
                    if rel_so in so_data:
                        mat_name = mrp_result.get(code, {}).get("name", code)
                        unit     = mrp_result.get(code, {}).get("unit", "")
                        for sku, qty in so_data[rel_so].items():
                            rel_rows.append({
                                "Material": f"{code} – {mat_name}",
                                "SKU": sku, "Reserved Qty": qty, "Unit": unit
                            })
                if rel_rows:
                    st.dataframe(pd.DataFrame(rel_rows), use_container_width=True, hide_index=True)
                    if st.button(f"🔓 Release All Reservations for {rel_so}", use_container_width=False):
                        for code in SS["soft_reservations"]:
                            if rel_so in SS["soft_reservations"][code]:
                                del SS["soft_reservations"][code][rel_so]
                        save_data()
                        st.success(f"✅ {rel_so} ki reservations release ho gayi!")
                        st.rerun()
                else:
                    st.markdown(f'<div class="info-box">Is SO ke liye koi reservation nahi hai abhi.</div>', unsafe_allow_html=True)



# ── MRP REPORTS ───────────────────────────────────────────────────────────────
elif nav_mrp == "📊 MRP Reports":
    st.markdown('<h1>MRP Reports</h1>', unsafe_allow_html=True)

    if not SS.get("mrp_result"):
        st.markdown('<div class="warn-box">Pehle MRP run karo.</div>', unsafe_allow_html=True)
    else:
        mrp_result = SS["mrp_result"]

        rep = st.selectbox("Report select karo", [
            "1. Material Requirement Report (All)",
            "2. Fabric Requirement Report",
            "3. Accessories Requirement Report",
            "4. Packaging Requirement Report",
            "5. Buyer Order Requirement Report",
        ], key="mrp_rep_sel")

        def mat_table(type_filter=None):
            rows = []
            for code, mat in mrp_result.items():
                if type_filter and mat["type"] not in type_filter:
                    continue
                rows.append({
                    "Code": code, "Material": mat["name"], "Type": mat["type"],
                    "Required": mat["total_req"], "Stock": mat["stock"],
                    "Available": mat["available"], "Net Req": mat["net_req"],
                    "Unit": mat["unit"],
                    "Status": "🔴 Short" if mat["net_req"] > 0 else "🟢 OK"
                })
            return rows

        if rep.startswith("1"):
            rows = mat_table()
            st.markdown(f"**Total {len(rows)} materials**")
            if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        elif rep.startswith("2"):
            rows = mat_table(["Raw Material (RM)"])
            fabric_rows = [r for r in rows if any(w in r["Material"].lower() for w in ["fabric","cloth","grey","printed","dyed","lycra","cotton","polyester","silk","linen","khadi"])]
            st.markdown(f"**Fabric items: {len(fabric_rows)}**")
            if fabric_rows: st.dataframe(pd.DataFrame(fabric_rows), use_container_width=True, hide_index=True)
            else:
                st.info("Koi fabric item nahi mila. All Raw Materials:")
                if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        elif rep.startswith("3"):
            rows = mat_table(["Accessories"])
            st.markdown(f"**Accessories: {len(rows)}**")
            if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else: st.markdown('<div class="warn-box">Koi accessories item nahi mila.</div>', unsafe_allow_html=True)

        elif rep.startswith("4"):
            rows = mat_table(["Packing Materials"])
            st.markdown(f"**Packaging items: {len(rows)}**")
            if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else: st.markdown('<div class="warn-box">Koi packaging item nahi mila.</div>', unsafe_allow_html=True)

        elif rep.startswith("5"):
            # Buyer-wise breakdown
            so_list_used = SS.get("mrp_so_list", [])
            buyer_data = {}
            for code, mat in mrp_result.items():
                for bd in mat.get("breakdown", []):
                    so = SS["so_list"].get(bd["so_no"], {})
                    buyer = so.get("buyer", "Unknown")
                    if buyer not in buyer_data:
                        buyer_data[buyer] = {}
                    if code not in buyer_data[buyer]:
                        buyer_data[buyer][code] = {"name": mat["name"], "type": mat["type"], "qty": 0, "unit": mat["unit"]}
                    buyer_data[buyer][code]["qty"] += bd["qty_req"]

            for buyer, mats in buyer_data.items():
                with st.expander(f"🛍️ {buyer} — {len(mats)} materials"):
                    brows = [{"Code": c, "Material": m["name"], "Type": m["type"],
                              "Required": round(m["qty"],2), "Unit": m["unit"]} for c, m in mats.items()]
                    st.dataframe(pd.DataFrame(brows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════════
# TNA MODULE — Time & Action Calendar
# ═══════════════════════════════════════════════════════════════════════════════

# ── Constants ─────────────────────────────────────────────────────────────────
TNA_ACTIVITY_GROUPS = [
    "Merchandising","Fabric","Sampling","CAD","Purchase",
    "Printing","Dyeing","Cutting","Stitching","Finishing",
    "Packing","Quality","Dispatch","Logistics"
]

TNA_STATUS_OPTIONS = [
    "Not Started","In Progress","Completed","Hold","Delayed","Cancelled","Partially Completed","Awaiting Approval"
]

TNA_PRIORITY = ["Normal","High","Urgent"]

# Standard templates
TNA_DEFAULT_TEMPLATES = {
    "Domestic Order TNA": [
        {"sr":1,  "activity":"Buyer Order Receive",          "group":"Merchandising","lead_days":45,"depends_on":""},
        {"sr":2,  "activity":"Tech Pack Receive",             "group":"Merchandising","lead_days":42,"depends_on":"Buyer Order Receive"},
        {"sr":3,  "activity":"Costing Final",                 "group":"Merchandising","lead_days":40,"depends_on":"Tech Pack Receive"},
        {"sr":4,  "activity":"BOM Final",                     "group":"Merchandising","lead_days":38,"depends_on":"Costing Final"},
        {"sr":5,  "activity":"Fabric Requirement Final",      "group":"Fabric",       "lead_days":37,"depends_on":"BOM Final"},
        {"sr":6,  "activity":"Accessories Requirement Final", "group":"Purchase",     "lead_days":37,"depends_on":"BOM Final"},
        {"sr":7,  "activity":"Grey Fabric Booking",           "group":"Fabric",       "lead_days":35,"depends_on":"Fabric Requirement Final"},
        {"sr":8,  "activity":"Accessories Purchase",          "group":"Purchase",     "lead_days":34,"depends_on":"Accessories Requirement Final"},
        {"sr":9,  "activity":"Size Set Approval",             "group":"Sampling",     "lead_days":32,"depends_on":"BOM Final"},
        {"sr":10, "activity":"Grey Fabric Inward",            "group":"Fabric",       "lead_days":28,"depends_on":"Grey Fabric Booking"},
        {"sr":11, "activity":"Accessories Inward",            "group":"Purchase",     "lead_days":26,"depends_on":"Accessories Purchase"},
        {"sr":12, "activity":"PP Sample",                     "group":"Sampling",     "lead_days":25,"depends_on":"Grey Fabric Inward"},
        {"sr":13, "activity":"Buyer Approval",                "group":"Merchandising","lead_days":22,"depends_on":"PP Sample"},
        {"sr":14, "activity":"Cutting Start",                 "group":"Cutting",      "lead_days":20,"depends_on":"Buyer Approval"},
        {"sr":15, "activity":"Cutting Complete",              "group":"Cutting",      "lead_days":17,"depends_on":"Cutting Start"},
        {"sr":16, "activity":"Stitching Start",               "group":"Stitching",    "lead_days":16,"depends_on":"Cutting Complete"},
        {"sr":17, "activity":"Stitching Complete",            "group":"Stitching",    "lead_days":11,"depends_on":"Stitching Start"},
        {"sr":18, "activity":"Finishing Start",               "group":"Finishing",    "lead_days":10,"depends_on":"Stitching Complete"},
        {"sr":19, "activity":"Finishing Complete",            "group":"Finishing",    "lead_days":8, "depends_on":"Finishing Start"},
        {"sr":20, "activity":"Packing Start",                 "group":"Packing",      "lead_days":7, "depends_on":"Finishing Complete"},
        {"sr":21, "activity":"Packing Complete",              "group":"Packing",      "lead_days":5, "depends_on":"Packing Start"},
        {"sr":22, "activity":"Final QC",                      "group":"Quality",      "lead_days":4, "depends_on":"Packing Complete"},
        {"sr":23, "activity":"Inspection",                    "group":"Quality",      "lead_days":3, "depends_on":"Final QC"},
        {"sr":24, "activity":"Dispatch Planning",             "group":"Dispatch",     "lead_days":2, "depends_on":"Inspection"},
        {"sr":25, "activity":"Dispatch",                      "group":"Dispatch",     "lead_days":1, "depends_on":"Dispatch Planning"},
        {"sr":26, "activity":"Delivery",                      "group":"Logistics",    "lead_days":0, "depends_on":"Dispatch"},
    ],
    "Export Order TNA": [
        {"sr":1,  "activity":"Buyer Order Receive",          "group":"Merchandising","lead_days":90,"depends_on":""},
        {"sr":2,  "activity":"Tech Pack Receive",             "group":"Merchandising","lead_days":85,"depends_on":"Buyer Order Receive"},
        {"sr":3,  "activity":"Costing Final",                 "group":"Merchandising","lead_days":82,"depends_on":"Tech Pack Receive"},
        {"sr":4,  "activity":"BOM Final",                     "group":"Merchandising","lead_days":80,"depends_on":"Costing Final"},
        {"sr":5,  "activity":"Lab Dip Approval",              "group":"Fabric",       "lead_days":78,"depends_on":"BOM Final"},
        {"sr":6,  "activity":"Shade Approval",                "group":"Fabric",       "lead_days":75,"depends_on":"Lab Dip Approval"},
        {"sr":7,  "activity":"Grey Fabric Booking",           "group":"Fabric",       "lead_days":72,"depends_on":"Shade Approval"},
        {"sr":8,  "activity":"Accessories Requirement Final", "group":"Purchase",     "lead_days":78,"depends_on":"BOM Final"},
        {"sr":9,  "activity":"Accessories Purchase",          "group":"Purchase",     "lead_days":70,"depends_on":"Accessories Requirement Final"},
        {"sr":10, "activity":"Proto Sample",                  "group":"Sampling",     "lead_days":75,"depends_on":"BOM Final"},
        {"sr":11, "activity":"Fit Sample",                    "group":"Sampling",     "lead_days":68,"depends_on":"Proto Sample"},
        {"sr":12, "activity":"Size Set Approval",             "group":"Sampling",     "lead_days":62,"depends_on":"Fit Sample"},
        {"sr":13, "activity":"Grey Fabric Inward",            "group":"Fabric",       "lead_days":60,"depends_on":"Grey Fabric Booking"},
        {"sr":14, "activity":"Accessories Inward",            "group":"Purchase",     "lead_days":55,"depends_on":"Accessories Purchase"},
        {"sr":15, "activity":"PP Sample",                     "group":"Sampling",     "lead_days":52,"depends_on":"Grey Fabric Inward"},
        {"sr":16, "activity":"Buyer Approval",                "group":"Merchandising","lead_days":45,"depends_on":"PP Sample"},
        {"sr":17, "activity":"Cutting Start",                 "group":"Cutting",      "lead_days":40,"depends_on":"Buyer Approval"},
        {"sr":18, "activity":"Cutting Complete",              "group":"Cutting",      "lead_days":35,"depends_on":"Cutting Start"},
        {"sr":19, "activity":"Stitching Start",               "group":"Stitching",    "lead_days":34,"depends_on":"Cutting Complete"},
        {"sr":20, "activity":"Stitching Complete",            "group":"Stitching",    "lead_days":25,"depends_on":"Stitching Start"},
        {"sr":21, "activity":"Finishing Complete",            "group":"Finishing",    "lead_days":20,"depends_on":"Stitching Complete"},
        {"sr":22, "activity":"Packing Complete",              "group":"Packing",      "lead_days":15,"depends_on":"Finishing Complete"},
        {"sr":23, "activity":"Final QC",                      "group":"Quality",      "lead_days":12,"depends_on":"Packing Complete"},
        {"sr":24, "activity":"Inspection",                    "group":"Quality",      "lead_days":10,"depends_on":"Final QC"},
        {"sr":25, "activity":"Dispatch",                      "group":"Dispatch",     "lead_days":7, "depends_on":"Inspection"},
        {"sr":26, "activity":"Shipment",                      "group":"Logistics",    "lead_days":3, "depends_on":"Dispatch"},
        {"sr":27, "activity":"Delivery",                      "group":"Logistics",    "lead_days":0, "depends_on":"Shipment"},
    ],
    "Printed Fabric TNA": [
        {"sr":1,  "activity":"Buyer Order Receive",          "group":"Merchandising","lead_days":45,"depends_on":""},
        {"sr":2,  "activity":"BOM Final",                     "group":"Merchandising","lead_days":42,"depends_on":"Buyer Order Receive"},
        {"sr":3,  "activity":"CAD Final",                     "group":"CAD",          "lead_days":40,"depends_on":"BOM Final"},
        {"sr":4,  "activity":"Grey Fabric Booking",           "group":"Fabric",       "lead_days":38,"depends_on":"BOM Final"},
        {"sr":5,  "activity":"Grey Fabric Inward",            "group":"Fabric",       "lead_days":32,"depends_on":"Grey Fabric Booking"},
        {"sr":6,  "activity":"Printing Approval",             "group":"Printing",     "lead_days":30,"depends_on":"CAD Final"},
        {"sr":7,  "activity":"Printed Fabric Inward",         "group":"Printing",     "lead_days":25,"depends_on":"Printing Approval"},
        {"sr":8,  "activity":"PP Sample",                     "group":"Sampling",     "lead_days":23,"depends_on":"Printed Fabric Inward"},
        {"sr":9,  "activity":"Buyer Approval",                "group":"Merchandising","lead_days":20,"depends_on":"PP Sample"},
        {"sr":10, "activity":"Cutting Start",                 "group":"Cutting",      "lead_days":18,"depends_on":"Buyer Approval"},
        {"sr":11, "activity":"Cutting Complete",              "group":"Cutting",      "lead_days":15,"depends_on":"Cutting Start"},
        {"sr":12, "activity":"Stitching Complete",            "group":"Stitching",    "lead_days":10,"depends_on":"Cutting Complete"},
        {"sr":13, "activity":"Finishing Complete",            "group":"Finishing",    "lead_days":7, "depends_on":"Stitching Complete"},
        {"sr":14, "activity":"Packing Complete",              "group":"Packing",      "lead_days":4, "depends_on":"Finishing Complete"},
        {"sr":15, "activity":"Final QC",                      "group":"Quality",      "lead_days":3, "depends_on":"Packing Complete"},
        {"sr":16, "activity":"Dispatch",                      "group":"Dispatch",     "lead_days":1, "depends_on":"Final QC"},
        {"sr":17, "activity":"Delivery",                      "group":"Logistics",    "lead_days":0, "depends_on":"Dispatch"},
    ],
}

def get_all_templates():
    custom   = SS.get("tna_templates", {})
    combined = dict(TNA_DEFAULT_TEMPLATES)
    combined.update(custom)
    return combined

def build_tna_lines(template_acts, delivery_date):
    """Build TNA lines from template activities + delivery date"""
    lines = []
    del_dt = date.fromisoformat(str(delivery_date))
    for act in template_acts:
        planned_end = del_dt - timedelta(days=act["lead_days"])
        planned_start = planned_end - timedelta(days=1)
        lines.append({
            "sr":           act["sr"],
            "activity":     act["activity"],
            "group":        act["group"],
            "responsible":  "",
            "backup":       "",
            "planned_start": str(planned_start),
            "planned_end":   str(planned_end),
            "actual_start":  "",
            "actual_end":    "",
            "status":        "Not Started",
            "delay_days":    0,
            "delay_reason":  "",
            "remarks":       "",
            "depends_on":    act.get("depends_on",""),
            "seq":           act["sr"],
            "history":       [],
        })
    return lines

def recalc_tna(tna):
    """Recalculate status + delay days for all lines"""
    today = str(date.today())
    for ln in tna.get("lines", []):
        if ln.get("status") == "Cancelled":
            continue
        if ln.get("actual_end"):
            actual = ln["actual_end"]
            planned = ln["planned_end"]
            delay = (date.fromisoformat(actual) - date.fromisoformat(planned)).days
            ln["delay_days"] = max(0, delay)
            if ln["status"] not in ["Cancelled","Hold"]:
                ln["status"] = "Completed"
        elif ln.get("planned_end","") < today and ln["status"] not in ["Completed","Cancelled","Hold"]:
            ln["status"] = "Delayed"
            ln["delay_days"] = (date.today() - date.fromisoformat(ln["planned_end"])).days
        elif ln.get("actual_start") and not ln.get("actual_end"):
            ln["status"] = "In Progress"
    return tna

def cascade_delays(tna, changed_activity, new_end_date):
    """Cascade delay from one activity to all dependents"""
    lines    = tna.get("lines", [])
    act_map  = {ln["activity"]: i for i, ln in enumerate(lines)}
    idx      = act_map.get(changed_activity)
    if idx is None: return tna

    orig_end = date.fromisoformat(lines[idx]["planned_end"])
    new_end  = date.fromisoformat(new_end_date)
    delay    = (new_end - orig_end).days
    if delay <= 0: return tna

    # BFS to find all dependents
    delayed_set = {changed_activity}
    changed = True
    while changed:
        changed = False
        for ln in lines:
            if ln["activity"] not in delayed_set and ln.get("depends_on") in delayed_set:
                delayed_set.add(ln["activity"])
                changed = True

    # Shift dates
    for ln in lines:
        if ln["activity"] in delayed_set and ln["activity"] != changed_activity:
            if not ln.get("actual_end"):
                for field in ["planned_start","planned_end"]:
                    if ln.get(field):
                        d = date.fromisoformat(ln[field])
                        ln[field] = str(d + timedelta(days=delay))
    return tna

def shipment_risk(tna):
    """Determine shipment risk based on critical delayed activities"""
    critical = {"Cutting Start","Stitching Start","Packing Complete","Final QC","Dispatch","Shipment"}
    delivery_str = tna.get("delivery_date","")
    if not delivery_str: return "Safe"
    days_to_delivery = (date.fromisoformat(delivery_str) - date.today()).days
    delayed_critical = [
        ln for ln in tna.get("lines",[])
        if ln["activity"] in critical and ln.get("status") == "Delayed"
    ]
    if len(delayed_critical) >= 3 or (delayed_critical and days_to_delivery < 7):
        return "High Risk"
    elif delayed_critical or days_to_delivery < 14:
        return "Moderate Risk"
    return "Safe"

def risk_badge(risk):
    colors = {"High Risk":"#ef4444","Moderate Risk":"#d97706","Safe":"#059669"}
    bg     = {"High Risk":"#fee2e2","Moderate Risk":"#fef3c7","Safe":"#d1fae5"}
    c = colors.get(risk,"#64748b"); b = bg.get(risk,"#f1f5f9")
    return f'<span style="background:{b};color:{c};padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;">{risk}</span>'

def status_dot(status):
    colors = {"Completed":"#059669","In Progress":"#d97706","Delayed":"#ef4444",
              "Not Started":"#94a3b8","Hold":"#6366f1","Cancelled":"#475569",
              "Partially Completed":"#0ea5e9","Awaiting Approval":"#8b5cf6"}
    c = colors.get(status,"#94a3b8")
    return f'<span style="background:{c};width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:4px;"></span>'


# ── TNA DASHBOARD ─────────────────────────────────────────────────────────────
if nav_tna == "📅 TNA Dashboard":
    st.markdown('<h1>TNA Dashboard</h1>', unsafe_allow_html=True)

    tna_list = SS.get("tna_list", {})
    # Recalc all
    for k in tna_list: tna_list[k] = recalc_tna(tna_list[k])

    total      = len(tna_list)
    delayed_ct = sum(1 for t in tna_list.values() for ln in t.get("lines",[]) if ln["status"]=="Delayed")
    due_today  = sum(1 for t in tna_list.values() for ln in t.get("lines",[])
                     if ln.get("planned_end")==str(date.today()) and ln["status"] not in ["Completed","Cancelled"])
    overdue_ct = sum(1 for t in tna_list.values() for ln in t.get("lines",[])
                     if ln["status"]=="Delayed")
    risk_ct    = sum(1 for t in tna_list.values() if shipment_risk(t) != "Safe")
    completed_ct = sum(1 for t in tna_list.values() if t.get("status")=="Completed")

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, val, label, cls in [
        (c1, total,       "Total TNAs",          ""),
        (c2, delayed_ct,  "Delayed Activities",  "red" if delayed_ct else ""),
        (c3, due_today,   "Due Today",           "amber" if due_today else ""),
        (c4, overdue_ct,  "Overdue",             "red" if overdue_ct else ""),
        (c5, risk_ct,     "Shipment Risk",       "red" if risk_ct else ""),
        (c6, completed_ct,"Completed",           "green"),
    ]:
        with col:
            st.markdown(f'<div class="metric-box {cls}"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    if not tna_list:
        st.markdown('<div class="warn-box">Koi TNA nahi bana abhi tak.</div>', unsafe_allow_html=True)
    else:
        dt1, dt2, dt3, dt4 = st.tabs(["🚨 Alerts", "👤 Responsible-wise", "🏢 Department-wise", "📋 All Orders"])

        with dt1:
            # Overdue
            st.markdown("#### 🔴 Overdue Activities")
            found = False
            for tna_no, tna in tna_list.items():
                for ln in tna.get("lines",[]):
                    if ln["status"] == "Delayed":
                        found = True
                        st.markdown(f'''<div class="danger-box" style="margin:2px 0;display:flex;justify-content:space-between;">
                            <span><strong>{tna.get("style_name","")} / {tna.get("buyer","")}</strong> — {ln["activity"]} ({ln["group"]})</span>
                            <span>Due: {ln["planned_end"]} | <strong style="color:#ef4444;">{ln["delay_days"]}d overdue</strong> | Assigned: {ln.get("responsible","—")}</span>
                        </div>''', unsafe_allow_html=True)
            if not found: st.markdown('<div class="ok-box">Koi overdue activity nahi hai! 🎉</div>', unsafe_allow_html=True)

            st.markdown("#### 🟡 Due Today / Tomorrow")
            tomorrow = str(date.today() + timedelta(days=1))
            found2 = False
            for tna_no, tna in tna_list.items():
                for ln in tna.get("lines",[]):
                    if ln.get("planned_end") in [str(date.today()), tomorrow] and ln["status"] not in ["Completed","Cancelled"]:
                        found2 = True
                        color = "#ef4444" if ln["planned_end"] == str(date.today()) else "#d97706"
                        st.markdown(f'''<div class="warn-box" style="margin:2px 0;">
                            <strong>{tna.get("style_name","")}</strong> — {ln["activity"]} — Due: <strong style="color:{color};">{ln["planned_end"]}</strong> — {ln.get("responsible","—")}
                        </div>''', unsafe_allow_html=True)
            if not found2: st.markdown('<div class="ok-box">Koi activity due nahi today/tomorrow.</div>', unsafe_allow_html=True)

        with dt2:
            st.markdown("#### 👤 Responsible Person-wise Pending")
            resp_data = {}
            for tna_no, tna in tna_list.items():
                for ln in tna.get("lines",[]):
                    if ln["status"] not in ["Completed","Cancelled"]:
                        resp = ln.get("responsible","Unassigned") or "Unassigned"
                        if resp not in resp_data: resp_data[resp] = []
                        resp_data[resp].append({
                            "TNA": tna_no, "Style": tna.get("style_name",""),
                            "Activity": ln["activity"], "Due": ln["planned_end"],
                            "Status": ln["status"], "Delay": ln["delay_days"],
                        })
            for resp, acts in sorted(resp_data.items()):
                with st.expander(f"👤 {resp} — {len(acts)} pending"):
                    st.dataframe(pd.DataFrame(acts), use_container_width=True, hide_index=True)

        with dt3:
            st.markdown("#### 🏢 Department-wise Pending")
            dept_data = {}
            for tna_no, tna in tna_list.items():
                for ln in tna.get("lines",[]):
                    if ln["status"] not in ["Completed","Cancelled"]:
                        grp = ln.get("group","Other")
                        if grp not in dept_data: dept_data[grp] = []
                        dept_data[grp].append({
                            "TNA": tna_no, "Style": tna.get("style_name",""),
                            "Activity": ln["activity"], "Due": ln["planned_end"],
                            "Status": ln["status"],
                        })
            for dept, acts in sorted(dept_data.items()):
                delayed_in_dept = sum(1 for a in acts if a["Status"]=="Delayed")
                with st.expander(f"🏢 {dept} — {len(acts)} pending {'🔴 '+str(delayed_in_dept)+' delayed' if delayed_in_dept else ''}"):
                    st.dataframe(pd.DataFrame(acts), use_container_width=True, hide_index=True)

        with dt4:
            st.markdown("#### 📋 All Orders TNA Summary")
            order_rows = []
            for tna_no, tna in tna_list.items():
                lines      = tna.get("lines",[])
                done       = sum(1 for ln in lines if ln["status"]=="Completed")
                delayed    = sum(1 for ln in lines if ln["status"]=="Delayed")
                pct        = int(done/len(lines)*100) if lines else 0
                risk       = shipment_risk(tna)
                del_dt     = tna.get("delivery_date","")
                days_left  = (date.fromisoformat(del_dt)-date.today()).days if del_dt else 0
                order_rows.append({
                    "TNA #": tna_no, "Style": tna.get("style_name",""),
                    "Buyer": tna.get("buyer",""), "SO #": tna.get("so_no",""),
                    "Delivery": del_dt, "Days Left": days_left,
                    "Progress%": pct, "Done": done, "Delayed": delayed,
                    "Risk": risk, "Priority": tna.get("priority","Normal"),
                })
            if order_rows:
                st.dataframe(pd.DataFrame(order_rows), use_container_width=True, hide_index=True)


# ── CREATE TNA ────────────────────────────────────────────────────────────────
elif nav_tna == "➕ Create TNA":
    st.markdown('<h1>Create TNA</h1>', unsafe_allow_html=True)

    so_list   = SS.get("so_list", {})
    templates = get_all_templates()

    create_tab1, create_tab2 = st.tabs(["📋 From SO / Buyer PO", "✍️ Manual Create"])

    with create_tab1:
        st.markdown('<div class="info-box">SO select karo → Template select karo → TNA auto-generate hoga delivery date se backward.</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        existing_tna_sos = {t.get("so_no") for t in SS.get("tna_list",{}).values()}

        cf1, cf2 = st.columns(2)
        with cf1:
            sel_so = st.selectbox("SO select karo *",
                [""] + list(so_list.keys()),
                format_func=lambda x: f"{x} – {so_list.get(x,{}).get('buyer','')} | Del: {so_list.get(x,{}).get('delivery_date','')}" if x else "— Select —",
                key="tna_create_so")
        with cf2:
            tmpl_name = st.selectbox("TNA Template *", list(templates.keys()), key="tna_tmpl_sel")

        if sel_so and sel_so in so_list:
            so = so_list[sel_so]
            if sel_so in existing_tna_sos:
                st.markdown(f'<div class="warn-box">⚠️ {sel_so} ke liye TNA already exist karta hai.</div>', unsafe_allow_html=True)
            else:
                # Header fields
                st.markdown("#### TNA Header Details")
                h1, h2, h3 = st.columns(3)
                with h1:
                    tna_buyer    = st.text_input("Buyer Name", value=so.get("buyer",""), key="tna_h_buyer")
                    tna_po_no    = st.text_input("Buyer PO Number", value=so.get("ref_number",""), key="tna_h_po")
                    tna_so_no    = st.text_input("SO Number", value=sel_so, disabled=True, key="tna_h_so")
                    tna_merchant = st.text_input("Merchant Code", value=so.get("merchant",""), key="tna_h_merch")
                with h2:
                    tna_style    = st.text_input("Style Code", key="tna_h_style",
                                                  value=so.get("lines",[{}])[0].get("parent","") if so.get("lines") else "")
                    tna_style_nm = st.text_input("Style Name", key="tna_h_stylenm",
                                                  value=so.get("lines",[{}])[0].get("sku_name","") if so.get("lines") else "")
                    tna_brand    = st.text_input("Brand", key="tna_h_brand")
                    tna_season   = st.selectbox("Season", SEASONS, key="tna_h_season")
                with h3:
                    tna_del_date = st.date_input("Buyer Delivery Date",
                                                  value=date.fromisoformat(so.get("delivery_date", str(date.today()))),
                                                  key="tna_h_del")
                    tna_exfac    = st.date_input("Ex-Factory Date", value=tna_del_date - timedelta(days=3), key="tna_h_exfac")
                    tna_ship     = st.date_input("Shipment Date", value=tna_del_date - timedelta(days=1), key="tna_h_ship")
                    tna_priority = st.selectbox("Priority", TNA_PRIORITY, key="tna_h_pri")

                h4, h5 = st.columns(2)
                with h4:
                    tna_ord_qty  = st.number_input("Order Quantity", value=sum(l.get("qty",0) for l in so.get("lines",[])), key="tna_h_qty")
                    tna_uom      = st.selectbox("UOM", ["Pieces","Set","Dozen"], key="tna_h_uom")
                    tna_prod_unit = st.text_input("Production Unit / Vendor", key="tna_h_pu")
                with h5:
                    tna_merchandiser = st.text_input("Merchandiser Name", key="tna_h_merch_nm")
                    tna_remarks  = st.text_area("Remarks", height=70, key="tna_h_rem")

                # Preview activities
                tmpl_acts = templates.get(tmpl_name, [])
                lines     = build_tna_lines(tmpl_acts, tna_del_date)

                st.markdown(f"#### Preview — {len(lines)} activities from '{tmpl_name}'")
                prev_df = pd.DataFrame([{
                    "Sr": ln["sr"], "Activity": ln["activity"], "Group": ln["group"],
                    "Planned Start": ln["planned_start"], "Planned End": ln["planned_end"],
                    "Depends On": ln["depends_on"],
                } for ln in lines])
                st.dataframe(prev_df, use_container_width=True, hide_index=True)

                if st.button("✅ Create TNA", use_container_width=False):
                    tna_no = f"TNA-{SS['tna_counter']:04d}"
                    SS["tna_list"][tna_no] = {
                        "tna_no":       tna_no,
                        "tna_date":     str(date.today()),
                        "so_no":        sel_so,
                        "buyer":        tna_buyer,
                        "po_number":    tna_po_no,
                        "style":        tna_style,
                        "style_name":   tna_style_nm,
                        "brand":        tna_brand,
                        "merchant":     tna_merchant,
                        "season":       tna_season,
                        "order_qty":    tna_ord_qty,
                        "uom":          tna_uom,
                        "delivery_date": str(tna_del_date),
                        "exfactory_date": str(tna_exfac),
                        "shipment_date": str(tna_ship),
                        "production_unit": tna_prod_unit,
                        "merchandiser": tna_merchandiser,
                        "priority":     tna_priority,
                        "remarks":      tna_remarks,
                        "template":     tmpl_name,
                        "lines":        lines,
                        "status":       "Active",
                        "created_at":   datetime.now().isoformat(),
                        "history":      [],
                    }
                    SS["tna_counter"] += 1
                    save_data()
                    st.success(f"✅ {tna_no} created with {len(lines)} activities!")
                    st.session_state["current_page"] = "📋 TNA List"
                    st.rerun()

    with create_tab2:
        st.markdown('<div class="info-box">Manual TNA — SO se independent create kar sakte ho.</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            m_buyer   = st.text_input("Buyer *", key="tna_m_buyer")
            m_style   = st.text_input("Style Code", key="tna_m_style")
            m_del     = st.date_input("Delivery Date", key="tna_m_del")
            m_pri     = st.selectbox("Priority", TNA_PRIORITY, key="tna_m_pri")
        with m2:
            m_tmpl    = st.selectbox("Template", list(templates.keys()), key="tna_m_tmpl")
            m_merch   = st.text_input("Merchandiser", key="tna_m_merch")
            m_remarks = st.text_area("Remarks", height=70, key="tna_m_rem")

        if st.button("✅ Create Manual TNA") and m_buyer:
            tmpl_acts = templates.get(m_tmpl, [])
            lines     = build_tna_lines(tmpl_acts, m_del)
            tna_no    = f"TNA-{SS['tna_counter']:04d}"
            SS["tna_list"][tna_no] = {
                "tna_no": tna_no, "tna_date": str(date.today()),
                "so_no": "", "buyer": m_buyer, "style": m_style,
                "style_name": m_style, "delivery_date": str(m_del),
                "priority": m_pri, "merchandiser": m_merch,
                "template": m_tmpl, "lines": lines,
                "remarks": m_remarks, "status": "Active",
                "created_at": datetime.now().isoformat(), "history": [],
            }
            SS["tna_counter"] += 1
            save_data()
            st.success(f"✅ {tna_no} created!")
            st.session_state["current_page"] = "📋 TNA List"
            st.rerun()


# ── TNA LIST ──────────────────────────────────────────────────────────────────
elif nav_tna == "📋 TNA List":

    if "selected_tna" not in st.session_state:
        st.session_state["selected_tna"] = None

    # ── Detail View ───────────────────────────────────────────────────────────
    if st.session_state["selected_tna"] and st.session_state["selected_tna"] in SS.get("tna_list",{}):
        tna_no = st.session_state["selected_tna"]
        tna    = recalc_tna(SS["tna_list"][tna_no])
        SS["tna_list"][tna_no] = tna

        bc1, bc2, bc3 = st.columns([1,4,2])
        with bc1:
            if st.button("← Back"):
                st.session_state["selected_tna"] = None
                st.rerun()
        with bc2:
            st.markdown(f'<h1 style="margin:0;">{tna_no} — {tna.get("style_name","")}</h1>', unsafe_allow_html=True)
        with bc3:
            risk = shipment_risk(tna)
            st.markdown(f'<div style="padding-top:14px;">{risk_badge(risk)}</div>', unsafe_allow_html=True)

        # Header cards
        st.markdown("---")
        hc1,hc2,hc3,hc4 = st.columns(4)
        lines = tna.get("lines",[])
        done  = sum(1 for ln in lines if ln["status"]=="Completed")
        deld  = sum(1 for ln in lines if ln["status"]=="Delayed")
        pct   = int(done/len(lines)*100) if lines else 0
        del_dt = tna.get("delivery_date","")
        days_left = (date.fromisoformat(del_dt)-date.today()).days if del_dt else 0
        with hc1:
            st.markdown(f'''<div class="card card-left"><div class="sec-label">Order Info</div>
                <div style="font-size:13px;">Buyer: <strong>{tna.get("buyer","")}</strong></div>
                <div style="font-size:13px;">SO: <strong>{tna.get("so_no","—")}</strong></div>
                <div style="font-size:13px;">PO: <strong>{tna.get("po_number","—")}</strong></div>
                <div style="font-size:13px;">Merchant: <strong>{tna.get("merchandiser","—")}</strong></div>
            </div>''', unsafe_allow_html=True)
        with hc2:
            d_col = "#ef4444" if days_left < 7 else "#d97706" if days_left < 15 else "#059669"
            st.markdown(f'''<div class="card card-left-blue"><div class="sec-label">Dates</div>
                <div style="font-size:13px;">Delivery: <strong style="color:{d_col};">{del_dt}</strong></div>
                <div style="font-size:13px;">Ex-Factory: <strong>{tna.get("exfactory_date","—")}</strong></div>
                <div style="font-size:13px;">Shipment: <strong>{tna.get("shipment_date","—")}</strong></div>
                <div style="font-size:14px;font-weight:800;color:{d_col};">{days_left} days left</div>
            </div>''', unsafe_allow_html=True)
        with hc3:
            st.markdown(f'''<div class="card card-left-green"><div class="sec-label">Progress</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;font-size:13px;">
                    <div>Total<br><strong>{len(lines)}</strong></div>
                    <div>Done<br><strong style="color:#059669">{done}</strong></div>
                    <div>Delayed<br><strong style="color:#ef4444">{deld}</strong></div>
                    <div>Progress<br><strong style="color:#c8a96e">{pct}%</strong></div>
                </div>
                <div class="prog-wrap" style="margin-top:8px;"><div class="prog-fill prog-fill-green" style="width:{pct}%;"></div></div>
            </div>''', unsafe_allow_html=True)
        with hc4:
            st.markdown(f'''<div class="card card-left-red"><div class="sec-label">Details</div>
                <div style="font-size:13px;">Style: <strong>{tna.get("style","—")}</strong></div>
                <div style="font-size:13px;">Season: <strong>{tna.get("season","—")}</strong></div>
                <div style="font-size:13px;">Order Qty: <strong>{tna.get("order_qty","—")}</strong></div>
                <div style="font-size:13px;">Priority: <strong>{tna.get("priority","Normal")}</strong></div>
            </div>''', unsafe_allow_html=True)

        st.markdown("---")

        # Activity lines
        act_tab1, act_tab2 = st.tabs(["📋 All Activities", "✏️ Update Activities"])

        with act_tab1:
            f_grp = st.selectbox("Filter by Group", ["All"] + TNA_ACTIVITY_GROUPS, key="tna_det_grp")
            f_sts = st.selectbox("Filter by Status", ["All"] + TNA_STATUS_OPTIONS, key="tna_det_sts")

            view_rows = []
            for ln in lines:
                if f_grp != "All" and ln["group"] != f_grp: continue
                if f_sts != "All" and ln["status"] != f_sts: continue
                delay_str = f"🔴 {ln['delay_days']}d" if ln["delay_days"] > 0 else "—"
                view_rows.append({
                    "Sr":           ln["sr"],
                    "Activity":     ln["activity"],
                    "Group":        ln["group"],
                    "Responsible":  ln.get("responsible","—"),
                    "Planned Start":ln["planned_start"],
                    "Planned End":  ln["planned_end"],
                    "Actual Start": ln.get("actual_start","—"),
                    "Actual End":   ln.get("actual_end","—"),
                    "Status":       ln["status"],
                    "Delay":        delay_str,
                    "Depends On":   ln.get("depends_on","—"),
                })
            if view_rows:
                st.dataframe(pd.DataFrame(view_rows), use_container_width=True, hide_index=True)

        with act_tab2:
            f_grp2 = st.selectbox("Filter by Group", ["All"] + TNA_ACTIVITY_GROUPS, key="tna_upd_grp")
            show_delayed_only = st.checkbox("Show only Delayed/Pending", key="tna_show_del")

            for i, ln in enumerate(lines):
                if f_grp2 != "All" and ln["group"] != f_grp2: continue
                if show_delayed_only and ln["status"] in ["Completed","Cancelled"]: continue

                status = ln["status"]
                is_del = status == "Delayed"
                is_done = status == "Completed"
                icon = "✅" if is_done else "🔴" if is_del else "🟡" if status=="In Progress" else "⚪"

                with st.expander(
                    f"{icon} [{ln['sr']}] {ln['activity']} ({ln['group']}) | Due: {ln['planned_end']} | {status}" +
                    (f" | 🔴 {ln['delay_days']}d late" if ln['delay_days'] > 0 else ""),
                    expanded=is_del
                ):
                    uc1,uc2,uc3 = st.columns(3)
                    with uc1:
                        st.markdown(f'<div style="font-size:12px;color:#94a3b8;">Planned</div><div style="font-size:13px;">{ln["planned_start"]} → {ln["planned_end"]}</div>', unsafe_allow_html=True)
                        new_status = st.selectbox("Status", TNA_STATUS_OPTIONS,
                                                   index=TNA_STATUS_OPTIONS.index(status) if status in TNA_STATUS_OPTIONS else 0,
                                                   key=f"tna_sts_{tna_no}_{i}")
                        new_resp   = st.text_input("Responsible", value=ln.get("responsible",""), key=f"tna_resp_{tna_no}_{i}")
                        new_backup = st.text_input("Backup Person", value=ln.get("backup",""), key=f"tna_bkp_{tna_no}_{i}")
                    with uc2:
                        new_act_start = st.date_input("Actual Start Date",
                            value=date.fromisoformat(ln["actual_start"]) if ln.get("actual_start") else None,
                            key=f"tna_as_{tna_no}_{i}")
                        new_act_end = st.date_input("Actual End Date",
                            value=date.fromisoformat(ln["actual_end"]) if ln.get("actual_end") else None,
                            key=f"tna_ae_{tna_no}_{i}")
                    with uc3:
                        new_delay_reason = st.text_input("Delay Reason", value=ln.get("delay_reason",""), key=f"tna_dr_{tna_no}_{i}")
                        new_remarks = st.text_area("Remarks", value=ln.get("remarks",""), height=60, key=f"tna_rk_{tna_no}_{i}")

                        if st.button("💾 Save", key=f"tna_sv_{tna_no}_{i}"):
                            old_ln = dict(ln)
                            new_actual_end_str = str(new_act_end) if new_act_end else ""

                            # Cascade delay check
                            if new_actual_end_str and new_actual_end_str > ln["planned_end"]:
                                SS["tna_list"][tna_no] = cascade_delays(tna, ln["activity"], new_actual_end_str)
                                tna = SS["tna_list"][tna_no]
                                st.warning(f"⚠️ Delay cascade applied — dependent activities shifted!")

                            # Update line
                            SS["tna_list"][tna_no]["lines"][i].update({
                                "status":       new_status,
                                "responsible":  new_resp,
                                "backup":       new_backup,
                                "actual_start": str(new_act_start) if new_act_start else "",
                                "actual_end":   new_actual_end_str,
                                "delay_reason": new_delay_reason,
                                "remarks":      new_remarks,
                            })
                            # Audit trail
                            SS["tna_list"][tna_no]["lines"][i]["history"].append({
                                "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
                                "old_status": old_ln["status"],
                                "new_status": new_status,
                                "old_end": old_ln.get("actual_end",""),
                                "new_end": new_actual_end_str,
                            })
                            save_data()
                            st.success("✅ Saved!")
                            st.rerun()

    # ── List View ─────────────────────────────────────────────────────────────
    else:
        st.markdown('<h1>TNA List</h1>', unsafe_allow_html=True)

        tna_list = SS.get("tna_list", {})

        # Filters
        lf1,lf2,lf3,lf4,lf5 = st.columns(5)
        with lf1: fl_buyer  = st.text_input("🔍 Buyer", key="tl_buyer")
        with lf2: fl_status = st.selectbox("Status", ["All","Active","Completed","On Hold"], key="tl_sts")
        with lf3: fl_pri    = st.selectbox("Priority", ["All"]+TNA_PRIORITY, key="tl_pri")
        with lf4: fl_risk   = st.selectbox("Risk", ["All","High Risk","Moderate Risk","Safe"], key="tl_risk")
        with lf5: fl_search = st.text_input("🔍 TNA # / Style", key="tl_search")

        if not tna_list:
            st.markdown('<div class="warn-box">Koi TNA nahi hai. "➕ Create TNA" se banao.</div>', unsafe_allow_html=True)
        else:
            for tna_no, tna in SS["tna_list"].items():
                tna = recalc_tna(tna)
                SS["tna_list"][tna_no] = tna

                risk = shipment_risk(tna)
                if fl_buyer  and fl_buyer.lower() not in tna.get("buyer","").lower(): continue
                if fl_status != "All" and tna.get("status","") != fl_status: continue
                if fl_pri    != "All" and tna.get("priority","") != fl_pri: continue
                if fl_risk   != "All" and risk != fl_risk: continue
                if fl_search and fl_search.lower() not in tna_no.lower() and fl_search.lower() not in tna.get("style_name","").lower(): continue

                lines    = tna.get("lines",[])
                done     = sum(1 for ln in lines if ln["status"]=="Completed")
                delayed  = sum(1 for ln in lines if ln["status"]=="Delayed")
                due_tod  = sum(1 for ln in lines if ln.get("planned_end")==str(date.today()) and ln["status"] not in ["Completed","Cancelled"])
                pct      = int(done/len(lines)*100) if lines else 0
                del_dt   = tna.get("delivery_date","")
                days_l   = (date.fromisoformat(del_dt)-date.today()).days if del_dt else 0
                d_col    = "#ef4444" if days_l<7 else "#d97706" if days_l<15 else "#64748b"

                r1,r2,r3,r4,r5,r6,r7,r8 = st.columns([1.2,2,1.2,1.2,1,1,1,0.8])
                with r1: st.markdown(f'<div style="padding-top:8px;font-family:JetBrains Mono,monospace;font-size:12px;font-weight:700;color:#c8a96e;">{tna_no}</div>', unsafe_allow_html=True)
                with r2: st.markdown(f'<div style="padding-top:6px;"><div style="font-size:13px;font-weight:600;">{tna.get("style_name","")}</div><div style="font-size:11px;color:#94a3b8;">{tna.get("buyer","")} | {tna.get("so_no","")}</div></div>', unsafe_allow_html=True)
                with r3: st.markdown(f'<div style="padding-top:8px;font-size:12px;">📅 {del_dt}<br><span style="color:{d_col};font-weight:600;">{days_l}d left</span></div>', unsafe_allow_html=True)
                with r4: st.markdown(f'<div style="padding-top:4px;"><div style="font-size:11px;color:#94a3b8;">Progress</div><div class="prog-wrap"><div class="prog-fill" style="width:{pct}%;"></div></div><div style="font-size:11px;">{pct}% ({done}/{len(lines)})</div></div>', unsafe_allow_html=True)
                with r5: st.markdown(f'<div style="padding-top:8px;font-size:12px;">{"🔴 "+str(delayed)+" delayed" if delayed else "🟢 OK"}</div>', unsafe_allow_html=True)
                with r6: st.markdown(f'<div style="padding-top:8px;font-size:12px;">{"🟡 "+str(due_tod)+" due" if due_tod else ""}</div>', unsafe_allow_html=True)
                with r7: st.markdown(f'<div style="padding-top:8px;">{risk_badge(risk)}</div>', unsafe_allow_html=True)
                with r8:
                    if st.button("Open →", key=f"open_tna_{tna_no}", use_container_width=True):
                        st.session_state["selected_tna"] = tna_no
                        st.rerun()
                st.markdown('<hr style="margin:4px 0;border-color:#e2e5ef;">', unsafe_allow_html=True)


# ── TNA TEMPLATES ─────────────────────────────────────────────────────────────
elif nav_tna == "📁 TNA Templates":
    st.markdown('<h1>TNA Templates</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Custom templates banao — buyer-wise ya order-type wise. Standard templates already available hain.</div>', unsafe_allow_html=True)

    tt1, tt2 = st.tabs(["📋 View Templates", "➕ Create Template"])

    with tt1:
        all_tmpls = get_all_templates()
        for tmpl_name, acts in all_tmpls.items():
            is_custom = tmpl_name in SS.get("tna_templates",{})
            with st.expander(f"{'⭐ Custom: ' if is_custom else '📋 Standard: '}{tmpl_name} — {len(acts)} activities"):
                df_t = pd.DataFrame([{"Sr":a["sr"],"Activity":a["activity"],"Group":a["group"],
                                       "Lead Days":a["lead_days"],"Depends On":a.get("depends_on","")} for a in acts])
                st.dataframe(df_t, use_container_width=True, hide_index=True)
                if is_custom:
                    if st.button(f"🗑 Delete '{tmpl_name}'", key=f"del_tmpl_{tmpl_name}"):
                        del SS["tna_templates"][tmpl_name]
                        save_data()
                        st.rerun()

    with tt2:
        st.markdown("#### Create Custom Template")
        new_tmpl_name = st.text_input("Template Name *", key="new_tmpl_name", placeholder="e.g. Myntra Export TNA")

        if "new_tmpl_lines" not in st.session_state:
            st.session_state["new_tmpl_lines"] = []

        # Copy from existing
        base_tmpl = st.selectbox("Start from existing template (optional)",
                                  ["— Start Fresh —"] + list(TNA_DEFAULT_TEMPLATES.keys()),
                                  key="base_tmpl")
        if st.button("📋 Load Base Template") and base_tmpl != "— Start Fresh —":
            st.session_state["new_tmpl_lines"] = [dict(a) for a in TNA_DEFAULT_TEMPLATES[base_tmpl]]
            st.rerun()

        # Add activity
        with st.expander("➕ Add Activity"):
            na1,na2,na3,na4 = st.columns(4)
            with na1: new_act = st.text_input("Activity Name *", key="tmpl_act")
            with na2: new_grp = st.selectbox("Group", TNA_ACTIVITY_GROUPS, key="tmpl_grp")
            with na3: new_ld  = st.number_input("Lead Days", min_value=0, step=1, key="tmpl_ld")
            with na4: new_dep = st.text_input("Depends On", key="tmpl_dep")
            if st.button("➕ Add") and new_act:
                sr = len(st.session_state["new_tmpl_lines"]) + 1
                st.session_state["new_tmpl_lines"].append({
                    "sr":sr,"activity":new_act,"group":new_grp,
                    "lead_days":new_ld,"depends_on":new_dep
                })
                st.rerun()

        if st.session_state["new_tmpl_lines"]:
            df_nl = pd.DataFrame([{"Sr":a["sr"],"Activity":a["activity"],"Group":a["group"],
                                    "Lead Days":a["lead_days"],"Depends On":a["depends_on"]}
                                   for a in st.session_state["new_tmpl_lines"]])
            st.dataframe(df_nl, use_container_width=True, hide_index=True)

            if st.button("💾 Save Template") and new_tmpl_name:
                SS["tna_templates"][new_tmpl_name] = st.session_state["new_tmpl_lines"].copy()
                st.session_state["new_tmpl_lines"] = []
                save_data()
                st.success(f"✅ Template '{new_tmpl_name}' saved!")
                st.rerun()


# ── TNA REPORTS ───────────────────────────────────────────────────────────────
elif nav_tna == "📊 TNA Reports":
    st.markdown('<h1>TNA Reports</h1>', unsafe_allow_html=True)

    tna_list = SS.get("tna_list", {})
    for k in tna_list: tna_list[k] = recalc_tna(tna_list[k])

    rep = st.selectbox("Report select karo", [
        "1. Buyer Wise TNA Report",
        "2. Order Wise Progress Report",
        "3. Department Wise Pending Report",
        "4. Delayed Activities Report",
        "5. Shipment Risk Report",
        "6. Completed vs Pending Report",
        "7. Responsible Person Wise Report",
    ], key="tna_rep_sel")

    if not tna_list:
        st.markdown('<div class="warn-box">Koi TNA data nahi hai.</div>', unsafe_allow_html=True)
    elif rep.startswith("1"):
        buyer_data = {}
        for tna_no, tna in tna_list.items():
            b = tna.get("buyer","Unknown")
            if b not in buyer_data: buyer_data[b] = []
            lines = tna.get("lines",[])
            buyer_data[b].append({
                "TNA #":tna_no,"Style":tna.get("style_name",""),
                "Delivery":tna.get("delivery_date",""),
                "Progress%":int(sum(1 for ln in lines if ln["status"]=="Completed")/len(lines)*100) if lines else 0,
                "Delayed":sum(1 for ln in lines if ln["status"]=="Delayed"),
                "Risk":shipment_risk(tna),
            })
        for buyer, rows in buyer_data.items():
            with st.expander(f"🛍️ {buyer} — {len(rows)} orders"):
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    elif rep.startswith("2"):
        rows = []
        for tna_no, tna in tna_list.items():
            lines = tna.get("lines",[])
            rows.append({
                "TNA #":tna_no,"Style":tna.get("style_name",""),"Buyer":tna.get("buyer",""),
                "Total":len(lines),
                "Completed":sum(1 for ln in lines if ln["status"]=="Completed"),
                "In Progress":sum(1 for ln in lines if ln["status"]=="In Progress"),
                "Delayed":sum(1 for ln in lines if ln["status"]=="Delayed"),
                "Not Started":sum(1 for ln in lines if ln["status"]=="Not Started"),
                "Progress%":int(sum(1 for ln in lines if ln["status"]=="Completed")/len(lines)*100) if lines else 0,
                "Delivery":tna.get("delivery_date",""), "Risk":shipment_risk(tna),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    elif rep.startswith("3"):
        dept_rows = {}
        for tna_no, tna in tna_list.items():
            for ln in tna.get("lines",[]):
                if ln["status"] not in ["Completed","Cancelled"]:
                    g = ln["group"]
                    if g not in dept_rows: dept_rows[g] = []
                    dept_rows[g].append({"TNA":tna_no,"Style":tna.get("style_name",""),
                        "Activity":ln["activity"],"Due":ln["planned_end"],"Status":ln["status"],
                        "Responsible":ln.get("responsible","—"),"Delay":ln["delay_days"]})
        for dept, rows in sorted(dept_rows.items()):
            st.markdown(f"**{dept}** — {len(rows)} pending")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    elif rep.startswith("4"):
        rows = []
        for tna_no, tna in tna_list.items():
            for ln in tna.get("lines",[]):
                if ln["status"] == "Delayed":
                    rows.append({"TNA":tna_no,"Buyer":tna.get("buyer",""),
                        "Style":tna.get("style_name",""),"Activity":ln["activity"],
                        "Group":ln["group"],"Planned End":ln["planned_end"],
                        "Delay Days":ln["delay_days"],"Responsible":ln.get("responsible","—"),
                        "Reason":ln.get("delay_reason","—")})
        if rows:
            rows.sort(key=lambda x: x["Delay Days"], reverse=True)
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="ok-box">Koi delayed activity nahi hai!</div>', unsafe_allow_html=True)

    elif rep.startswith("5"):
        rows = []
        for tna_no, tna in tna_list.items():
            risk = shipment_risk(tna)
            if risk != "Safe":
                del_dt = tna.get("delivery_date","")
                days_l = (date.fromisoformat(del_dt)-date.today()).days if del_dt else 0
                delayed_acts = [ln["activity"] for ln in tna.get("lines",[]) if ln["status"]=="Delayed"]
                rows.append({"TNA":tna_no,"Style":tna.get("style_name",""),
                    "Buyer":tna.get("buyer",""),"Delivery":del_dt,
                    "Days Left":days_l,"Risk":risk,
                    "Delayed Activities":", ".join(delayed_acts[:3])})
        if rows:
            rows.sort(key=lambda x: x["Days Left"])
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="ok-box">Koi shipment risk nahi hai!</div>', unsafe_allow_html=True)

    elif rep.startswith("6"):
        total_acts = sum(len(tna.get("lines",[])) for tna in tna_list.values())
        comp_acts  = sum(sum(1 for ln in tna.get("lines",[]) if ln["status"]=="Completed") for tna in tna_list.values())
        pend_acts  = total_acts - comp_acts
        st.markdown(f'''<div class="card" style="padding:20px;">
            <div style="display:flex;gap:32px;font-size:16px;">
                <div>Total Activities: <strong>{total_acts}</strong></div>
                <div>Completed: <strong style="color:#059669">{comp_acts}</strong></div>
                <div>Pending: <strong style="color:#ef4444">{pend_acts}</strong></div>
                <div>Completion %: <strong style="color:#c8a96e">{int(comp_acts/total_acts*100) if total_acts else 0}%</strong></div>
            </div>
        </div>''', unsafe_allow_html=True)

    elif rep.startswith("7"):
        resp_rows = {}
        for tna_no, tna in tna_list.items():
            for ln in tna.get("lines",[]):
                resp = ln.get("responsible","Unassigned") or "Unassigned"
                if resp not in resp_rows: resp_rows[resp] = {"pending":0,"completed":0,"delayed":0}
                if ln["status"] == "Completed": resp_rows[resp]["completed"] += 1
                elif ln["status"] == "Delayed":  resp_rows[resp]["delayed"]   += 1
                else:                             resp_rows[resp]["pending"]   += 1
        rows = [{"Person":k,"Pending":v["pending"],"Completed":v["completed"],"Delayed":v["delayed"]} for k,v in resp_rows.items()]
        if rows:
            st.dataframe(pd.DataFrame(rows).sort_values("Delayed",ascending=False), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PURCHASE MODULE — PR / PO / JWO / GRN
# ═══════════════════════════════════════════════════════════════════════════════

PR_STATUS  = ["Draft","Pending Approval","Approved","Rejected","PO Created","JWO Created","Closed"]
PO_STATUS  = ["Draft","Sent to Supplier","Confirmed","Partial Received","Received","Closed","Cancelled"]
JWO_STATUS = ["Draft","Issued to Processor","In Process","Partial Received","Received","Closed","Cancelled"]
GRN_STATUS = ["Draft","Verified","Posted"]

def next_pr():
    n = f"PR-{SS['pr_counter']:04d}"; SS["pr_counter"] += 1; return n
def next_po():
    n = f"PO-{SS['po_counter']:04d}"; SS["po_counter"] += 1; return n
def next_jwo():
    n = f"JWO-{SS['jwo_counter']:04d}"; SS["jwo_counter"] += 1; return n
def next_grn():
    n = f"GRN-{SS['grn_counter']:04d}"; SS["grn_counter"] += 1; return n

def pur_badge(status):
    colors = {
        "Draft":"#64748b","Pending Approval":"#8b5cf6","Approved":"#059669",
        "Rejected":"#ef4444","PO Created":"#0ea5e9","JWO Created":"#0ea5e9",
        "Closed":"#475569","Sent to Supplier":"#d97706","Confirmed":"#059669",
        "Partial Received":"#d97706","Received":"#059669","Cancelled":"#ef4444",
        "Issued to Processor":"#d97706","In Process":"#d97706","Posted":"#059669",
        "Verified":"#0ea5e9",
    }
    bg = {
        "Draft":"#f1f5f9","Pending Approval":"#ede9fe","Approved":"#d1fae5",
        "Rejected":"#fee2e2","PO Created":"#dbeafe","JWO Created":"#dbeafe",
        "Closed":"#f1f5f9","Sent to Supplier":"#fef3c7","Confirmed":"#d1fae5",
        "Partial Received":"#fef3c7","Received":"#d1fae5","Cancelled":"#fee2e2",
        "Issued to Processor":"#fef3c7","In Process":"#fef3c7","Posted":"#d1fae5",
        "Verified":"#dbeafe",
    }
    c = colors.get(status,"#64748b"); b = bg.get(status,"#f1f5f9")
    return f'<span style="background:{b};color:{c};padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;">{status}</span>'


# ── PURCHASE DASHBOARD ────────────────────────────────────────────────────────
if nav_pur == "🛒 Purchase Dashboard":
    st.markdown('<h1>Purchase Dashboard</h1>', unsafe_allow_html=True)

    pr_list  = SS.get("pr_list", {})
    po_list  = SS.get("po_list", {})
    jwo_list = SS.get("jwo_list", {})
    grn_list = SS.get("grn_list", {})

    # KPIs
    open_prs  = sum(1 for p in pr_list.values()  if p.get("status") in ["Pending Approval","Draft"])
    open_pos  = sum(1 for p in po_list.values()  if p.get("status") not in ["Received","Closed","Cancelled"])
    open_jwos = sum(1 for p in jwo_list.values() if p.get("status") not in ["Received","Closed","Cancelled"])
    pending_grn = sum(1 for p in po_list.values() if p.get("status") in ["Confirmed","Partial Received"]) + \
                  sum(1 for p in jwo_list.values() if p.get("status") in ["Issued to Processor","In Process","Partial Received"])

    c1,c2,c3,c4 = st.columns(4)
    for col, val, label, cls in [
        (c1, open_prs,   "Open PRs",       "amber" if open_prs else ""),
        (c2, open_pos,   "Open POs",       ""),
        (c3, open_jwos,  "Open JWOs",      ""),
        (c4, pending_grn,"Pending Receipt", "amber" if pending_grn else ""),
    ]:
        with col:
            st.markdown(f'<div class="metric-box {cls}"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    pd1, pd2, pd3 = st.columns(3)

    with pd1:
        st.markdown("#### 📋 Recent PRs")
        if pr_list:
            for pr_no, pr in list(pr_list.items())[-5:]:
                st.markdown(f'<div class="card" style="padding:8px 12px;margin:3px 0;"><div style="display:flex;justify-content:space-between;"><span style="font-family:monospace;font-size:12px;color:#c8a96e;">{pr_no}</span>{pur_badge(pr.get("status",""))}</div><div style="font-size:12px;margin-top:2px;">{len(pr.get("lines",[]))} items | {pr.get("so_ref","—")}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">Koi PR nahi.</div>', unsafe_allow_html=True)

    with pd2:
        st.markdown("#### 📦 Open POs")
        if po_list:
            for po_no, po in po_list.items():
                if po.get("status") not in ["Received","Closed","Cancelled"]:
                    st.markdown(f'<div class="card" style="padding:8px 12px;margin:3px 0;"><div style="display:flex;justify-content:space-between;"><span style="font-family:monospace;font-size:12px;color:#c8a96e;">{po_no}</span>{pur_badge(po.get("status",""))}</div><div style="font-size:12px;">{po.get("supplier_name","—")} | Due: {po.get("delivery_date","—")}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">Koi open PO nahi.</div>', unsafe_allow_html=True)

    with pd3:
        st.markdown("#### 🔧 Open JWOs")
        if jwo_list:
            for jwo_no, jwo in jwo_list.items():
                if jwo.get("status") not in ["Received","Closed","Cancelled"]:
                    st.markdown(f'<div class="card" style="padding:8px 12px;margin:3px 0;"><div style="display:flex;justify-content:space-between;"><span style="font-family:monospace;font-size:12px;color:#c8a96e;">{jwo_no}</span>{pur_badge(jwo.get("status",""))}</div><div style="font-size:12px;">{jwo.get("processor_name","—")} | {jwo.get("material_name","—")}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">Koi open JWO nahi.</div>', unsafe_allow_html=True)


# ── PURCHASE REQUISITIONS ─────────────────────────────────────────────────────
elif nav_pur == "📋 Purchase Requisitions":
    st.markdown('<h1>Purchase Requisitions</h1>', unsafe_allow_html=True)

    if "selected_pr" not in st.session_state:
        st.session_state["selected_pr"] = None

    pr_tab1, pr_tab2, pr_tab3 = st.tabs(["📋 PR List", "➕ Create PR", "🔄 From MRP"])

    with pr_tab3:
        st.markdown("#### Generate PRs from MRP")
        mrp_result = SS.get("mrp_result", {})
        if not mrp_result:
            st.markdown('<div class="warn-box">Pehle MRP run karo.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box">MRP results se materials categorize karo — RM/Accessories ke liye Purchase PR, SFG ke liye Job Work ya Purchase choose karo.</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            so_ref = st.selectbox("SO Reference", [""] + SS.get("mrp_so_list",[]), key="pr_so_ref")
            req_date = st.date_input("Required By Date", value=date.today() + timedelta(days=14), key="pr_req_date")

            # Categorize materials
            rm_items  = {c: m for c,m in mrp_result.items() if m["type"] in ["Raw Material (RM)","Accessories"] and m["net_req"] > 0}
            sfg_items = {c: m for c,m in mrp_result.items() if m["type"] == "Semi Finished Goods (SFG)" and m["net_req"] > 0}

            if rm_items:
                st.markdown("#### 🛒 Purchase PR — Raw Materials & Accessories")
                rm_rows = []
                for code, mat in rm_items.items():
                    rm_rows.append({
                        "Material Code": code, "Material Name": mat["name"],
                        "Type": mat["type"], "Required": mat["net_req"], "Unit": mat["unit"]
                    })
                st.dataframe(pd.DataFrame(rm_rows), use_container_width=True, hide_index=True)

            if sfg_items:
                st.markdown("#### 🔧 SFG Materials — Choose Purchase or Job Work")
                sfg_choices = {}
                boms_data   = st.session_state.get("boms", {})

                for code, mat in sfg_items.items():
                    # Get input materials from BOM
                    bom_lines = [l for l in boms_data.get(code,{}).get("lines",[]) if l.get("line_type") != "Process"]

                    st.markdown(f'''<div class="card card-left" style="padding:12px 16px;margin:6px 0;">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                            <div>
                                <div style="font-size:14px;font-weight:700;">{code} — {mat["name"]}</div>
                                <div style="font-size:12px;color:#64748b;">Required: <strong>{mat["net_req"]} {mat["unit"]}</strong></div>
                                {"".join([f'<span class="tag" style="margin-top:4px;">Input: {l.get("item_code","")} ({l.get("qty",0)} {l.get("unit","")})</span>' for l in bom_lines]) if bom_lines else '<span class="tag tag-red">BOM mein input material define nahi</span>'}
                            </div>
                        </div>
                    </div>''', unsafe_allow_html=True)

                    ac1, ac2 = st.columns([2,3])
                    with ac1:
                        choice = st.radio("Action *", ["Job Work", "Direct Purchase"],
                                          key=f"sfg_choice_{code}", horizontal=True)
                    with ac2:
                        if choice == "Job Work":
                            processors = {k:v for k,v in SS.get("suppliers",{}).items() if "Job Work" in v.get("type","")}
                            if processors:
                                proc = st.selectbox("Processor / Printer",
                                                     [""] + [f"{k} – {v['name']}" for k,v in processors.items()],
                                                     key=f"sfg_proc_{code}")
                            else:
                                st.markdown('<div class="warn-box" style="font-size:12px;">Supplier Master mein Job Work type ka supplier add karo.</div>', unsafe_allow_html=True)
                            if bom_lines:
                                st.markdown('<div class="info-box" style="font-size:12px;">✅ Input materials (Grey Fabric etc.) ka Purchase PR bhi automatically ban jaayega.</div>', unsafe_allow_html=True)
                    sfg_choices[code] = choice
                    st.markdown("---")

            if st.button("✅ Generate PRs", use_container_width=False):
                pr_lines_purchase = []
                pr_lines_jw = {}
                # input materials for JW items (to be purchased)
                jw_input_lines = []

                boms_data = st.session_state.get("boms", {})

                # RM/Accessories → Purchase PR
                for code, mat in rm_items.items():
                    pr_lines_purchase.append({
                        "material_code": code, "material_name": mat["name"],
                        "material_type": mat["type"], "required_qty": mat["net_req"],
                        "po_created_qty": 0, "received_qty": 0, "unit": mat["unit"],
                        "so_ref": so_ref, "mrp_req": mat["total_req"],
                    })

                # SFG → Purchase or JWO
                for code, mat in sfg_items.items():
                    choice = sfg_choices.get(code, "Direct Purchase")
                    if choice == "Direct Purchase":
                        pr_lines_purchase.append({
                            "material_code": code, "material_name": mat["name"],
                            "material_type": mat["type"], "required_qty": mat["net_req"],
                            "received_qty": 0, "unit": mat["unit"],
                            "so_ref": so_ref, "mrp_req": mat["total_req"],
                        })
                    else:
                        proc_key  = st.session_state.get(f"sfg_proc_{code}", "")
                        proc_code = proc_key.split(" – ")[0] if " – " in proc_key else ""
                        pr_lines_jw[code] = {
                            "material_code":  code,
                            "material_name":  mat["name"],
                            "required_qty":   mat["net_req"],
                            "unit":           mat["unit"],
                            "processor":      proc_code,
                            "so_ref":         so_ref,
                        }
                        # Auto-add input materials (from BOM) to Purchase PR
                        bom_input_lines = [l for l in boms_data.get(code,{}).get("lines",[])
                                           if l.get("line_type") != "Process"]
                        items_data = st.session_state.get("items", {})
                        for bl in bom_input_lines:
                            in_code = bl.get("item_code","")
                            in_qty  = round(float(bl.get("qty",0)) * mat["net_req"], 3)
                            in_item = items_data.get(in_code, {})
                            # Only add if not already in RM list (avoid duplicate)
                            already_in_rm = any(l["material_code"] == in_code for l in pr_lines_purchase + jw_input_lines)
                            if in_code and in_qty > 0 and not already_in_rm:
                                jw_input_lines.append({
                                    "material_code":  in_code,
                                    "material_name":  in_item.get("name", in_code),
                                    "material_type":  in_item.get("item_type","Raw Material (RM)"),
                                    "required_qty":   in_qty,
                                    "received_qty":   0,
                                    "unit":           bl.get("unit",""),
                                    "so_ref":         so_ref,
                                    "for_jwo":        code,
                                    "mrp_req":        in_qty,
                                })

                # Merge jw_input_lines into purchase lines
                pr_lines_purchase.extend(jw_input_lines)

                # Create Purchase PR
                if pr_lines_purchase:
                    pr_no = next_pr()
                    SS["pr_list"][pr_no] = {
                        "pr_no": pr_no, "pr_date": str(date.today()),
                        "pr_type": "Purchase", "so_ref": so_ref,
                        "required_date": str(req_date),
                        "lines": pr_lines_purchase,
                        "status": "Pending Approval",
                        "created_from": "MRP",
                        "created_at": datetime.now().isoformat(),
                    }
                    st.success(f"✅ Purchase PR **{pr_no}** created — {len(pr_lines_purchase)} items (including Job Work input materials)")

                # Create JW PRs
                for code, jw_data in pr_lines_jw.items():
                    pr_no = next_pr()
                    SS["pr_list"][pr_no] = {
                        "pr_no": pr_no, "pr_date": str(date.today()),
                        "pr_type": "Job Work", "so_ref": so_ref,
                        "required_date": str(req_date),
                        "lines": [jw_data],
                        "status": "Pending Approval",
                        "created_from": "MRP",
                        "processor": jw_data.get("processor",""),
                        "created_at": datetime.now().isoformat(),
                    }
                    st.success(f"✅ Job Work PR **{pr_no}** created for {jw_data['material_name']}")

                save_data()
                st.rerun()

    with pr_tab2:
        st.markdown("#### Manual PR Create")
        items_data = st.session_state.get("items", {})

        mp1, mp2 = st.columns(2)
        with mp1:
            pr_type_manual = st.selectbox("PR Type", ["Purchase","Job Work"], key="pr_m_type")
            pr_so_ref      = st.selectbox("SO Reference (optional)", [""]+list(SS.get("so_list",{}).keys()), key="pr_m_so")
            pr_req_dt      = st.date_input("Required Date", value=date.today()+timedelta(days=14), key="pr_m_dt")
        with mp2:
            pr_remarks = st.text_area("Remarks", height=80, key="pr_m_rem")

        if "manual_pr_lines" not in st.session_state:
            st.session_state["manual_pr_lines"] = []

        with st.expander("➕ Add Material Line"):
            ml1, ml2, ml3 = st.columns(3)
            with ml1:
                all_items_pr = {k: v["name"] for k,v in items_data.items()}
                pr_mat = st.selectbox("Material *", [""] + list(all_items_pr.keys()),
                                       format_func=lambda x: f"{x} – {all_items_pr.get(x,'')}" if x else "Select",
                                       key="pr_mat_sel")
            with ml2:
                pr_qty  = st.number_input("Required Qty *", min_value=0.0, step=1.0, key="pr_qty")
                pr_unit = st.selectbox("Unit", UNITS, key="pr_unit")
            with ml3:
                pr_remarks_line = st.text_input("Remarks", key="pr_line_rem")

            if st.button("➕ Add Line") and pr_mat and pr_qty > 0:
                st.session_state["manual_pr_lines"].append({
                    "material_code": pr_mat,
                    "material_name": items_data.get(pr_mat,{}).get("name", pr_mat),
                    "material_type": items_data.get(pr_mat,{}).get("item_type",""),
                    "required_qty": pr_qty, "received_qty": 0,
                    "unit": pr_unit, "so_ref": pr_so_ref,
                    "remarks": pr_remarks_line,
                })
                st.rerun()

        if st.session_state["manual_pr_lines"]:
            for idx, ln in enumerate(st.session_state["manual_pr_lines"]):
                lc1,lc2,lc3,lc4 = st.columns([2,2,1,0.5])
                with lc1: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>{ln["material_code"]}</strong> — {ln["material_name"]}</div>', unsafe_allow_html=True)
                with lc2: st.markdown(f'<div style="padding-top:8px;font-size:13px;">{ln["required_qty"]} {ln["unit"]}</div>', unsafe_allow_html=True)
                with lc3: st.markdown(f'<div style="padding-top:8px;font-size:12px;color:#64748b;">{ln["material_type"]}</div>', unsafe_allow_html=True)
                with lc4:
                    if st.button("🗑", key=f"del_pr_line_{idx}"):
                        st.session_state["manual_pr_lines"].pop(idx); st.rerun()
                st.markdown('<hr style="margin:2px 0;">', unsafe_allow_html=True)

            if st.button("💾 Save PR", use_container_width=False):
                pr_no = next_pr()
                SS["pr_list"][pr_no] = {
                    "pr_no": pr_no, "pr_date": str(date.today()),
                    "pr_type": pr_type_manual, "so_ref": pr_so_ref,
                    "required_date": str(pr_req_dt),
                    "lines": st.session_state["manual_pr_lines"].copy(),
                    "status": "Pending Approval",
                    "created_from": "Manual",
                    "remarks": pr_remarks,
                    "created_at": datetime.now().isoformat(),
                }
                st.session_state["manual_pr_lines"] = []
                save_data()
                st.success(f"✅ {pr_no} created!")
                st.rerun()

    with pr_tab1:
        # Filters
        pf1, pf2, pf3 = st.columns(3)
        with pf1: pf_type   = st.selectbox("Type", ["All","Purchase","Job Work"], key="prl_type")
        with pf2: pf_status = st.selectbox("Status", ["All"]+PR_STATUS, key="prl_sts")
        with pf3: pf_search = st.text_input("🔍 PR # / SO", key="prl_search")

        pr_list = SS.get("pr_list", {})
        if not pr_list:
            st.markdown('<div class="warn-box">Koi PR nahi hai. "From MRP" tab se generate karo.</div>', unsafe_allow_html=True)
        else:
            for pr_no, pr in reversed(list(pr_list.items())):
                if pf_type   != "All" and pr.get("pr_type","") != pf_type: continue
                if pf_status != "All" and pr.get("status","")  != pf_status: continue
                if pf_search and pf_search.lower() not in pr_no.lower() and pf_search.lower() not in pr.get("so_ref","").lower(): continue

                # Calculate pending qty across all lines
                total_req  = sum(ln.get("required_qty",0) for ln in pr.get("lines",[]))
                total_po   = sum(ln.get("po_created_qty",0) for ln in pr.get("lines",[]))
                total_pend = max(0, total_req - total_po)

                with st.expander(
                    f"{'📦' if pr.get('pr_type')=='Purchase' else '🔧'} {pr_no} | {pr.get('pr_type','')} | SO: {pr.get('so_ref','—')} | {len(pr.get('lines',[]))} items | Pending: {total_pend:.0f}",
                    expanded=False
                ):
                    # Header
                    ph1, ph2, ph3, ph4 = st.columns(4)
                    with ph1: st.markdown(f'<div class="sec-label">PR Info</div><div style="font-size:13px;">Date: {pr.get("pr_date","")}<br>Req By: {pr.get("required_date","")}</div>', unsafe_allow_html=True)
                    with ph2: st.markdown(f'<div class="sec-label">Source</div><div style="font-size:13px;">SO: {pr.get("so_ref","—")}<br>From: {pr.get("created_from","")}</div>', unsafe_allow_html=True)
                    with ph3: st.markdown(f'<div class="sec-label">Status</div>{pur_badge(pr.get("status",""))}', unsafe_allow_html=True)
                    with ph4:
                        if pr.get("status") == "Pending Approval":
                            ap1,ap2 = st.columns(2)
                            with ap1:
                                if st.button("✅ Approve", key=f"apr_{pr_no}", use_container_width=True):
                                    SS["pr_list"][pr_no]["status"] = "Approved"
                                    save_data(); st.rerun()
                            with ap2:
                                if st.button("❌ Reject", key=f"rej_{pr_no}", use_container_width=True):
                                    SS["pr_list"][pr_no]["status"] = "Rejected"
                                    save_data(); st.rerun()

                    st.markdown("---")

                    # Lines table with pending qty
                    st.markdown("**PR Lines — Pending Qty:**")
                    line_rows = []
                    for ln in pr.get("lines",[]):
                        req  = ln.get("required_qty",0)
                        done = ln.get("po_created_qty",0)
                        pend = max(0, req - done)
                        line_rows.append({
                            "Material":      f"{ln['material_code']} – {ln['material_name']}",
                            "Type":          ln.get("material_type",""),
                            "Required Qty":  req,
                            "PO Created":    done,
                            "Pending":       pend,
                            "Unit":          ln.get("unit",""),
                        })
                    st.dataframe(pd.DataFrame(line_rows), use_container_width=True, hide_index=True)

                    # Create PO/JWO inline
                    if pr.get("status") == "Approved" and total_pend > 0:
                        st.markdown("---")
                        if pr.get("pr_type") == "Purchase":
                            st.markdown("#### 📦 Create Purchase Order from this PR")
                            suppliers = SS.get("suppliers",{})
                            # Group pending lines by material type
                            pending_lines = []
                            for i, ln in enumerate(pr.get("lines",[])):
                                req  = ln.get("required_qty",0)
                                done = ln.get("po_created_qty",0)
                                pend = max(0, req - done)
                                if pend > 0:
                                    pending_lines.append((i, ln, pend))

                            if not pending_lines:
                                st.markdown('<div class="ok-box">Saari lines ke liye PO ban chuka hai.</div>', unsafe_allow_html=True)
                            else:
                                # Get unique material types
                                mat_types = list(dict.fromkeys(ln.get("material_type","Other") for _,ln,_ in pending_lines))
                                supp_opts = [""] + [f"{k} – {v['name']}" for k,v in suppliers.items() if "Job Work" not in v.get("type","")]

                                st.markdown(f'<div class="info-box">💡 Alag suppliers ke liye alag PO banao — neeche material type wise grouped hain.</div>', unsafe_allow_html=True)

                                # Common delivery & payment
                                cd1,cd2 = st.columns(2)
                                with cd1: inline_del = st.date_input("Delivery Date", value=date.today()+timedelta(days=14), key=f"inline_del_{pr_no}")
                                with cd2: inline_pay = st.selectbox("Payment Terms", SS.get("payment_terms",[""]), key=f"inline_pay_{pr_no}")

                                # Per material type: supplier + lines
                                po_groups = {}  # mat_type -> {supplier, lines[]}

                                for mat_type in mat_types:
                                    type_lines = [(i,ln,pend) for i,ln,pend in pending_lines if ln.get("material_type","Other") == mat_type]
                                    if not type_lines: continue

                                    st.markdown(f"##### 📦 {mat_type}")
                                    ts1, ts2 = st.columns([3,2])
                                    with ts1:
                                        t_supp = st.selectbox(f"Supplier for {mat_type} *",
                                                               supp_opts, key=f"tsupp_{pr_no}_{mat_type}")
                                    with ts2:
                                        st.markdown(f'<div style="padding-top:28px;font-size:12px;color:#64748b;">{len(type_lines)} item(s)</div>', unsafe_allow_html=True)

                                    t_lines = []
                                    for i, ln, pend in type_lines:
                                        lc1,lc2,lc3,lc4 = st.columns([3,1,1,1])
                                        with lc1: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>{ln["material_code"]}</strong> — {ln["material_name"]}<br><span style="font-size:11px;color:#94a3b8;">Pending: {pend} {ln.get("unit","")}</span></div>', unsafe_allow_html=True)
                                        with lc2: po_qty  = st.number_input("Qty", min_value=0.0, max_value=float(pend), value=float(pend), step=1.0, key=f"po_qty_{pr_no}_{i}")
                                        with lc3: po_rate = st.number_input("Rate(₹)", min_value=0.0, step=0.5, key=f"po_rate_{pr_no}_{i}")
                                        with lc4: po_gst  = st.selectbox("GST%", GST_RATES, index=2, key=f"po_gst_{pr_no}_{i}")

                                        t_lines.append({
                                            "material_code": ln["material_code"],
                                            "material_name": ln["material_name"],
                                            "material_type": ln.get("material_type",""),
                                            "required_qty":  ln.get("required_qty",0),
                                            "po_qty":        po_qty,
                                            "received_qty":  0,
                                            "unit":          ln.get("unit",""),
                                            "rate":          po_rate,
                                            "gst_pct":       po_gst,
                                            "amount":        round(po_qty * po_rate, 2),
                                            "so_ref":        ln.get("so_ref",""),
                                            "pr_line_idx":   i,
                                        })

                                    po_groups[mat_type] = {"supplier": t_supp, "lines": t_lines}
                                    sub = sum(l["amount"] for l in t_lines)
                                    gst = sum(l["amount"]*l["gst_pct"]/100 for l in t_lines)
                                    st.markdown(f'<div style="text-align:right;font-size:12px;color:#64748b;">Subtotal: ₹{sub:,.2f} | GST: ₹{gst:,.2f} | Total: ₹{sub+gst:,.2f}</div>', unsafe_allow_html=True)
                                    st.markdown('<hr style="margin:6px 0;">', unsafe_allow_html=True)

                                if st.button(f"✅ Create POs from {pr_no}", key=f"create_po_{pr_no}", use_container_width=False):
                                    created_pos = []
                                    for mat_type, grp in po_groups.items():
                                        if not grp["supplier"] or not grp["lines"]: continue
                                        lines_with_qty = [l for l in grp["lines"] if l["po_qty"] > 0]
                                        if not lines_with_qty: continue
                                        supp_code = grp["supplier"].split(" – ")[0] if " – " in grp["supplier"] else grp["supplier"]
                                        subtotal  = sum(l["amount"] for l in lines_with_qty)
                                        gst_amt   = sum(l["amount"]*l["gst_pct"]/100 for l in lines_with_qty)
                                        total     = subtotal + gst_amt
                                        po_no = next_po()
                                        SS["po_list"][po_no] = {
                                            "po_no": po_no, "po_date": str(date.today()),
                                            "supplier_code": supp_code,
                                            "supplier_name": suppliers.get(supp_code,{}).get("name", supp_code),
                                            "pr_ref": pr_no, "so_ref": pr.get("so_ref",""),
                                            "delivery_date": str(inline_del),
                                            "payment_terms": inline_pay, "currency": "INR",
                                            "lines": lines_with_qty,
                                            "subtotal": subtotal, "gst_amount": gst_amt, "total": total,
                                            "status": "Draft",
                                            "created_at": datetime.now().isoformat(),
                                        }
                                        created_pos.append(po_no)
                                        # Update PR line po_created_qty
                                        for il in lines_with_qty:
                                            idx = il["pr_line_idx"]
                                            prev = SS["pr_list"][pr_no]["lines"][idx].get("po_created_qty",0)
                                            SS["pr_list"][pr_no]["lines"][idx]["po_created_qty"] = prev + il["po_qty"]

                                    # Update PR status
                                    all_done = all(
                                        ln.get("po_created_qty",0) >= ln.get("required_qty",0)
                                        for ln in SS["pr_list"][pr_no]["lines"]
                                    )
                                    SS["pr_list"][pr_no]["status"] = "PO Created" if all_done else "Approved"
                                    save_data()
                                    st.success(f"✅ {len(created_pos)} PO(s) created: {', '.join(created_pos)}")
                                    st.rerun()

                        else:  # Job Work
                            st.markdown("#### 🔧 Create Job Work Order from this PR")
                            suppliers  = SS.get("suppliers",{})
                            jw_supps   = {k:v for k,v in suppliers.items() if "Job Work" in v.get("type","")}
                            jw_opts    = [""] + [f"{k} – {v['name']}" for k,v in jw_supps.items()]
                            jc1,jc2,jc3 = st.columns(3)
                            with jc1:
                                inline_proc = st.selectbox("Processor *", jw_opts, key=f"inline_proc_{pr_no}")
                            with jc2:
                                inline_jw_del = st.date_input("Expected Return", value=date.today()+timedelta(days=10), key=f"inline_jw_del_{pr_no}")
                            with jc3:
                                inline_jw_rate = st.number_input("Job Work Rate (₹/unit)", min_value=0.0, step=1.0, key=f"inline_jw_rate_{pr_no}")

                            items_data = st.session_state.get("items",{})
                            boms_data  = st.session_state.get("boms",{})
                            jwo_inline_lines = []
                            for i, ln in enumerate(pr.get("lines",[])):
                                req  = ln.get("required_qty",0)
                                done = ln.get("po_created_qty",0)
                                pend = max(0, req - done)
                                if pend <= 0: continue
                                # Get input material from BOM
                                bom_inputs = [b for b in boms_data.get(ln["material_code"],{}).get("lines",[]) if b.get("line_type") != "Process"]
                                jl1,jl2,jl3 = st.columns([3,1,1])
                                with jl1:
                                    st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>OUT: {ln["material_code"]}</strong> — {ln["material_name"]} | Pending: {pend} {ln.get("unit","")}</div>', unsafe_allow_html=True)
                                    if bom_inputs:
                                        in_code = bom_inputs[0].get("item_code","")
                                        in_qty  = round(float(bom_inputs[0].get("qty",0)) * pend, 3)
                                        st.markdown(f'<div style="font-size:12px;color:#64748b;">IN: {in_code} — {in_qty} {bom_inputs[0].get("unit","")}</div>', unsafe_allow_html=True)
                                with jl2:
                                    jw_qty = st.number_input("Qty", min_value=0.0, max_value=float(pend), value=float(pend), step=1.0, key=f"jw_qty_{pr_no}_{i}")
                                with jl3:
                                    jw_line_rate = st.number_input("Rate", min_value=0.0, step=0.5, value=float(inline_jw_rate), key=f"jw_lrate_{pr_no}_{i}")

                                in_mat = bom_inputs[0].get("item_code","") if bom_inputs else ""
                                in_qty_val = round(float(bom_inputs[0].get("qty",0)) * jw_qty, 3) if bom_inputs else 0
                                jwo_inline_lines.append({
                                    "output_material": ln["material_code"],
                                    "output_name":     ln["material_name"],
                                    "output_qty":      jw_qty,
                                    "output_unit":     ln.get("unit",""),
                                    "input_material":  in_mat,
                                    "input_name":      items_data.get(in_mat,{}).get("name","") if in_mat else "",
                                    "input_qty":       in_qty_val,
                                    "input_unit":      bom_inputs[0].get("unit","") if bom_inputs else "",
                                    "rate":            jw_line_rate,
                                    "received_qty":    0.0,
                                    "pr_line_idx":     i,
                                })

                            if inline_proc and jwo_inline_lines:
                                jw_total = sum(l["output_qty"]*l["rate"] for l in jwo_inline_lines)
                                st.markdown(f'<div class="info-box" style="text-align:right;"><strong>JW Total: ₹{jw_total:,.2f}</strong></div>', unsafe_allow_html=True)

                                if st.button(f"✅ Create JWO from {pr_no}", key=f"create_jwo_{pr_no}", use_container_width=False):
                                    proc_code = inline_proc.split(" – ")[0] if " – " in inline_proc else inline_proc
                                    jwo_no = next_jwo()

                                    # Issue input materials from stock
                                    for jl in jwo_inline_lines:
                                        in_c = jl.get("input_material","")
                                        in_q = float(jl.get("input_qty",0))
                                        if in_c and in_q > 0 and in_c in st.session_state["items"]:
                                            cur = float(st.session_state["items"][in_c].get("stock",0))
                                            st.session_state["items"][in_c]["stock"] = max(0, cur - in_q)

                                    SS["jwo_list"][jwo_no] = {
                                        "jwo_no":         jwo_no,
                                        "jwo_date":       str(date.today()),
                                        "processor_code": proc_code,
                                        "processor_name": suppliers.get(proc_code,{}).get("name", proc_code),
                                        "pr_ref":         pr_no,
                                        "so_ref":         pr.get("so_ref",""),
                                        "expected_date":  str(inline_jw_del),
                                        "lines":          jwo_inline_lines,
                                        "total":          jw_total,
                                        "status":         "Issued to Processor",
                                        "created_at":     datetime.now().isoformat(),
                                    }
                                    # Update PR line po_created_qty
                                    for jl in jwo_inline_lines:
                                        idx = jl["pr_line_idx"]
                                        prev = SS["pr_list"][pr_no]["lines"][idx].get("po_created_qty",0)
                                        SS["pr_list"][pr_no]["lines"][idx]["po_created_qty"] = prev + jl["output_qty"]

                                    all_done = all(
                                        ln.get("po_created_qty",0) >= ln.get("required_qty",0)
                                        for ln in SS["pr_list"][pr_no]["lines"]
                                    )
                                    SS["pr_list"][pr_no]["status"] = "JWO Created" if all_done else "Approved"
                                    save_data()
                                    st.success(f"✅ {jwo_no} created! Input materials issued from stock.")
                                    st.rerun()

                st.markdown('<hr style="margin:4px 0;border-color:#e2e5ef;">', unsafe_allow_html=True)


# ── PURCHASE ORDERS ───────────────────────────────────────────────────────────
elif nav_pur == "📦 Purchase Orders":
    st.markdown('<h1>Purchase Orders</h1>', unsafe_allow_html=True)

    suppliers = SS.get("suppliers", {})
    pr_list   = SS.get("pr_list", {})

    po_tab1, po_tab2 = st.tabs(["📋 PO List", "➕ Create PO"])

    with po_tab2:
        # Pre-fill from PR if coming from PR page
        pr_ref = st.session_state.get("pr_to_po", "")

        st.markdown("#### PO Header")
        pc1, pc2, pc3 = st.columns(3)
        with pc1:
            supp_opts = [""] + [f"{k} – {v['name']}" for k,v in suppliers.items() if v.get("type","") != "Job Work"]
            sel_supp  = st.selectbox("Supplier *", supp_opts, key="po_supp")
            po_date   = st.date_input("PO Date", value=date.today(), key="po_date")
            po_del_dt = st.date_input("Expected Delivery", value=date.today()+timedelta(days=14), key="po_del")
        with pc2:
            pr_opts = [""] + [k for k,v in pr_list.items() if v.get("status")=="Approved" and v.get("pr_type")=="Purchase"]
            sel_pr  = st.selectbox("PR Reference", pr_opts, index=pr_opts.index(pr_ref) if pr_ref in pr_opts else 0, key="po_pr_ref")
            po_so_ref = st.text_input("SO Reference", value=pr_list.get(sel_pr,{}).get("so_ref","") if sel_pr else "", key="po_so")
            po_currency = st.selectbox("Currency", ["INR","USD","EUR"], key="po_curr")
        with pc3:
            po_payment = st.selectbox("Payment Terms", SS.get("payment_terms",[]), key="po_pay")
            po_remarks = st.text_area("Remarks", height=70, key="po_rem")

        # Load lines from PR or manual
        if "po_lines" not in st.session_state:
            st.session_state["po_lines"] = []

        if sel_pr and sel_pr in pr_list and not st.session_state["po_lines"]:
            for ln in pr_list[sel_pr].get("lines",[]):
                st.session_state["po_lines"].append({
                    "material_code": ln["material_code"],
                    "material_name": ln["material_name"],
                    "material_type": ln.get("material_type",""),
                    "required_qty":  ln["required_qty"],
                    "po_qty":        ln["required_qty"],
                    "received_qty":  0,
                    "unit":          ln["unit"],
                    "rate":          0.0,
                    "gst_pct":       12,
                    "amount":        0.0,
                    "so_ref":        ln.get("so_ref",""),
                })

        # Add manual line
        with st.expander("➕ Add Line"):
            items_data = st.session_state.get("items",{})
            al1,al2,al3 = st.columns(3)
            with al1:
                po_mat = st.selectbox("Material", [""] + list(items_data.keys()),
                                       format_func=lambda x: f"{x} – {items_data.get(x,{}).get('name','')}" if x else "Select",
                                       key="po_mat_add")
                po_add_qty = st.number_input("Qty", min_value=0.0, step=1.0, key="po_add_qty")
            with al2:
                po_add_rate = st.number_input("Rate (₹)", min_value=0.0, step=1.0, key="po_add_rate")
                po_add_gst  = st.selectbox("GST %", GST_RATES, index=2, key="po_add_gst")
            with al3:
                po_add_unit = st.selectbox("Unit", UNITS, key="po_add_unit")
                if st.button("➕ Add", key="po_add_btn") and po_mat and po_add_qty > 0:
                    st.session_state["po_lines"].append({
                        "material_code": po_mat,
                        "material_name": items_data.get(po_mat,{}).get("name",po_mat),
                        "material_type": items_data.get(po_mat,{}).get("item_type",""),
                        "required_qty": po_add_qty, "po_qty": po_add_qty,
                        "received_qty": 0, "unit": po_add_unit,
                        "rate": po_add_rate, "gst_pct": po_add_gst,
                        "amount": round(po_add_qty * po_add_rate, 2),
                    })
                    st.rerun()

        # Show PO lines (editable)
        if st.session_state["po_lines"]:
            st.markdown("#### PO Lines")
            edit_po = pd.DataFrame([{
                "Material":    ln["material_code"],
                "Name":        ln["material_name"],
                "PO Qty":      ln["po_qty"],
                "Unit":        ln["unit"],
                "Rate (₹)":   ln["rate"],
                "GST %":       ln["gst_pct"],
                "Amount (₹)": ln["amount"],
            } for ln in st.session_state["po_lines"]])

            edited_po = st.data_editor(edit_po, use_container_width=True, hide_index=False,
                column_config={
                    "Material": st.column_config.TextColumn(disabled=True),
                    "Name":     st.column_config.TextColumn(disabled=True),
                    "PO Qty":   st.column_config.NumberColumn(min_value=0, step=1),
                    "Rate (₹)":st.column_config.NumberColumn(min_value=0.0, step=0.5),
                    "GST %":   st.column_config.SelectboxColumn(options=GST_RATES),
                }, key="po_editor")

            # Apply edits
            for i, row in edited_po.iterrows():
                if i < len(st.session_state["po_lines"]):
                    qty  = float(row["PO Qty"])
                    rate = float(row["Rate (₹)"])
                    gst  = int(row["GST %"]) if row["GST %"] else 12
                    st.session_state["po_lines"][i]["po_qty"]  = qty
                    st.session_state["po_lines"][i]["rate"]    = rate
                    st.session_state["po_lines"][i]["gst_pct"] = gst
                    st.session_state["po_lines"][i]["amount"]  = round(qty * rate, 2)

            subtotal = sum(ln["amount"] for ln in st.session_state["po_lines"])
            gst_amt  = sum(ln["amount"] * ln["gst_pct"] / 100 for ln in st.session_state["po_lines"])
            total    = subtotal + gst_amt
            st.markdown(f'<div class="card card-left" style="text-align:right;padding:12px 20px;">Subtotal: ₹{subtotal:,.2f} | GST: ₹{gst_amt:,.2f} | <strong style="font-size:16px;color:#c8a96e;">Total: ₹{total:,.2f}</strong></div>', unsafe_allow_html=True)

            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                if st.button("💾 Save as Draft", use_container_width=True):
                    po_no = next_po()
                    supp_code = sel_supp.split(" – ")[0] if " – " in sel_supp else sel_supp
                    SS["po_list"][po_no] = {
                        "po_no": po_no, "po_date": str(po_date),
                        "supplier_code": supp_code,
                        "supplier_name": suppliers.get(supp_code,{}).get("name", supp_code),
                        "pr_ref": sel_pr, "so_ref": po_so_ref,
                        "delivery_date": str(po_del_dt),
                        "payment_terms": po_payment, "currency": po_currency,
                        "lines": st.session_state["po_lines"].copy(),
                        "subtotal": subtotal, "gst_amount": gst_amt, "total": total,
                        "status": "Draft", "remarks": po_remarks,
                        "created_at": datetime.now().isoformat(),
                    }
                    if sel_pr: SS["pr_list"][sel_pr]["status"] = "PO Created"
                    st.session_state["po_lines"] = []
                    st.session_state["pr_to_po"] = ""
                    save_data()
                    st.success(f"✅ {po_no} saved!")
                    st.rerun()
            with sc2:
                if st.button("📤 Save & Send to Supplier", use_container_width=True):
                    po_no = next_po()
                    supp_code = sel_supp.split(" – ")[0] if " – " in sel_supp else sel_supp
                    SS["po_list"][po_no] = {
                        "po_no": po_no, "po_date": str(po_date),
                        "supplier_code": supp_code,
                        "supplier_name": suppliers.get(supp_code,{}).get("name", supp_code),
                        "pr_ref": sel_pr, "so_ref": po_so_ref,
                        "delivery_date": str(po_del_dt),
                        "payment_terms": po_payment, "currency": po_currency,
                        "lines": st.session_state["po_lines"].copy(),
                        "subtotal": subtotal, "gst_amount": gst_amt, "total": total,
                        "status": "Sent to Supplier", "remarks": po_remarks,
                        "created_at": datetime.now().isoformat(),
                    }
                    if sel_pr: SS["pr_list"][sel_pr]["status"] = "PO Created"
                    st.session_state["po_lines"] = []
                    st.session_state["pr_to_po"] = ""
                    save_data()
                    st.success(f"✅ {po_no} sent to supplier!")
                    st.rerun()
            with sc3:
                if st.button("🗑 Clear Lines", use_container_width=True):
                    st.session_state["po_lines"] = []; st.rerun()

    with po_tab1:
        po_list = SS.get("po_list", {})
        pof1, pof2 = st.columns(2)
        with pof1: pof_sts = st.selectbox("Status", ["All"]+PO_STATUS, key="pol_sts")
        with pof2: pof_srch = st.text_input("🔍 PO # / Supplier", key="pol_srch")

        if not po_list:
            st.markdown('<div class="warn-box">Koi PO nahi hai.</div>', unsafe_allow_html=True)
        else:
            for po_no, po in reversed(list(po_list.items())):
                if pof_sts != "All" and po.get("status","") != pof_sts: continue
                if pof_srch and pof_srch.lower() not in po_no.lower() and pof_srch.lower() not in po.get("supplier_name","").lower(): continue

                r1,r2,r3,r4,r5,r6 = st.columns([1.2,2,1.5,1.2,1.5,1.5])
                with r1: st.markdown(f'<div style="padding-top:8px;font-family:monospace;font-size:12px;font-weight:700;color:#c8a96e;">{po_no}</div>', unsafe_allow_html=True)
                with r2: st.markdown(f'<div style="padding-top:6px;font-size:13px;font-weight:600;">{po.get("supplier_name","—")}</div>', unsafe_allow_html=True)
                with r3: st.markdown(f'<div style="padding-top:8px;font-size:12px;">Del: {po.get("delivery_date","—")}<br>SO: {po.get("so_ref","—")}</div>', unsafe_allow_html=True)
                with r4: st.markdown(f'<div style="padding-top:8px;font-size:13px;font-weight:600;color:#c8a96e;">₹{po.get("total",0):,.0f}</div>', unsafe_allow_html=True)
                with r5: st.markdown(f'<div style="padding-top:6px;">{pur_badge(po.get("status",""))}</div>', unsafe_allow_html=True)
                with r6:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if po.get("status") in ["Sent to Supplier","Confirmed","Partial Received"]:
                            if st.button("📥 GRN", key=f"grn_po_{po_no}", use_container_width=True):
                                st.session_state["grn_from_po"] = po_no
                                st.session_state["current_page"] = "📥 GRN"
                                st.rerun()
                    with col_b:
                        new_po_sts = st.selectbox("", PO_STATUS,
                                                    index=PO_STATUS.index(po.get("status","Draft")),
                                                    key=f"po_sts_{po_no}", label_visibility="collapsed")
                        if new_po_sts != po.get("status"):
                            SS["po_list"][po_no]["status"] = new_po_sts
                            save_data(); st.rerun()

                st.markdown('<hr style="margin:3px 0;border-color:#e2e5ef;">', unsafe_allow_html=True)


# ── JOB WORK ORDERS ───────────────────────────────────────────────────────────
elif nav_pur == "🔧 Job Work Orders":
    st.markdown('<h1>Job Work Orders</h1>', unsafe_allow_html=True)

    suppliers  = SS.get("suppliers", {})
    pr_list    = SS.get("pr_list", {})
    items_data = st.session_state.get("items", {})

    jw_tab1, jw_tab2 = st.tabs(["📋 JWO List", "➕ Create JWO"])

    with jw_tab2:
        pr_ref_jw = st.session_state.get("pr_to_jwo", "")
        st.markdown("#### JWO Header")

        jc1, jc2 = st.columns(2)
        with jc1:
            # Job work suppliers
            jw_supps = {k:v for k,v in suppliers.items() if "Job Work" in v.get("type","")}
            jw_supp_opts = [""] + [f"{k} – {v['name']}" for k,v in jw_supps.items()]
            sel_processor = st.selectbox("Processor / Job Worker *", jw_supp_opts, key="jwo_proc")
            jwo_date      = st.date_input("JWO Date", value=date.today(), key="jwo_date")
            jwo_del_dt    = st.date_input("Expected Return Date", value=date.today()+timedelta(days=10), key="jwo_del")
        with jc2:
            jw_pr_opts = [""] + [k for k,v in pr_list.items() if v.get("status")=="Approved" and v.get("pr_type")=="Job Work"]
            sel_jw_pr  = st.selectbox("PR Reference", jw_pr_opts,
                                       index=jw_pr_opts.index(pr_ref_jw) if pr_ref_jw in jw_pr_opts else 0,
                                       key="jwo_pr")
            jwo_so_ref = st.text_input("SO Reference", value=pr_list.get(sel_jw_pr,{}).get("so_ref","") if sel_jw_pr else "", key="jwo_so")
            jwo_remarks = st.text_area("Remarks", height=60, key="jwo_rem")

        st.markdown("---")
        st.markdown("#### Material to be Processed")

        if "jwo_lines" not in st.session_state:
            st.session_state["jwo_lines"] = []

        # Load from PR
        if sel_jw_pr and sel_jw_pr in pr_list and not st.session_state["jwo_lines"]:
            for ln in pr_list[sel_jw_pr].get("lines",[]):
                st.session_state["jwo_lines"].append({
                    "output_material": ln["material_code"],
                    "output_name":     ln["material_name"],
                    "output_qty":      ln["required_qty"],
                    "output_unit":     ln["unit"],
                    "input_material":  "",
                    "input_name":      "",
                    "input_qty":       0.0,
                    "input_unit":      "",
                    "rate":            0.0,
                    "received_qty":    0.0,
                    "so_ref":          ln.get("so_ref",""),
                })

        with st.expander("➕ Add Job Work Line"):
            jl1, jl2 = st.columns(2)
            with jl1:
                st.markdown("**Output Material (jo receive hoga)**")
                jw_out = st.selectbox("Output Material *", [""] + list(items_data.keys()),
                                       format_func=lambda x: f"{x} – {items_data.get(x,{}).get('name','')}" if x else "Select",
                                       key="jwo_out_mat")
                jw_out_qty  = st.number_input("Output Qty", min_value=0.0, step=1.0, key="jwo_out_qty")
                jw_out_unit = st.selectbox("Output Unit", UNITS, key="jwo_out_unit")
            with jl2:
                st.markdown("**Input Material (jo issue karna hai)**")
                jw_in = st.selectbox("Input Material (Grey Fabric etc.)", [""] + list(items_data.keys()),
                                      format_func=lambda x: f"{x} – {items_data.get(x,{}).get('name','')}" if x else "Select",
                                      key="jwo_in_mat")
                jw_in_qty  = st.number_input("Input Qty to Issue", min_value=0.0, step=1.0, key="jwo_in_qty")
                jw_in_unit = st.selectbox("Input Unit", UNITS, key="jwo_in_unit")
                jw_rate    = st.number_input("Job Work Rate (₹/unit)", min_value=0.0, step=1.0, key="jwo_rate")

            if st.button("➕ Add JW Line") and jw_out and jw_out_qty > 0:
                in_code = jw_in.split(" – ")[0] if " – " in jw_in else jw_in
                out_code = jw_out.split(" – ")[0] if " – " in jw_out else jw_out
                st.session_state["jwo_lines"].append({
                    "output_material": out_code,
                    "output_name":     items_data.get(out_code,{}).get("name", out_code),
                    "output_qty":      jw_out_qty,
                    "output_unit":     jw_out_unit,
                    "input_material":  in_code,
                    "input_name":      items_data.get(in_code,{}).get("name", in_code) if in_code else "",
                    "input_qty":       jw_in_qty,
                    "input_unit":      jw_in_unit,
                    "rate":            jw_rate,
                    "received_qty":    0.0,
                })
                st.rerun()

        if st.session_state["jwo_lines"]:
            st.markdown("#### JWO Lines")
            for idx, ln in enumerate(st.session_state["jwo_lines"]):
                lc1,lc2,lc3,lc4 = st.columns([2,2,2,0.5])
                with lc1: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>OUT:</strong> {ln["output_material"]} — {ln["output_name"]}<br>{ln["output_qty"]} {ln["output_unit"]}</div>', unsafe_allow_html=True)
                with lc2: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>IN:</strong> {ln.get("input_material","—")} — {ln.get("input_name","—")}<br>{ln.get("input_qty",0)} {ln.get("input_unit","")}</div>', unsafe_allow_html=True)
                with lc3: st.markdown(f'<div style="padding-top:8px;font-size:13px;">Rate: ₹{ln["rate"]}/unit<br>Amount: ₹{ln["output_qty"]*ln["rate"]:,.2f}</div>', unsafe_allow_html=True)
                with lc4:
                    if st.button("🗑", key=f"del_jw_{idx}"):
                        st.session_state["jwo_lines"].pop(idx); st.rerun()
                st.markdown('<hr style="margin:2px 0;">', unsafe_allow_html=True)

            jw_total = sum(ln["output_qty"]*ln["rate"] for ln in st.session_state["jwo_lines"])
            st.markdown(f'<div class="card card-left" style="text-align:right;padding:10px 20px;"><strong style="color:#c8a96e;">Job Work Total: ₹{jw_total:,.2f}</strong></div>', unsafe_allow_html=True)

            if st.button("✅ Create JWO & Issue Material", use_container_width=False):
                proc_code = sel_processor.split(" – ")[0] if " – " in sel_processor else sel_processor
                jwo_no    = next_jwo()

                # Issue input materials from stock
                for ln in st.session_state["jwo_lines"]:
                    in_code = ln.get("input_material","")
                    in_qty  = float(ln.get("input_qty", 0))
                    if in_code and in_qty > 0 and in_code in st.session_state["items"]:
                        cur_stock = float(st.session_state["items"][in_code].get("stock", 0))
                        st.session_state["items"][in_code]["stock"] = max(0, cur_stock - in_qty)

                SS["jwo_list"][jwo_no] = {
                    "jwo_no":         jwo_no,
                    "jwo_date":       str(jwo_date),
                    "processor_code": proc_code,
                    "processor_name": suppliers.get(proc_code,{}).get("name", proc_code),
                    "pr_ref":         sel_jw_pr,
                    "so_ref":         jwo_so_ref,
                    "expected_date":  str(jwo_del_dt),
                    "lines":          st.session_state["jwo_lines"].copy(),
                    "total":          jw_total,
                    "status":         "Issued to Processor",
                    "remarks":        jwo_remarks,
                    "created_at":     datetime.now().isoformat(),
                }
                if sel_jw_pr: SS["pr_list"][sel_jw_pr]["status"] = "JWO Created"
                st.session_state["jwo_lines"] = []
                st.session_state["pr_to_jwo"] = ""
                save_data()
                st.success(f"✅ {jwo_no} created! Input materials issued from stock.")
                st.rerun()

    with jw_tab1:
        jwo_list = SS.get("jwo_list", {})
        if not jwo_list:
            st.markdown('<div class="warn-box">Koi JWO nahi hai.</div>', unsafe_allow_html=True)
        else:
            for jwo_no, jwo in reversed(list(jwo_list.items())):
                r1,r2,r3,r4,r5,r6 = st.columns([1.2,2,1.5,1.2,1.5,1.5])
                with r1: st.markdown(f'<div style="padding-top:8px;font-family:monospace;font-size:12px;font-weight:700;color:#c8a96e;">{jwo_no}</div>', unsafe_allow_html=True)
                with r2: st.markdown(f'<div style="padding-top:6px;font-size:13px;font-weight:600;">{jwo.get("processor_name","—")}</div>', unsafe_allow_html=True)
                with r3: st.markdown(f'<div style="padding-top:8px;font-size:12px;">Return: {jwo.get("expected_date","—")}<br>{len(jwo.get("lines",[]))} items</div>', unsafe_allow_html=True)
                with r4: st.markdown(f'<div style="padding-top:8px;font-size:13px;font-weight:600;color:#c8a96e;">₹{jwo.get("total",0):,.0f}</div>', unsafe_allow_html=True)
                with r5: st.markdown(f'<div style="padding-top:6px;">{pur_badge(jwo.get("status",""))}</div>', unsafe_allow_html=True)
                with r6:
                    if jwo.get("status") in ["Issued to Processor","In Process","Partial Received"]:
                        if st.button("📥 Receive", key=f"rec_jwo_{jwo_no}", use_container_width=True):
                            st.session_state["grn_from_jwo"] = jwo_no
                            st.session_state["current_page"] = "📥 GRN"
                            st.rerun()
                st.markdown('<hr style="margin:3px 0;border-color:#e2e5ef;">', unsafe_allow_html=True)


# ── GRN ───────────────────────────────────────────────────────────────────────
elif nav_pur == "📥 GRN":
    st.markdown('<h1>GRN — Goods Receipt Note</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">PO ya JWO ke against material receive karo — stock automatically update hoga.</div>', unsafe_allow_html=True)

    grn_tab1, grn_tab2 = st.tabs(["📋 GRN List", "➕ Create GRN"])

    with grn_tab2:
        po_ref_grn  = st.session_state.get("grn_from_po", "")
        jwo_ref_grn = st.session_state.get("grn_from_jwo", "")

        gc1, gc2 = st.columns(2)
        with gc1:
            grn_type = st.radio("GRN Type", ["PO Receipt","JWO Receipt"], horizontal=True, key="grn_type")
        with gc2:
            grn_date = st.date_input("Receipt Date", value=date.today(), key="grn_date")

        if grn_type == "PO Receipt":
            po_opts = [""] + [k for k,v in SS.get("po_list",{}).items() if v.get("status") in ["Sent to Supplier","Confirmed","Partial Received"]]
            sel_grn_po = st.selectbox("PO Select *", po_opts,
                                       index=po_opts.index(po_ref_grn) if po_ref_grn in po_opts else 0,
                                       key="grn_po_sel")
            if sel_grn_po:
                po = SS["po_list"][sel_grn_po]
                st.markdown(f'<div class="ok-box">Supplier: <strong>{po.get("supplier_name","")}</strong> | PO Date: {po.get("po_date","")} | Total: ₹{po.get("total",0):,.0f}</div>', unsafe_allow_html=True)

                st.markdown("#### Receipt Lines")
                grn_lines = []
                for i, ln in enumerate(po.get("lines",[])):
                    pending = ln["po_qty"] - ln.get("received_qty",0)
                    if pending <= 0: continue
                    gc1,gc2,gc3,gc4 = st.columns([2,1,1,1])
                    with gc1: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>{ln["material_code"]}</strong> — {ln["material_name"]}</div>', unsafe_allow_html=True)
                    with gc2: st.markdown(f'<div style="padding-top:8px;font-size:12px;">PO Qty: {ln["po_qty"]}<br>Pending: {pending}</div>', unsafe_allow_html=True)
                    with gc3:
                        recv_qty = st.number_input(f"Recv Qty", min_value=0.0, max_value=float(pending),
                                                    value=float(pending), step=1.0, key=f"grn_recv_{sel_grn_po}_{i}")
                    with gc4:
                        qc_status = st.selectbox("QC", ["Pass","Fail","Hold"], key=f"grn_qc_{sel_grn_po}_{i}")
                    grn_lines.append({
                        "material_code": ln["material_code"],
                        "material_name": ln["material_name"],
                        "unit":          ln["unit"],
                        "po_qty":        ln["po_qty"],
                        "received_qty":  recv_qty,
                        "rate":          ln.get("rate",0),
                        "qc_status":     qc_status,
                        "amount":        round(recv_qty * ln.get("rate",0), 2),
                    })
                    st.markdown('<hr style="margin:2px 0;">', unsafe_allow_html=True)

                grn_remarks = st.text_area("Remarks", key="grn_rem_po")
                if st.button("✅ Post GRN & Update Stock", use_container_width=False) and grn_lines:
                    grn_no = next_grn()
                    total_recv = sum(ln["received_qty"] for ln in grn_lines)

                    # Update stock
                    for ln in grn_lines:
                        mat_code = ln["material_code"]
                        recv_q   = float(ln["received_qty"])
                        if ln["qc_status"] == "Pass" and mat_code in st.session_state["items"]:
                            cur = float(st.session_state["items"][mat_code].get("stock", 0))
                            st.session_state["items"][mat_code]["stock"] = round(cur + recv_q, 3)

                    # Update PO received qty
                    for i, ln in enumerate(SS["po_list"][sel_grn_po]["lines"]):
                        grn_ln = next((g for g in grn_lines if g["material_code"]==ln["material_code"]), None)
                        if grn_ln:
                            SS["po_list"][sel_grn_po]["lines"][i]["received_qty"] = \
                                ln.get("received_qty",0) + grn_ln["received_qty"]

                    # Update PO status
                    all_recv = all(ln["po_qty"] <= ln.get("received_qty",0)
                                   for ln in SS["po_list"][sel_grn_po]["lines"])
                    SS["po_list"][sel_grn_po]["status"] = "Received" if all_recv else "Partial Received"

                    SS["grn_list"][grn_no] = {
                        "grn_no": grn_no, "grn_date": str(grn_date),
                        "grn_type": "PO Receipt", "ref_no": sel_grn_po,
                        "lines": grn_lines, "status": "Posted",
                        "total_received": total_recv, "remarks": grn_remarks,
                        "created_at": datetime.now().isoformat(),
                    }
                    st.session_state["grn_from_po"] = ""
                    save_data()
                    st.success(f"✅ {grn_no} posted! Stock updated.")
                    st.rerun()

        else:  # JWO Receipt
            jwo_opts = [""] + [k for k,v in SS.get("jwo_list",{}).items() if v.get("status") in ["Issued to Processor","In Process","Partial Received"]]
            sel_grn_jwo = st.selectbox("JWO Select *", jwo_opts,
                                        index=jwo_opts.index(jwo_ref_grn) if jwo_ref_grn in jwo_opts else 0,
                                        key="grn_jwo_sel")
            if sel_grn_jwo:
                jwo = SS["jwo_list"][sel_grn_jwo]
                st.markdown(f'<div class="ok-box">Processor: <strong>{jwo.get("processor_name","")}</strong> | Expected: {jwo.get("expected_date","")}</div>', unsafe_allow_html=True)

                st.markdown("#### Receipt Lines (Processed Material)")
                jwo_grn_lines = []
                for i, ln in enumerate(jwo.get("lines",[])):
                    pending = ln["output_qty"] - float(ln.get("received_qty",0))
                    if pending <= 0: continue
                    jc1,jc2,jc3 = st.columns([3,1,1])
                    with jc1: st.markdown(f'<div style="padding-top:8px;font-size:13px;"><strong>{ln["output_material"]}</strong> — {ln["output_name"]}<br>Ordered: {ln["output_qty"]} | Pending: {pending:.0f}</div>', unsafe_allow_html=True)
                    with jc2:
                        jwo_recv = st.number_input("Recv Qty", min_value=0.0, max_value=float(pending),
                                                    value=float(pending), step=1.0, key=f"jwo_recv_{sel_grn_jwo}_{i}")
                    with jc3:
                        jwo_qc = st.selectbox("QC", ["Pass","Fail","Hold"], key=f"jwo_qc_{sel_grn_jwo}_{i}")
                    jwo_grn_lines.append({
                        "material_code": ln["output_material"],
                        "material_name": ln["output_name"],
                        "unit":          ln["output_unit"],
                        "ordered_qty":   ln["output_qty"],
                        "received_qty":  jwo_recv,
                        "qc_status":     jwo_qc,
                    })
                    st.markdown('<hr style="margin:2px 0;">', unsafe_allow_html=True)

                jwo_grn_rem = st.text_area("Remarks", key="jwo_grn_rem")
                if st.button("✅ Post GRN & Update Stock", use_container_width=False, key="post_jwo_grn") and jwo_grn_lines:
                    grn_no = next_grn()
                    # Update stock for received processed material
                    for ln in jwo_grn_lines:
                        if ln["qc_status"] == "Pass" and ln["material_code"] in st.session_state["items"]:
                            cur = float(st.session_state["items"][ln["material_code"]].get("stock", 0))
                            st.session_state["items"][ln["material_code"]]["stock"] = round(cur + ln["received_qty"], 3)
                        # Update JWO received qty
                        for i, jln in enumerate(SS["jwo_list"][sel_grn_jwo]["lines"]):
                            if jln["output_material"] == ln["material_code"]:
                                SS["jwo_list"][sel_grn_jwo]["lines"][i]["received_qty"] = \
                                    float(jln.get("received_qty",0)) + ln["received_qty"]

                    all_recv = all(ln["output_qty"] <= float(ln.get("received_qty",0))
                                   for ln in SS["jwo_list"][sel_grn_jwo]["lines"])
                    SS["jwo_list"][sel_grn_jwo]["status"] = "Received" if all_recv else "Partial Received"

                    SS["grn_list"][grn_no] = {
                        "grn_no": grn_no, "grn_date": str(grn_date),
                        "grn_type": "JWO Receipt", "ref_no": sel_grn_jwo,
                        "lines": jwo_grn_lines, "status": "Posted",
                        "remarks": jwo_grn_rem,
                        "created_at": datetime.now().isoformat(),
                    }
                    st.session_state["grn_from_jwo"] = ""
                    save_data()
                    st.success(f"✅ {grn_no} posted! Processed material stock updated.")
                    st.rerun()

    with grn_tab1:
        grn_list = SS.get("grn_list", {})
        if not grn_list:
            st.markdown('<div class="warn-box">Koi GRN nahi hai.</div>', unsafe_allow_html=True)
        else:
            grn_rows = []
            for grn_no, grn in reversed(list(grn_list.items())):
                grn_rows.append({
                    "GRN #": grn_no, "Date": grn.get("grn_date",""),
                    "Type": grn.get("grn_type",""), "Ref": grn.get("ref_no",""),
                    "Items": len(grn.get("lines",[])),
                    "Status": grn.get("status",""),
                })
            st.dataframe(pd.DataFrame(grn_rows), use_container_width=True, hide_index=True)


# ── SUPPLIER MASTER ───────────────────────────────────────────────────────────
elif nav_pur == "👥 Supplier Master":
    st.markdown('<h1>Supplier Master</h1>', unsafe_allow_html=True)

    sup_tab1, sup_tab2 = st.tabs(["📋 Supplier List", "➕ Add Supplier"])

    with sup_tab2:
        sc1, sc2 = st.columns(2)
        with sc1:
            sup_code    = st.text_input("Supplier Code *", placeholder="e.g. SUP001", key="sup_code")
            sup_name    = st.text_input("Supplier Name *", placeholder="e.g. Sharma Textiles", key="sup_name")
            sup_type    = st.multiselect("Supplier Type", ["Raw Material","Accessories","Packing","Job Work","Fabric","Printing","Dyeing"], key="sup_type")
            sup_contact = st.text_input("Contact Person", key="sup_contact")
        with sc2:
            sup_phone   = st.text_input("Phone", key="sup_phone")
            sup_email   = st.text_input("Email", key="sup_email")
            sup_gst     = st.text_input("GST Number", key="sup_gst")
            sup_payment = st.selectbox("Payment Terms", SS.get("payment_terms",[]), key="sup_pay")
            sup_city    = st.text_input("City", key="sup_city")
            sup_remarks = st.text_area("Remarks", height=60, key="sup_rem")

        if st.button("💾 Save Supplier", use_container_width=False):
            if sup_code and sup_name:
                SS["suppliers"][sup_code] = {
                    "name": sup_name, "type": ", ".join(sup_type),
                    "contact": sup_contact, "phone": sup_phone,
                    "email": sup_email, "gst": sup_gst,
                    "payment_terms": sup_payment, "city": sup_city,
                    "remarks": sup_remarks,
                    "created_at": datetime.now().isoformat(),
                }
                save_data()
                st.success(f"✅ Supplier '{sup_name}' saved!")
                st.rerun()
            else:
                st.error("Code and Name required!")

    with sup_tab1:
        suppliers = SS.get("suppliers", {})
        if not suppliers:
            st.markdown('<div class="warn-box">Koi supplier nahi hai.</div>', unsafe_allow_html=True)
        else:
            sup_rows = []
            for code, sup in suppliers.items():
                sup_rows.append({
                    "Code": code, "Name": sup["name"], "Type": sup.get("type",""),
                    "Contact": sup.get("contact",""), "Phone": sup.get("phone",""),
                    "City": sup.get("city",""), "GST": sup.get("gst",""),
                    "Payment": sup.get("payment_terms",""),
                })
            st.dataframe(pd.DataFrame(sup_rows), use_container_width=True, hide_index=True)

            # Edit/Delete
            st.markdown("---")
            del_sup = st.selectbox("Supplier delete karo", [""] + list(suppliers.keys()), key="del_sup_sel",
                                    format_func=lambda x: f"{x} – {suppliers.get(x,{}).get('name','')}" if x else "Select")
            if del_sup:
                if st.button(f"🗑 Delete {del_sup}", key="del_sup_btn"):
                    del SS["suppliers"][del_sup]
                    save_data()
                    st.success("Deleted!")
                    st.rerun()


# ── PURCHASE REPORTS ──────────────────────────────────────────────────────────
elif nav_pur == "📊 Purchase Reports":
    st.markdown('<h1>Purchase Reports</h1>', unsafe_allow_html=True)

    rep = st.selectbox("Report", [
        "1. PR Status Report",
        "2. PO Status Report",
        "3. JWO Status Report",
        "4. Supplier-wise Purchase",
        "5. Material-wise Purchase",
        "6. Pending Receipt Report",
        "7. GRN Summary",
    ], key="pur_rep")

    pr_list  = SS.get("pr_list", {})
    po_list  = SS.get("po_list", {})
    jwo_list = SS.get("jwo_list", {})
    grn_list = SS.get("grn_list", {})

    if rep.startswith("1"):
        rows = [{"PR #":k,"Type":v.get("pr_type",""),"SO":v.get("so_ref",""),
                 "Items":len(v.get("lines",[])),"Req Date":v.get("required_date",""),
                 "Status":v.get("status",""),"Source":v.get("created_from","")}
                for k,v in pr_list.items()]
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("Koi PR nahi.")

    elif rep.startswith("2"):
        rows = [{"PO #":k,"Supplier":v.get("supplier_name",""),"SO":v.get("so_ref",""),
                 "Total":f"₹{v.get('total',0):,.0f}","Delivery":v.get("delivery_date",""),
                 "Status":v.get("status","")}
                for k,v in po_list.items()]
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("Koi PO nahi.")

    elif rep.startswith("3"):
        rows = [{"JWO #":k,"Processor":v.get("processor_name",""),"SO":v.get("so_ref",""),
                 "Total":f"₹{v.get('total',0):,.0f}","Expected":v.get("expected_date",""),
                 "Status":v.get("status","")}
                for k,v in jwo_list.items()]
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("Koi JWO nahi.")

    elif rep.startswith("4"):
        sup_summary = {}
        for po_no, po in po_list.items():
            s = po.get("supplier_name","Unknown")
            if s not in sup_summary: sup_summary[s] = {"po_count":0,"total":0}
            sup_summary[s]["po_count"] += 1
            sup_summary[s]["total"] += po.get("total",0)
        rows = [{"Supplier":k,"PO Count":v["po_count"],"Total Value":f"₹{v['total']:,.0f}"}
                for k,v in sup_summary.items()]
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("Koi data nahi.")

    elif rep.startswith("5"):
        mat_summary = {}
        for po in po_list.values():
            for ln in po.get("lines",[]):
                c = ln["material_code"]
                if c not in mat_summary: mat_summary[c] = {"name":ln["material_name"],"qty":0,"amount":0}
                mat_summary[c]["qty"]    += ln.get("po_qty",0)
                mat_summary[c]["amount"] += ln.get("amount",0)
        rows = [{"Code":k,"Material":v["name"],"Total Qty":v["qty"],"Total Amount":f"₹{v['amount']:,.0f}"}
                for k,v in mat_summary.items()]
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("Koi data nahi.")

    elif rep.startswith("6"):
        rows = []
        for po_no, po in po_list.items():
            if po.get("status") in ["Sent to Supplier","Confirmed","Partial Received"]:
                for ln in po.get("lines",[]):
                    pending = ln["po_qty"] - ln.get("received_qty",0)
                    if pending > 0:
                        rows.append({"PO #":po_no,"Supplier":po.get("supplier_name",""),
                                     "Material":ln["material_name"],"PO Qty":ln["po_qty"],
                                     "Received":ln.get("received_qty",0),"Pending":pending,
                                     "Unit":ln["unit"],"Due":po.get("delivery_date","")})
        for jwo_no, jwo in jwo_list.items():
            if jwo.get("status") in ["Issued to Processor","In Process","Partial Received"]:
                for ln in jwo.get("lines",[]):
                    pending = ln["output_qty"] - float(ln.get("received_qty",0))
                    if pending > 0:
                        rows.append({"PO #":jwo_no,"Supplier":jwo.get("processor_name",""),
                                     "Material":ln["output_name"],"PO Qty":ln["output_qty"],
                                     "Received":ln.get("received_qty",0),"Pending":pending,
                                     "Unit":ln["output_unit"],"Due":jwo.get("expected_date","")})
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.markdown('<div class="ok-box">Koi pending receipt nahi!</div>', unsafe_allow_html=True)

    elif rep.startswith("7"):
        rows = [{"GRN #":k,"Date":v.get("grn_date",""),"Type":v.get("grn_type",""),
                 "Ref":v.get("ref_no",""),"Items":len(v.get("lines",[])),"Status":v.get("status","")}
                for k,v in grn_list.items()]
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else: st.info("Koi GRN nahi.")
