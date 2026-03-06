import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import base64, io

st.set_page_config(page_title="Item Master – Yash Gallery", page_icon="🏭", layout="wide")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Outfit', sans-serif; }
.stApp { background: #f0f2f6; }

.page-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #0f4c81 100%);
    color: white; padding: 24px 32px; border-radius: 14px;
    margin-bottom: 24px; position: relative; overflow: hidden;
}
.page-header::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 180px; height: 180px; border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.page-header h1 { margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px; }
.page-header p  { margin: 6px 0 0; opacity: 0.7; font-size: 14px; }

.card {
    background: white; border-radius: 12px; padding: 20px 24px;
    border: 1px solid #e2e8f0; margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card-title {
    font-size: 13px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #64748b; margin-bottom: 16px;
    padding-bottom: 10px; border-bottom: 2px solid #f1f5f9;
}
.step-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 28px; height: 28px; border-radius: 50%;
    background: #0f4c81; color: white; font-size: 13px;
    font-weight: 700; margin-right: 8px;
}
.sku-chip {
    display: inline-block; background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 6px; padding: 4px 10px; font-size: 12px;
    font-family: 'JetBrains Mono', monospace; color: #1d4ed8;
    margin: 3px; font-weight: 600;
}
.bom-row-header {
    background: #f8fafc; border-radius: 8px; padding: 8px 12px;
    font-size: 12px; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 0.5px;
    display: grid; grid-template-columns: 2fr 1.2fr 0.8fr 0.8fr 0.8fr 1fr 0.8fr 0.8fr;
    gap: 8px; margin-bottom: 4px;
}
.cost-summary {
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    color: white; border-radius: 10px; padding: 16px 20px; margin-top: 12px;
}
.cost-row { display: flex; justify-content: space-between; padding: 4px 0;
            font-size: 14px; opacity: 0.85; }
.cost-total { display: flex; justify-content: space-between; padding: 10px 0 4px;
              font-size: 18px; font-weight: 800; border-top: 1px solid rgba(255,255,255,0.2);
              margin-top: 6px; }
