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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=IBM+Plex+Mono:wght@500&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background: #f0f4f8 !important;
    color: #2c3e50 !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #1a2332 !important;
    min-width: 260px !important;
    max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small {
    color: #7a95a8 !important;
    font-family: 'Nunito', sans-serif !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px dashed rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stDownloadButton > button {
    background: rgba(135,90,123,0.25) !important;
    color: #d4a8c7 !important;
    border: 1px solid rgba(135,90,123,0.4) !important;
    border-radius: 7px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    width: 100%;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background: #875A7B !important;
    color: white !important;
}

/* ── MAIN AREA ── */
.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 100% !important;
}

/* ── PAGE HEADER CARD ── */
.page-header {
    background: linear-gradient(135deg, #875A7B 0%, #5e3260 100%);
    border-radius: 14px;
    padding: 22px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(135,90,123,0.35);
}
.ph-left h1 {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: #fff !important;
    margin: 0 0 4px 0 !important;
}
.ph-left p { font-size: 0.83rem; color: rgba(255,255,255,0.65); margin: 0; }
.ph-right  { font-size: 0.8rem; color: rgba(255,255,255,0.55); font-weight: 600; text-align: right; }
.ph-date   { font-size: 1.1rem; font-weight: 800; color: rgba(255,255,255,0.9); }

/* ── SECTION LABEL ── */
.sec-label {
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    color: #95a5a6;
    margin: 20px 0 10px;
}

/* ── SEARCH BOX ── */
.stTextInput > div > div > input {
    border: 1.5px solid #d0d7e2 !important;
    border-radius: 10px !important;
    padding: 11px 16px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    background: #ffffff !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #875A7B !important;
    box-shadow: 0 0 0 3px rgba(135,90,123,0.12) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #875A7B, #6c4765) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 11px 24px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important; font-size: 0.92rem !important;
    box-shadow: 0 3px 12px rgba(135,90,123,0.3) !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(135,90,123,0.4) !important;
}

/* ── KPI CARDS ── */
.kcard {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px 20px 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    position: relative; overflow: hidden;
    transition: transform 0.18s, box-shadow 0.18s;
}
.kcard:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
.kcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    border-radius: 12px 12px 0 0;
}
.kc1::before { background: linear-gradient(90deg, #875A7B, #c084b0); }
.kc2::before { background: linear-gradient(90deg, #059669, #34d399); }
.kc3::before { background: linear-gradient(90deg, #d97706, #fbbf24); }
.kc4::before { background: linear-gradient(90deg, #2563eb, #60a5fa); }
.kcard-icon { font-size: 1.6rem; margin-bottom: 10px; display: block; }
.kcard-val  { font-size: 2rem; font-weight: 800; color: #1a202c; font-family: 'IBM Plex Mono', monospace; line-height: 1; margin-bottom: 5px; }
.kcard-lbl  { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; }

/* ── PIPELINE ── */
.pipeline-wrap {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 20px 28px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.pipe-title {
    font-size: 0.67rem; font-weight: 800;
    text-transform: uppercase; letter-spacing: 1.8px;
    color: #94a3b8; margin-bottom: 20px;
}
.pipe-track { display: flex; align-items: flex-start; }
.pipe-step  { flex: 1; display: flex; flex-direction: column; align-items: center; position: relative; }
.pipe-step::after { content: ''; position: absolute; top: 16px; left: 50%; width: 100%; height: 3px; z-index: 0; }
.pipe-step:last-child::after { display: none; }
.ps-done::after   { background: #059669; }
.ps-active::after { background: linear-gradient(90deg, #d97706 50%, #e2e8f0 50%); }
.ps-pending::after{ background: #e2e8f0; }
.pipe-dot {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800;
    position: relative; z-index: 1; border: 3px solid;
}
.ps-done   .pipe-dot { background: #059669; border-color: #059669; color: white; }
.ps-active .pipe-dot { background: white; border-color: #d97706; color: #d97706; animation: pulse 1.5s infinite; }
.ps-pending .pipe-dot{ background: #f8fafc; border-color: #cbd5e1; color: #cbd5e1; }
@keyframes pulse {
    0%,100% { box-shadow: 0 0 0 3px rgba(217,119,6,0.2); }
    50%      { box-shadow: 0 0 0 8px rgba(217,119,6,0.04); }
}
.pipe-label { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; text-align: center; margin-top: 8px; color: #cbd5e1; }
.ps-done   .pipe-label { color: #059669; }
.ps-active .pipe-label { color: #d97706; }

/* ── STAGE CARDS ── */
.scard {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 14px;
    overflow: hidden;
    transition: box-shadow 0.18s;
}
.scard:hover { box-shadow: 0 4px 18px rgba(0,0,0,0.1); }
.scard-head {
    padding: 13px 20px;
    display: flex; align-items: center; justify-content: space-between;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
}
.scard-ico  { width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 16px; margin-right: 12px; flex-shrink: 0; }
.scard-name { font-size: 0.92rem; font-weight: 800; color: #1a202c; }
.scard-sub  { font-size: 0.7rem; color: #94a3b8; margin-top: 1px; }
.badge      { padding: 3px 11px; border-radius: 20px; font-size: 0.66rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.4px; }
.b-done     { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.b-active   { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.b-pending  { background: #f1f5f9; color: #64748b; border: 1px solid #cbd5e1; }
.scard-body { padding: 16px 20px; }
.info-grid  { display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; margin-bottom: 16px; }
.info-label { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; margin-bottom: 3px; }
.info-value { font-size: 0.86rem; font-weight: 700; color: #2d3748; }
.info-mono  { font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; }
.size-strip { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.sz {
    background: #f1f5f9; border: 1px solid #e2e8f0;
    border-radius: 8px; padding: 4px 9px;
    text-align: center; min-width: 44px;
}
.sz .sl { font-size: 0.56rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; display: block; }
.sz .sq { font-size: 0.9rem; font-weight: 800; color: #2d3748; font-family: 'IBM Plex Mono', monospace; display: block; }
.sz.on  { background: #fdf4ff; border-color: #d8b4fe; }
.sz.on .sl { color: #7c3aed; }
.sz.on .sq { color: #4c1d95; }
.sz.tot { background: linear-gradient(135deg,#875A7B,#6c4765); border: none; min-width: 52px; }
.sz.tot .sl { color: rgba(255,255,255,0.7); }
.sz.tot .sq { color: white; }

/* ── SUMMARY TABLE ── */
.tbl-wrap { background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow: hidden; margin-bottom: 20px; }
.tbl-top  { padding: 13px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; font-size: 0.67rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.8px; color: #64748b; }

/* ── DOWNLOAD BUTTONS ── */
.stDownloadButton > button {
    background: #ffffff !important;
    color: #875A7B !important;
    border: 1.5px solid #875A7B !important;
    border-radius: 8px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.84rem !important;
    transition: all 0.18s !important;
}
.stDownloadButton > button:hover {
    background: #875A7B !important;
    color: white !important;
}

/* ── EMPTY STATE ── */
.empty-state {
    background: #ffffff;
    border-radius: 14px;
    border: 2px dashed #e2e8f0;
    padding: 64px 32px;
    text-align: center;
    margin-top: 8px;
}
.empty-state .ei   { font-size: 3.2rem; margin-bottom: 14px; }
.empty-state h3    { font-size: 1.05rem; font-weight: 800; color: #64748b; margin-bottom: 6px; }
.empty-state p     { font-size: 0.82rem; color: #94a3b8; }

hr.divider { border: none; border-top: 1px solid #e2e8f0; margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
SIZES  = ["XS","S","M","L","XL","XXL","3XL","4XL","5XL","6XL","7XL","8XL"]
STAGES = [
    ("cutting",   "Cutting",          "✂️",  "#875A7B"),
    ("stitching", "Stitching",        "🧵",  "#2563eb"),
    ("handwork",  "Hand Work / Kaaz", "🖐️",  "#d97706"),
    ("finishing", "Finishing",        "✨",  "#059669"),
]

def safe_read(f):
    try:
        df = pd.read_excel(f)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return pd.DataFrame()

def fcol(df, *cands):
    m = {c.lower(): c for c in df.columns}
    for c in cands:
        if c.lower() in m: return m[c.lower()]
    return None

def get_sizes(df, style):
    sc = fcol(df,"style no","style","order no","order")
    if sc is None or df.empty: return {}
    row = df[df[sc].astype(str).str.upper() == style.upper()]
    if row.empty: return {}
    row = row.iloc[0]
    return {s: int(row[fcol(df,s)]) if fcol(df,s) and pd.notna(row.get(fcol(df,s))) else 0 for s in SIZES}

def get_info(df, style):
    sc = fcol(df,"style no","style","order no","order")
    if sc is None or df.empty: return {}
    row = df[df[sc].astype(str).str.upper() == style.upper()]
    if row.empty: return {}
    row = row.iloc[0]; info = {}
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

def gstatus(info, sizes):
    hr = info.get("r_date","—") not in ("—","nan","NaT","")
    hi = info.get("i_date","—") not in ("—","nan","NaT","")
    if hr and sum(sizes.values()) > 0: return "done"
    if hi: return "active"
    return "pending"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style='background:linear-gradient(135deg,#875A7B,#5e3260);
                padding:20px 16px 18px; margin:-1rem -1rem 0; margin-bottom:16px'>
      <div style='font-size:1.05rem;font-weight:800;color:#fff;margin-bottom:3px'>🏭 Prod. Tracker</div>
      <div style='font-size:0.68rem;color:rgba(255,255,255,0.5)'>Garment Production System</div>
    </div>
    """, unsafe_allow_html=True)

    # Nav items
    st.markdown("""
    <div style='padding:0 4px'>
      <div style='font-size:0.58rem;font-weight:800;text-transform:uppercase;
                  letter-spacing:2px;color:#374a5a;padding:4px 8px 8px'>Main Menu</div>
      <div style='background:rgba(135,90,123,0.3);border-radius:8px;padding:9px 12px;
                  display:flex;align-items:center;gap:10px;margin-bottom:2px'>
        <span style='font-size:16px'>📋</span>
        <span style='font-size:0.82rem;font-weight:700;color:#fff'>Production Status</span>
      </div>

      <div style='font-size:0.58rem;font-weight:800;text-transform:uppercase;
                  letter-spacing:2px;color:#374a5a;padding:14px 8px 8px;
                  border-top:1px solid rgba(255,255,255,0.05);margin-top:8px'>Coming Soon</div>
    """, unsafe_allow_html=True)

    for ico, name in [("📦","Order Management"),("✂️","Cutting Dept."),
                      ("🧵","Stitching Dept."),("✨","Finishing Dept."),
                      ("📊","Reports"),("🧶","Fabric Stock")]:
        st.markdown(f"""
        <div style='border-radius:8px;padding:8px 12px;display:flex;align-items:center;
                    gap:10px;margin-bottom:2px;cursor:pointer;
                    transition:background 0.15s' 
             onmouseover="this.style.background='rgba(255,255,255,0.06)'"
             onmouseout="this.style.background='transparent'">
          <span style='font-size:15px'>{ico}</span>
          <span style='font-size:0.79rem;font-weight:700;color:#566f80;flex:1'>{name}</span>
          <span style='background:rgba(135,90,123,0.3);color:#c49aba;
                       font-size:0.55rem;font-weight:800;padding:2px 6px;
                       border-radius:8px'>Soon</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Upload section
    st.markdown("""
    <hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:12px 0'>
    <div style='font-size:0.58rem;font-weight:800;text-transform:uppercase;
                letter-spacing:2px;color:#374a5a;padding:4px 4px 10px'>
      📂 Excel Files Upload
    </div>
    """, unsafe_allow_html=True)

    f_cut = st.file_uploader("✂️ Cutting",          type=["xlsx","xls"], key="c")
    f_sti = st.file_uploader("🧵 Stitching",        type=["xlsx","xls"], key="s")
    f_hnd = st.file_uploader("🖐️ Hand Work / Kaaz", type=["xlsx","xls"], key="h")
    f_fin = st.file_uploader("✨ Finishing",         type=["xlsx","xls"], key="f")

    st.markdown("""
    <div style='font-size:0.65rem;color:#374a5a;padding:8px 4px 6px'>
      Column names: Style No • CH No • Vendor Name<br>
      I. Date • R. Date • Delivery Date<br>
      XS S M L XL XXL 3XL 4XL 5XL 6XL 7XL 8XL
    </div>
    """, unsafe_allow_html=True)

    sdf = pd.DataFrame({
        "Style No":["1557YKRED","2341BKBLU"],"CH No":["CH-001","CH-002"],
        "Vendor Name":["ABC Stitching","XYZ Tailor"],
        "I. Date":["01-Jan-2025","05-Jan-2025"],"R. Date":["10-Jan-2025",""],
        "Delivery Date":["15-Jan-2025","20-Jan-2025"],
        "XS":[10,5],"S":[20,10],"M":[30,15],"L":[25,12],
        "XL":[20,8],"XXL":[10,5],"3XL":[5,2],"4XL":[3,1],
        "5XL":[2,0],"6XL":[1,0],"7XL":[0,0],"8XL":[0,0],
    })
    sb = io.BytesIO(); sdf.to_excel(sb, index=False)
    st.download_button("⬇️ Sample Excel Download", sb.getvalue(),
        file_name="sample.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

    st.markdown(f"""
    <div style='text-align:center;color:#2a3d4e;font-size:0.62rem;padding:16px 0 4px;
                border-top:1px solid rgba(255,255,255,0.05);margin-top:12px'>
      v1.0 &nbsp;•&nbsp; {date.today().strftime("%d %b %Y")}
    </div>""", unsafe_allow_html=True)

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────

# Page header banner
st.markdown(f"""
<div class='page-header'>
  <div class='ph-left'>
    <h1>🏭 Production Order Tracker</h1>
    <p>Style number daalo — Cutting se Finishing tak saari stages ek jagah</p>
  </div>
  <div class='ph-right'>
    <div class='ph-date'>{date.today().strftime("%d %B %Y")}</div>
    <div>Production › Style Tracking</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Search
c1, c2 = st.columns([5, 1])
with c1:
    style_input = st.text_input("",
        placeholder="🔍  Style number daalo — jaise: 1557YKRED",
        label_visibility="collapsed").strip().upper()
with c2:
    st.button("🔎 Search", type="primary", use_container_width=True)

if not style_input:
    st.markdown("""
    <div class='empty-state'>
      <div class='ei'>🏭</div>
      <h3>Style number daalo aur search karo</h3>
      <p>Sidebar mein Excel files upload karke style number search karo</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# Load data
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

if not any(stage_data[sk][0] for sk,*_ in STAGES):
    st.markdown(f"""
    <div class='empty-state'>
      <div class='ei'>🔍</div>
      <h3>Style <b>{style_input}</b> nahi mila</h3>
      <p>Style number check karo ya Excel files upload karo</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# KPI
cut_s  = stage_data["cutting"][1]
total  = sum(cut_s.values())
done_n = sum(1 for sk,*_ in STAGES if gstatus(*stage_data[sk])=="done")
act_n  = sum(1 for sk,*_ in STAGES if gstatus(*stage_data[sk])=="active")
pct    = int(done_n/4*100)

st.markdown("<div class='sec-label'>📊 Overview</div>", unsafe_allow_html=True)
k1,k2,k3,k4 = st.columns(4)
for col,val,lbl,em,kc in [
    (k1, total or "—", "Total Order Qty",  "📦","kc1"),
    (k2, f"{done_n}/4","Stages Complete",  "✅","kc2"),
    (k3, act_n,        "In Progress",      "🔄","kc3"),
    (k4, f"{pct}%",    "Overall Progress", "📈","kc4"),
]:
    with col:
        st.markdown(f"""
        <div class='kcard {kc}'>
          <span class='kcard-icon'>{em}</span>
          <div class='kcard-val'>{val}</div>
          <div class='kcard-lbl'>{lbl}</div>
        </div>""", unsafe_allow_html=True)

# Pipeline
di = {"done":"✓","active":"⟳","pending":"○"}
pc = {"done":"ps-done","active":"ps-active","pending":"ps-pending"}
steps = ""
for sk,sl,icon,_ in STAGES:
    s = gstatus(*stage_data[sk])
    steps += f"""<div class='pipe-step {pc[s]}'>
      <div class='pipe-dot'>{di[s]}</div>
      <div class='pipe-label'>{icon} {sl}</div>
    </div>"""

st.markdown(f"""
<div class='pipeline-wrap'>
  <div class='pipe-title'>📍 Production Pipeline — Style: {style_input}</div>
  <div class='pipe-track'>{steps}</div>
</div>""", unsafe_allow_html=True)

# Stage Cards
st.markdown("<div class='sec-label'>🗂️ Stage-wise Details</div>", unsafe_allow_html=True)
bmap = {
    "done":    "<span class='badge b-done'>✓ Complete</span>",
    "active":  "<span class='badge b-active'>⟳ In Progress</span>",
    "pending": "<span class='badge b-pending'>○ Pending</span>",
}

for sk,sl,icon,color in STAGES:
    info, sizes = stage_data[sk]
    s     = gstatus(info,sizes) if info else "pending"
    total = sum(sizes.values())

    chips = ""
    for sz in SIZES:
        qty = sizes.get(sz,0)
        chips += f"<div class='sz {'on' if qty else ''}'><span class='sl'>{sz}</span><span class='sq'>{qty if qty else '—'}</span></div>"
    if total:
        chips += f"<div class='sz tot'><span class='sl'>TOTAL</span><span class='sq'>{total}</span></div>"

    ihtml = ""
    if info:
        for lbl,val,mono in [
            ("CH. No",     info.get("challan","—"), "info-mono"),
            ("Vendor",     info.get("vendor","—"),  ""),
            ("Issue Date", info.get("i_date","—"),  "info-mono"),
            ("Rcv. Date",  info.get("r_date","—"),  "info-mono"),
            ("Delivery",   info.get("del_date","—"),"info-mono"),
        ]:
            ihtml += f"<div><div class='info-label'>{lbl}</div><div class='info-value {mono}'>{val}</div></div>"

    body = f"""<div class='scard-body'>
      <div class='info-grid'>{ihtml}</div>
      <div class='info-label' style='margin-bottom:8px'>Size-wise Quantity</div>
      <div class='size-strip'>{chips if chips else "<span style='color:#94a3b8;font-size:.82rem'>Data nahi mila</span>"}</div>
    </div>""" if info else "<div class='scard-body' style='color:#94a3b8;font-size:.82rem'>File upload nahi hui ya style nahi mila.</div>"

    st.markdown(f"""
    <div class='scard'>
      <div class='scard-head'>
        <div style='display:flex;align-items:center'>
          <div class='scard-ico' style='background:{color}18'>{icon}</div>
          <div>
            <div class='scard-name'>{sl}</div>
            <div class='scard-sub'>Total: {total if total else "—"} pieces</div>
          </div>
        </div>
        {bmap[s]}
      </div>
      {body}
    </div>""", unsafe_allow_html=True)

# Summary Table
rows = []
for sk,sl,icon,_ in STAGES:
    _,sizes = stage_data[sk]
    if sizes:
        r = {"Stage": f"{icon} {sl}"}
        for sz in SIZES: r[sz] = sizes.get(sz,0) or ""
        r["TOTAL"] = sum(sizes.values())
        rows.append(r)

if rows:
    st.markdown("""<div class='tbl-wrap'><div class='tbl-top'>📐 Size-wise Summary — All Stages</div>""", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows).set_index("Stage"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Export
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div class='sec-label'>📤 Export</div>", unsafe_allow_html=True)

def build_report(style, sd):
    r = ""
    for sk,sl,icon,_ in STAGES:
        inf,szs = sd.get(sk,({},{}))
        sc = "".join(f"<td>{szs.get(s,0) or ''}</td>" for s in SIZES)
        r += f"<tr style='background:#f8f9fa'><td colspan='14' style='padding:8px;font-weight:700'>{icon} {sl} | CH:{inf.get('challan','—')} | Vendor:{inf.get('vendor','—')} | Issue:{inf.get('i_date','—')} | Rcvd:{inf.get('r_date','—')} | Del:{inf.get('del_date','—')}</td></tr><tr>{sc}<td><b>{sum(szs.values())}</b></td></tr>"
    ths = "".join(f"<th>{s}</th>" for s in SIZES)
    return f"<html><head><style>body{{font-family:Arial;font-size:11px;margin:24px}}h2{{color:#875A7B}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{border:1px solid #ddd;padding:5px 8px;text-align:center}}th{{background:#875A7B;color:white;font-size:10px}}</style></head><body><h2>Production Report — {style}</h2><p style='color:#94a3b8'>Generated: {date.today()}</p><table><tr><th>Stage</th>{ths}<th>TOTAL</th></tr>{r}</table></body></html>"

e1,e2,_ = st.columns(3)
with e1:
    st.download_button("🖨️ Print-Ready Report (HTML)", build_report(style_input, stage_data),
        file_name=f"report_{style_input}_{date.today()}.html",
        mime="text/html", use_container_width=True)
with e2:
    if rows:
        xl = io.BytesIO(); pd.DataFrame(rows).to_excel(xl, index=False)
        st.download_button("📊 Excel Summary", xl.getvalue(),
            file_name=f"summary_{style_input}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

st.markdown("""
<div style='text-align:center;color:#94a3b8;font-size:0.68rem;padding:20px 0 4px'>
  Production Tracker v1.0 &nbsp;•&nbsp; Data sirf aapki Excel files se aata hai
</div>""", unsafe_allow_html=True)
