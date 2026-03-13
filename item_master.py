import os
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="ERP Item Master & BOM Module",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "Garment ERP – Item Master & BOM Module"
DB_PATH = "erp_item_master.db"
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

SIZE_LIBRARY = ["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL", "6XL", "7XL", "8XL"]
DEFAULT_ROUTING_STEPS = ["Cutting", "Printing", "Dyeing", "Stitching", "Finishing", "Packing"]
ITEM_TYPES = [
    "Finished Goods",
    "Semi Finished Goods",
    "Raw Material",
    "Accessories",
    "Packing Materials",
    "Fuel & Lubricants",
]
UNITS = ["MTR", "PCS", "KG", "LTR", "SET", "ROLL", "BOX"]
SEASONS = ["Spring", "Summer", "Monsoon", "Autumn", "Winter", "Festive", "All Season"]
APPROVAL_STATUS = ["Draft", "Certified", "Approved"]
PROCESS_MASTER_DEFAULT = [
    "Cutting",
    "Printing",
    "Dyeing",
    "Embroidery",
    "Stitching",
    "Finishing",
    "Packing",
    "Dispatch Prep",
]

# =========================================================
# STYLES
# =========================================================
st.markdown(
    """
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    .main-title {
        font-size: 30px; font-weight: 700; margin-bottom: 4px;
    }
    .sub-title {
        color: #6b7280; font-size: 14px; margin-bottom: 16px;
    }
    .soft-card {
        background: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        margin-bottom: 14px;
    }
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 14px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
    }
    .small-note {
        color:#6b7280; font-size:12px;
    }
    .done-chip {
        display:inline-block; background:#dcfce7; color:#166534;
        padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600;
    }
    .pending-chip {
        display:inline-block; background:#fef3c7; color:#92400e;
        padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# DB HELPERS
# =========================================================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_code TEXT UNIQUE,
            merchant_name TEXT NOT NULL,
            created_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS process_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_name TEXT UNIQUE,
            is_active INTEGER DEFAULT 1,
            created_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS item_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT UNIQUE,
            item_name TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_category TEXT,
            merchant_code TEXT,
            hsn_code TEXT,
            season TEXT,
            launch_date TEXT,
            parent_item_code TEXT,
            selling_price REAL DEFAULT 0,
            purchase_price REAL DEFAULT 0,
            cmt_cost REAL DEFAULT 0,
            process_cost REAL DEFAULT 0,
            size_group_json TEXT,
            auto_variant_prefix TEXT,
            approval_status TEXT DEFAULT 'Draft',
            buyer_packaging_json TEXT,
            remarks TEXT,
            front_image_path TEXT,
            back_image_path TEXT,
            detail_image_path TEXT,
            photo_path TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS item_attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT,
            file_type TEXT,
            file_name TEXT,
            file_path TEXT,
            uploaded_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS routing_master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT,
            step_no INTEGER,
            process_name TEXT,
            remarks TEXT,
            created_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bom_header (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bom_code TEXT UNIQUE,
            parent_item_code TEXT NOT NULL,
            bom_name TEXT,
            bom_type TEXT,
            apply_mode TEXT,
            size_group_json TEXT,
            width_note TEXT,
            version_no INTEGER DEFAULT 1,
            approval_status TEXT DEFAULT 'Draft',
            created_by TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bom_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bom_code TEXT,
            line_no INTEGER,
            component_item_code TEXT,
            component_item_name TEXT,
            component_item_type TEXT,
            quantity REAL DEFAULT 0,
            unit TEXT,
            rate REAL DEFAULT 0,
            process_name TEXT,
            shrinkage_pct REAL DEFAULT 0,
            wastage_pct REAL DEFAULT 0,
            amount REAL DEFAULT 0,
            remarks TEXT,
            process_used_in TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS buyer_packaging (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT,
            buyer_name TEXT,
            pack_item_code TEXT,
            pack_item_name TEXT,
            qty REAL DEFAULT 0,
            unit TEXT,
            remarks TEXT
        )
        """
    )

    conn.commit()

    for p in PROCESS_MASTER_DEFAULT:
        cur.execute(
            "INSERT OR IGNORE INTO process_master(process_name, created_at) VALUES (?, ?)",
            (p, datetime.now().isoformat()),
        )
    conn.commit()
    conn.close()


# =========================================================
# COMMON HELPERS
# =========================================================
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fetch_df(query, params=None):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params or [])
    conn.close()
    return df


def execute(query, params=None, many=False):
    conn = get_conn()
    cur = conn.cursor()
    if many:
        cur.executemany(query, params)
    else:
        cur.execute(query, params or [])
    conn.commit()
    conn.close()


def save_upload(file, folder_name="general"):
    if not file:
        return None
    folder = UPLOAD_DIR / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S_%f')}_{file.name}"
    file_path = folder / safe_name
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return str(file_path)


def generate_item_code(item_type, item_name, category=None):
    prefix_map = {
        "Finished Goods": "FG",
        "Semi Finished Goods": "SFG",
        "Raw Material": "RM",
        "Accessories": "ACC",
        "Packing Materials": "PK",
        "Fuel & Lubricants": "FL",
    }
    prefix = prefix_map.get(item_type, "ITM")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM item_master WHERE item_type=?", (item_type,))
    cnt = cur.fetchone()[0] + 1
    conn.close()
    return f"{prefix}-{cnt:04d}"


