import streamlit as st
import pandas as pd
from datetime import date
import io

st.set_page_config(
    page_title="Production Tracker",
    page_icon="🏭",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=IBM+Plex+Mono:wght@500&display=swap');

/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
    background: #f0f2f6 !important;
    color: #2c3e50 !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── APP SHELL ── */
.app-shell {
    display: flex;
    min-height: 100vh;
}

/* ── LEFT NAV ── */
.leftnav {
    width: 220px;
    min-width: 220px;
    background: #1e2a35;
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    z-index: 100;
    overflow-y: auto;
}
.ln-brand {
    background: linear-gradient(135deg, #875A7B, #5e3260);
    padding: 18px 16px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.ln-brand-icon {
    width: 36px; height: 36px;
    background: rgba(255,255,255,0.15);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px;
}
.ln-brand-text { line-height: 1.2; }
.ln-brand-title { font-size: 0.95rem; font-weight: 800; color: #fff; }
.ln-brand-sub   { font-size: 0.65rem; color: rgba(255,255,255,0.55); }

.ln-section {
    padding: 18px 14px 6px;
    font-size: 0.58rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #4a6070;
}
.ln-item {
    margin: 2px 8px;
    padding: 9px 12px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    transition: background 0.15s;
    text-decoration: none;
}
.ln-item:hover { background: rgba(255,255,255,0.07); }
.ln-item.active { background: rgba(135,90,123,0.35); }
.ln-item .ico { font-size: 17px; width: 22px; text-align: center; }
.ln-item .txt { font-size: 0.82rem; font-weight: 700; color: #8fa8bc; }
.ln-item.active .txt { color: #fff; }
.ln-item:hover .txt { color: #c8d8e4; }

.ln-badge {
    margin-left: auto;
    background: rgba(135,90,123,0.5);
    color: #e8c5e0;
    font-size: 0.6rem;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 10px;
}

.ln-footer {
    margin-top: auto;
    padding: 14px 16px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 0.65rem;
    color: #3d5468;
    text-align: center;
}

/* ── MAIN CONTENT ── */
.main-wrap {
    margin-left: 220px;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

/* ── TOPBAR ── */
.topbar {
    background: #fff;
    border-bottom: 1.5px solid #e4e8ee;
    padding: 0 28px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: sticky;
    top: 0;
    z-index: 50;
}
.tb-left { display: flex; align-items: center; gap: 8px; }
.tb-crumb { font-size: 0.78rem; color: #95a5a6; font-weight: 600; }
.tb-crumb b { color: #875A7B; }
.tb-right { font-size: 0.75rem; color: #95a5a6; font-weight: 600; }

/* ── PAGE BODY ── */
.page-body { padding: 26px 30px 40px; }
.pg-title { font-size: 1.4rem; font-weight: 800; color: #1a252f; margin-bottom: 3px; }
.pg-sub   { font-size: 0.83rem; color: #7f8c8d; margin-bottom: 22px; }

/* ── UPLOAD SECTION ── */
.upload-bar {
    background: #fff;
    border-radius: 12px;
    border: 1px solid #e4e8ee;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.upload-bar-title {
    font-size: 0.68rem; font-weight: 800;
    text-transform: uppercase; letter-spacing: 1.6px;
    color: #7f8c8d; margin-bottom: 12px;
}

/* ── SEARCH ── */
.stTextInput > div > div > input {
    border: 1.5px solid #d8dde4 !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem !important;
    background: #fff !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    transition: all 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #875A7B !important;
    box-shadow: 0 0 0 3px rgba(135,90,123,0.12) !important;
    outline: none !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #875A7B, #6c4765) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; padding: 11px 20px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important; font-size: 0.88rem !important;
    box-shadow: 0 3px 10px rgba(135,90,123,0.3) !important;
    transition: all 0.18s !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 16px rgba(135,90,123,0.42) !important;
}

/* ── KPI CARDS ── */
.kpi {
    background: #fff; border-radius: 12px;
    padding: 18px 18px 14px;
    border: 1px solid #e4e8ee;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: relative; overflow: hidden;
    transition: transform 0.15s, box-shadow 0.15s;
}
.kpi:hover { transform: translateY(-2px); box-shadow: 0 5px 16px rgba(0,0,0,0.09); }
.kpi::after {
    content:''; position:absolute;
    bottom:0; left:0; right:0; height:3px;
    border-radius: 0 0 12px 12px;
}
.kp::after { background: linear-gradient(90deg,#875A7B,#b386a8); }
.kg::after { background: linear-gradient(90deg,#1abc9c,#27ae60); }
.ka::after { background: linear-gradient(90deg,#f39c12,#e67e22); }
.kb::after { background: linear-gradient(90deg,#3498db,#2980b9); }
.kpi-em  { font-size:1.4rem; margin-bottom:8px; display:block; }
.kpi-val { font-size:1.85rem; font-weight:800; color:#1a252f; font-family:'IBM Plex Mono',monospace; line-height:1; margin-bottom:4px; }
.kpi-lbl { font-size:0.67rem; font-weight:700; text-transform:uppercase; letter-spacing:0.9px; color:#95a5a6; }

/* ── PIPELINE ── */
.pipeline {
    background:#fff; border-radius:12px;
    border:1px solid #e4e8ee;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
    padding:18px 26px; margin:18px 0;
}
.pl-lbl { font-size:0.65rem; font-weight:800; text-transform:uppercase; letter-spacing:1.8px; color:#95a5a6; margin-bottom:18px; }
.pl-track { display:flex; align-items:flex-start; }
.pl-step { flex:1; display:flex; flex-direction:column; align-items:center; position:relative; }
.pl-step::after { content:''; position:absolute; top:15px; left:50%; width:100%; height:3px; z-index:0; }
.pl-step:last-child::after { display:none; }
.pld::after { background:#1abc9c; }
.pla::after { background:linear-gradient(90deg,#e67e22 50%,#e4e8ee 50%); }
.plp::after { background:#e4e8ee; }
.pl-dot {
    width:30px; height:30px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:13px; font-weight:800; position:relative; z-index:1; border:2.5px solid;
}
.pld .pl-dot { background:#1abc9c; border-color:#1abc9c; color:#fff; }
.pla .pl-dot { background:#fff; border-color:#e67e22; color:#e67e22; animation:beat 1.4s infinite; }
.plp .pl-dot { background:#f4f6f9; border-color:#cdd4db; color:#b2bec3; }
@keyframes beat {
    0%,100%{box-shadow:0 0 0 3px rgba(230,126,34,.2)}
    50%{box-shadow:0 0 0 8px rgba(230,126,34,.04)}
}
.pl-name { font-size:0.63rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; text-align:center; margin-top:7px; color:#b2bec3; }
.pld .pl-name { color:#1abc9c; }
.pla .pl-name { color:#e67e22; }

/* ── STAGE CARDS ── */
.sc { background:#fff; border-radius:12px; border:1px solid #e4e8ee; box-shadow:0 1px 4px rgba(0,0,0,0.05); margin-bottom:12px; overflow:hidden; transition:box-shadow 0.15s; }
.sc:hover { box-shadow:0 4px 16px rgba(0,0,0,0.09); }
.sc-hd { padding:12px 18px; display:flex; align-items:center; justify-content:space-between; background:#fafbfc; border-bottom:1px solid #f0f3f6; }
.sc-ico { width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:15px; margin-right:11px; flex-shrink:0; }
.sc-nm { font-size:0.9rem; font-weight:800; color:#1a252f; }
.sc-sb { font-size:0.68rem; color:#95a5a6; margin-top:1px; }
.badge { padding:3px 10px; border-radius:20px; font-size:0.65rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; }
.bd { background:#e8faf4; color:#1a8a5e; border:1px solid #a3dfc7; }
.ba { background:#fef8ec; color:#b7740a; border:1px solid #f8d99b; }
.bp { background:#f2f4f6; color:#95a5a6; border:1px solid #dde1e6; }
.sc-bd { padding:14px 18px; }
.irow { display:grid; grid-template-columns:repeat(5,1fr); gap:11px; margin-bottom:14px; }
.il { font-size:0.59rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#95a5a6; margin-bottom:2px; }
.iv { font-size:0.84rem; font-weight:700; color:#2c3e50; }
.im { font-family:'IBM Plex Mono',monospace; font-size:0.78rem; }
.szrow { display:flex; flex-wrap:wrap; gap:6px; }
.szc { background:#f4f6f9; border:1px solid #e0e4ea; border-radius:7px; padding:4px 8px; text-align:center; min-width:42px; }
.szc .s { font-size:0.56rem; font-weight:700; color:#95a5a6; text-transform:uppercase; display:block; }
.szc .q { font-size:0.87rem; font-weight:800; color:#2c3e50; font-family:'IBM Plex Mono',monospace; display:block; }
.szon { background:#f3eaf6 !important; border-color:#c89ddb !important; }
.szon .s { color:#875A7B !important; }
.szon .q { color:#5e3268 !important; }
.sztot { background:linear-gradient(135deg,#875A7B,#6c4765) !important; border:none !important; min-width:50px; }
.sztot .s { color:rgba(255,255,255,0.7) !important; }
.sztot .q { color:#fff !important; }

/* ── TABLE ── */
.tbl-box { background:#fff; border-radius:12px; border:1px solid #e4e8ee; box-shadow:0 1px 4px rgba(0,0,0,0.05); overflow:hidden; margin-bottom:18px; }
.tbl-hd  { padding:11px 18px; background:#fafbfc; border-bottom:1px solid #e4e8ee; font-size:0.66rem; font-weight:800; text-transform:uppercase; letter-spacing:1.6px; color:#7f8c8d; }

/* ── EXPORT BUTTONS ── */
.stDownloadButton > button {
    background:#fff !important; color:#875A7B !important;
    border:1.5px solid #875A7B !important; border-radius:8px !important;
    font-family:'Nunito',sans-serif !important; font-weight:700 !important; font-size:0.82rem !important;
    transition:all 0.18s !important;
}
.stDownloadButton > button:hover { background:#875A7B !important; color:#fff !important; }

/* ── EMPTY STATE ── */
.empty { background:#fff; border-radius:12px; border:1.5px dashed #d8dde4; padding:60px 32px; text-align:center; margin-top:8px; }
.empty .ei { font-size:3rem; margin-bottom:12px; }
.empty h3  { font-size:1rem; font-weight:800; color:#7f8c8d; margin-bottom:5px; }
.empty p   { font-size:0.8rem; color:#b2bec3; }

.divider { border:none; border-top:1px solid #e4e8ee; margin:18px 0; }
.sec-hdr { font-size:0.73rem; font-weight:800; text-transform:uppercase; letter-spacing:1.2px; color:#7f8c8d; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
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

# ── LEFT NAV (HTML — permanent, no toggle) ───────────────────────────────────
st.markdown(f"""
<div class="leftnav">
  <div class="ln-brand">
    <div class="ln-brand-icon">🏭</div>
    <div class="ln-brand-text">
      <div class="ln-brand-title">Prod. Tracker</div>
      <div class="ln-brand-sub">Garment Management</div>
    </div>
  </div>

  <div class="ln-section">Main Menu</div>
  <div class="ln-item active">
    <span class="ico">📋</span>
    <span class="txt">Production Status</span>
  </div>

  <div class="ln-section" style="margin-top:8px">Coming Soon</div>
  <div class="ln-item">
    <span class="ico">📦</span>
    <span class="txt">Order Management</span>
    <span class="ln-badge">Soon</span>
  </div>
  <div class="ln-item">
    <span class="ico">✂️</span>
    <span class="txt">Cutting Dept.</span>
    <span class="ln-badge">Soon</span>
  </div>
  <div class="ln-item">
    <span class="ico">🧵</span>
    <span class="txt">Stitching Dept.</span>
    <span class="ln-badge">Soon</span>
  </div>
  <div class="ln-item">
    <span class="ico">✨</span>
    <span class="txt">Finishing Dept.</span>
    <span class="ln-badge">Soon</span>
  </div>
  <div class="ln-item">
    <span class="ico">📊</span>
    <span class="txt">Reports</span>
    <span class="ln-badge">Soon</span>
  </div>
  <div class="ln-item">
    <span class="ico">🧶</span>
    <span class="txt">Fabric Stock</span>
    <span class="ln-badge">Soon</span>
  </div>

  <div class="ln-footer">v1.0 &nbsp;•&nbsp; {date.today().strftime("%d %b %Y")}</div>
</div>
""", unsafe_allow_html=True)

# ── MAIN CONTENT WRAPPER ──────────────────────────────────────────────────────
st.markdown("""<div class="main-wrap">""", unsafe_allow_html=True)

# Topbar
st.markdown(f"""
<div class="topbar">
  <div class="tb-left">
    <span class="tb-crumb">Production › <b>Style Tracking</b></span>
  </div>
  <div class="tb-right">📅 {date.today().strftime("%d %B %Y")}</div>
</div>
""", unsafe_allow_html=True)

# Page body starts
st.markdown("""<div class="page-body">""", unsafe_allow_html=True)

st.markdown("""
<div class="pg-title">Production Order Tracker</div>
<div class="pg-sub">Style number daalo — saari stages ka status ek jagah dikhe</div>
""", unsafe_allow_html=True)

# ── FILE UPLOADS ──────────────────────────────────────────────────────────────
st.markdown("<div class='upload-bar'><div class='upload-bar-title'>📂 Excel Files Upload Karo</div></div>", unsafe_allow_html=True)

u1, u2, u3, u4 = st.columns(4)
with u1: f_cut = st.file_uploader("✂️ Cutting",          type=["xlsx","xls"], key="c")
with u2: f_sti = st.file_uploader("🧵 Stitching",        type=["xlsx","xls"], key="s")
with u3: f_hnd = st.file_uploader("🖐️ Hand Work / Kaaz", type=["xlsx","xls"], key="h")
with u4: f_fin = st.file_uploader("✨ Finishing",         type=["xlsx","xls"], key="f")

# Sample download
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
st.download_button("⬇️ Sample Excel Format", sb.getvalue(),
    file_name="sample_stage.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── SEARCH ────────────────────────────────────────────────────────────────────
sc1, sc2 = st.columns([5, 1])
with sc1:
    style_input = st.text_input("", placeholder="🔍  Style number daalo — jaise: 1557YKRED",
                                 label_visibility="collapsed").strip().upper()
with sc2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔎 Search", type="primary", use_container_width=True)

if not style_input:
    st.markdown("""
    <div class='empty'>
      <div class='ei'>🏭</div>
      <h3>Koi style search nahi kiya abhi</h3>
      <p>Upar style number daalo aur Excel files upload karo</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
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
    <div class='empty'>
      <div class='ei'>🔍</div>
      <h3>Style <b>{style_input}</b> nahi mila</h3>
      <p>Style number check karo ya Excel files upload karo</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ── KPI ───────────────────────────────────────────────────────────────────────
cut_sizes = stage_data["cutting"][1]
total_qty = sum(cut_sizes.values())
done_n    = sum(1 for sk,*_ in STAGES if gstatus(*stage_data[sk]) == "done")
active_n  = sum(1 for sk,*_ in STAGES if gstatus(*stage_data[sk]) == "active")
pct       = int(done_n / 4 * 100)

k1, k2, k3, k4 = st.columns(4)
for col, val, lbl, em, cls in [
    (k1, total_qty or "—", "Total Order Qty",  "📦", "kp"),
    (k2, f"{done_n}/4",    "Stages Complete",   "✅", "kg"),
    (k3, active_n,         "In Progress",       "🔄", "ka"),
    (k4, f"{pct}%",        "Overall Progress",  "📊", "kb"),
]:
    with col:
        st.markdown(f"""
        <div class='kpi {cls}'>
          <span class='kpi-em'>{em}</span>
          <div class='kpi-val'>{val}</div>
          <div class='kpi-lbl'>{lbl}</div>
        </div>""", unsafe_allow_html=True)

# ── PIPELINE ──────────────────────────────────────────────────────────────────
di = {"done":"✓","active":"⟳","pending":"○"}
steps = ""
for sk, sl, icon, _ in STAGES:
    s = gstatus(*stage_data[sk])
    cls = {"done":"pld","active":"pla","pending":"plp"}[s]
    steps += f"<div class='pl-step {cls}'><div class='pl-dot'>{di[s]}</div><div class='pl-name'>{icon} {sl}</div></div>"

st.markdown(f"""
<div class='pipeline'>
  <div class='pl-lbl'>📍 Production Pipeline — Style: {style_input}</div>
  <div class='pl-track'>{steps}</div>
</div>""", unsafe_allow_html=True)

# ── STAGE CARDS ───────────────────────────────────────────────────────────────
st.markdown("<div class='sec-hdr'>Stage-wise Details</div>", unsafe_allow_html=True)

bmap = {
    "done":    "<span class='badge bd'>✓ Complete</span>",
    "active":  "<span class='badge ba'>⟳ In Progress</span>",
    "pending": "<span class='badge bp'>○ Pending</span>",
}

for sk, sl, icon, color in STAGES:
    info, sizes = stage_data[sk]
    s     = gstatus(info, sizes) if info else "pending"
    total = sum(sizes.values())

    chips = ""
    for sz in SIZES:
        qty = sizes.get(sz, 0)
        cls = "szon" if qty else ""
        chips += f"<div class='szc {cls}'><span class='s'>{sz}</span><span class='q'>{qty if qty else '—'}</span></div>"
    if total:
        chips += f"<div class='szc sztot'><span class='s'>TOTAL</span><span class='q'>{total}</span></div>"

    ihtml = ""
    if info:
        for lbl, val, mono in [
            ("CH. No",     info.get("challan","—"),  "im"),
            ("Vendor",     info.get("vendor","—"),   ""),
            ("Issue Date", info.get("i_date","—"),   "im"),
            ("Rcv. Date",  info.get("r_date","—"),   "im"),
            ("Delivery",   info.get("del_date","—"), "im"),
        ]:
            ihtml += f"<div><div class='il'>{lbl}</div><div class='iv {mono}'>{val}</div></div>"

    body = ""
    if info:
        body = f"""
        <div class='sc-bd'>
          <div class='irow'>{ihtml}</div>
          <div class='il' style='margin-bottom:9px'>Size-wise Quantity</div>
          <div class='szrow'>{chips if chips else "<span style='color:#b2bec3;font-size:.82rem'>Data nahi mila</span>"}</div>
        </div>"""
    else:
        body = "<div class='sc-bd' style='color:#b2bec3;font-size:.82rem'>File upload nahi hui ya style nahi mila.</div>"

    st.markdown(f"""
    <div class='sc'>
      <div class='sc-hd'>
        <div style='display:flex;align-items:center'>
          <div class='sc-ico' style='background:{color}22'>{icon}</div>
          <div>
            <div class='sc-nm'>{sl}</div>
            <div class='sc-sb'>Total: {total if total else "—"} pieces</div>
          </div>
        </div>
        {bmap[s]}
      </div>
      {body}
    </div>""", unsafe_allow_html=True)

# ── SUMMARY TABLE ─────────────────────────────────────────────────────────────
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
    <div class='tbl-box'>
      <div class='tbl-hd'>📐 Size-wise Summary — All Stages</div>""",
    unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows).set_index("Stage"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── EXPORT ────────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div class='sec-hdr'>📤 Export</div>", unsafe_allow_html=True)

def build_report(style, sd):
    r = ""
    for sk, sl, icon, _ in STAGES:
        inf, szs = sd.get(sk, ({},{}))
        total = sum(szs.values())
        sc = "".join(f"<td>{szs.get(s,0) or ''}</td>" for s in SIZES)
        r += f"<tr style='background:#f8f9fa'><td colspan='14' style='padding:8px;font-weight:700'>{icon} {sl} | CH:{inf.get('challan','—')} | Vendor:{inf.get('vendor','—')} | Issue:{inf.get('i_date','—')} | Rcvd:{inf.get('r_date','—')} | Del:{inf.get('del_date','—')}</td></tr><tr>{sc}<td><b>{total}</b></td></tr>"
    ths = "".join(f"<th>{s}</th>" for s in SIZES)
    return f"<html><head><style>body{{font-family:Arial;font-size:11px;margin:24px}}h2{{color:#875A7B}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{border:1px solid #ddd;padding:5px 8px;text-align:center}}th{{background:#875A7B;color:white;font-size:10px}}</style></head><body><h2>Production Report — {style}</h2><p style='color:#7f8c8d'>Generated: {date.today()}</p><table><tr><th>Stage</th>{ths}<th>TOTAL</th></tr>{r}</table></body></html>"

e1, e2, _ = st.columns(3)
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
<div style='text-align:center;color:#b2bec3;font-size:0.68rem;padding:20px 0 6px'>
  Production Tracker v1.0 &nbsp;•&nbsp; Data sirf aapki Excel files se &nbsp;•&nbsp; Koi data server pe save nahi hota
</div>
</div></div>""", unsafe_allow_html=True)
