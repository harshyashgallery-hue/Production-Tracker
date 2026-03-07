import io
import json
import os
import re
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Yash Gallery - Merchant Control Tower",
    page_icon="👗",
    layout="wide"
)

# =============================================================================
# CUSTOM CSS
# =============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0d47a1 0%, #283593 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 18px;
    }
    .section-title {
        background: #e3f2fd;
        border-left: 5px solid #1565c0;
        padding: 8px 14px;
        font-weight: 700;
        font-size: 15px;
        margin: 16px 0 8px 0;
        border-radius: 4px;
        color: #0d47a1;
    }
    .metric-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .metric-val {
        font-size: 26px;
        font-weight: 800;
        color: #1565c0;
    }
    .metric-lbl {
        font-size: 12px;
        color: #666;
        margin-top: 4px;
    }
    .ok-chip {
        display:inline-block;
        background:#e8f5e9;
        color:#2e7d32;
        padding:4px 10px;
        border-radius:20px;
        font-size:12px;
        margin-right:6px;
    }
    .warn-chip {
        display:inline-block;
        background:#fff3e0;
        color:#e65100;
        padding:4px 10px;
        border-radius:20px;
        font-size:12px;
        margin-right:6px;
    }
    .bad-chip {
        display:inline-block;
        background:#ffebee;
        color:#c62828;
        padding:4px 10px;
        border-radius:20px;
        font-size:12px;
        margin-right:6px;
    }
    .no-photo {
        background: #f5f5f5;
        border: 2px dashed #bdbdbd;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        color: #9e9e9e;
        font-size: 13px;
    }
    .info-box {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px 14px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PATHS
# =============================================================================
DATA_DIR = Path("/tmp/yash_gallery_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = DATA_DIR / "report_source.bin"
IMAGES_DIR = DATA_DIR / "images"
META_PATH = DATA_DIR / "meta.json"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".jfif", ".webp", ".bmp"}

# =============================================================================
# CONFIG
# =============================================================================
PROCESS_ORDER = [
    'Modal Shout', 'Dyeing', 'Printing', 'Fabric Check', 'Re Process',
    'Cutting', 'Gola Cutting', 'Embroidary', '5 Threads', 'Stitching',
    'Alteration', 'Kaaz Button', 'Fabric Button', 'Handwork', 'Finishing',
    'Stitch to Pack', 'Washing', 'Consume Item', 'Consine Bobin Elastic', 'Partchange'
]

SIZE_ORDER_MASTER = [
    'XS','S','S-M','S-M-L','M','L','L-XL','L-XL-XXL','XL','XL-XXL',
    'XL-XXL-3XL','XXL','XXL-3XL','3XL','3XL-4XL','4XL','4XL-5XL',
    '5XL','5XL-6XL','6XL','7XL','7XL-8XL','8XL','Free Size','Mix',
    '7 -8 Years','9 -10 Years','11 -12 Years','13 -14 Years'
]

COLUMN_ALIASES = {
    "JONo": ["jo no", "jono", "jo", "job no", "jobno", "jo number"],
    "JODate": ["jo date", "jodate"],
    "SONo": ["so no", "sono", "so", "sales order no", "salesorderno"],
    "SODate": ["so date", "sodate"],
    "Karigar": ["karigar", "artisan", "contractor", "worker", "vendor"],
    "IssueNo": ["issue no", "issueno", "challan no", "ch no", "ch. no.", "chno", "challan"],
    "IssueDate": ["issue date", "issuedate"],
    "Process": ["process", "stage", "department"],
    "Design": ["design", "style", "style code", "stylecode", "item code"],
    "Size": ["size"],
    "NoColour_MI": ["nocolour mi", "no colour mi", "no colour issue", "nocolor mi", "nocolour_issue"],
    "NoColour_MR": ["nocolour mr", "no colour mr", "no colour receive", "nocolor mr", "nocolour_receive"],
    "NoColour_BAL": ["nocolour bal", "no colour bal", "nocolor bal"],
    "Mix_MI": ["mix mi", "mix issue"],
    "Mix_MR": ["mix mr", "mix receive"],
    "Mix_BAL": ["mix bal"],
}

CANONICAL_COLS = [
    "JONo", "JODate", "SONo", "SODate", "Karigar", "IssueNo", "IssueDate",
    "Process", "Design", "Size", "NoColour_MI", "NoColour_MR", "NoColour_BAL",
    "Mix_MI", "Mix_MR", "Mix_BAL"
]

NUMERIC_COLS = ["NoColour_MI", "NoColour_MR", "NoColour_BAL", "Mix_MI", "Mix_MR", "Mix_BAL"]

# =============================================================================
# HELPERS
# =============================================================================
def normalize_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())