.type-badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 11px; font-weight: 600;
}
.type-FG   { background:#dcfce7; color:#166534; }
.type-SFG  { background:#dbeafe; color:#1e40af; }
.type-RM   { background:#fef9c3; color:#854d0e; }
.type-ACC  { background:#fce7f3; color:#9d174d; }
.type-PKG  { background:#f3e8ff; color:#6b21a8; }
.type-FUEL { background:#fee2e2; color:#991b1b; }

.item-card {
    background: white; border-radius: 10px; border: 1px solid #e2e8f0;
    padding: 14px; transition: box-shadow 0.2s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.item-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
.item-code { font-family: 'JetBrains Mono', monospace; font-size: 11px;
             color: #0f4c81; font-weight: 600; }

div[data-testid="stTabs"] button { font-weight: 600; font-size: 14px; }
.stButton > button {
    border-radius: 8px; font-weight: 600; font-size: 14px;
    transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-1px); }
div[data-testid="stDataFrame"] { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Google Sheets Connection ───────────────────────────────────────────────────
SHEET_ID = "1ak6e6_0O8CZMcjYaILtPe0ENnygWbvuOenkGclFVloY"
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_TABS = {
    "Items":     ["ItemCode","ItemName","ItemType","Category","MerchantCode",
                  "HSNCode","Season","LaunchDate","ParentItem","SellingPrice",
                  "PurchasePrice","Routing","SizeVariants","PhotoURL","Attachments",
                  "CreatedAt","UpdatedAt","Status"],
    "BOM":       ["BOMId","ItemCode","BOMName","FabricWidth","IsDefault",
                  "ComponentCode","ComponentName","ComponentType","Qty","Unit",
                  "Rate","Amount","ProcessName","Shrinkage","Wastage","Remarks","CreatedAt"],
    "SKUs":      ["SKUCode","ParentItemCode","Size","SellingPrice","PurchasePrice","Status"],
    "Routing":   ["RoutingName","ProcessList","CreatedAt"],
}

@st.cache_resource
def get_gsheet_client():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

def get_or_create_sheet(client, tab_name):
    try:
        sh = client.open_by_key(SHEET_ID)
        try:
            ws = sh.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=tab_name, rows=1000, cols=30)
            headers = SHEET_TABS.get(tab_name, [])
            if headers:
                ws.append_row(headers)
        return ws
    except Exception as e:
        st.error(f"Sheet error: {e}")
        return None

@st.cache_data(ttl=30)
def read_sheet(tab_name):
    client = get_gsheet_client()
    if not client:
        return pd.DataFrame()
    ws = get_or_create_sheet(client, tab_name)
    if not ws:
        return pd.DataFrame()
    try:
        data = ws.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame(columns=SHEET_TABS.get(tab_name,[]))
    except:
        return pd.DataFrame(columns=SHEET_TABS.get(tab_name,[]))

def write_row(tab_name, row_dict):
    client = get_gsheet_client()
    if not client:
        st.error("Google Sheets not connected!")
        return False
    ws = get_or_create_sheet(client, tab_name)
    if not ws:
        return False
    headers = SHEET_TABS.get(tab_name, list(row_dict.keys()))
    row = [str(row_dict.get(h, '')) for h in headers]
    ws.append_row(row)
    read_sheet.clear()
    return True

def update_row(tab_name, key_col, key_val, updates):
    client = get_gsheet_client()
    if not client: return False
    ws = get_or_create_sheet(client, tab_name)
    if not ws: return False
    try:
        cell = ws.find(str(key_val))
        headers = ws.row_values(1)
        for col_name, val in updates.items():
            if col_name in headers:
                col_idx = headers.index(col_name) + 1
                ws.update_cell(cell.row, col_idx, str(val))
        read_sheet.clear()
        return True
    except:
        return False

def delete_row(tab_name, key_col, key_val):
    client = get_gsheet_client()
    if not client: return False
    ws = get_or_create_sheet(client, tab_name)
    if not ws: return False
    try:
        headers = ws.row_values(1)
        col_idx = headers.index(key_col) + 1
        col_values = ws.col_values(col_idx)
        if str(key_val) in col_values:
            row_idx = col_values.index(str(key_val)) + 1
            ws.delete_rows(row_idx)
        read_sheet.clear()
        return True
    except:
        return False

# ── Helpers ────────────────────────────────────────────────────────────────────
ITEM_TYPES = {
    "FG":   "Finished Goods",
    "SFG":  "Semi Finished Goods",
    "RM":   "Raw Material",
    "ACC":  "Accessories",
    "PKG":  "Packing Material",
    "FUEL": "Fuel & Lubricants",
}
ITEM_CATEGORIES = {
    "FG":   ["Kurta","Kurta Set","Dress","Blouse","Pant","Dupatta","Suit Set","Other FG"],
    "SFG":  ["Printed Fabric","Dyed Fabric","Cut Panels","Embroidered Fabric","Other SFG"],
    "RM":   ["Grey Fabric","Base Fabric","Lining Fabric","Other RM"],
    "ACC":  ["Button","Zipper","Lace","Hook","Elastic","Thread","Other ACC"],
    "PKG":  ["Polybag","Brand Tag","Size Tag","Carton","Tissue","Hanger","Other PKG"],
    "FUEL": ["Diesel","Machine Oil","Gas","Other Fuel"],
}
SIZES_STANDARD = ["XS","S","M","L","XL","XXL","3XL","4XL","5XL","6XL","7XL","8XL"]
SIZES_KIDS     = ["7-8 Years","9-10 Years","11-12 Years","13-14 Years"]
UNITS          = ["Meter","Kg","Gram","Piece","Set","Dozen","Litre","Roll","Box"]
PROCESSES      = ["Modal Shout","Dyeing","Printing","Fabric Check","Re Process",
                  "Cutting","Gola Cutting","Embroidary","5 Threads","Stitching",
                  "Alteration","Kaaz Button","Fabric Button","Handwork","Finishing",
                  "Stitch to Pack","Washing","Packing"]

def generate_item_code(item_type, category, existing_codes):
    prefix = f"YG-{item_type}"
    cat_short = category[:3].upper().replace(" ","")
    nums = [int(re.search(r'\d+$', c).group())
            for c in existing_codes
            if re.search(r'\d+$', c) and c.startswith(prefix)]
    next_num = (max(nums) + 1) if nums else 1
    return f"{prefix}-{cat_short}-{next_num:03d}"

def generate_skus(item_code, sizes):
    return [f"{item_code}-{s.replace(' ','-')}" for s in sizes]

def calc_bom_cost(bom_rows):
    cost_by_process = {}
    total = 0
    for r in bom_rows:
        try:
            qty  = float(r.get('Qty', 0))
            rate = float(r.get('Rate', 0))
            shrink = float(r.get('Shrinkage', 0)) / 100
            actual_qty = qty * (1 + shrink)
            amt = actual_qty * rate
            proc = r.get('ProcessName','Other') or 'Other'
            cost_by_process[proc] = cost_by_process.get(proc, 0) + amt
            total += amt
        except:
            pass
    return cost_by_process, total

# ── Session state ─────────────────────────────────────────────────────────────
if 'bom_rows' not in st.session_state:
    st.session_state.bom_rows = [{}]
if 'size_bom' not in st.session_state:
    st.session_state.size_bom = {}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>🏭 Item Master & BOM Module</h1>
    <p>Yash Gallery Private Limited — ERP System</p>
</div>
""", unsafe_allow_html=True)

# ── Check connection ──────────────────────────────────────────────────────────
client = get_gsheet_client()
if not client:
    st.error("""
    ⚠️ **Google Sheets connected nahi hai!**

    Streamlit Cloud pe `secrets.toml` setup karna hoga:

    1. Streamlit Cloud → App Settings → **Secrets**
    2. Yeh paste karo:
    ```toml
    [gcp_service_account]
    type = "service_account"
    project_id = "your-project-id"
    private_key_id = "..."
    private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
    client_email = "your-service@project.iam.gserviceaccount.com"
    client_id = "..."
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    ```
    3. Google Cloud Console se **Service Account** banao aur Sheet share karo us email pe.
    """)
    st.info("👉 Setup guide chahiye? Batao — step by step bata dunga.")
    st.stop()

# ── Main Tabs ─────────────────────────────────────────────────────────────────
tab_create, tab_list, tab_bom, tab_skus = st.tabs([
    "➕ Create Item", "📋 Item List", "🔧 BOM Manager", "📦 SKU List"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Create Item
# ══════════════════════════════════════════════════════════════════════════════
with tab_create:
    st.markdown("### <span class='step-badge'>1</span> Basic Details", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Item Information</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            item_type_key = st.selectbox("Item Type *", list(ITEM_TYPES.keys()),
                                          format_func=lambda x: f"{x} – {ITEM_TYPES[x]}")
        with c2:
            category = st.selectbox("Category *", ITEM_CATEGORIES.get(item_type_key, ["Other"]))
        with c3:
            # Auto code
            existing_df = read_sheet("Items")
            existing_codes = existing_df['ItemCode'].tolist() if not existing_df.empty and 'ItemCode' in existing_df.columns else []
            auto_code = generate_item_code(item_type_key, category, existing_codes)
            code_mode = st.radio("Item Code", ["Auto", "Manual"], horizontal=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if code_mode == "Auto":
                item_code = st.text_input("Item Code", value=auto_code, disabled=True)
            else:
                item_code = st.text_input("Item Code *", placeholder="YG-FG-KUR-001")
        with c2:
            item_name = st.text_input("Item Name / Style Name *", placeholder="e.g. 1557YKRED Kurta")
        with c3:
            merchant_code = st.text_input("Merchant Code", placeholder="MC-001")

        c1, c2, c3, c4 = st.columns(4)
        with c1: hsn_code     = st.text_input("HSN Code", placeholder="62044200")
        with c2: season       = st.text_input("Season", placeholder="SS-2026")
        with c3: launch_date  = st.date_input("Launch Date")
        with c4:
            parent_items = [""] + (existing_df['ItemCode'].tolist()
                                    if not existing_df.empty and 'ItemCode' in existing_df.columns else [])
            parent_item  = st.selectbox("Parent Item", parent_items)

        c1, c2 = st.columns(2)
        with c1: selling_price  = st.number_input("Selling Price (₹)", min_value=0.0, step=0.5)
        with c2: purchase_price = st.number_input("Purchase Price (₹)", min_value=0.0, step=0.5)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Photo Upload ──────────────────────────────────────────────────────────
    st.markdown("### <span class='step-badge'>2</span> Photos & Attachments", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Images</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            front_img = st.file_uploader("Front Image", type=['jpg','jpeg','png','webp'], key="front")
            if front_img: st.image(front_img, caption="Front", use_container_width=True)
        with c2:
            back_img  = st.file_uploader("Back Image",  type=['jpg','jpeg','png','webp'], key="back")
            if back_img:  st.image(back_img,  caption="Back",  use_container_width=True)
        with c3:
            detail_img = st.file_uploader("Detail Image", type=['jpg','jpeg','png','webp'], key="detail")
            if detail_img: st.image(detail_img, caption="Detail", use_container_width=True)

        st.markdown('<div class="card-title" style="margin-top:16px">Attachments</div>', unsafe_allow_html=True)
        attach_cols = st.columns(4)
        attach_types = ["CAD File","Design Sheet","Tech Pack","Artwork"]
        attachments = {}
        for i, atype in enumerate(attach_types):
            with attach_cols[i]:
                f = st.file_uploader(atype, key=f"attach_{i}")
                if f: attachments[atype] = f.name
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Routing ───────────────────────────────────────────────────────────────
    st.markdown("### <span class='step-badge'>3</span> Process Routing", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Production Routing</div>', unsafe_allow_html=True)
        selected_processes = st.multiselect(
            "Select processes in order",
            PROCESSES,
            default=["Cutting","Stitching","Finishing","Packing"] if item_type_key == "FG" else []
        )
        if selected_processes:
            st.markdown(" → ".join([f"**{p}**" for p in selected_processes]))
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Size Variants ─────────────────────────────────────────────────────────
    if item_type_key in ["FG", "SFG"]:
        st.markdown("### <span class='step-badge'>4</span> Size Variants", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Auto SKU Generation</div>', unsafe_allow_html=True)
            size_group = st.radio("Size Group", ["Adult Sizes","Kids Sizes","Custom","Not Applicable"], horizontal=True)
            if size_group == "Adult Sizes":
                selected_sizes = st.multiselect("Select Sizes", SIZES_STANDARD, default=["S","M","L","XL","XXL"])
            elif size_group == "Kids Sizes":
                selected_sizes = st.multiselect("Select Sizes", SIZES_KIDS, default=SIZES_KIDS)
            elif size_group == "Custom":
                custom = st.text_input("Enter sizes (comma separated)", placeholder="S,M,L,XL,Free Size")
                selected_sizes = [s.strip() for s in custom.split(",") if s.strip()]
            else:
                selected_sizes = []

            if selected_sizes and item_code:
                skus = generate_skus(item_code, selected_sizes)
                st.markdown("**Auto-generated SKUs:**")
                sku_html = "".join([f'<span class="sku-chip">{s}</span>' for s in skus])
                st.markdown(sku_html, unsafe_allow_html=True)
            else:
                skus = []
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        selected_sizes, skus = [], []

    # ── Save Button ───────────────────────────────────────────────────────────
    st.markdown("---")
    col_save, col_reset = st.columns([1, 4])
    with col_save:
        save_btn = st.button("💾 Save Item", type="primary", use_container_width=True)

    if save_btn:
        if not item_name.strip():
            st.error("Item Name is required!")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item_row = {
                "ItemCode": item_code, "ItemName": item_name,
                "ItemType": item_type_key, "Category": category,
                "MerchantCode": merchant_code, "HSNCode": hsn_code,
                "Season": season, "LaunchDate": str(launch_date),
                "ParentItem": parent_item, "SellingPrice": selling_price,
                "PurchasePrice": purchase_price,
                "Routing": " → ".join(selected_processes),
                "SizeVariants": ", ".join(selected_sizes),
                "PhotoURL": "", "Attachments": json.dumps(attachments),
                "CreatedAt": now, "UpdatedAt": now, "Status": "Active"
            }
            ok = write_row("Items", item_row)
            if ok:
                # Save SKUs
                for sku, size in zip(skus, selected_sizes):
                    write_row("SKUs", {
                        "SKUCode": sku, "ParentItemCode": item_code,
                        "Size": size, "SellingPrice": selling_price,
                        "PurchasePrice": purchase_price, "Status": "Active"
                    })
                st.success(f"✅ Item **{item_code}** saved! {len(skus)} SKUs created.")
                st.balloons()
            else:
                st.error("Save failed. Check Google Sheets connection.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – Item List
# ══════════════════════════════════════════════════════════════════════════════
with tab_list:
    items_df = read_sheet("Items")

    if items_df.empty:
        st.info("Koi item nahi mila. Pehle item create karo.")
    else:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            f_type = st.multiselect("Filter: Item Type", list(ITEM_TYPES.keys()),
                                     format_func=lambda x: f"{x} – {ITEM_TYPES[x]}")
        with fc2:
            f_status = st.selectbox("Status", ["All","Active","Inactive"])
        with fc3:
            f_search = st.text_input("🔍 Search", placeholder="Item code or name...")

        disp = items_df.copy()
        if f_type:   disp = disp[disp['ItemType'].isin(f_type)]
        if f_status != "All": disp = disp[disp['Status'] == f_status]
        if f_search: disp = disp[disp['ItemCode'].str.contains(f_search, case=False, na=False) |
                                  disp['ItemName'].str.contains(f_search, case=False, na=False)]

        st.markdown(f"**{len(disp)} items found**")

        # Card grid view
        cols_per_row = 3
        rows = [disp.iloc[i:i+cols_per_row] for i in range(0, len(disp), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for col, (_, item) in zip(cols, row.iterrows()):
                with col:
                    itype = item.get('ItemType','')
                    badge_class = f"type-{itype}"
                    st.markdown(f"""
                    <div class="item-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <span class="item-code">{item.get('ItemCode','')}</span>
                            <span class="type-badge {badge_class}">{itype}</span>
                        </div>
                        <div style="font-weight:700;font-size:15px;margin:8px 0 4px;color:#0f172a">
                            {item.get('ItemName','')}
                        </div>
                        <div style="font-size:12px;color:#64748b">{item.get('Category','')}</div>
                        <div style="display:flex;justify-content:space-between;margin-top:10px;
                                    padding-top:8px;border-top:1px solid #f1f5f9">
                            <span style="font-size:12px;color:#64748b">Sell: <b style="color:#0f172a">
                                ₹{item.get('SellingPrice','0')}</b></span>
                            <span style="font-size:12px;color:#64748b">Season: <b style="color:#0f172a">
                                {item.get('Season','–')}</b></span>
                        </div>
                        <div style="margin-top:6px;font-size:11px;color:#94a3b8">
                            Sizes: {item.get('SizeVariants','–')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Full Table View**")
        show_cols = ['ItemCode','ItemName','ItemType','Category','Season',
                     'SellingPrice','SizeVariants','Routing','Status']
        show_cols = [c for c in show_cols if c in disp.columns]
        st.dataframe(disp[show_cols], use_container_width=True, hide_index=True)

        # Download
        csv = disp.to_csv(index=False)
        st.download_button("⬇️ Export CSV", csv, "item_master.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – BOM Manager
# ══════════════════════════════════════════════════════════════════════════════
with tab_bom:
    st.markdown("### BOM (Bill of Materials)")

    items_df = read_sheet("Items")
    bom_df   = read_sheet("BOM")

    if items_df.empty:
        st.info("Pehle items create karo.")
        st.stop()

    # Select item
    bc1, bc2, bc3 = st.columns([2,1,1])
    with bc1:
        fg_items = items_df[items_df['ItemType'].isin(['FG','SFG'])]['ItemCode'].tolist() \
                   if not items_df.empty else []
        bom_item = st.selectbox("Select Item for BOM", [""] + fg_items)
    with bc2:
        bom_name = st.text_input("BOM Name", placeholder="e.g. BOM-56inch")
    with bc3:
        is_default = st.checkbox("Set as Default BOM", value=True)

    if not bom_item:
        st.info("Ek item select karo BOM define karne ke liye.")
        st.stop()

    # Show existing BOMs for this item
    if not bom_df.empty and 'ItemCode' in bom_df.columns:
        existing_boms = bom_df[bom_df['ItemCode'] == bom_item]['BOMName'].unique().tolist()
        if existing_boms:
            st.markdown(f"**Existing BOMs:** " + " | ".join([f"`{b}`" for b in existing_boms]))
            copy_from = st.selectbox("📋 Copy from existing BOM (optional)", [""] + existing_boms)
            if copy_from and st.button("Copy BOM"):
                copy_rows = bom_df[(bom_df['ItemCode']==bom_item) &
                                    (bom_df['BOMName']==copy_from)].to_dict('records')
                st.session_state.bom_rows = copy_rows
                st.success(f"BOM '{copy_from}' copied! Edit karo aur save karo.")

    # BOM type
    item_info = items_df[items_df['ItemCode'] == bom_item].iloc[0] if not items_df.empty else {}
    size_variants = str(item_info.get('SizeVariants','')) if hasattr(item_info, 'get') else ''
    sizes_in_item = [s.strip() for s in size_variants.split(',') if s.strip()]

    bom_type = "Common BOM"
    if sizes_in_item:
        bom_type = st.radio("BOM Type",
                             ["Common BOM (sabhi sizes same)", "Size-wise BOM (alag alag)"],
                             horizontal=True)

    # ── BOM Rows ──────────────────────────────────────────────────────────────
    st.markdown('<div class="card-title" style="margin-top:16px">BOM Components</div>',
                unsafe_allow_html=True)

    all_items_list = items_df['ItemCode'].tolist() if not items_df.empty else []

    def bom_row_editor(key_prefix, num_rows=1):
        if f"{key_prefix}_rows" not in st.session_state:
            st.session_state[f"{key_prefix}_rows"] = [{}] * max(num_rows, 1)
        rows = st.session_state[f"{key_prefix}_rows"]

        header_cols = st.columns([2,1.2,0.7,0.7,0.7,1,0.7,0.7,0.4])
        for col, lbl in zip(header_cols, ["Component","Type","Qty","Unit","Rate(₹)","Process","Shrink%","Remarks","Del"]):
            col.markdown(f"<div style='font-size:11px;font-weight:700;color:#64748b'>{lbl}</div>",
                         unsafe_allow_html=True)

        updated_rows = []
        del_idx = None
        for i, row in enumerate(rows):
            cols = st.columns([2,1.2,0.7,0.7,0.7,1,0.7,0.7,0.4])
            with cols[0]:
                comp_name = st.text_input("", value=row.get('ComponentName',''),
                                           placeholder="Item/Component", key=f"{key_prefix}_cn_{i}",
                                           label_visibility="collapsed")
            with cols[1]:
                comp_type = st.selectbox("", list(ITEM_TYPES.keys()),
                                          index=list(ITEM_TYPES.keys()).index(row.get('ComponentType','RM'))
                                                if row.get('ComponentType','RM') in ITEM_TYPES else 2,
                                          key=f"{key_prefix}_ct_{i}", label_visibility="collapsed")
            with cols[2]:
                qty = st.number_input("", value=float(row.get('Qty',0) or 0),
                                       min_value=0.0, step=0.1,
                                       key=f"{key_prefix}_qty_{i}", label_visibility="collapsed")
            with cols[3]:
                unit = st.selectbox("", UNITS,
                                     index=UNITS.index(row.get('Unit','Meter'))
                                           if row.get('Unit','Meter') in UNITS else 0,
                                     key=f"{key_prefix}_unit_{i}", label_visibility="collapsed")
            with cols[4]:
                rate = st.number_input("", value=float(row.get('Rate',0) or 0),
                                        min_value=0.0, step=1.0,
                                        key=f"{key_prefix}_rate_{i}", label_visibility="collapsed")
            with cols[5]:
                process = st.selectbox("", [""] + PROCESSES,
                                        index=([""] + PROCESSES).index(row.get('ProcessName',''))
                                              if row.get('ProcessName','') in ([""] + PROCESSES) else 0,
                                        key=f"{key_prefix}_proc_{i}", label_visibility="collapsed")
            with cols[6]:
                shrink = st.number_input("", value=float(row.get('Shrinkage',0) or 0),
                                          min_value=0.0, max_value=50.0, step=0.5,
                                          key=f"{key_prefix}_shrink_{i}", label_visibility="collapsed")
            with cols[7]:
                remarks = st.text_input("", value=row.get('Remarks',''),
                                         key=f"{key_prefix}_rem_{i}", label_visibility="collapsed")
            with cols[8]:
                if st.button("🗑️", key=f"{key_prefix}_del_{i}"):
                    del_idx = i

            if del_idx != i:
                shrink_qty = qty * (1 + shrink/100)
                updated_rows.append({
                    'ComponentName': comp_name, 'ComponentType': comp_type,
                    'Qty': qty, 'Unit': unit, 'Rate': rate,
                    'Amount': round(shrink_qty * rate, 2),
                    'ProcessName': process, 'Shrinkage': shrink, 'Remarks': remarks
                })

        if del_idx is not None:
            st.session_state[f"{key_prefix}_rows"] = updated_rows
            st.rerun()

        if st.button("➕ Add Component", key=f"{key_prefix}_add"):
            updated_rows.append({})
            st.session_state[f"{key_prefix}_rows"] = updated_rows
            st.rerun()

        st.session_state[f"{key_prefix}_rows"] = updated_rows
        return updated_rows

    # Render BOM editor
    if "Common" in bom_type or not sizes_in_item:
        bom_data = {"ALL": bom_row_editor("common")}
    else:
        st.info("Har size group ke liye alag BOM define karo:")
        # Group sizes
        size_groups = {}
        group_name = st.text_input("Size Group 1 name", value="Small Sizes")
        group_sizes = st.multiselect("Sizes in this group", sizes_in_item,
                                      default=sizes_in_item[:3] if len(sizes_in_item)>=3 else sizes_in_item)
        st.markdown(f"**{group_name}** BOM:")
        bom_data = {group_name: bom_row_editor(f"grp_0")}

        if st.checkbox("Add another size group"):
            g2_name  = st.text_input("Size Group 2 name", value="Large Sizes")
            g2_sizes = [s for s in sizes_in_item if s not in group_sizes]
            st.markdown(f"**{g2_name}** BOM:")
            bom_data[g2_name] = bom_row_editor(f"grp_1")

    # ── Cost Summary ──────────────────────────────────────────────────────────
    all_rows_flat = [r for rows in bom_data.values() for r in rows if r.get('ComponentName')]
    if all_rows_flat:
        cost_by_proc, total_cost = calc_bom_cost(all_rows_flat)
        st.markdown('<div class="cost-summary">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:700;opacity:0.7;'
                    'margin-bottom:10px">💰 BOM COST SUMMARY</div>', unsafe_allow_html=True)
        for proc, amt in cost_by_proc.items():
            st.markdown(f'<div class="cost-row"><span>{proc}</span>'
                        f'<span>₹{amt:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="cost-total"><span>TOTAL PRODUCTION COST</span>'
                    f'<span>₹{total_cost:,.2f}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Save BOM ──────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("💾 Save BOM", type="primary"):
        if not bom_name.strip():
            st.error("BOM Name required!")
        elif not all_rows_flat:
            st.error("Kam se kam ek component add karo!")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            saved = 0
            for group, rows in bom_data.items():
                for r in rows:
                    if r.get('ComponentName'):
                        bom_id = f"{bom_item}-{bom_name}-{group}"
                        write_row("BOM", {
                            "BOMId": bom_id, "ItemCode": bom_item,
                            "BOMName": bom_name, "FabricWidth": "",
                            "IsDefault": "Yes" if is_default else "No",
                            "ComponentCode": "", "ComponentName": r.get('ComponentName',''),
                            "ComponentType": r.get('ComponentType',''),
                            "Qty": r.get('Qty',0), "Unit": r.get('Unit',''),
                            "Rate": r.get('Rate',0), "Amount": r.get('Amount',0),
                            "ProcessName": r.get('ProcessName',''),
                            "Shrinkage": r.get('Shrinkage',0),
                            "Wastage": 0, "Remarks": r.get('Remarks',''),
                            "CreatedAt": now
                        })
                        saved += 1
            st.success(f"✅ BOM saved! {saved} components saved for **{bom_item}**.")

    # ── View existing BOMs ────────────────────────────────────────────────────
    if not bom_df.empty and bom_item and 'ItemCode' in bom_df.columns:
        item_bom = bom_df[bom_df['ItemCode'] == bom_item]
        if not item_bom.empty:
            st.markdown("---")
            st.markdown(f"**Saved BOMs for {bom_item}:**")
            for bname in item_bom['BOMName'].unique():
                b_rows = item_bom[item_bom['BOMName'] == bname]
                with st.expander(f"📄 {bname} ({len(b_rows)} components)"):
                    show_cols = ['ComponentName','ComponentType','Qty','Unit',
                                 'Rate','Amount','ProcessName','Shrinkage','Remarks']
                    show_cols = [c for c in show_cols if c in b_rows.columns]
                    st.dataframe(b_rows[show_cols], use_container_width=True, hide_index=True)
                    _, total = calc_bom_cost(b_rows.to_dict('records'))
                    st.markdown(f"**Total Cost: ₹{total:,.2f}**")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – SKU List
# ══════════════════════════════════════════════════════════════════════════════
with tab_skus:
    st.markdown("### 📦 SKU Master")
    skus_df = read_sheet("SKUs")

    if skus_df.empty:
        st.info("Koi SKU nahi mila. Items create karte waqt auto-generate hote hain.")
    else:
        s1, s2 = st.columns(2)
        with s1:
            parent_filter = st.multiselect("Filter by Parent Item",
                                            skus_df['ParentItemCode'].unique().tolist()
                                            if 'ParentItemCode' in skus_df.columns else [])
        with s2:
            size_filter = st.multiselect("Filter by Size",
                                          skus_df['Size'].unique().tolist()
                                          if 'Size' in skus_df.columns else [])

        disp_sku = skus_df.copy()
        if parent_filter: disp_sku = disp_sku[disp_sku['ParentItemCode'].isin(parent_filter)]
        if size_filter:   disp_sku = disp_sku[disp_sku['Size'].isin(size_filter)]

        st.markdown(f"**{len(disp_sku)} SKUs**")
        st.dataframe(disp_sku, use_container_width=True, hide_index=True)
        csv = disp_sku.to_csv(index=False)
        st.download_button("⬇️ Export SKUs", csv, "skus.csv", "text/csv")
