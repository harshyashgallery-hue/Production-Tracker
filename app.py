import streamlit as st
import pandas as pd
from datetime import date
import io

st.set_page_config(
    page_title="Production Tracker",
    page_icon="🧵",
    layout="wide"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background: #0f1117; }

h1, h2, h3 { font-family: 'Rajdhani', sans-serif !important; letter-spacing: 1px; }

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #e94560;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.header-banner h1 {
    color: #fff;
    font-size: 2.4rem !important;
    margin: 0 !important;
}
.header-banner p { color: #aab4c8; margin: 0; font-size: 0.95rem; }

/* Stage cards */
.stage-card {
    background: #1a1f2e;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    border-left: 4px solid;
}
.stage-done   { border-color: #00d68f; }
.stage-active { border-color: #f0a500; }
.stage-pending{ border-color: #444; }

/* Status badges */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-done    { background:#003d2b; color:#00d68f; }
.badge-active  { background:#3d2800; color:#f0a500; }
.badge-pending { background:#222; color:#888; }

/* Metric boxes */
.metric-row { display:flex; gap:12px; margin-bottom:20px; }
.metric-box {
    flex:1;
    background:#1a1f2e;
    border-radius:10px;
    padding:16px;
    text-align:center;
    border:1px solid #2a2f3e;
}
.metric-box .num { font-size:1.8rem; font-weight:700; font-family:'Rajdhani',sans-serif; }
.metric-box .lbl { font-size:0.75rem; color:#778; text-transform:uppercase; letter-spacing:1px; }

/* Size table */
.size-table th { background:#16213e !important; color:#e94560 !important; font-family:'Rajdhani',sans-serif; letter-spacing:1px; }
.size-table td { background:#1a1f2e !important; color:#dde !important; text-align:center !important; }

/* Print button */
.stDownloadButton button {
    background: #e94560 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Divider */
.styled-divider { border: none; border-top: 1px solid #2a2f3e; margin: 16px 0; }
</style>
""", unsafe_allow_html=True)

# ── Helper functions ────────────────────────────────────────────────────────
SIZES = ["XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL", "6XL", "7XL", "8XL"]

STAGES = [
    ("cutting",   "✂️  Cutting"),
    ("stitching", "🧵  Stitching"),
    ("handwork",  "🖐️  Hand Work / Kaaz Button"),
    ("finishing", "✨  Finishing"),
]

def safe_read(uploaded, label):
    """Read an uploaded Excel file into a DataFrame."""
    try:
        df = pd.read_excel(uploaded)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"❌ {label} file padhne mein problem: {e}")
        return pd.DataFrame()

def find_col(df, *candidates):
    """Return first matching column name (case-insensitive)."""
    mapping = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in mapping:
            return mapping[cand.lower()]
    return None

def get_size_row(df, style):
    """Return a dict {size: qty} for the given style."""
    style_col = find_col(df, "style no", "style", "order no", "order")
    if style_col is None or df.empty:
        return {}
    row = df[df[style_col].astype(str).str.upper() == style.upper()]
    if row.empty:
        return {}
    row = row.iloc[0]
    result = {}
    for s in SIZES:
        col = find_col(df, s)
        if col:
            val = row.get(col, 0)
            result[s] = int(val) if pd.notna(val) else 0
    return result

def get_stage_info(df, style):
    """Return dict with issue_date, receive_date, challan, vendor, delivery_date."""
    style_col = find_col(df, "style no", "style", "order no", "order")
    if style_col is None or df.empty:
        return {}
    row = df[df[style_col].astype(str).str.upper() == style.upper()]
    if row.empty:
        return {}
    row = row.iloc[0]
    info = {}
    for key, *cands in [
        ("challan",  "ch no", "challan no", "ch. no", "challan"),
        ("vendor",   "vendor name", "vendor", "party"),
        ("i_date",   "issue date", "i. date", "i date", "idate"),
        ("r_date",   "receive date", "r. date", "r date", "rdate", "received date"),
        ("del_date", "delivery date", "del date", "delivery"),
    ]:
        col = find_col(df, *cands)
        info[key] = str(row[col]) if col and pd.notna(row.get(col)) else "—"
    return info

def stage_status(info, sizes):
    """Determine status string from available data."""
    has_r = info.get("r_date", "—") not in ("—", "nan", "NaT", "")
    has_i = info.get("i_date", "—") not in ("—", "nan", "NaT", "")
    total = sum(sizes.values())
    if has_r and total > 0:
        return "done"
    if has_i:
        return "active"
    return "pending"

def build_html_report(style, order_info, stage_data):
    """Build a printable HTML report string."""
    rows = ""
    for stage_key, stage_label in STAGES:
        info, sizes = stage_data.get(stage_key, ({}, {}))
        total = sum(sizes.values())
        size_cells = "".join(f"<td>{sizes.get(s,0) or ''}</td>" for s in SIZES)
        rows += f"""
        <tr class='stage-header'><td colspan='16'><b>{stage_label}</b> &nbsp;
            CH: {info.get('challan','—')} &nbsp;|&nbsp;
            Vendor: {info.get('vendor','—')} &nbsp;|&nbsp;
            Issue: {info.get('i_date','—')} &nbsp;|&nbsp;
            Rcvd: {info.get('r_date','—')} &nbsp;|&nbsp;
            Del: {info.get('del_date','—')}
        </td></tr>
        <tr>{size_cells}<td><b>{total}</b></td></tr>
        """
    size_headers = "".join(f"<th>{s}</th>" for s in SIZES) + "<th>TOTAL</th>"
    html = f"""
    <html><head><style>
    body{{font-family:Arial,sans-serif;font-size:11px;margin:20px}}
    h2{{text-align:center}} table{{width:100%;border-collapse:collapse}}
    th,td{{border:1px solid #999;padding:4px 6px;text-align:center}}
    .stage-header td{{background:#eee;text-align:left;font-size:12px;padding:6px 8px}}
    </style></head><body>
    <h2>Production Status — Style: {style}</h2>
    <p>Order Date: {order_info.get('order_date','—')} &nbsp;|&nbsp;
       Close Date: {order_info.get('close_date','—')} &nbsp;|&nbsp;
       Due Days: {order_info.get('due_days','—')}</p>
    <table><tr><th>Size →</th>{size_headers}</tr>{rows}</table>
    <p style='margin-top:20px;color:#888;font-size:10px'>
        Generated on {date.today()} via Production Tracker App</p>
    </body></html>"""
    return html

# ── App Layout ───────────────────────────────────────────────────────────────
st.markdown("""
<div class='header-banner'>
  <div>
    <h1>🧵 Production Tracker</h1>
    <p>Style-wise status • Har stage ek jagah • Excel se automatically fill</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: File Uploads ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Excel Files Upload Karo")
    st.caption("Har stage ki alag file upload karo")

    f_cutting   = st.file_uploader("✂️ Cutting Excel",   type=["xlsx","xls"], key="cut")
    f_stitching = st.file_uploader("🧵 Stitching Excel", type=["xlsx","xls"], key="sti")
    f_handwork  = st.file_uploader("🖐️ Hand Work Excel", type=["xlsx","xls"], key="hnd")
    f_finishing = st.file_uploader("✨ Finishing Excel", type=["xlsx","xls"], key="fin")

    st.markdown("---")
    st.markdown("#### ℹ️ Excel Format Guide")
    st.caption("""Aapki Excel mein yeh columns hone chahiye:
- **Style No** (ya Order No)
- **CH No** (Challan)
- **Vendor Name**
- **I. Date** (Issue Date)
- **R. Date** (Receive Date)
- **Delivery Date**
- **XS, S, M, L, XL, XXL, 3XL...** (size columns)""")

    st.markdown("---")
    # Sample Excel download
    sample_data = {
        "Style No": ["1557YKRED", "2341BKBLU"],
        "CH No": ["CH-001", "CH-002"],
        "Vendor Name": ["ABC Stitching", "XYZ Tailor"],
        "I. Date": ["01-Jan-2025", "05-Jan-2025"],
        "R. Date": ["10-Jan-2025", ""],
        "Delivery Date": ["15-Jan-2025", "20-Jan-2025"],
        "XS": [10, 5], "S": [20, 10], "M": [30, 15],
        "L": [25, 12], "XL": [20, 8], "XXL": [10, 5],
        "3XL": [5, 2], "4XL": [3, 1], "5XL": [2, 0],
        "6XL": [1, 0], "7XL": [0, 0], "8XL": [0, 0],
    }
    sample_df = pd.DataFrame(sample_data)
    buf = io.BytesIO()
    sample_df.to_excel(buf, index=False)
    st.download_button(
        "⬇️ Sample Excel Download Karo",
        buf.getvalue(),
        file_name="sample_cutting.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ── Main: Style Search ──────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    style_input = st.text_input(
        "🔍 Style Number Daalo",
        placeholder="jaise: 1557YKRED",
        help="Exact style number daalo jo aapki Excel mein hai"
    ).strip().upper()
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("🔎 Search Karo", use_container_width=True, type="primary")

if not style_input:
    st.markdown("""
    <div style='background:#1a1f2e;border-radius:12px;padding:40px;text-align:center;margin-top:20px;border:1px dashed #2a2f3e'>
        <h3 style='color:#778;font-family:Rajdhani,sans-serif'>Upar style number daalo aur files upload karo</h3>
        <p style='color:#556'>Sample Excel download karke format samjho → sidebar mein button hai</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load all DataFrames ─────────────────────────────────────────────────────
dfs = {
    "cutting":   safe_read(f_cutting,   "Cutting")   if f_cutting   else pd.DataFrame(),
    "stitching": safe_read(f_stitching, "Stitching") if f_stitching else pd.DataFrame(),
    "handwork":  safe_read(f_handwork,  "Hand Work") if f_handwork  else pd.DataFrame(),
    "finishing": safe_read(f_finishing, "Finishing") if f_finishing else pd.DataFrame(),
}

# ── Build stage data ────────────────────────────────────────────────────────
stage_data = {}
for key, _ in STAGES:
    df = dfs[key]
    info  = get_stage_info(df, style_input) if not df.empty else {}
    sizes = get_size_row(df,  style_input) if not df.empty else {}
    stage_data[key] = (info, sizes)

# Check if style found in any file
any_found = any(stage_data[k][0] for k, _ in STAGES)

if not any_found:
    st.warning(f"⚠️ Style **{style_input}** kisi bhi uploaded file mein nahi mila. Style number check karo ya files upload karo.")
    if all(df.empty for df in dfs.values()):
        st.info("💡 Koi file upload nahi hui hai abhi. Sidebar mein files upload karo.")
    st.stop()

# ── Summary metrics ─────────────────────────────────────────────────────────
st.markdown(f"## 📋 Style: `{style_input}`")

stages_done    = sum(1 for k,_ in STAGES if stage_status(*stage_data[k]) == "done")
stages_active  = sum(1 for k,_ in STAGES if stage_status(*stage_data[k]) == "active")
stages_pending = sum(1 for k,_ in STAGES if stage_status(*stage_data[k]) == "pending")

# Total qty from cutting (first stage)
cut_sizes = stage_data["cutting"][1]
total_order_qty = sum(cut_sizes.values())

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("📦 Total Order Qty", total_order_qty or "—")
with m2:
    st.metric("✅ Stages Done", f"{stages_done}/4")
with m3:
    st.metric("🔄 Active Stages", stages_active)
with m4:
    st.metric("⏳ Pending Stages", stages_pending)

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Stage-wise Detail ───────────────────────────────────────────────────────
st.markdown("### 📊 Stage-wise Status")

for stage_key, stage_label in STAGES:
    info, sizes = stage_data[stage_key]
    status = stage_status(info, sizes) if info else "pending"
    total  = sum(sizes.values())

    badge_map = {
        "done":    ("<span class='badge badge-done'>✅ COMPLETE</span>",    "stage-done"),
        "active":  ("<span class='badge badge-active'>🔄 IN PROGRESS</span>","stage-active"),
        "pending": ("<span class='badge badge-pending'>⏳ PENDING</span>",   "stage-pending"),
    }
    badge_html, card_class = badge_map[status]

    with st.expander(f"{stage_label}  —  {badge_html}", expanded=(status=="active")):
        if not info:
            st.caption("Is stage ki file upload nahi hui ya style nahi mila.")
            continue

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📋 Challan No",   info.get("challan","—"))
        c2.metric("🏭 Vendor",       info.get("vendor","—"))
        c3.metric("📤 Issue Date",   info.get("i_date","—"))
        c4.metric("📥 Receive Date", info.get("r_date","—"))
        c5.metric("🚚 Delivery",     info.get("del_date","—"))

        st.markdown("**Size-wise Quantity:**")
        if sizes:
            size_df = pd.DataFrame([sizes])
            size_df["TOTAL"] = total
            # Only show sizes with qty > 0
            nonzero = [s for s in SIZES if sizes.get(s, 0) > 0]
            if nonzero:
                display_df = size_df[nonzero + ["TOTAL"]]
            else:
                display_df = size_df[["TOTAL"]]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.caption("Size data nahi mila.")

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Full size summary table ─────────────────────────────────────────────────
st.markdown("### 📐 Size-wise Summary (Sabhi Stages)")

summary_rows = []
for stage_key, stage_label in STAGES:
    info, sizes = stage_data[stage_key]
    if sizes:
        row = {"Stage": stage_label.split("  ")[-1].strip()}
        for s in SIZES:
            row[s] = sizes.get(s, 0) or ""
        row["TOTAL"] = sum(sizes.values())
        summary_rows.append(row)

if summary_rows:
    summary_df = pd.DataFrame(summary_rows).set_index("Stage")
    st.dataframe(summary_df, use_container_width=True)
else:
    st.caption("Koi size data available nahi.")

st.markdown("<hr class='styled-divider'>", unsafe_allow_html=True)

# ── Print / Export ──────────────────────────────────────────────────────────
st.markdown("### 🖨️ Print / Export")

order_info_dummy = {"order_date": "—", "close_date": "—", "due_days": "—"}
html_report = build_html_report(style_input, order_info_dummy, stage_data)

col_a, col_b = st.columns(2)
with col_a:
    st.download_button(
        label="⬇️ HTML Report Download (Print Ready)",
        data=html_report,
        file_name=f"production_{style_input}_{date.today()}.html",
        mime="text/html",
        use_container_width=True,
        type="primary"
    )
with col_b:
    # Export to Excel summary
    if summary_rows:
        xl_buf = io.BytesIO()
        pd.DataFrame(summary_rows).to_excel(xl_buf, index=False)
        st.download_button(
            label="📊 Excel Summary Download",
            data=xl_buf.getvalue(),
            file_name=f"summary_{style_input}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.markdown("""
<div style='text-align:center;color:#445;font-size:0.75rem;margin-top:32px'>
    Production Tracker • Data aapki Excel files se aata hai • Koi data server pe save nahi hota
</div>
""", unsafe_allow_html=True)
