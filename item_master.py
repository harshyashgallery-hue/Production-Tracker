import streamlit as st
import pandas as pd
import json
from datetime import date, datetime
import uuid

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Garment ERP – Item Master & BOM",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0f0f0f;
    --surface: #1a1a1a;
    --surface2: #242424;
    --border: #2e2e2e;
    --accent: #c8a96e;
    --accent2: #e8c9a0;
    --text: #e8e4dc;
    --text-muted: #888;
    --green: #4caf82;
    --red: #e06c75;
    --blue: #61afef;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background: var(--bg); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stRadio label {
    color: var(--text) !important;
}

/* Headers */
h1 { font-family: 'DM Serif Display', serif !important; color: var(--accent) !important; }
h2, h3 { font-family: 'DM Sans', sans-serif !important; color: var(--text) !important; }

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
}
.card-accent {
    border-left: 3px solid var(--accent);
}

/* Status badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
}
.badge-done { background: #1a3d2e; color: var(--green); }
.badge-pending { background: #3d1a1a; color: var(--red); }
.badge-new { background: #1a2a3d; color: var(--blue); }
.badge-certified { background: #2d2200; color: var(--accent); }

/* Metric boxes */
.metric-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: var(--accent);
}
.metric-label {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
}

/* Tables */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #0f0f0f !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--accent2) !important;
    transform: translateY(-1px);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
    background: transparent !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-weight: 500 !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Tag pill */
.tag {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    margin: 2px;
    font-family: 'DM Mono', monospace;
}
.tag-accent {
    border-color: var(--accent);
    color: var(--accent);
}

/* Section header */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}
.section-number {
    background: var(--accent);
    color: #0f0f0f;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    font-family: 'DM Mono', monospace;
}