def generate_bom_code(parent_item_code):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM bom_header WHERE parent_item_code=?", (parent_item_code,))
    cnt = cur.fetchone()[0] + 1
    conn.close()
    return f"BOM-{parent_item_code}-{cnt:02d}"


def get_merchants():
    return fetch_df("SELECT merchant_code, merchant_name FROM merchants ORDER BY merchant_name")


def get_processes():
    df = fetch_df("SELECT process_name FROM process_master WHERE is_active=1 ORDER BY process_name")
    return df["process_name"].tolist() if not df.empty else []


def get_items(item_type=None):
    if item_type:
        return fetch_df("SELECT * FROM item_master WHERE item_type=? ORDER BY item_name", [item_type])
    return fetch_df("SELECT * FROM item_master ORDER BY item_name")


def get_item_codes_map():
    df = get_items()
    if df.empty:
        return {}
    return {f"{r['item_code']} | {r['item_name']}": r['item_code'] for _, r in df.iterrows()}


def parse_json_safe(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def calc_line_amount(qty, rate, shrinkage, wastage):
    factor = 1 + (shrinkage / 100.0) + (wastage / 100.0)
    return round(qty * factor * rate, 4)


def create_variants(parent_code, item_name, item_type, item_category, merchant_code, hsn_code, season,
                    launch_date, selling_price, purchase_price, cmt_cost, process_cost, sizes, remarks):
    timestamp = now_str()
    for sz in sizes:
        child_code = f"{parent_code}-{sz}"
        execute(
            """
            INSERT OR IGNORE INTO item_master(
                item_code, item_name, item_type, item_category, merchant_code, hsn_code, season,
                launch_date, parent_item_code, selling_price, purchase_price, cmt_cost, process_cost,
                size_group_json, approval_status, remarks, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            [
                child_code,
                f"{item_name} - {sz}",
                item_type,
                item_category,
                merchant_code,
                hsn_code,
                season,
                launch_date,
                parent_code,
                selling_price,
                purchase_price,
                cmt_cost,
                process_cost,
                json.dumps([sz]),
                "Draft",
                remarks,
                timestamp,
                timestamp,
            ],
        )


def copy_bom(source_bom_code, new_parent_item_code, new_bom_name, apply_mode, size_group_json, width_note, created_by="Admin"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bom_header WHERE bom_code=?", (source_bom_code,))
    hdr = cur.fetchone()
    if not hdr:
        conn.close()
        return None

    new_bom_code = generate_bom_code(new_parent_item_code)
    cur.execute(
        """
        INSERT INTO bom_header(
            bom_code, parent_item_code, bom_name, bom_type, apply_mode, size_group_json,
            width_note, version_no, approval_status, created_by, created_at, updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            new_bom_code,
            new_parent_item_code,
            new_bom_name,
            hdr["bom_type"],
            apply_mode,
            size_group_json,
            width_note,
            1,
            "Draft",
            created_by,
            now_str(),
            now_str(),
        ),
    )

    cur.execute("SELECT * FROM bom_lines WHERE bom_code=? ORDER BY line_no", (source_bom_code,))
    lines = cur.fetchall()
    for ln in lines:
        cur.execute(
            """
            INSERT INTO bom_lines(
                bom_code, line_no, component_item_code, component_item_name, component_item_type,
                quantity, unit, rate, process_name, shrinkage_pct, wastage_pct, amount, remarks, process_used_in
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                new_bom_code,
                ln["line_no"],
                ln["component_item_code"],
                ln["component_item_name"],
                ln["component_item_type"],
                ln["quantity"],
                ln["unit"],
                ln["rate"],
                ln["process_name"],
                ln["shrinkage_pct"],
                ln["wastage_pct"],
                ln["amount"],
                ln["remarks"],
                ln["process_used_in"],
            ),
        )
    conn.commit()
    conn.close()
    return new_bom_code


def get_dashboard_metrics():
    items = fetch_df("SELECT COUNT(*) AS cnt FROM item_master")
    bom = fetch_df("SELECT COUNT(*) AS cnt FROM bom_header")
    merchants = fetch_df("SELECT COUNT(*) AS cnt FROM merchants")
    routes = fetch_df("SELECT COUNT(*) AS cnt FROM routing_master")
    return {
        "Items": int(items.iloc[0]["cnt"]),
        "BOMs": int(bom.iloc[0]["cnt"]),
        "Merchants": int(merchants.iloc[0]["cnt"]),
        "Routing Lines": int(routes.iloc[0]["cnt"]),
    }


def bom_cost_summary(bom_code):
    df = fetch_df("SELECT * FROM bom_lines WHERE bom_code=? ORDER BY line_no", [bom_code])
    if df.empty:
        return {
            "Fabric Cost": 0,
            "Accessory Cost": 0,
            "Packing Cost": 0,
            "Other RM Cost": 0,
            "Total Component Cost": 0,
        }
    def classify(row):
        t = str(row["component_item_type"])
        n = str(row["component_item_name"]).lower()
        if t in ["Raw Material", "Semi Finished Goods"] and "fabric" in n:
            return "Fabric Cost"
        if t == "Accessories":
            return "Accessory Cost"
        if t == "Packing Materials":
            return "Packing Cost"
        return "Other RM Cost"
    df["bucket"] = df.apply(classify, axis=1)
    summary = df.groupby("bucket", as_index=False)["amount"].sum()
    result = {"Fabric Cost": 0, "Accessory Cost": 0, "Packing Cost": 0, "Other RM Cost": 0, "Total Component Cost": round(df['amount'].sum(), 2)}
    for _, r in summary.iterrows():
        result[r["bucket"]] = round(r["amount"], 2)
    return result


def render_header():
    st.markdown(f"<div class='main-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>Item Master, Size Variants, Routing, Multi-Level BOM, Buyer Packaging, Attachment & Image Support</div>",
        unsafe_allow_html=True,
    )


def render_metrics():
    metrics = get_dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, val) in zip([c1, c2, c3, c4], metrics.items()):
        with col:
            st.markdown(f"<div class='metric-card'><div class='small-note'>{label}</div><div style='font-size:28px;font-weight:700'>{val}</div></div>", unsafe_allow_html=True)


# =========================================================
# MODULES
# =========================================================
def module_dashboard():
    render_header()
    render_metrics()

    st.markdown("### Requirement Coverage")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
        st.markdown("**Covered in this app**")
        covered = [
            "Item Type master with future flexibility",
            "Finished Goods / SFG / RM / Accessories / Packing / Fuel items",
            "Merchant master dropdown",
            "Routing master and item-wise route order",
            "Automatic size variant creation",
            "Parent-child item structure",
            "Common BOM + Size-wise BOM + Multiple BOM",
            "BOM approval/certification",
            "Multi-level BOM structure",
            "Shrinkage + wastage + costing",
            "Process cost + CMT cost",
            "Buyer-wise packaging",
            "Attachment upload support",
            "Front / Back / Detail image storage",
            "Existing BOM copy and reuse",
        ]
        for x in covered:
            st.markdown(f"<span class='done-chip'>DONE</span> {x}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='soft-card'>", unsafe_allow_html=True)
        st.markdown("**Recommended next upgrades**")
        upgrades = [
            "User login and role rights (Admin / Merchant / Planning / Sampling)",
            "SO linked requirement planning and reservation engine",
            "Inventory stock validation in BOM",
            "Approval workflow with audit trail",
            "Tech Pack preview viewer",
            "Excel / PDF export for BOM and item cards",
            "Production order BOM selection and consumption issue",
            "Department-wise dashboards",
        ]
        for x in upgrades:
            st.markdown(f"<span class='pending-chip'>NEXT</span> {x}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Quick View")
    items_df = get_items()
    bom_df = fetch_df("SELECT * FROM bom_header ORDER BY created_at DESC LIMIT 10")
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.dataframe(items_df, use_container_width=True, height=350)
    with c2:
        st.dataframe(bom_df, use_container_width=True, height=350)


def module_merchant_master():
    render_header()
    st.markdown("### Merchant Master")
    with st.form("merchant_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        merchant_code = c1.text_input("Merchant Code", placeholder="MRC-001")
        merchant_name = c2.text_input("Merchant Name", placeholder="Harsh / Priyanka / Export Buyer Team")
        submitted = st.form_submit_button("Save Merchant", use_container_width=True)
        if submitted:
            if merchant_code and merchant_name:
                try:
                    execute(
                        "INSERT INTO merchants(merchant_code, merchant_name, created_at) VALUES(?,?,?)",
                        [merchant_code.strip(), merchant_name.strip(), now_str()],
                    )
                    st.success("Merchant saved successfully.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Merchant code and name both required.")

    st.dataframe(get_merchants(), use_container_width=True, height=450)


def module_process_master():
    render_header()
    st.markdown("### Process Master")
    with st.form("process_form", clear_on_submit=True):
        p1, p2 = st.columns([2, 1])
        process_name = p1.text_input("Process Name", placeholder="Cutting / Printing / Stitching")
        active = p2.selectbox("Active", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
        submitted = st.form_submit_button("Save Process", use_container_width=True)
        if submitted:
            if process_name:
                try:
                    execute(
                        "INSERT OR IGNORE INTO process_master(process_name, is_active, created_at) VALUES(?,?,?)",
                        [process_name.strip(), int(active), now_str()],
                    )
                    st.success("Process saved.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Process name required.")

    df = fetch_df("SELECT * FROM process_master ORDER BY process_name")
    st.dataframe(df, use_container_width=True, height=450)


def module_item_creation():
    render_header()
    st.markdown("### Item Creation")

    merchants_df = get_merchants()
    merchant_options = [""] + merchants_df["merchant_code"].tolist() if not merchants_df.empty else [""]
    items_df = get_items()
    item_options = [""] + items_df["item_code"].tolist() if not items_df.empty else [""]

    with st.form("item_form"):
        st.markdown("#### Basic Details")
        c1, c2, c3 = st.columns(3)
        item_type = c1.selectbox("Item Type", ITEM_TYPES)
        item_category = c2.text_input("Item Category", placeholder="Kurta / Kurta Set / Dress / Blouse / Grey Fabric")
        item_name = c3.text_input("Item Name / Style Name", placeholder="Kurta Style 101")

        c4, c5, c6 = st.columns(3)
        item_code_mode = c4.radio("Item Code", ["Auto", "Manual"], horizontal=True)
        manual_code = c5.text_input("Manual Item Code", placeholder="YG-KURTA-001")
        merchant_code = c6.selectbox("Merchant Code", merchant_options)

        c7, c8, c9 = st.columns(3)
        hsn_code = c7.text_input("HSN Code")
        season = c8.selectbox("Season", [""] + SEASONS)
        launch_date = c9.date_input("Launch Date", value=date.today())

        c10, c11, c12 = st.columns(3)
        parent_item_code = c10.selectbox("Parent Item", item_options)
        selling_price = c11.number_input("Selling Price", min_value=0.0, step=0.01)
        purchase_price = c12.number_input("Purchase Price", min_value=0.0, step=0.01)

        c13, c14 = st.columns(2)
        cmt_cost = c13.number_input("CMT Cost", min_value=0.0, step=0.01)
        process_cost = c14.number_input("Process Cost", min_value=0.0, step=0.01)

        st.markdown("#### Size Variant Setup")
        sizes = st.multiselect("Select Size Range", SIZE_LIBRARY, default=["S", "M", "L", "XL"] if item_type == "Finished Goods" else [])

        st.markdown("#### Buyer Packaging (Optional JSON Preview)")
        buyer_packaging_text = st.text_area(
            "Buyer Packaging JSON",
            value='[{"buyer_name":"Amazon","pack_item":"Polybag","qty":1,"unit":"PCS"}]',
            height=100,
        )

        remarks = st.text_area("Remarks")

        st.markdown("#### Images")
        img1, img2, img3, img4 = st.columns(4)
        item_photo = img1.file_uploader("Item Photo", type=["png", "jpg", "jpeg"], key="item_photo")
        front_image = img2.file_uploader("Front Image", type=["png", "jpg", "jpeg"], key="front_image")
        back_image = img3.file_uploader("Back Image", type=["png", "jpg", "jpeg"], key="back_image")
        detail_image = img4.file_uploader("Detail Image", type=["png", "jpg", "jpeg"], key="detail_image")

        st.markdown("#### Attachments")
        cad_files = st.file_uploader("CAD File", accept_multiple_files=True, key="cad_files")
        design_files = st.file_uploader("Design Sheet", accept_multiple_files=True, key="design_files")
        techpack_files = st.file_uploader("Tech Pack", accept_multiple_files=True, key="techpack_files")
        artwork_files = st.file_uploader("Artwork", accept_multiple_files=True, key="artwork_files")
        ref_files = st.file_uploader("Reference Images", accept_multiple_files=True, key="ref_files")

        save_item = st.form_submit_button("Save Item", use_container_width=True)

        if save_item:
            try:
                if not item_name:
                    st.warning("Item name required.")
                    return
                item_code = manual_code.strip() if item_code_mode == "Manual" and manual_code.strip() else generate_item_code(item_type, item_name, item_category)
                photo_path = save_upload(item_photo, item_code) if item_photo else None
                front_path = save_upload(front_image, item_code) if front_image else None
                back_path = save_upload(back_image, item_code) if back_image else None
                detail_path = save_upload(detail_image, item_code) if detail_image else None

                execute(
                    """
                    INSERT INTO item_master(
                        item_code, item_name, item_type, item_category, merchant_code, hsn_code, season,
                        launch_date, parent_item_code, selling_price, purchase_price, cmt_cost, process_cost,
                        size_group_json, auto_variant_prefix, approval_status, buyer_packaging_json, remarks,
                        front_image_path, back_image_path, detail_image_path, photo_path, created_at, updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    [
                        item_code,
                        item_name,
                        item_type,
                        item_category,
                        merchant_code,
                        hsn_code,
                        season,
                        str(launch_date),
                        parent_item_code,
                        selling_price,
                        purchase_price,
                        cmt_cost,
                        process_cost,
                        json.dumps(sizes),
                        item_code,
                        "Draft",
                        buyer_packaging_text,
                        remarks,
                        front_path,
                        back_path,
                        detail_path,
                        photo_path,
                        now_str(),
                        now_str(),
                    ],
                )

                attachment_groups = {
                    "CAD File": cad_files,
                    "Design Sheet": design_files,
                    "Tech Pack": techpack_files,
                    "Artwork": artwork_files,
                    "Reference Images": ref_files,
                }
                rows = []
                for file_type, files in attachment_groups.items():
                    for file in files or []:
                        path = save_upload(file, item_code)
                        rows.append((item_code, file_type, file.name, path, now_str()))
                if rows:
                    execute(
                        "INSERT INTO item_attachments(item_code, file_type, file_name, file_path, uploaded_at) VALUES(?,?,?,?,?)",
                        rows,
                        many=True,
                    )

                if item_type == "Finished Goods" and sizes:
                    create_variants(
                        item_code,
                        item_name,
                        item_type,
                        item_category,
                        merchant_code,
                        hsn_code,
                        season,
                        str(launch_date),
                        selling_price,
                        purchase_price,
                        cmt_cost,
                        process_cost,
                        sizes,
                        remarks,
                    )

                st.success(f"Item saved successfully. Main Item Code: {item_code}")
                if item_type == "Finished Goods" and sizes:
                    st.info("Size variants auto-created successfully.")
            except Exception as e:
                st.error(f"Save failed: {e}")

    st.markdown("### Item Master View")
    view_df = get_items()
    st.dataframe(view_df, use_container_width=True, height=420)


def module_routing():
    render_header()
    st.markdown("### Routing / Process Flow")
    item_map = get_item_codes_map()
    process_options = get_processes()

    if not item_map:
        st.warning("Please create items first.")
        return

    selected_label = st.selectbox("Select Item", list(item_map.keys()))
    item_code = item_map[selected_label]

    st.info("Yahan aap SKU/item wise routing order define kar sakte ho. Different SKU ke liye different sequence possible hai.")

    existing = fetch_df("SELECT * FROM routing_master WHERE item_code=? ORDER BY step_no", [item_code])
    if not existing.empty:
        st.dataframe(existing, use_container_width=True, height=200)

    row_count = st.number_input("How many routing steps?", min_value=1, max_value=20, value=max(3, len(existing) if len(existing) else 5))

    route_rows = []
    for i in range(int(row_count)):
        c1, c2, c3 = st.columns([1, 2, 2])
        step_no = c1.number_input(f"Step {i+1} No", min_value=1, value=i+1, key=f"step_{i}")
        process_name = c2.selectbox(f"Process {i+1}", process_options, key=f"proc_{i}")
        remarks = c3.text_input(f"Remarks {i+1}", key=f"r_{i}")
        route_rows.append((item_code, step_no, process_name, remarks, now_str()))

    csave, cclear = st.columns(2)
    if csave.button("Save Routing", use_container_width=True):
        execute("DELETE FROM routing_master WHERE item_code=?", [item_code])
        execute(
            "INSERT INTO routing_master(item_code, step_no, process_name, remarks, created_at) VALUES(?,?,?,?,?)",
            route_rows,
            many=True,
        )
        st.success("Routing saved successfully.")
        st.rerun()

    if cclear.button("Clear Routing", use_container_width=True):
        execute("DELETE FROM routing_master WHERE item_code=?", [item_code])
        st.success("Routing cleared.")
        st.rerun()


def module_bom_creation():
    render_header()
    st.markdown("### BOM Creation")
    item_map = get_item_codes_map()
    all_items_df = get_items()
    process_options = get_processes()

    if all_items_df.empty:
        st.warning("Please create item master data first.")
        return

    parent_fg = all_items_df[all_items_df["item_type"].isin(["Finished Goods", "Semi Finished Goods"])]
    if parent_fg.empty:
        st.warning("Create at least one FG or SFG item first.")
        return

    parent_options = {f"{r['item_code']} | {r['item_name']}": r['item_code'] for _, r in parent_fg.iterrows()}
    selected_parent_label = st.selectbox("Parent Item", list(parent_options.keys()))
    parent_item_code = parent_options[selected_parent_label]

    with st.form("bom_form"):
        c1, c2, c3, c4 = st.columns(4)
        bom_name = c1.text_input("BOM Name", placeholder='56" Fabric BOM / Export BOM')
        bom_type = c2.selectbox("BOM Type", ["Main BOM", "Alternate BOM", "Buyer BOM", "Sampling BOM"])
        apply_mode = c3.selectbox("Apply Mode", ["Common BOM", "Size-wise BOM"])
        width_note = c4.text_input("Width / Note", placeholder='56" / 48" / Buyer Specific')
        size_group = st.multiselect("Applicable Sizes", SIZE_LIBRARY)

        st.markdown("#### BOM Lines")
        line_count = st.number_input("How many BOM lines?", min_value=1, max_value=80, value=6)
        component_select_options = list(item_map.keys())

        line_rows = []
        for i in range(int(line_count)):
            st.markdown(f"**Line {i+1}**")
            a, b, c, d = st.columns([2.2, 1, 1, 1])
            e, f, g, h = st.columns([1.4, 1, 1, 2])
            comp_label = a.selectbox(f"Component Item {i+1}", component_select_options, key=f"comp_{i}")
            qty = b.number_input(f"Qty {i+1}", min_value=0.0, step=0.01, key=f"qty_{i}")
            unit = c.selectbox(f"Unit {i+1}", UNITS, key=f"unit_{i}")
            rate = d.number_input(f"Rate {i+1}", min_value=0.0, step=0.01, key=f"rate_{i}")
            process_name = e.selectbox(f"Process Link {i+1}", [""] + process_options, key=f"proc_bom_{i}")
            shrinkage = f.number_input(f"Shrinkage % {i+1}", min_value=0.0, step=0.1, key=f"shk_{i}")
            wastage = g.number_input(f"Wastage % {i+1}", min_value=0.0, step=0.1, key=f"wst_{i}")
            remarks = h.text_input(f"Remarks {i+1}", key=f"rmk_{i}")

            comp_code = item_map[comp_label]
            comp_row = all_items_df[all_items_df["item_code"] == comp_code].iloc[0]
            amt = calc_line_amount(qty, rate, shrinkage, wastage)
            line_rows.append(
                (
                    i + 1,
                    comp_code,
                    comp_row["item_name"],
                    comp_row["item_type"],
                    qty,
                    unit,
                    rate,
                    process_name,
                    shrinkage,
                    wastage,
                    amt,
                    remarks,
                    process_name,
                )
            )

        created_by = st.text_input("Created By", value="Admin")
        submit_bom = st.form_submit_button("Save BOM", use_container_width=True)

        if submit_bom:
            try:
                bom_code = generate_bom_code(parent_item_code)
                execute(
                    """
                    INSERT INTO bom_header(
                        bom_code, parent_item_code, bom_name, bom_type, apply_mode, size_group_json,
                        width_note, version_no, approval_status, created_by, created_at, updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    [
                        bom_code,
                        parent_item_code,
                        bom_name,
                        bom_type,
                        apply_mode,
                        json.dumps(size_group),
                        width_note,
                        1,
                        "Draft",
                        created_by,
                        now_str(),
                        now_str(),
                    ],
                )
                insert_rows = []
                for row in line_rows:
                    insert_rows.append((bom_code, *row))
                execute(
                    """
                    INSERT INTO bom_lines(
                        bom_code, line_no, component_item_code, component_item_name, component_item_type,
                        quantity, unit, rate, process_name, shrinkage_pct, wastage_pct, amount, remarks, process_used_in
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    insert_rows,
                    many=True,
                )
                st.success(f"BOM saved successfully. BOM Code: {bom_code}")
            except Exception as e:
                st.error(str(e))

    st.markdown("### Existing BOMs")
    hdr = fetch_df("SELECT * FROM bom_header ORDER BY created_at DESC")
    st.dataframe(hdr, use_container_width=True, height=250)


def module_bom_viewer():
    render_header()
    st.markdown("### BOM Viewer / Costing / Approval")
    hdr = fetch_df("SELECT * FROM bom_header ORDER BY created_at DESC")
    if hdr.empty:
        st.warning("No BOM found.")
        return

    bom_map = {f"{r['bom_code']} | {r['bom_name']} | {r['parent_item_code']}": r['bom_code'] for _, r in hdr.iterrows()}
    selected = st.selectbox("Select BOM", list(bom_map.keys()))
    bom_code = bom_map[selected]

    bom_header_df = fetch_df("SELECT * FROM bom_header WHERE bom_code=?", [bom_code])
    lines_df = fetch_df("SELECT * FROM bom_lines WHERE bom_code=? ORDER BY line_no", [bom_code])
    summary = bom_cost_summary(bom_code)

    if not bom_header_df.empty:
        row = bom_header_df.iloc[0]
        item_info = fetch_df("SELECT * FROM item_master WHERE item_code=?", [row['parent_item_code']])
        extra_process = float(item_info.iloc[0]["process_cost"]) if not item_info.empty else 0
        cmt_cost = float(item_info.iloc[0]["cmt_cost"]) if not item_info.empty else 0
        total_prod_cost = round(summary["Total Component Cost"] + extra_process + cmt_cost, 2)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fabric Cost", summary["Fabric Cost"])
        c2.metric("Accessory Cost", summary["Accessory Cost"])
        c3.metric("Packing Cost", summary["Packing Cost"])
        c4.metric("Other RM Cost", summary["Other RM Cost"])

        c5, c6, c7 = st.columns(3)
        c5.metric("Component Cost", summary["Total Component Cost"])
        c6.metric("Process Cost", extra_process)
        c7.metric("CMT Cost", cmt_cost)
        st.success(f"Total Production Cost = {total_prod_cost}")

        st.markdown("#### BOM Header")
        st.dataframe(bom_header_df, use_container_width=True, height=100)
        st.markdown("#### BOM Lines")
        st.dataframe(lines_df, use_container_width=True, height=350)

        col1, col2, col3 = st.columns(3)
        if col1.button("Mark Certified", use_container_width=True):
            execute("UPDATE bom_header SET approval_status='Certified', updated_at=? WHERE bom_code=?", [now_str(), bom_code])
            st.success("BOM marked as Certified.")
            st.rerun()
        if col2.button("Mark Approved", use_container_width=True):
            execute("UPDATE bom_header SET approval_status='Approved', updated_at=? WHERE bom_code=?", [now_str(), bom_code])
            st.success("BOM marked as Approved.")
            st.rerun()
        if col3.button("Reset to Draft", use_container_width=True):
            execute("UPDATE bom_header SET approval_status='Draft', updated_at=? WHERE bom_code=?", [now_str(), bom_code])
            st.success("BOM status reset to Draft.")
            st.rerun()


def module_bom_copy_reuse():
    render_header()
    st.markdown("### BOM Copy / Reuse")
    bom_df = fetch_df("SELECT * FROM bom_header ORDER BY created_at DESC")
    items_df = get_items()

    if bom_df.empty or items_df.empty:
        st.warning("Create BOM and Item first.")
        return

    bom_opts = {f"{r['bom_code']} | {r['bom_name']}": r['bom_code'] for _, r in bom_df.iterrows()}
    item_opts = {f"{r['item_code']} | {r['item_name']}": r['item_code'] for _, r in items_df.iterrows()}

    with st.form("copy_bom_form"):
        source_bom = st.selectbox("Source BOM", list(bom_opts.keys()))
        new_parent = st.selectbox("New Parent Item", list(item_opts.keys()))
        new_bom_name = st.text_input("New BOM Name", placeholder="Copied BOM - Edit as Required")
        apply_mode = st.selectbox("Apply Mode", ["Common BOM", "Size-wise BOM"])
        size_group = st.multiselect("Applicable Sizes", SIZE_LIBRARY)
        width_note = st.text_input("Width / Note")
        created_by = st.text_input("Created By", value="Admin")
        submitted = st.form_submit_button("Copy BOM", use_container_width=True)

        if submitted:
            new_bom_code = copy_bom(
                bom_opts[source_bom],
                item_opts[new_parent],
                new_bom_name,
                apply_mode,
                json.dumps(size_group),
                width_note,
                created_by,
            )
            if new_bom_code:
                st.success(f"BOM copied successfully. New BOM Code: {new_bom_code}")
            else:
                st.error("Source BOM not found.")


def module_buyer_packaging():
    render_header()
    st.markdown("### Buyer Wise Packaging")
    items_df = get_items()
    pack_items_df = get_items("Packing Materials")

    if items_df.empty:
        st.warning("Create items first.")
        return

    item_opts = {f"{r['item_code']} | {r['item_name']}": r['item_code'] for _, r in items_df.iterrows()}
    pack_opts = {f"{r['item_code']} | {r['item_name']}": r['item_code'] for _, r in pack_items_df.iterrows()} if not pack_items_df.empty else {}

    with st.form("buyer_pack_form"):
        selected_item = st.selectbox("Item", list(item_opts.keys()))
        buyer_name = st.text_input("Buyer Name", placeholder="Amazon / Myntra / Export Buyer")
        if pack_opts:
            selected_pack = st.selectbox("Packaging Item", list(pack_opts.keys()))
            pack_code = pack_opts[selected_pack]
            pack_name = selected_pack.split(" | ", 1)[1]
        else:
            pack_code = st.text_input("Packaging Item Code")
            pack_name = st.text_input("Packaging Item Name")
        c1, c2 = st.columns(2)
        qty = c1.number_input("Qty", min_value=0.0, step=0.01, value=1.0)
        unit = c2.selectbox("Unit", UNITS, index=1)
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Save Buyer Packaging", use_container_width=True)
        if submitted:
            execute(
                "INSERT INTO buyer_packaging(item_code, buyer_name, pack_item_code, pack_item_name, qty, unit, remarks) VALUES(?,?,?,?,?,?,?)",
                [item_opts[selected_item], buyer_name, pack_code, pack_name, qty, unit, remarks],
            )
            st.success("Buyer wise packaging saved.")

    df = fetch_df("SELECT * FROM buyer_packaging ORDER BY item_code, buyer_name")
    st.dataframe(df, use_container_width=True, height=450)


def module_item_browser():
    render_header()
    st.markdown("### Item Browser / Hierarchy / Attachments")
    items_df = get_items()
    if items_df.empty:
        st.warning("No items found.")
        return

    item_opts = {f"{r['item_code']} | {r['item_name']}": r['item_code'] for _, r in items_df.iterrows()}
    selected = st.selectbox("Select Item", list(item_opts.keys()))
    item_code = item_opts[selected]

    item_df = fetch_df("SELECT * FROM item_master WHERE item_code=?", [item_code])
    child_df = fetch_df("SELECT * FROM item_master WHERE parent_item_code=? ORDER BY item_code", [item_code])
    attachment_df = fetch_df("SELECT * FROM item_attachments WHERE item_code=? ORDER BY uploaded_at DESC", [item_code])
    routing_df = fetch_df("SELECT * FROM routing_master WHERE item_code=? ORDER BY step_no", [item_code])
    buyer_pack_df = fetch_df("SELECT * FROM buyer_packaging WHERE item_code=? ORDER BY buyer_name", [item_code])
    bom_df = fetch_df("SELECT * FROM bom_header WHERE parent_item_code=? ORDER BY created_at DESC", [item_code])

    st.markdown("#### Item Details")
    st.dataframe(item_df, use_container_width=True, height=120)

    if not item_df.empty:
        row = item_df.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        if row.get("photo_path") and os.path.exists(row["photo_path"]):
            c1.image(row["photo_path"], caption="Item Photo", use_container_width=True)
        if row.get("front_image_path") and os.path.exists(row["front_image_path"]):
            c2.image(row["front_image_path"], caption="Front Image", use_container_width=True)
        if row.get("back_image_path") and os.path.exists(row["back_image_path"]):
            c3.image(row["back_image_path"], caption="Back Image", use_container_width=True)
        if row.get("detail_image_path") and os.path.exists(row["detail_image_path"]):
            c4.image(row["detail_image_path"], caption="Detail Image", use_container_width=True)

    st.markdown("#### Child Variants")
    st.dataframe(child_df, use_container_width=True, height=180)

    st.markdown("#### Routing")
    st.dataframe(routing_df, use_container_width=True, height=160)

    st.markdown("#### Attachments")
    st.dataframe(attachment_df, use_container_width=True, height=180)

    st.markdown("#### Buyer Packaging")
    st.dataframe(buyer_pack_df, use_container_width=True, height=160)

    st.markdown("#### Linked BOMs")
    st.dataframe(bom_df, use_container_width=True, height=200)


def module_multi_level_bom_explorer():
    render_header()
    st.markdown("### Multi-Level BOM Explorer")
    bom_df = fetch_df("SELECT * FROM bom_header ORDER BY created_at DESC")
    if bom_df.empty:
        st.warning("No BOM found.")
        return

    bom_opts = {f"{r['bom_code']} | {r['parent_item_code']} | {r['bom_name']}": r['bom_code'] for _, r in bom_df.iterrows()}
    selected = st.selectbox("Select BOM", list(bom_opts.keys()))
    bom_code = bom_opts[selected]

    def expand_bom(current_bom_code, level=0, visited=None):
        visited = visited or set()
        if current_bom_code in visited:
            return []
        visited.add(current_bom_code)
        header = fetch_df("SELECT * FROM bom_header WHERE bom_code=?", [current_bom_code])
        lines = fetch_df("SELECT * FROM bom_lines WHERE bom_code=? ORDER BY line_no", [current_bom_code])
        rows = []
        for _, r in lines.iterrows():
            rows.append({
                "Level": level,
                "BOM Code": current_bom_code,
                "Component Code": r["component_item_code"],
                "Component Name": r["component_item_name"],
                "Item Type": r["component_item_type"],
                "Qty": r["quantity"],
                "Unit": r["unit"],
                "Process": r["process_name"],
                "Amount": r["amount"],
            })
            child_bom = fetch_df("SELECT bom_code FROM bom_header WHERE parent_item_code=? ORDER BY created_at DESC LIMIT 1", [r["component_item_code"]])
            if not child_bom.empty:
                rows.extend(expand_bom(child_bom.iloc[0]["bom_code"], level + 1, visited))
        return rows

    expanded = pd.DataFrame(expand_bom(bom_code))
    if expanded.empty:
        st.info("No lower-level BOM found.")
    else:
        st.dataframe(expanded, use_container_width=True, height=520)


def module_reports():
    render_header()
    st.markdown("### Reports & Export")

    items_df = get_items()
    bom_hdr = fetch_df("SELECT * FROM bom_header ORDER BY created_at DESC")
    bom_lines = fetch_df("SELECT * FROM bom_lines ORDER BY bom_code, line_no")
    buyer_pack = fetch_df("SELECT * FROM buyer_packaging ORDER BY item_code")

    tab1, tab2, tab3, tab4 = st.tabs(["Item Master", "BOM Header", "BOM Lines", "Buyer Packaging"])
    with tab1:
        st.dataframe(items_df, use_container_width=True, height=420)
        st.download_button("Download Item Master CSV", items_df.to_csv(index=False).encode("utf-8"), file_name="item_master.csv", mime="text/csv")
    with tab2:
        st.dataframe(bom_hdr, use_container_width=True, height=420)
        st.download_button("Download BOM Header CSV", bom_hdr.to_csv(index=False).encode("utf-8"), file_name="bom_header.csv", mime="text/csv")
    with tab3:
        st.dataframe(bom_lines, use_container_width=True, height=420)
        st.download_button("Download BOM Lines CSV", bom_lines.to_csv(index=False).encode("utf-8"), file_name="bom_lines.csv", mime="text/csv")
    with tab4:
        st.dataframe(buyer_pack, use_container_width=True, height=420)
        st.download_button("Download Buyer Packaging CSV", buyer_pack.to_csv(index=False).encode("utf-8"), file_name="buyer_packaging.csv", mime="text/csv")


# =========================================================
# APP
# =========================================================
def main():
    init_db()

    with st.sidebar:
        st.markdown("## 🧵 ERP Navigation")
        menu = st.radio(
            "Go to",
            [
                "Dashboard",
                "Merchant Master",
                "Process Master",
                "Item Creation",
                "Routing",
                "BOM Creation",
                "BOM Viewer",
                "BOM Copy & Reuse",
                "Buyer Packaging",
                "Item Browser",
                "Multi-Level BOM Explorer",
                "Reports",
            ],
        )
        st.markdown("---")
        st.caption("Built for garment manufacturing workflow – FG / SFG / RM / Accessories / Packing / Multi BOM")

    if menu == "Dashboard":
        module_dashboard()
    elif menu == "Merchant Master":
        module_merchant_master()
    elif menu == "Process Master":
        module_process_master()
    elif menu == "Item Creation":
        module_item_creation()
    elif menu == "Routing":
        module_routing()
    elif menu == "BOM Creation":
        module_bom_creation()
    elif menu == "BOM Viewer":
        module_bom_viewer()
    elif menu == "BOM Copy & Reuse":
        module_bom_copy_reuse()
    elif menu == "Buyer Packaging":
        module_buyer_packaging()
    elif menu == "Item Browser":
        module_item_browser()
    elif menu == "Multi-Level BOM Explorer":
        module_multi_level_bom_explorer()
    elif menu == "Reports":
        module_reports()


if __name__ == "__main__":
    main()
