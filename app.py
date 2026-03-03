import streamlit as st
import pandas as pd
from datetime import date
import io

st.set_page_config(
    page_title="Production Tracker",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background-color: #f4f6f9 !important;
    color: #2c3e50 !important;
}

/* ── Hide Streamlit default chrome ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: #2d3a4a !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * {
    color: #c8d3df !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* Sidebar brand header */
.sb-brand {
    background: linear-gradient(135deg, #875A7B 0%, #6c4765 100%);
    padding: 20px 20px 16px;
    margin-bottom: 8px;
}
.sb-brand-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff !important;
    letter-spacing: 0.3px;
}
.sb-brand-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.65) !important;
    margin-top: 2px;
}

/* Sidebar section labels */
.sb-label {
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    font-weight: 700;
    color: #6b7f94 !important;
    padding: 14px 20px 6px;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin-top: 4px;
}

/* File uploader in sidebar */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px dashed rgba(255,255,255,0.18) !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
    border-color: #875A7B !important;
    background: rgba(135,90,123,0.15) !important;
}

/* Sidebar download button */
[data-testid="stSidebar"] .stDownloadButton button {
    background: rgba(255,255,255,0.08) !important;
    color: #c8d3df !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 6px !important;
    width: 100%;
    font-size: 0.8rem !important;
}
[data-testid="stSidebar"] .stDownloadButton button:hover {
    background: #875A7B !important;
    color: white !important;
    border-color: #875A7B !important;
}