def metric_card(col, value, label, color="#1565c0"):
    col.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-val" style="color:{color}">{value}</div>
            <div class="metric-lbl">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def section(title: str):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def save_meta(**kwargs):
    meta = load_meta()
    meta.update(kwargs)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def load_meta() -> dict:
    if META_PATH.exists():
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def clear_saved_data(remove_images: bool = False):
    if REPORT_PATH.exists():
        REPORT_PATH.unlink()
    if remove_images:
        for fp in IMAGES_DIR.iterdir():
            if fp.is_file():
                fp.unlink()
    if META_PATH.exists():
        META_PATH.unlink()

def save_uploaded_report(uploaded_file):
    REPORT_PATH.write_bytes(uploaded_file.getvalue())
    save_meta(report_name=uploaded_file.name, last_report_upload=str(date.today()))
    load_data.clear()

def save_images_from_zip(uploaded_zip, clear_old: bool = False) -> int:
    if clear_old:
        for fp in IMAGES_DIR.iterdir():
            if fp.is_file():
                fp.unlink()

    zf = zipfile.ZipFile(io.BytesIO(uploaded_zip.getvalue()))
    count = 0

    for name in zf.namelist():
        basename = os.path.basename(name)
        if not basename or basename.startswith("."):
            continue
        ext = Path(basename).suffix.lower()
        if ext not in IMAGE_EXTS:
            continue

        target = IMAGES_DIR / basename
        with zf.open(name) as src, open(target, "wb") as dst:
            dst.write(src.read())
        count += 1

    save_meta(images_count=len([x for x in IMAGES_DIR.iterdir() if x.is_file()]))
    get_image_lookup.clear()
    return count

@st.cache_data(show_spinner=False)
def get_image_lookup():
    lookup = {}
    for fp in IMAGES_DIR.iterdir():
        if fp.is_file() and fp.suffix.lower() in IMAGE_EXTS:
            lookup[normalize_key(fp.stem)] = str(fp)
    return lookup

def get_style_image(style_code: str):
    return get_image_lookup().get(normalize_key(style_code))

def process_sort_key(process_name: str):
    norm = normalize_key(process_name)
    master = [normalize_key(x) for x in PROCESS_ORDER]
    return (master.index(norm) if norm in master else 999, str(process_name).lower())

def size_sort_key(size_name: str):
    if size_name in SIZE_ORDER_MASTER:
        return SIZE_ORDER_MASTER.index(size_name)
    return 999

def join_unique(values, limit: int = 6, sort_func=None) -> str:
    items = []
    for v in values:
        txt = str(v).strip()
        if txt and txt.lower() not in {"nan", "none"} and txt not in items:
            items.append(txt)
    if sort_func:
        items = sorted(items, key=sort_func)
    if len(items) > limit:
        return ", ".join(items[:limit]) + f" +{len(items)-limit}"
    return ", ".join(items)

def header_score(headers) -> int:
    normalized_headers = {normalize_key(h) for h in headers}
    score = 0
    for canon, aliases in COLUMN_ALIASES.items():
        alias_set = {normalize_key(canon)} | {normalize_key(a) for a in aliases}
        if normalized_headers & alias_set:
            score += 1
    return score

def standardize_candidate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    if df.empty:
        return df

    df.columns = [str(c).strip() for c in df.columns]

    current_score = header_score(df.columns)
    if len(df) > 0:
        first_row_headers = [str(x).strip() for x in df.iloc[0].tolist()]
        first_row_score = header_score(first_row_headers)
        if first_row_score > current_score:
            df.columns = first_row_headers
            df = df.iloc[1:].reset_index(drop=True)

    rename_map = {}
    for col in df.columns:
        ncol = normalize_key(col)
        for canon, aliases in COLUMN_ALIASES.items():
            alias_set = {normalize_key(canon)} | {normalize_key(a) for a in aliases}
            if ncol in alias_set:
                rename_map[col] = canon
                break

    df = df.rename(columns=rename_map)

    for col in CANONICAL_COLS:
        if col not in df.columns:
            df[col] = "" if col not in NUMERIC_COLS else 0

    return df[CANONICAL_COLS].copy()