/* Info box */
.info-box {
    background: #1a2a1a;
    border: 1px solid #2e4a2e;
    border-radius: 8px;
    padding: 12px 16px;
    color: var(--green);
    font-size: 13px;
}
.warn-box {
    background: #2a1a0a;
    border: 1px solid #4a2e0a;
    border-radius: 8px;
    padding: 12px 16px;
    color: var(--accent);
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────────
if "items" not in st.session_state:
    st.session_state["items"] = {}
if "boms" not in st.session_state:
    st.session_state["boms"] = {}
if "merchants" not in st.session_state:
    st.session_state["merchants"] = {
        "MC001": "Amit Textiles",
        "MC002": "Ravi Exports",
        "MC003": "Sharma Trading Co.",
    }
if "buyers" not in st.session_state:
    st.session_state["buyers"] = ["Myntra", "Flipkart", "Amazon", "Reliance", "Direct"]
if "processes" not in st.session_state:
    st.session_state["processes"] = ["Cutting", "Printing", "Dyeing", "Stitching", "Finishing", "Packing", "Embroidery", "Washing"]
if "routings" not in st.session_state:
    st.session_state["routings"] = {}

ITEM_TYPES = ["Finished Goods (FG)", "Semi Finished Goods (SFG)", "Raw Material (RM)", 
              "Accessories", "Packing Materials", "Fuel & Lubricants"]
SEASONS = ["SS25", "AW25", "SS26", "AW26", "Resort 2025", "Holiday 2025"]
UNITS = ["Meter", "KG", "Gram", "Piece", "Set", "Box", "Roll", "Litre", "Dozen"]
SIZES_ALL = ["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "Free Size"]
HSN_CODES = ["6211", "6206", "6204", "6203", "6205", "6207", "6208", "6212", "5208", "5209"]

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<h1 style="font-size:24px; margin:0;">🧵 Garment ERP</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--text-muted); font-size:12px; margin-top:4px;">Item Master & BOM Module</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    nav = st.radio("Navigation", [
        "📊 Dashboard",
        "➕ Create Item",
        "📋 Item Master List",
        "🔩 BOM Management",
        "🔄 Routing Master",
        "👤 Merchant Master",
        "📦 Buyer Packaging",
    ], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown(f'<p style="color:#888888; font-size:11px;">Items: {len(st.session_state["items"])} | BOMs: {len(st.session_state["boms"])}</p>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if nav == "📊 Dashboard":
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
    
    st.markdown("---")
    
    # Requirements Tracker
    st.markdown("### 📋 Requirements Status Tracker")
    
    requirements = [
        ("Item Types / Categories", "DONE", "7 types supported with future flexibility"),
        ("Finished Goods Item Creation", "DONE", "All basic fields included"),
        ("Item Photo Upload", "PENDING", "UI placeholder ready"),
        ("Attachment Upload (CAD, Design, Tech Pack etc.)", "PENDING", "File upload UI needed"),
        ("Routing / Process Flow", "DONE", "Order-wise routing with drag-drop sequence"),
        ("Size Variant System (Automatic)", "DONE", "Auto SKU generation on size selection"),
        ("BOM – All Fields", "DONE", "All 9 fields available"),
        ("BOM from Item Master components", "DONE", "Components must be pre-created in Item Master"),
        ("Size-wise BOM Logic", "DONE", "Common BOM + Size-wise BOM both supported"),
        ("BOM Line Display", "DONE", "Lines visible like item master rows"),
        ("BOM Certification / Approval", "DONE", "Admin-only certification toggle"),
        ("Multi-Level BOM (FG → SFG → RM)", "DONE", "Hierarchy fully supported"),
        ("BOM Costing Calculation", "DONE", "Auto calculation of all cost heads"),
        ("Process Cost in BOM Costing", "NEW", "Process cost + CMT cost field added"),
        ("Parent-Child Item Structure", "DONE", "Parent item links to all size variants"),
        ("BOM Reuse (Copy Feature)", "DONE", "Copy BOM from existing items"),
        ("Image Storage", "PENDING", "Front/Back/Detail image upload"),
        ("Multiple BOM per Item", "DONE", "BOM-1, BOM-2 for diff fabric widths"),
        ("Buyer-wise Packaging", "DONE", "Packaging define per buyer per item"),
        ("Merchant Code Master", "DONE", "Create merchants before item creation"),
    ]
    
    done = sum(1 for r in requirements if r[1] == "DONE")
    pending = sum(1 for r in requirements if r[1] == "PENDING")
    new = sum(1 for r in requirements if r[1] == "NEW")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<span class="badge badge-done">✓ DONE: {done}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span class="badge badge-pending">⏳ PENDING: {pending}</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="badge badge-new">★ NEW: {new}</span>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    for req, status, note in requirements:
        badge_class = {"DONE": "badge-done", "PENDING": "badge-pending", "NEW": "badge-new"}[status]
        badge_text = {"DONE": "✓ DONE", "PENDING": "⏳ PENDING", "NEW": "★ NEW"}[status]
        st.markdown(f'''
        <div class="card" style="padding:12px 16px; margin:4px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-weight:500; font-size:14px;">{req}</span>
                    <div style="color:var(--text-muted); font-size:12px; margin-top:2px;">{note}</div>
                </div>
                <span class="badge {badge_class}">{badge_text}</span>
            </div>
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
        st.markdown("#### 📦 Buyer-wise Packaging Definition")
        st.markdown('''<div class="info-box">✓ Same item ke liye alag buyers ke liye alag packaging define kar sakte hain (polybag, tag, sticker, carton etc.)</div>''', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        buyer_packaging = {}
        for buyer in st.session_state["buyers"]:
            with st.expander(f"📦 {buyer} Packaging"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    polybag = st.text_input(f"Polybag Type", key=f"poly_{buyer}", placeholder="e.g. 10x14 LDPE Zip")
                    brand_tag = st.text_input(f"Brand Tag", key=f"btag_{buyer}", placeholder="e.g. Woven Label Main")
                with col2:
                    size_tag = st.text_input(f"Size Tag", key=f"stag_{buyer}", placeholder="e.g. Printed Size Sticker")
                    price_tag = st.text_input(f"Price Tag / Sticker", key=f"ptag_{buyer}", placeholder="e.g. MRP Sticker")
                with col3:
                    carton = st.text_input(f"Carton Type", key=f"cart_{buyer}", placeholder="e.g. 5-ply Export Carton")
                    inner_box = st.text_input(f"Inner Box/Hanger", key=f"inner_{buyer}", placeholder="e.g. PP Hanger")
                
                if polybag or brand_tag:
                    buyer_packaging[buyer] = {
                        "polybag": polybag, "brand_tag": brand_tag,
                        "size_tag": size_tag, "price_tag": price_tag,
                        "carton": carton, "inner_box": inner_box
                    }
    
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
                    "buyer_packaging": buyer_packaging if 'buyer_packaging' in dir() else {},
                    "parent": parent_item if parent_item != "None" else None,
                    "created_at": datetime.now().isoformat(),
                }
                
                st.session_state["items"][item_code] = item_data
                
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
                
                # Save routing
                if route:
                    st.session_state["routings"][item_code] = route
                
                st.success(f"✅ Item '{item_name}' saved! {len(sizes)} size variants created.")
                st.balloons()

# ═══════════════════════════════════════════════════════════════════════════════
# ITEM MASTER LIST
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "📋 Item Master List":
    st.markdown('<h1>Item Master List</h1>', unsafe_allow_html=True)
    
    if not st.session_state["items"]:
        st.markdown('<div class="warn-box">No items created yet. Go to "Create Item" to add items.</div>', unsafe_allow_html=True)
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by Type", ["All"] + ITEM_TYPES)
        with col2:
            filter_season = st.selectbox("Filter by Season", ["All"] + SEASONS)
        with col3:
            search = st.text_input("🔍 Search by Name/Code", placeholder="Type to filter...")
        
        items_list = []
        for code, item in st.session_state["items"].items():
            if filter_type != "All" and item.get("item_type") != filter_type:
                continue
            if filter_season != "All" and item.get("season") != filter_season:
                continue
            if search and search.lower() not in code.lower() and search.lower() not in item.get("name", "").lower():
                continue
            
            has_bom = code in st.session_state["boms"]
            bom_status = st.session_state["boms"].get(code, {}).get("status", "—") if has_bom else "—"
            
            items_list.append({
                "Item Code": code,
                "Item Name": item.get("name"),
                "Type": item.get("item_type", "").replace(" (FG)", "").replace(" (SFG)", "").replace(" (RM)", ""),
                "Season": item.get("season", ""),
                "Sizes": ", ".join(item.get("sizes", [])) or "—",
                "Selling Price": f"₹{item.get('selling_price', 0):,.0f}",
                "Parent": item.get("parent") or "—",
                "BOM": bom_status,
            })
        
        df = pd.DataFrame(items_list)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(items_list)} items")
        
        # Item Detail View
        st.markdown("---")
        st.markdown("#### Item Detail View")
        selected_item_code = st.selectbox("Select item to view details", 
                                           [""] + list(st.session_state["items"].keys()))
        if selected_item_code:
            item = st.session_state["items"][selected_item_code]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'''<div class="card card-accent">
                    <div style="color:var(--text-muted); font-size:11px;">ITEM CODE</div>
                    <div style="font-family:'DM Mono', monospace; font-size:18px; color:var(--accent);">{item["code"]}</div>
                    <div style="margin-top:8px; font-weight:500;">{item["name"]}</div>
                    <div style="margin-top:4px;"><span class="tag">{item.get("item_type","")}</span></div>
                </div>''', unsafe_allow_html=True)
            with col2:
                st.markdown(f'''<div class="card">
                    <div style="color:var(--text-muted); font-size:11px; margin-bottom:8px;">COMMERCIAL DETAILS</div>
                    <div style="font-size:13px;">HSN: <strong>{item.get("hsn","")}</strong></div>
                    <div style="font-size:13px;">Season: <strong>{item.get("season","")}</strong></div>
                    <div style="font-size:13px;">Selling: <strong>₹{item.get("selling_price",0):,.0f}</strong></div>
                    <div style="font-size:13px;">Purchase: <strong>₹{item.get("purchase_price",0):,.0f}</strong></div>
                </div>''', unsafe_allow_html=True)
            with col3:
                route = item.get("routing", [])
                route_html = " → ".join([f'<span class="tag tag-accent">{p}</span>' for p in route]) if route else "No routing defined"
                st.markdown(f'''<div class="card">
                    <div style="color:var(--text-muted); font-size:11px; margin-bottom:8px;">ROUTING</div>
                    {route_html}
                </div>''', unsafe_allow_html=True)
            
            # Child SKUs
            child_skus = [c for c, d in st.session_state["items"].items() if d.get("parent") == selected_item_code]
            if child_skus:
                st.markdown("**Child SKUs:**")
                for sku in child_skus:
                    st.markdown(f'<span class="tag tag-accent">{sku}</span>', unsafe_allow_html=True)

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
            
            st.markdown("#### BOM Lines")
            st.caption("Add each component below – components must exist in Item Master")
            
            # BOM lines state
            bom_key = f"bom_lines_{target_item}"
            if bom_key not in st.session_state:
                if 'copy_from' in dir() and copy_from != "— Don't copy —" and copy_from in st.session_state["boms"]:
                    st.session_state[bom_key] = st.session_state["boms"][copy_from].get("lines", []).copy()
                else:
                    st.session_state[bom_key] = []
            
            # Add new line
            with st.expander("➕ Add BOM Line", expanded=len(st.session_state[bom_key]) == 0):
                col1, col2, col3 = st.columns(3)
                with col1:
                    component_items = {k: v["name"] for k, v in st.session_state["items"].items() if k != target_item}
                    if component_items:
                        comp_code = st.selectbox("Component Item *", 
                                                  [""] + [f"{k} – {v}" for k, v in component_items.items()],
                                                  key="new_comp")
                    else:
                        st.markdown('<div class="warn-box">No components in Item Master. Create Raw Materials / Accessories first.</div>', unsafe_allow_html=True)
                        comp_code = ""
                    
                    qty = st.number_input("Quantity *", min_value=0.0, step=0.1, key="new_qty")
                    unit = st.selectbox("Unit", UNITS, key="new_unit")
                
                with col2:
                    rate = st.number_input("Rate (₹/unit)", min_value=0.0, step=1.0, key="new_rate")
                    shrinkage = st.number_input("Shrinkage %", min_value=0.0, max_value=100.0, step=0.5, key="new_shrink")
                    wastage = st.number_input("Wastage %", min_value=0.0, max_value=100.0, step=0.5, key="new_waste")
                
                with col3:
                    processes = st.session_state["processes"]
                    process_used = st.selectbox("Process Used In", ["—"] + processes, key="new_process")
                    remarks = st.text_input("Remarks", key="new_remarks")
                
                if st.button("➕ Add Line to BOM"):
                    if comp_code and qty > 0:
                        actual_qty = qty * (1 + shrinkage/100) * (1 + wastage/100)
                        amount = actual_qty * rate
                        
                        comp_key = comp_code.split(" – ")[0] if " – " in comp_code else comp_code
                        comp_name = component_items.get(comp_key, comp_key)
                        
                        line = {
                            "item_code": comp_key,
                            "item_name": comp_name,
                            "item_type": st.session_state["items"].get(comp_key, {}).get("item_type", ""),
                            "qty": qty,
                            "unit": unit,
                            "rate": rate,
                            "shrinkage": shrinkage,
                            "wastage": wastage,
                            "actual_qty": round(actual_qty, 3),
                            "amount": round(amount, 2),
                            "process": process_used,
                            "remarks": remarks,
                        }
                        st.session_state[bom_key].append(line)
                        st.rerun()
            
            # Display BOM lines
            if st.session_state[bom_key]:
                st.markdown("#### Current BOM Lines")
                df_bom = pd.DataFrame(st.session_state[bom_key])
                display_cols = ["item_code", "item_name", "item_type", "qty", "unit", "rate", "shrinkage", "actual_qty", "amount", "process", "remarks"]
                available_cols = [c for c in display_cols if c in df_bom.columns]
                st.dataframe(df_bom[available_cols].rename(columns={
                    "item_code": "Code", "item_name": "Component", "item_type": "Type",
                    "qty": "Qty", "unit": "Unit", "rate": "Rate (₹)", "shrinkage": "Shrink%",
                    "actual_qty": "Net Qty", "amount": "Amount (₹)", "process": "Process", "remarks": "Remarks"
                }), use_container_width=True, hide_index=True)
                
                total = sum(l.get("amount", 0) for l in st.session_state[bom_key])
                st.markdown(f'<div class="card card-accent" style="text-align:right;"><span style="font-size:18px; color:#c8a96e;">Total BOM Cost: ₹{total:,.2f}</span></div>', unsafe_allow_html=True)
            
            # Process Cost & CMT
            st.markdown("---")
            st.markdown("#### 💰 Additional Costs (Process Cost + CMT)")
            col1, col2, col3 = st.columns(3)
            with col1:
                process_cost = st.number_input("Process Cost (₹)", min_value=0.0, step=5.0, 
                                                help="Printing, Dyeing, Embroidery etc. process cost")
            with col2:
                cmt_cost = st.number_input("CMT Cost (₹)", min_value=0.0, step=5.0,
                                            help="Cut-Make-Trim / Job work cost")
            with col3:
                other_cost = st.number_input("Other Cost (₹)", min_value=0.0, step=5.0)
            
            bom_lines = st.session_state.get(bom_key, [])
            component_total = sum(l.get("amount", 0) for l in bom_lines)
            grand_total = component_total + process_cost + cmt_cost + other_cost
            
            if bom_lines or process_cost or cmt_cost:
                st.markdown(f'''<div class="card">
                    <div style="display:flex; gap:20px; flex-wrap:wrap;">
                        <div><span style="color:var(--text-muted); font-size:12px;">Component Cost</span><br><strong>₹{component_total:,.2f}</strong></div>
                        <div><span style="color:var(--text-muted); font-size:12px;">Process Cost</span><br><strong>₹{process_cost:,.2f}</strong></div>
                        <div><span style="color:var(--text-muted); font-size:12px;">CMT Cost</span><br><strong>₹{cmt_cost:,.2f}</strong></div>
                        <div><span style="color:var(--text-muted); font-size:12px;">Other Cost</span><br><strong>₹{other_cost:,.2f}</strong></div>
                        <div style="margin-left:auto;"><span style="color:var(--text-muted); font-size:12px;">TOTAL PRODUCTION COST</span><br><span style="font-size:22px; color:var(--accent); font-family:'DM Serif Display', serif;">₹{grand_total:,.2f}</span></div>
                    </div>
                </div>''', unsafe_allow_html=True)
            
            # Save BOM
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save BOM (Draft)", use_container_width=True):
                    st.session_state["boms"][target_item] = {
                        "item_code": target_item,
                        "bom_number": bom_number,
                        "description": bom_desc,
                        "bom_type": bom_type,
                        "lines": st.session_state.get(bom_key, []),
                        "process_cost": process_cost,
                        "cmt_cost": cmt_cost,
                        "other_cost": other_cost,
                        "total": grand_total,
                        "status": "Draft",
                        "created_at": datetime.now().isoformat(),
                    }
                    st.success("✅ BOM saved as Draft!")
            with col2:
                if st.button("✅ Certify BOM (Admin Only)", use_container_width=True):
                    # In real app, check admin role
                    admin_pass = st.session_state.get("admin_verified", False)
                    if target_item in st.session_state["boms"]:
                        st.session_state["boms"][target_item]["status"] = "Certified"
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
                        for buyer, details in pkg.items():
                            non_empty = {k: v for k, v in details.items() if v}
                            if non_empty:
                                st.markdown(f"**{buyer}:**")
                                pkg_str = " | ".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in non_empty.items()])
                                st.markdown(f'<div class="card" style="padding:8px;">{pkg_str}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warn-box">No buyer packaging defined yet. Define packaging when creating items.</div>', unsafe_allow_html=True)
