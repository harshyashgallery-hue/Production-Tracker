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
]
IM_PAGES  = [p for m, p in ALL_PAGES if m == "IM"]
SO_PAGES  = [p for m, p in ALL_PAGES if m == "SO"]
MRP_PAGES = [p for m, p in ALL_PAGES if m == "MRP"]

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
                if 'copy_from' in dir() and copy_from != "\u2014 Don't copy \u2014" and copy_from in st.session_state["boms"]:
                    st.session_state[bom_key]  = st.session_state["boms"][copy_from].get("lines", []).copy()
                    st.session_state[proc_key] = st.session_state["boms"][copy_from].get("process_lines", []).copy()
                else:
                    st.session_state[bom_key]  = []
                    st.session_state[proc_key] = []

            if proc_key not in st.session_state:
                st.session_state[proc_key] = []

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

            # Check if this component is SFG/FG with its own BOM — recurse
            has_sub_bom = comp_code in boms and len(boms[comp_code].get("lines", [])) > 0
            comp_is_intermediate = comp_type in ["Semi Finished Goods (SFG)", "Finished Goods (FG)"]

            if has_sub_bom and comp_is_intermediate:
                # Go deeper — explode this component's BOM
                explode_bom(comp_code, total_qty, so_no, sku, buyer, depth+1)
            else:
                # Leaf node — this is raw material / accessory
                if comp_code not in result:
                    result[comp_code] = {
                        "name": comp_name, "type": comp_type,
                        "unit": unit, "total_req": 0,
                        "stock": float(comp_item.get("stock", 0)),
                        "reserved": float(comp_item.get("reserved", 0)),
                        "breakdown": []
                    }
                result[comp_code]["total_req"] = round(result[comp_code]["total_req"] + total_qty, 3)
                result[comp_code]["breakdown"].append({
                    "so_no": so_no, "sku": sku, "qty_req": total_qty,
                    "source": f"BOM: {item_code} (Level {depth})"
                })

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

    # Calculate net requirement
    for code, mat in result.items():
        avail = mat["stock"] - mat["reserved"]
        mat["available"] = max(0, avail)
        mat["net_req"]   = max(0, round(mat["total_req"] - avail, 3))

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
            rows.append({
                "Material Code": code,
                "Material Name": mat["name"],
                "Type":          mat["type"],
                "Unit":          mat["unit"],
                "Total Required": mat["total_req"],
                "In Stock":       mat["stock"],
                "Reserved":       mat["reserved"],
                "Available":      mat["available"],
                "Net Requirement": mat["net_req"],
                "Status":         "🔴 Shortage" if shortage else "🟢 OK",
            })

        if rows:
            df_mrp = pd.DataFrame(rows)
            st.dataframe(df_mrp, use_container_width=True, hide_index=True)

            # Summary KPIs
            shortage_count = sum(1 for r in rows if r["Net Requirement"] > 0)
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
    st.markdown('<h1>Material Reservations</h1>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Material requirements ke basis pe stock reserve karo — reserved stock available stock mein count nahi hoga future MRP mein.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not SS.get("mrp_result"):
        st.markdown('<div class="warn-box">Pehle MRP run karo "▶ Run MRP" se.</div>', unsafe_allow_html=True)
    else:
        mrp_result = SS["mrp_result"]
        items_data = st.session_state.get("items", {})

        if "reservations" not in SS:
            SS["reservations"] = {}

        # Reserve all button
        if st.button("🔒 Reserve All Available Stock for MRP", use_container_width=False):
            for code, mat in mrp_result.items():
                if mat["available"] > 0 and mat["net_req"] > 0:
                    reserve_qty = min(mat["available"], mat["total_req"])
                    if code in items_data:
                        current_res = float(items_data[code].get("reserved", 0))
                        st.session_state["items"][code]["reserved"] = current_res + reserve_qty
                    # Track reservation
                    SS["reservations"][code] = {
                        "material_name": mat["name"],
                        "reserved_qty": reserve_qty,
                        "unit": mat["unit"],
                        "mrp_run": SS.get("mrp_run_time",""),
                        "so_list": SS.get("mrp_so_list",[]),
                    }
            save_data()
            st.success("✅ Stock reserved!")
            st.rerun()

        # Reservation table
        res_rows = []
        for code, mat in mrp_result.items():
            item = items_data.get(code, {})
            reserved = float(item.get("reserved", 0))
            res_rows.append({
                "Material Code": code,
                "Material Name": mat["name"],
                "Total Required": mat["total_req"],
                "In Stock":       mat["stock"],
                "Reserved":       reserved,
                "Available":      max(0, mat["stock"] - reserved),
                "Net Req":        max(0, mat["total_req"] - max(0, mat["stock"] - reserved)),
                "Unit":           mat["unit"],
            })

        if res_rows:
            st.dataframe(pd.DataFrame(res_rows), use_container_width=True, hide_index=True)

            # Manual reserve
            st.markdown("---")
            st.markdown("#### Manual Reservation")
            r1, r2, r3 = st.columns(3)
            with r1:
                res_mat = st.selectbox("Material", [""] + list(mrp_result.keys()),
                                        format_func=lambda x: f"{x} – {mrp_result[x]['name']}" if x else "Select",
                                        key="res_mat")
            with r2:
                res_qty = st.number_input("Reserve Qty", min_value=0.0, step=1.0, key="res_qty")
            with r3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔒 Reserve", use_container_width=True) and res_mat and res_qty > 0:
                    if res_mat in items_data:
                        current = float(st.session_state["items"][res_mat].get("reserved", 0))
                        st.session_state["items"][res_mat]["reserved"] = current + res_qty
                        save_data()
                        st.success(f"✅ {res_qty} {mrp_result[res_mat]['unit']} reserved for {res_mat}!")
                        st.rerun()


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