def extract_candidate_tables(file_bytes: bytes):
    candidates = []

    # Try HTML tables first (many .xls exports are actually HTML)
    try:
        decoded = file_bytes.decode("utf-8", errors="ignore")
        if "<table" in decoded.lower():
            html_tables = pd.read_html(io.StringIO(decoded))
            candidates.extend(html_tables)
    except Exception:
        pass

    # Try Excel
    try:
        excel_book = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None, dtype=str)
        candidates.extend(list(excel_book.values()))
    except Exception:
        pass

    return candidates

def parse_date_series(series: pd.Series) -> pd.Series:
    cleaned = series.fillna("").astype(str).str.strip().str.lstrip("'")
    dt = pd.to_datetime(cleaned, errors="coerce", dayfirst=True)
    return dt

@st.cache_data(show_spinner="Loading report data...")
def load_data(file_bytes: bytes):
    candidates = extract_candidate_tables(file_bytes)
    if not candidates:
        raise ValueError(
            "Report file read nahi ho paaya. Agar file true .xls hai to environment me xlrd install hona chahiye."
        )

    best_df = None
    best_score = -1

    for cand in candidates:
        try:
            test_df = standardize_candidate(cand)
            essential_present = sum(col in test_df.columns for col in ["Design", "Process", "Size", "JONo"])
            non_empty_design = (test_df["Design"].astype(str).str.strip() != "").sum()
            score = (essential_present * 1000) + non_empty_design
            if score > best_score:
                best_score = score
                best_df = test_df
        except Exception:
            continue

    if best_df is None or best_df.empty:
        raise ValueError("Valid data table nahi mili. Source file format check karo.")

    df = best_df.copy()

    # Clean text
    for col in ["JONo", "JODate", "SONo", "SODate", "Karigar", "IssueNo", "IssueDate", "Process", "Design", "Size"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # Keep only useful rows
    df = df[(df["Design"] != "") & (df["Process"] != "")]
    df = df.reset_index(drop=True)

    # Numeric conversion
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Dates
    df["IssueDate_dt"] = parse_date_series(df["IssueDate"])
    df["JODate_dt"] = parse_date_series(df["JODate"])
    df["SODate_dt"] = parse_date_series(df["SODate"])

    # Totals
    df["Total_MI"] = df["NoColour_MI"] + df["Mix_MI"]
    df["Total_MR"] = df["NoColour_MR"] + df["Mix_MR"]
    df["Total_BAL"] = df["Total_MI"] - df["Total_MR"]

    # Style code alias
    df["StyleCode"] = df["Design"]

    # Sort columns
    df["Size_order"] = df["Size"].apply(size_sort_key)
    df["Process_order"] = df["Process"].apply(lambda x: process_sort_key(x)[0])

    # Days pending
    today_ts = pd.Timestamp(date.today())
    df["Days Pending"] = (today_ts - df["IssueDate_dt"]).dt.days
    df["Days Pending"] = df["Days Pending"].fillna(0).clip(lower=0).astype(int)

    return df

def apply_aging(df: pd.DataFrame, d1: int, d2: int, d3: int) -> pd.DataFrame:
    out = df.copy()

    def bucket(days: int) -> str:
        if days <= d1:
            return f"🟢 0-{d1} days"
        elif days <= d2:
            return f"🟡 {d1+1}-{d2} days"
        elif days <= d3:
            return f"🟠 {d2+1}-{d3} days"
        return f"🔴 {d3}+ days"

    out["Aging"] = out["Days Pending"].apply(bucket)
    return out

def apply_global_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df.copy()

    search_text = filters.get("search_text", "").strip().lower()
    if search_text:
        search_cols = ["StyleCode", "Design", "JONo", "SONo", "Karigar", "Process", "IssueNo", "Size"]
        mask = pd.Series(False, index=out.index)
        for col in search_cols:
            mask = mask | out[col].fillna("").astype(str).str.lower().str.contains(search_text, regex=False)
        out = out[mask]

    if filters.get("styles"):
        out = out[out["StyleCode"].isin(filters["styles"])]
    if filters.get("jos"):
        out = out[out["JONo"].isin(filters["jos"])]
    if filters.get("sos"):
        out = out[out["SONo"].isin(filters["sos"])]
    if filters.get("processes"):
        out = out[out["Process"].isin(filters["processes"])]
    if filters.get("karigars"):
        out = out[out["Karigar"].isin(filters["karigars"])]

    if filters.get("only_pending"):
        out = out[out["Total_BAL"] > 0]

    if filters.get("only_critical"):
        out = out[out["Days Pending"] > filters.get("critical_days", 30)]

    if filters.get("has_photo_only"):
        out = out[out["StyleCode"].apply(lambda s: bool(get_style_image(s)))]

    date_basis = filters.get("date_basis")
    if date_basis and date_basis != "No Date Filter":
        date_col_map = {
            "Issue Date": "IssueDate_dt",
            "JO Date": "JODate_dt",
            "SO Date": "SODate_dt",
        }
        dt_col = date_col_map.get(date_basis)
        date_range = filters.get("date_range")
        if dt_col and date_range and len(date_range) == 2:
            start_date, end_date = date_range
            if start_date and end_date:
                mask = out[dt_col].notna() & out[dt_col].dt.date.between(start_date, end_date)
                out = out[mask]

    return out

def build_tracking_table(proc_df: pd.DataFrame) -> pd.DataFrame:
    if proc_df.empty:
        return pd.DataFrame()

    proc_df = proc_df.sort_values(["Karigar", "IssueNo", "Size_order", "Size"])
    pivot_rows = []

    for (karigar_name, issue_no), iss_df in proc_df.groupby(["Karigar", "IssueNo"], sort=False, dropna=False):
        iss_df = iss_df.sort_values(["Size_order", "Size"])
        issue_date = iss_df["IssueDate"].iloc[0]
        so_no = iss_df["SONo"].iloc[0]
        jo_no = iss_df["JONo"].iloc[0]

        issue_row = {
            "SO No.": so_no,
            "JO No.": jo_no,
            "Issue Date": issue_date,
            "Issue No.": issue_no,
            "Karigar": karigar_name,
            "Type": "Issued (MI)"
        }
        for _, r in iss_df.iterrows():
            issue_row[r["Size"]] = int(r["Total_MI"]) if r["Total_MI"] else ""
        pivot_rows.append(issue_row)

        if iss_df["Total_MR"].sum() > 0:
            rec_row = {
                "SO No.": "",
                "JO No.": "",
                "Issue Date": "",
                "Issue No.": issue_no,
                "Karigar": karigar_name,
                "Type": "Received (MR)"
            }
            for _, r in iss_df.iterrows():
                rec_row[r["Size"]] = int(r["Total_MR"]) if r["Total_MR"] else ""
            pivot_rows.append(rec_row)

        if iss_df["Total_BAL"].sum() != 0:
            bal_total = iss_df["Total_BAL"].sum()
            bal_row = {
                "SO No.": "",
                "JO No.": "",
                "Issue Date": "",
                "Issue No.": issue_no,
                "Karigar": karigar_name,
                "Type": "🔴 Balance" if bal_total > 0 else "✅ Balance"
            }
            for _, r in iss_df.iterrows():
                bal = int(r["Total_BAL"])
                bal_row[r["Size"]] = bal if bal != 0 else ""
            pivot_rows.append(bal_row)

    pv_df = pd.DataFrame(pivot_rows)
    base_cols = ["SO No.", "JO No.", "Issue Date", "Issue No.", "Karigar", "Type"]
    size_cols = [s for s in SIZE_ORDER_MASTER if s in pv_df.columns]
    other_cols = [c for c in pv_df.columns if c not in base_cols and c not in size_cols]
    pv_df = pv_df.reindex(columns=base_cols + size_cols + other_cols).fillna("")

    qty_cols = size_cols + other_cols
    if qty_cols:
        qty_numeric = pv_df[qty_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        pv_df["TOTAL"] = qty_numeric.sum(axis=1).astype(int)
        pv_df.loc[pv_df["TOTAL"] == 0, "TOTAL"] = ""

    return pv_df

def status_from_days(days: int, d1: int, d2: int, d3: int) -> str:
    if days > d3:
        return "Critical"
    elif days > d2:
        return "Delayed"
    elif days > d1:
        return "Monitor"
    return "On Track"

def action_from_status(status: str) -> str:
    mapping = {
        "Critical": "Immediate follow-up with karigar + production team",
        "Delayed": "Follow-up today and revise dispatch plan",
        "Monitor": "Monitor closely and confirm next update",
        "On Track": "Regular follow-up only"
    }
    return mapping.get(status, "")

def build_merchant_action_report(pending_df: pd.DataFrame, d1: int, d2: int, d3: int) -> pd.DataFrame:
    if pending_df.empty:
        return pd.DataFrame()

    grouped = (
        pending_df.groupby(["StyleCode", "JONo", "SONo"], dropna=False)
        .agg(
            Pending_Pcs=("Total_BAL", "sum"),
            Issued=("Total_MI", "sum"),
            Received=("Total_MR", "sum"),
            Open_Stages=("Process", "nunique"),
            Stages=("Process", lambda x: join_unique(x, limit=10, sort_func=process_sort_key)),
            Karigars=("Karigar", lambda x: join_unique(x, limit=8)),
            Last_Issue_Date=("IssueDate_dt", "max"),
            Max_Days=("Days Pending", "max"),
            Critical_Lines=("Days Pending", lambda x: int((x > d3).sum())),
        )
        .reset_index()
    )

    grouped["Completion %"] = (
        (grouped["Received"] / grouped["Issued"].replace(0, pd.NA)) * 100
    ).fillna(0).round(1)

    grouped["Last Issue Date"] = grouped["Last_Issue_Date"].dt.strftime("%d-%m-%Y").fillna("")
    grouped["Status"] = grouped["Max_Days"].apply(lambda x: status_from_days(int(x), d1, d2, d3))
    grouped["Next Action"] = grouped["Status"].apply(action_from_status)
    grouped["📷"] = grouped["StyleCode"].apply(lambda s: "✅" if get_style_image(s) else "❌")

    grouped = grouped.rename(columns={
        "StyleCode": "Style",
        "JONo": "JO No.",
        "SONo": "SO No.",
        "Pending_Pcs": "Pending Pcs",
        "Open_Stages": "Open Stages",
        "Stages": "Pending Stages",
        "Karigars": "Karigars",
        "Max_Days": "Max Days Pending",
        "Critical_Lines": "Critical Lines",
    })

    final_cols = [
        "📷", "Style", "JO No.", "SO No.", "Pending Pcs", "Issued", "Received",
        "Completion %", "Open Stages", "Pending Stages", "Karigars",
        "Last Issue Date", "Max Days Pending", "Critical Lines", "Status", "Next Action"
    ]
    grouped = grouped[final_cols].sort_values(["Status", "Pending Pcs", "Max Days Pending"], ascending=[True, False, False])
    return grouped

def build_quality_tables(src: pd.DataFrame):
    base_cols = ["StyleCode", "JONo", "SONo", "Process", "Karigar", "IssueNo", "IssueDate", "Size", "Total_MI", "Total_MR", "Total_BAL"]

    missing_photo_styles = sorted(
        [s for s in src["StyleCode"].dropna().astype(str).unique() if s.strip() and not get_style_image(s)]
    )
    missing_photos_df = pd.DataFrame({"Style": missing_photo_styles})

    negative_balance_df = src[src["Total_BAL"] < 0][base_cols].copy()
    missing_required_df = src[
        (src["StyleCode"].astype(str).str.strip() == "") |
        (src["Process"].astype(str).str.strip() == "") |
        (src["Size"].astype(str).str.strip() == "")
    ][base_cols].copy()

    invalid_issue_dates_df = src[
        (src["IssueDate"].astype(str).str.strip() != "") & (src["IssueDate_dt"].isna())
    ][["StyleCode", "JONo", "IssueNo", "IssueDate", "Process", "Karigar"]].copy()

    unknown_sizes_df = src[
        (src["Size"].astype(str).str.strip() != "") & (~src["Size"].isin(SIZE_ORDER_MASTER))
    ][["StyleCode", "JONo", "SONo", "Process", "Karigar", "Size"]].copy()

    return {
        "missing_photos": missing_photos_df,
        "negative_balance": negative_balance_df,
        "missing_required": missing_required_df,
        "invalid_issue_dates": invalid_issue_dates_df,
        "unknown_sizes": unknown_sizes_df
    }

def build_excel_report(raw_df: pd.DataFrame, merchant_df: pd.DataFrame, pending_detail_df: pd.DataFrame, quality_tables: dict) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output) as writer:
        raw_df.to_excel(writer, sheet_name="Filtered Raw", index=False)

        if not merchant_df.empty:
            merchant_df.to_excel(writer, sheet_name="Merchant Action", index=False)

        if not pending_detail_df.empty:
            pending_detail_df.to_excel(writer, sheet_name="Pending Detail", index=False)

        for name, table in quality_tables.items():
            if table is not None and not table.empty:
                table.to_excel(writer, sheet_name=name[:31], index=False)

    output.seek(0)
    return output.getvalue()

# =============================================================================
# HEADER
# =============================================================================
st.markdown("""
<div class="main-header">
    <h2 style="margin:0">👗 Yash Gallery Private Limited</h2>
    <p style="margin:6px 0 0 0; opacity:0.9">Merchant Control Tower • Material Issue / Receive • Style Tracking • Pendency Analysis</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - DATA MANAGEMENT
# =============================================================================
with st.sidebar:
    st.header("📂 Data Management")

    meta = load_meta()
    report_exists = REPORT_PATH.exists()
    image_count = len([x for x in IMAGES_DIR.iterdir() if x.is_file()])

    if report_exists:
        st.markdown(
            f"""
            <div class="info-box">
                <b>Report:</b> {meta.get('report_name', 'Uploaded file')}<br>
                <b>Images:</b> {image_count}<br>
                <b>Last Upload:</b> {meta.get('last_report_upload', '-')}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Upload / Replace")

    uploaded_report = st.file_uploader(
        "Upload Report (.xls / .xlsx / .html / .htm)",
        type=["xls", "xlsx", "html", "htm"],
        key="report_uploader"
    )
    if uploaded_report is not None:
        try:
            save_uploaded_report(uploaded_report)
            st.success("✅ Report saved successfully")
        except Exception as e:
            st.error(f"Report save error: {e}")

    clear_old_images = st.checkbox("ZIP upload se pehle purani images clear kar do", value=False)
    uploaded_zip = st.file_uploader("Upload Images ZIP", type=["zip"], key="images_zip")
    if uploaded_zip is not None:
        try:
            count = save_images_from_zip(uploaded_zip, clear_old=clear_old_images)
            st.success(f"✅ {count} images saved")
        except Exception as e:
            st.error(f"Image upload error: {e}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 Clear Report"):
            if REPORT_PATH.exists():
                REPORT_PATH.unlink()
                load_data.clear()
                st.success("Report removed")
                st.rerun()

    with c2:
        if st.button("🗑️ Clear All"):
            clear_saved_data(remove_images=True)
            load_data.clear()
            get_image_lookup.clear()
            st.success("All saved data removed")
            st.rerun()

# =============================================================================
# LOAD DATA
# =============================================================================
if not REPORT_PATH.exists():
    st.info("👈 Sidebar se pehle report upload karo. Images optional hain but recommended.")
    st.stop()

try:
    file_bytes = REPORT_PATH.read_bytes()
    df = load_data(file_bytes)
except Exception as e:
    st.error(f"Data load error: {e}")
    st.stop()

# =============================================================================
# SIDEBAR - GLOBAL FILTERS
# =============================================================================
with st.sidebar:
    st.markdown("---")
    st.header("🎯 Global Filters")

    search_text = st.text_input("Quick Search", placeholder="Style / JO / SO / Karigar / Issue No")

    # Dynamic aging thresholds
    st.markdown("**Aging Buckets**")
    d1 = st.slider("Green upto", min_value=1, max_value=15, value=7)
    d2 = st.slider("Yellow upto", min_value=d1 + 1, max_value=30, value=15)
    d3 = st.slider("Orange upto", min_value=d2 + 1, max_value=60, value=30)

    # Apply aging
    df = apply_aging(df, d1, d2, d3)

    date_basis = st.selectbox("Date Filter Basis", 