/* ── Page Top Bar ── */
.topbar {
    background: #ffffff;
    border-bottom: 2px solid #e4e8ee;
    padding: 14px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #875A7B, #6c4765);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.topbar-title {
    font-size: 1.2rem;
    font-weight: 800;
    color: #2c3e50;
}
.topbar-title em { color: #875A7B; font-style: normal; }
.topbar-right {
    font-size: 0.78rem;
    color: #95a5a6;
    font-weight: 600;
}

/* ── Page Heading ── */
.page-heading {
    margin-bottom: 22px;
}
.breadcrumb {
    font-size: 0.75rem;
    color: #95a5a6;
    margin-bottom: 5px;
    font-weight: 600;
}
.breadcrumb b { color: #875A7B; }
.page-heading h2 {
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #1a252f !important;
    margin-bottom: 3px !important;
}
.page-heading p {
    font-size: 0.85rem;
    color: #7f8c8d;
}

/* ── Search ── */
.stTextInput > div > div > input {
    border: 1.5px solid #d8dde4 !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem !important;
    background: #fff !important;
    color: #2c3e50 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #875A7B !important;
    box-shadow: 0 0 0 3px rgba(135,90,123,0.12) !important;
    outline: none !important;
}

/* Primary search button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #875A7B 0%, #6c4765 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 11px 22px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    box-shadow: 0 3px 10px rgba(135,90,123,0.35) !important;
    transition: all 0.2s !important;
    letter-spacing: 0.2px !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 16px rgba(135,90,123,0.45) !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px 20px 16px;
    border: 1px solid #e4e8ee;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    position: relative;
    overflow: hidden;
    transition: transform 0.18s, box-shadow 0.18s;
    height: 100%;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.10);
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 0 0 12px 12px;
}
.kc-purple::after { background: linear-gradient(90deg,#875A7B,#b386a8); }
.kc-green::after  { background: linear-gradient(90deg,#1abc9c,#27ae60); }
.kc-amber::after  { background: linear-gradient(90deg,#f39c12,#e67e22); }
.kc-blue::after   { background: linear-gradient(90deg,#3498db,#2980b9); }

.kpi-emoji { font-size: 1.6rem; margin-bottom: 10px; display: block; }
.kpi-val {
    font-size: 2rem;
    font-weight: 800;
    color: #1a252f;
    line-height: 1;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 5px;
}
.kpi-lbl {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #95a5a6;
}

/* ── Pipeline ── */
.pipeline-box {
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e4e8ee;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    padding: 20px 28px;
    margin: 20px 0;
}
.pipeline-lbl {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    color: #95a5a6;
    margin-bottom: 22px;
}
.pipeline-track {
    display: flex;
    align-items: flex-start;
    position: relative;
}
.p-step {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
}
.p-step::after {
    content: '';
    position: absolute;
    top: 17px; left: 50%;
    width: 100%; height: 3px;
    z-index: 0;
}
.p-step:last-child::after { display: none; }
.p-done::after    { background: #1abc9c; }
.p-active::after  { background: linear-gradient(90deg, #e67e22 50%, #e4e8ee 50%); }
.p-pending::after { background: #e4e8ee; }

.p-dot {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800;
    position: relative; z-index: 1;
    border: 2.5px solid;
    transition: all 0.2s;
}
.p-done   .p-dot { background: #1abc9c; border-color: #1abc9c; color: #fff; }
.p-active .p-dot { background: #fff; border-color: #e67e22; color: #e67e22; box-shadow: 0 0 0 5px rgba(230,126,34,0.15); animation: beat 1.4s ease-in-out infinite; }
.p-pending .p-dot { background: #f4f6f9; border-color: #cdd4db; color: #b2bec3; }

@keyframes beat {
    0%,100% { box-shadow: 0 0 0 3px rgba(230,126,34,0.2); }
    50%      { box-shadow: 0 0 0 9px rgba(230,126,34,0.05); }
}

.p-name {
    font-size: 0.67rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.6px;
    text-align: center; margin-top: 8px;
    color: #b2bec3;
}
.p-done   .p-name { color: #1abc9c; }
.p-active .p-name { color: #e67e22; }

/* ── Stage Cards ── */
.sc {
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e4e8ee;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 14px;
    overflow: hidden;
    transition: box-shadow 0.18s;
}
.sc:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.09); }
.sc-head {
    padding: 13px 20px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #f0f3f6;
    background: #fafbfc;
}
.sc-icon-wrap {
    width: 36px; height: 36px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; margin-right: 12px; flex-shrink: 0;
}
.sc-title { font-size: 0.95rem; font-weight: 800; color: #1a252f; }
.sc-sub   { font-size: 0.72rem; color: #95a5a6; margin-top: 1px; }
.badge {
    padding: 4px 11px; border-radius: 20px;
    font-size: 0.68rem; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.6px;
}
.badge-done    { background: #e8faf4; color: #1a8a5e; border: 1px solid #a3dfc7; }
.badge-active  { background: #fef8ec; color: #b7740a; border: 1px solid #f8d99b; }
.badge-pending { background: #f2f4f6; color: #95a5a6; border: 1px solid #dde1e6; }

.sc-body { padding: 16px 20px; }

.info-row {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 16px;
}
.inf-lbl { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #95a5a6; margin-bottom: 3px; }
.inf-val { font-size: 0.86rem; font-weight: 700; color: #2c3e50; }
.inf-mono { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; }

.size-row { display: flex; flex-wrap: wrap; gap: 7px; }
.sz-chip {
    background: #f4f6f9; border: 1px solid #e0e4ea;
    border-radius: 8px; padding: 5px 9px; text-align: center; min-width: 44px;
}
.sz-chip .s  { font-size: 0.58rem; font-weight: 700; color: #95a5a6; text-transform: uppercase; display: block; }
.sz-chip .q  { font-size: 0.92rem; font-weight: 800; color: #2c3e50; font-family: 'IBM Plex Mono', monospace; display: block; }
.sz-chip.on  { background: #f3eaf6; border-color: #c89ddb; }
.sz-chip.on .s  { color: #875A7B; }
.sz-chip.on .q  { color: #5e3268; }
.sz-total    { background: linear-gradient(135deg,#875A7B,#6c4765); border: none; min-width: 52px; }
.sz-total .s { color: rgba(255,255,255,0.7) !important; }
.sz-total .q { color: #fff !important; }

/* ── Summary Table ── */
.tbl-wrap {
    background: #fff;
    border-radius: 12px; border: 1px solid #e4e8ee;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    overflow: hidden; margin-bottom: 22px;
}
.tbl-head {
    padding: 13px 20px;
    background: #fafbfc; border-bottom: 1px solid #e4e8ee;
    font-size: 0.7rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 1.6px; color: #7f8c8d;
}
.stDataFrame { border: none !important; }
.stDataFrame [data-testid="stDataFrameResizable"] {
    border: none !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: #fff !important;
    color: #875A7B !important;
    border: 1.5px solid #875A7B !important;
    border-radius: 8px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 9px 16px !important;
    transition: all 0.18s !important;
}
.stDownloadButton > button:hover {
    background: #875A7B !important;
    color: #fff !important;
}

/* ── Empty state ── */
.empty-box {
    background: #fff; border-radius: 12px;
    border: 1.5px dashed #d8dde4;
    padding: 64px 32px; text-align: center; margin-top: 8px;
}
.empty-box .ei { font-size: 3.2rem; margin-bottom: 14px; }
.empty-box h3  { font-size: 1rem; font-weight: 800; color: #7f8c8d; margin-bottom: 6px; }
.empty-box p   { font-size: 0.82rem; color: #b2bec3; }

.divider { border: none; border-top: 1px solid #e4e8ee; margin: 20px 0; }
.section-hdr { font-size: 0.78rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.2px; color: #7f8c8d; margin-bottom: 14px; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ────────────────────────────────────────────────────────────────
SIZES  = ["XS","S","M","L","XL","XXL","3XL","4XL","5XL","6XL","7XL","8XL"]
STAGES = [
    ("cutting",   "Cutting",          "✂️",  "#875A7B"),
    ("stitching", "Stitching",        "🧵",  "#3498db"),
    ("handwork",  "Hand Work / Kaaz", "🖐️",  "#e67e22"),
    ("finishing", "Finishing",        "✨",  "#1abc9c"),
]

def safe_read(f):
    try:
        df = pd.read_excel(f)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def fcol(df, *cands):
    m = {c.lower(): c for c in df.columns}
    for c in cands:
        if c.lower() in m: return m[c.lower()]
    return None

def get_sizes(df, style):
    sc = fcol(df, "style no", "style", "order no", "order")
    if sc is None or df.empty: return {}
    row = df[df[sc].astype(str).str.upper() == style.upper()]
    if row.empty: return {}
    row = row.iloc[0]
    out = {}
    for s in SIZES:
        col = fcol(df, s)
        out[s] = int(row[col]) if col and pd.notna(row.get(col)) else 0
    return out

def get_info(df, style):
    sc = fcol(df, "style no", "style", "order no", "order")
    if sc is None or df.empty: return {}
    row = df[df[sc].astype(str).str.upper() == style.upper()]
    if row.empty: return {}
    row = row.iloc[0]
    info = {}
    for key, *cands in [
        ("challan",  "ch no","challan no","ch. no","challan"),
        ("vendor",   "vendor name","vendor","party"),
        ("i_date",   "issue date","i. date","i date","idate"),
        ("r_date",   "receive date","r. date","r date","rdate","received date"),
        ("del_date", "delivery date","del date","delivery"),
    ]:
        col = fcol(df, *cands)
        info[key] = str(row[col]) if col and pd.notna(row.get(col)) else "—"
    return info

def get_status(info, sizes):
    has_r = info.get("r_date","—") not in ("—","nan","NaT","")
    has_i = info.get("i_date","—") not in ("—","nan","NaT","")
    if has_r and sum(sizes.values()) > 0: return "done"
    if has_i: return "active"
    return "pending"

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sb-brand'>
      <div class='sb-brand-title'>🏭 Production Tracker</div>
      <div class='sb-brand-sub'>Garment Production Management</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sb-label'>📂 Excel Files</div>", unsafe_allow_html=True)
    f_cut = st.file_uploader("✂️ Cutting",          type=["xlsx","xls"], key="c", label_visibility="visible")
    f_sti = st.file_uploader("🧵 Stitching",        type=["xlsx","xls"], key="s")
    f_hnd = st.file_uploader("🖐️ Hand Work / Kaaz", type=["xlsx","xls"], key="h")
    f_fin = st.file_uploader("✨ Finishing",         type=["xlsx","xls"], key="f")

    st.markdown("<div class='sb-label'>📋 Column Guide</div>", unsafe_allow_html=True)
    st.caption("Style No • CH No • Vendor Name\nI. Date • R. Date • Delivery Date\nXS S M L XL XXL 3XL…8XL")

    st.markdown("<div class='sb-label'>⬇️ Sample File</div>", unsafe_allow_html=True)
    sdf = pd.DataFrame({
        "Style No":["1557YKRED","2341BKBLU"], "CH No":["CH-001","CH-002"],
        "Vendor Name":["ABC Stitching","XYZ Tailor"],
        "I. Date":["01-Jan-2025","05-Jan-2025"], "R. Date":["10-Jan-2025",""],
        "Delivery Date":["15-Jan-2025","20-Jan-2025"],
        "XS":[10,5],"S":[20,10],"M":[30,15],"L":[25,12],
        "XL":[20,8],"XXL":[10,5],"3XL":[5,2],"4XL":[3,1],
        "5XL":[2,0],"6XL":[1,0],"7XL":[0,0],"8XL":[0,0],
    })
    sb = io.BytesIO(); sdf.to_excel(sb, index=False)
    st.download_button("⬇️ Download Sample Excel", sb.getvalue(),
        file_name="sample_stage.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

# ─── MAIN AREA ───────────────────────────────────────────────────────────────

# Top bar
st.markdown(f"""
<div class='topbar'>
  <div class='topbar-left'>
    <div class='topbar-icon'>🏭</div>
    <div class='topbar-title'>Production <em>Tracker</em></div>
  </div>
  <div class='topbar-right'>📅 {date.today().strftime("%d %B %Y")}</div>
</div>""", unsafe_allow_html=True)

# Page heading
st.markdown("""
<div class='page-heading'>
  <div class='breadcrumb'>Production › <b>Style Tracking</b></div>
  <h2>Production Order Tracker</h2>
  <p>Style number daalo — saari stages ka status ek jagah dikhe</p>
</div>""", unsafe_allow_html=True)

# Search bar
col1, col2 = st.columns([5, 1])
with col1:
    style_input = st.text_input(
        "", placeholder="🔍  Style number daalo — jaise: 1557YKRED",
        label_visibility="collapsed"
    ).strip().upper()
with col2:
    search_btn = st.button("🔎 Search", type="primary", use_container_width=True)

# Empty state
if not style_input:
    st.markdown("""
    <div class='empty-box'>
      <div class='ei'>🏭</div>
      <h3>Koi style search nahi kiya abhi</h3>
      <p>Upar style number daalo aur sidebar mein Excel files upload karo</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ─── Load Data ───────────────────────────────────────────────────────────────
dfs = {
    "cutting":   safe_read(f_cut) if f_cut else pd.DataFrame(),
    "stitching": safe_read(f_sti) if f_sti else pd.DataFrame(),
    "handwork":  safe_read(f_hnd) if f_hnd else pd.DataFrame(),
    "finishing": safe_read(f_fin) if f_fin else pd.DataFrame(),
}
stage_data = {}
for sk, *_ in STAGES:
    df = dfs[sk]
    info  = get_info(df,  style_input) if not df.empty else {}
    sizes = get_sizes(df, style_input) if not df.empty else {}
    stage_data[sk] = (info, sizes)

if not any(stage_data[sk][0] for sk, *_ in STAGES):
    st.markdown(f"""
    <div class='empty-box'>
      <div class='ei'>🔍</div>
      <h3>Style <b>{style_input}</b> nahi mila</h3>
      <p>Style number check karo ya Excel files sidebar mein upload karo</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ─── KPI Row ────────────────────────────────────────────────────────────────
cut_sizes  = stage_data["cutting"][1]
total_qty  = sum(cut_sizes.values())
done_n     = sum(1 for sk,*_ in STAGES if get_status(*stage_data[sk]) == "done")
active_n   = sum(1 for sk,*_ in STAGES if get_status(*stage_data[sk]) == "active")
pct        = int(done_n / 4 * 100)

k1, k2, k3, k4 = st.columns(4)
for col, val, lbl, emoji, cls in [
    (k1, total_qty or "—", "Total Order Qty",  "📦", "kc-purple"),
    (k2, f"{done_n}/4",    "Stages Complete",   "✅", "kc-green"),
    (k3, active_n,         "In Progress",       "🔄", "kc-amber"),
    (k4, f"{pct}%",        "Overall Progress",  "📊", "kc-blue"),
]:
    with col:
        st.markdown(f"""
        <div class='kpi-card {cls}'>
          <span class='kpi-emoji'>{emoji}</span>
          <div class='kpi-val'>{val}</div>
          <div class='kpi-lbl'>{lbl}</div>
        </div>""", unsafe_allow_html=True)

# ─── Pipeline ───────────────────────────────────────────────────────────────
dot_icon = {"done": "✓", "active": "⟳", "pending": "○"}
steps_html = ""
for sk, sl, icon, _ in STAGES:
    s = get_status(*stage_data[sk])
    steps_html += f"""
    <div class='p-step p-{s}'>
      <div class='p-dot'>{dot_icon[s]}</div>
      <div class='p-name'>{icon} {sl}</div>
    </div>"""

st.markdown(f"""
<div class='pipeline-box'>
  <div class='pipeline-lbl'>📍 Production Pipeline — Style: {style_input}</div>
  <div class='pipeline-track'>{steps_html}</div>
</div>""", unsafe_allow_html=True)

# ─── Stage Cards ────────────────────────────────────────────────────────────
st.markdown("<div class='section-hdr'>Stage-wise Details</div>", unsafe_allow_html=True)

badge_map = {
    "done":    "<span class='badge badge-done'>✓ Complete</span>",
    "active":  "<span class='badge badge-active'>⟳ In Progress</span>",
    "pending": "<span class='badge badge-pending'>○ Pending</span>",
}

for sk, sl, icon, color in STAGES:
    info, sizes = stage_data[sk]
    s     = get_status(info, sizes) if info else "pending"
    total = sum(sizes.values())

    # size chips
    chips = ""
    for sz in SIZES:
        qty = sizes.get(sz, 0)
        cls = "on" if qty else ""
        chips += f"<div class='sz-chip {cls}'><span class='s'>{sz}</span><span class='q'>{qty if qty else '—'}</span></div>"
    if total:
        chips += f"<div class='sz-chip sz-total'><span class='s'>TOTAL</span><span class='q'>{total}</span></div>"

    # info row
    info_html = ""
    if info:
        for lbl, val, mono in [
            ("CH. No",      info.get("challan","—"),  "inf-mono"),
            ("Vendor",      info.get("vendor","—"),   ""),
            ("Issue Date",  info.get("i_date","—"),   "inf-mono"),
            ("Rcv. Date",   info.get("r_date","—"),   "inf-mono"),
            ("Delivery",    info.get("del_date","—"), "inf-mono"),
        ]:
            info_html += f"<div><div class='inf-lbl'>{lbl}</div><div class='inf-val {mono}'>{val}</div></div>"

    body = ""
    if info:
        body = f"""
        <div class='sc-body'>
          <div class='info-row'>{info_html}</div>
          <div class='inf-lbl' style='margin-bottom:9px'>Size-wise Quantity</div>
          <div class='size-row'>{chips if chips else "<span style='color:#b2bec3;font-size:.83rem'>Data nahi mila</span>"}</div>
        </div>"""
    else:
        body = "<div class='sc-body' style='color:#b2bec3;font-size:.83rem'>File upload nahi hui ya style nahi mila.</div>"

    st.markdown(f"""
    <div class='sc'>
      <div class='sc-head'>
        <div style='display:flex;align-items:center'>
          <div class='sc-icon-wrap' style='background:{color}20'>{icon}</div>
          <div>
            <div class='sc-title'>{sl}</div>
            <div class='sc-sub'>Total: {total if total else "—"} pieces</div>
          </div>
        </div>
        {badge_map[s]}
      </div>
      {body}
    </div>""", unsafe_allow_html=True)

# ─── Summary Table ───────────────────────────────────────────────────────────
rows = []
for sk, sl, icon, _ in STAGES:
    _, sizes = stage_data[sk]
    if sizes:
        r = {"Stage": f"{icon} {sl}"}
        for sz in SIZES: r[sz] = sizes.get(sz, 0) or ""
        r["TOTAL"] = sum(sizes.values())
        rows.append(r)

if rows:
    st.markdown("""
    <div class='tbl-wrap'>
      <div class='tbl-head'>📐 Size-wise Summary — All Stages</div>""",
    unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows).set_index("Stage"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Export ──────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div class='section-hdr'>📤 Export</div>", unsafe_allow_html=True)

def build_report(style, sd):
    r = ""
    for sk, sl, icon, _ in STAGES:
        inf, szs = sd.get(sk, ({}, {}))
        total = sum(szs.values())
        sc = "".join(f"<td>{szs.get(s,0) or ''}</td>" for s in SIZES)
        r += f"<tr style='background:#f8f9fa'><td colspan='14' style='padding:8px;font-weight:700'>{icon} {sl} &nbsp;|&nbsp; CH: {inf.get('challan','—')} &nbsp;|&nbsp; Vendor: {inf.get('vendor','—')} &nbsp;|&nbsp; Issue: {inf.get('i_date','—')} &nbsp;|&nbsp; Rcvd: {inf.get('r_date','—')} &nbsp;|&nbsp; Del: {inf.get('del_date','—')}</td></tr><tr>{sc}<td><b>{total}</b></td></tr>"
    ths = "".join(f"<th>{s}</th>" for s in SIZES)
    return f"<html><head><style>body{{font-family:Arial;font-size:11px;margin:24px}}h2{{color:#875A7B}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{border:1px solid #ddd;padding:5px 8px;text-align:center}}th{{background:#875A7B;color:white;font-size:10px}}</style></head><body><h2>🏭 Production Report — {style}</h2><p style='color:#7f8c8d'>Generated: {date.today()}</p><table><tr><th>Stage</th>{ths}<th>TOTAL</th></tr>{r}</table></body></html>"

e1, e2, e3 = st.columns(3)
with e1:
    st.download_button("🖨️ Print-Ready HTML", build_report(style_input, stage_data),
        file_name=f"report_{style_input}_{date.today()}.html",
        mime="text/html", use_container_width=True)
with e2:
    if rows:
        xl = io.BytesIO()
        pd.DataFrame(rows).to_excel(xl, index=False)
        st.download_button("📊 Excel Summary", xl.getvalue(),
            file_name=f"summary_{style_input}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

st.markdown("""
<div style='text-align:center;color:#b2bec3;font-size:0.7rem;padding:20px 0 6px'>
  Production Tracker &nbsp;•&nbsp; Data sirf aapki Excel files se aata hai &nbsp;•&nbsp; Koi data server pe save nahi hota
</div>""", unsafe_allow_html=True)
