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
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Nunito', sans-serif !important;
    background: #f0f2f5 !important;
    color: #2c3e50 !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp > header { display: none; }
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

/* NAVBAR */
.navbar {
    background: #ffffff;
    border-bottom: 2px solid #e8eaed;
    padding: 0 32px;
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.navbar-logo {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #875A7B, #6c4a65);
    border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 18px; margin-right: 10px; vertical-align: middle;
}
.navbar-title { font-size: 1.15rem; font-weight: 800; color: #2c3e50; }
.navbar-title span { color: #875A7B; }
.navbar-meta { font-size: 0.78rem; color: #95a5a6; font-weight: 500; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #2c3e50 !important;
    min-width: 270px !important; max-width: 270px !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div { color: #bdc3c7 !important; }
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px dashed rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
}
.sb-section {
    padding: 16px 0 6px;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #7f8c8d !important;
    font-weight: 700;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin-top: 8px;
}

/* MAIN AREA */
.main-content { padding: 28px 32px; }
.page-header h1 { font-size: 1.5rem !important; font-weight: 800 !important; color: #2c3e50 !important; margin-bottom: 4px !important; }
.breadcrumb { font-size: 0.76rem; color: #95a5a6; margin-bottom: 4px; }
.breadcrumb span { color: #875A7B; font-weight: 700; }
.page-sub { font-size: 0.85rem; color: #7f8c8d; margin-bottom: 22px; }

/* SEARCH */
.stTextInput input {
    border: 1.5px solid #d5d9e0 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem !important;
    background: #fff !important;
}
.stTextInput input:focus {
    border-color: #875A7B !important;
    box-shadow: 0 0 0 3px rgba(135,90,123,0.12) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #875A7B, #6c4a65) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; padding: 10px 24px !important;
    font-weight: 700 !important; font-family: 'Nunito', sans-serif !important;
    box-shadow: 0 2px 8px rgba(135,90,123,0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover { transform: translateY(-1px) !important; }

/* KPI CARDS */
.kpi-card {
    background: #fff; border-radius: 12px;
    padding: 20px 22px; border: 1px solid #e8eaed;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    position: relative; overflow: hidden;
    transition: box-shadow 0.2s, transform 0.2s;
}
.kpi-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.10); transform: translateY(-2px); }
.kpi-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.kpi-purple::before { background: linear-gradient(90deg, #875A7B, #b07ca8); }
.kpi-green::before  { background: linear-gradient(90deg, #27ae60, #2ecc71); }
.kpi-orange::before { background: linear-gradient(90deg, #e67e22, #f39c12); }
.kpi-blue::before   { background: linear-gradient(90deg, #2980b9, #3498db); }
.kpi-icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px; margin-bottom:12px; }
.kpi-purple .kpi-icon { background:#f5eef8; }
.kpi-green  .kpi-icon { background:#eafaf1; }
.kpi-orange .kpi-icon { background:#fef9e7; }
.kpi-blue   .kpi-icon { background:#ebf5fb; }
.kpi-num { font-size:1.9rem; font-weight:800; color:#2c3e50; font-family:'IBM Plex Mono',monospace; line-height:1; margin-bottom:4px; }
.kpi-label { font-size:0.72rem; color:#7f8c8d; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; }

/* PIPELINE */
.pipeline-wrap {
    background:#fff; border-radius:12px; padding:22px 24px;
    border:1px solid #e8eaed; box-shadow:0 1px 4px rgba(0,0,0,0.05);
    margin: 20px 0;
}
.pipeline-title { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:#95a5a6; margin-bottom:20px; }
.pipeline-steps { display:flex; align-items:flex-start; }
.pipeline-step { flex:1; display:flex; flex-direction:column; align-items:center; position:relative; }
.pipeline-step::after { content:''; position:absolute; top:18px; left:50%; width:100%; height:3px; z-index:0; }
.pipeline-step:last-child::after { display:none; }
.step-done::after   { background:#27ae60; }
.step-active::after { background: linear-gradient(90deg,#e67e22,#e0e4e8); }
.step-pending::after{ background:#e0e4e8; }
.step-circle {
    width:36px; height:36px; border-radius:50%; display:flex;
    align-items:center; justify-content:center; font-size:15px;
    position:relative; z-index:1; font-weight:800; border:2.5px solid;
}
.step-done   .step-circle { background:#27ae60; border-color:#27ae60; color:#fff; }
.step-active .step-circle { background:#fff; border-color:#e67e22; color:#e67e22; animation:pulse 1.5s infinite; }
.step-pending .step-circle{ background:#f0f2f5; border-color:#d5d9e0; color:#bdc3c7; }
@keyframes pulse { 0%{box-shadow:0 0 0 0 rgba(230,126,34,.4)} 70%{box-shadow:0 0 0 8px rgba(230,126,34,0)} 100%{box-shadow:0 0 0 0 rgba(230,126,34,0)} }
.step-name { font-size:0.68rem; font-weight:700; margin-top:8px; text-align:center; color:#7f8c8d; text-transform:uppercase; letter-spacing:0.5px; }
.step-done   .step-name { color:#27ae60; }
.step-active .step-name { color:#e67e22; }

/* STAGE CARDS */
.stage-card { background:#fff; border-radius:12px; border:1px solid #e8eaed; box-shadow:0 1px 4px rgba(0,0,0,0.05); margin-bottom:14px; overflow:hidden; }
.sc-header { padding:14px 20px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #f0f2f5; }
.sc-icon { width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:17px; margin-right:12px; }
.sc-name { font-size:0.95rem; font-weight:700; color:#2c3e50; }
.sc-sub  { font-size:0.73rem; color:#95a5a6; }
.badge { padding:4px 12px; border-radius:20px; font-size:0.7rem; font-weight:700; letter-spacing:0.5px; text-transform:uppercase; }
.badge-done    { background:#eafaf1; color:#1e8449; border:1px solid #a9dfbf; }
.badge-active  { background:#fef9e7; color:#b7770d; border:1px solid #f9e4a0; }
.badge-pending { background:#f2f3f4; color:#95a5a6; border:1px solid #d5d8dc; }
.sc-body { padding:18px 20px; }
.info-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin-bottom:18px; }
.info-lbl { font-size:0.63rem; text-transform:uppercase; letter-spacing:1px; color:#95a5a6; font-weight:700; margin-bottom:3px; }
.info-val { font-size:0.88rem; font-weight:600; color:#2c3e50; }
.info-mono { font-family:'IBM Plex Mono',monospace; font-size:0.82rem; }
.sizes-label { font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:#95a5a6; margin-bottom:10px; }
.size-strip { display:flex; flex-wrap:wrap; gap:8px; }
.size-chip { background:#f0f2f5; border:1px solid #e0e4e8; border-radius:8px; padding:5px 10px; text-align:center; min-width:46px; }
.size-chip .sz { font-size:0.6rem; font-weight:700; color:#95a5a6; text-transform:uppercase; }
.size-chip .qty { font-size:0.95rem; font-weight:800; color:#2c3e50; font-family:'IBM Plex Mono',monospace; }
.has-qty { background:#f5eef8 !important; border-color:#d2b4de !important; }
.has-qty .sz { color:#875A7B !important; }
.has-qty .qty { color:#6c4a65 !important; }
.total-chip { background:linear-gradient(135deg,#875A7B,#6c4a65) !important; border:none !important; min-width:54px; }
.total-chip .sz { color:rgba(255,255,255,0.75) !important; }
.total-chip .qty { color:#fff !important; }

/* SUMMARY TABLE */
.summary-box { background:#fff; border-radius:12px; border:1px solid #e8eaed; box-shadow:0 1px 4px rgba(0,0,0,0.05); overflow:hidden; margin-bottom:20px; }
.summary-hdr { padding:14px 20px; background:#f8f9fa; border-bottom:1px solid #e8eaed; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:#7f8c8d; }
.stDataFrame thead th { background:#f8f9fa !important; color:#875A7B !important; font-family:'Nunito',sans-serif !important; font-weight:700 !important; font-size:0.78rem !important; text-transform:uppercase !important; }
.stDataFrame tbody td { font-family:'IBM Plex Mono',monospace !important; font-size:0.85rem !important; text-align:center !important; }

/* DOWNLOAD BUTTONS */
.stDownloadButton button {
    background:#fff !important; color:#875A7B !important;
    border:1.5px solid #875A7B !important; border-radius:8px !important;
    font-weight:700 !important; font-family:'Nunito',sans-serif !important;
    transition:all 0.2s !important;
}
.stDownloadButton button:hover { background:#875A7B !important; color:#fff !important; }

/* EMPTY STATE */
.empty-state { background:#fff; border-radius:12px; border:1px dashed #d5d9e0; padding:60px 40px; text-align:center; margin-top:12px; }
.empty-icon { font-size:3rem; margin-bottom:16px; }
.empty-h { font-size:1.05rem; font-weight:700; color:#7f8c8d; margin-bottom:8px; }
.empty-p { font-size:0.83rem; color:#bdc3c7; }

hr { border:none; border-top:1px solid #e8eaed; margin:20px 0; }
.section-title { font-size:0.9rem; font-weight:800; color:#2c3e50; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:14px; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────
SIZES = ["XS","S","M","L","XL","XXL","3XL","4XL","5XL","6XL","7XL","8XL"]
STAGES = [
    ("cutting",   "Cutting",           "✂️",  "#875A7B"),
    ("stitching", "Stitching",         "🧵",  "#2980b9"),
    ("handwork",  "Hand Work / Kaaz",  "🖐️",  "#e67e22"),
    ("finishing", "Finishing",         "✨",  "#27ae60"),
]

def safe_read(f):
    try:
        df = pd.read_excel(f); df.columns=[str(c).strip() for c in df.columns]; return df
    except: return pd.DataFrame()

def find_col(df, *cands):
    m={c.lower():c for c in df.columns}
    for c in cands:
        if c.lower() in m: return m[c.lower()]
    return None

def get_sizes(df, style):
    sc=find_col(df,"style no","style","order no","order")
    if sc is None or df.empty: return {}
    row=df[df[sc].astype(str).str.upper()==style.upper()]
    if row.empty: return {}
    row=row.iloc[0]
    out={}
    for s in SIZES:
        col=find_col(df,s)
        out[s]=int(row[col]) if col and pd.notna(row.get(col)) else 0
    return out

def get_info(df, style):
    sc=find_col(df,"style no","style","order no","order")
    if sc is None or df.empty: return {}
    row=df[df[sc].astype(str).str.upper()==style.upper()]
    if row.empty: return {}
    row=row.iloc[0]
    info={}
    for key,*cands in [
        ("challan","ch no","challan no","ch. no","challan"),
        ("vendor","vendor name","vendor","party"),
        ("i_date","issue date","i. date","i date","idate"),
        ("r_date","receive date","r. date","r date","rdate","received date"),
        ("del_date","delivery date","del date","delivery"),
    ]:
        col=find_col(df,*cands)
        info[key]=str(row[col]) if col and pd.notna(row.get(col)) else "—"
    return info

def status(info, sizes):
    hr=info.get("r_date","—") not in ("—","nan","NaT","")
    hi=info.get("i_date","—") not in ("—","nan","NaT","")
    if hr and sum(sizes.values())>0: return "done"
    if hi: return "active"
    return "pending"

# ── NAVBAR ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='navbar'>
  <div>
    <span class='navbar-logo'>🏭</span>
    <span class='navbar-title'>Production <span>Tracker</span></span>
  </div>
  <div class='navbar-meta'>📅 {date.today().strftime("%d %B %Y")} &nbsp;|&nbsp; Garment Production Management</div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sb-section' style='border-top:none'>📂 Excel Files Upload</div>", unsafe_allow_html=True)
    st.caption("Har stage ki alag Excel file upload karo")
    f_cut = st.file_uploader("✂️  Cutting",          type=["xlsx","xls"], key="c")
    f_sti = st.file_uploader("🧵  Stitching",        type=["xlsx","xls"], key="s")
    f_hnd = st.file_uploader("🖐️  Hand Work / Kaaz", type=["xlsx","xls"], key="h")
    f_fin = st.file_uploader("✨  Finishing",         type=["xlsx","xls"], key="f")
    st.markdown("<div class='sb-section'>📋 Column Guide</div>", unsafe_allow_html=True)
    st.caption("Style No • CH No • Vendor Name\nI. Date • R. Date • Delivery Date\nXS S M L XL XXL 3XL 4XL 5XL 6XL 7XL 8XL")
    st.markdown("<div class='sb-section'>⬇️ Sample File</div>", unsafe_allow_html=True)
    sample=pd.DataFrame({
        "Style No":["1557YKRED","2341BKBLU"],"CH No":["CH-001","CH-002"],
        "Vendor Name":["ABC Stitching","XYZ Tailor"],
        "I. Date":["01-Jan-2025","05-Jan-2025"],"R. Date":["10-Jan-2025",""],
        "Delivery Date":["15-Jan-2025","20-Jan-2025"],
        "XS":[10,5],"S":[20,10],"M":[30,15],"L":[25,12],
        "XL":[20,8],"XXL":[10,5],"3XL":[5,2],"4XL":[3,1],
        "5XL":[2,0],"6XL":[1,0],"7XL":[0,0],"8XL":[0,0],
    })
    buf=io.BytesIO(); sample.to_excel(buf,index=False)
    st.download_button("⬇️ Sample Excel Download", buf.getvalue(),
        file_name="sample_stage.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)

# ── MAIN ────────────────────────────────────────────────────────────────────
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.markdown("""
<div class='page-header'>
  <div class='breadcrumb'>Production › <span>Style Tracking</span></div>
  <h1>Production Order Tracker</h1>
  <div class='page-sub'>Style number daalo — saari stages ka status ek jagah dikhe</div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([4,1])
with c1:
    style_input = st.text_input("", placeholder="🔍  Style number daalo  —  jaise: 1557YKRED", label_visibility="collapsed").strip().upper()
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔎 Search", type="primary", use_container_width=True)

if not style_input:
    st.markdown("""
    <div class='empty-state'>
      <div class='empty-icon'>🏭</div>
      <div class='empty-h'>Koi style search nahi kiya abhi</div>
      <div class='empty-p'>Upar style number daalo aur sidebar mein Excel files upload karo</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Load data
dfs={"cutting":safe_read(f_cut) if f_cut else pd.DataFrame(),
     "stitching":safe_read(f_sti) if f_sti else pd.DataFrame(),
     "handwork":safe_read(f_hnd) if f_hnd else pd.DataFrame(),
     "finishing":safe_read(f_fin) if f_fin else pd.DataFrame()}

stage_data={}
for sk,*_ in STAGES:
    df=dfs[sk]
    info=get_info(df,style_input) if not df.empty else {}
    sizes=get_sizes(df,style_input) if not df.empty else {}
    stage_data[sk]=(info,sizes)

if not any(stage_data[sk][0] for sk,*_ in STAGES):
    st.markdown(f"""
    <div class='empty-state'>
      <div class='empty-icon'>🔍</div>
      <div class='empty-h'>Style <b>{style_input}</b> nahi mila</div>
      <div class='empty-p'>Style number check karo ya Excel files upload karo sidebar mein</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# KPI
cut_sizes=stage_data["cutting"][1]
total_qty=sum(cut_sizes.values())
done_n   =sum(1 for sk,*_ in STAGES if status(*stage_data[sk])=="done")
active_n =sum(1 for sk,*_ in STAGES if status(*stage_data[sk])=="active")
pct      =int(done_n/4*100)

k1,k2,k3,k4=st.columns(4)
for col, num, lbl, icon, klass in [
    (k1, total_qty or "—", "Total Order Qty",   "📦", "kpi-purple"),
    (k2, f"{done_n}/4",    "Stages Complete",    "✅", "kpi-green"),
    (k3, active_n,         "In Progress",        "🔄", "kpi-orange"),
    (k4, f"{pct}%",        "Overall Progress",   "📊", "kpi-blue"),
]:
    with col:
        st.markdown(f"""
        <div class='kpi-card {klass}'>
          <div class='kpi-icon'>{icon}</div>
          <div class='kpi-num'>{num}</div>
          <div class='kpi-label'>{lbl}</div>
        </div>""", unsafe_allow_html=True)

# Pipeline
step_icon={"done":"✓","active":"⟳","pending":"○"}
steps_html=""
for sk,sl,icon,_ in STAGES:
    s=status(*stage_data[sk])
    steps_html+=f"<div class='pipeline-step step-{s}'><div class='step-circle'>{step_icon[s]}</div><div class='step-name'>{icon} {sl}</div></div>"
st.markdown(f"""
<div class='pipeline-wrap'>
  <div class='pipeline-title'>📍 Production Pipeline — Style: {style_input}</div>
  <div class='pipeline-steps'>{steps_html}</div>
</div>""", unsafe_allow_html=True)

# Stage Cards
st.markdown("<div class='section-title'>Stage-wise Details</div>", unsafe_allow_html=True)
badge_html={"done":"<span class='badge badge-done'>✓ Complete</span>",
            "active":"<span class='badge badge-active'>⟳ In Progress</span>",
            "pending":"<span class='badge badge-pending'>○ Pending</span>"}

for sk,sl,icon,color in STAGES:
    info,sizes=stage_data[sk]
    s=status(info,sizes) if info else "pending"
    total=sum(sizes.values())

    chips=""
    for sz in SIZES:
        qty=sizes.get(sz,0)
        cls="has-qty" if qty else ""
        chips+=f"<div class='size-chip {cls}'><div class='sz'>{sz}</div><div class='qty'>{qty if qty else '—'}</div></div>"
    if total:
        chips+=f"<div class='size-chip total-chip'><div class='sz'>TOTAL</div><div class='qty'>{total}</div></div>"

    info_html=""
    if info:
        for lbl,val,mono in [
            ("CH. No",       info.get("challan","—"), "info-mono"),
            ("Vendor",       info.get("vendor","—"),  ""),
            ("Issue Date",   info.get("i_date","—"),  "info-mono"),
            ("Receive Date", info.get("r_date","—"),  "info-mono"),
            ("Delivery",     info.get("del_date","—"),"info-mono"),
        ]:
            info_html+=f"<div><div class='info-lbl'>{lbl}</div><div class='info-val {mono}'>{val}</div></div>"

    body=""
    if info:
        body=f"""
        <div class='sc-body'>
          <div class='info-grid'>{info_html}</div>
          <div class='sizes-label'>Size-wise Quantity</div>
          <div class='size-strip'>{chips if chips else "<span style='color:#bdc3c7;font-size:.85rem'>Size data nahi mila</span>"}</div>
        </div>"""
    else:
        body="<div class='sc-body' style='color:#bdc3c7;font-size:.85rem;padding:18px 20px'>File upload nahi hui ya style nahi mila.</div>"

    st.markdown(f"""
    <div class='stage-card'>
      <div class='sc-header'>
        <div style='display:flex;align-items:center'>
          <div class='sc-icon' style='background:{color}22'>{icon}</div>
          <div>
            <div class='sc-name'>{sl}</div>
            <div class='sc-sub'>Total: {total if total else "—"} pieces</div>
          </div>
        </div>
        {badge_html[s]}
      </div>
      {body}
    </div>""", unsafe_allow_html=True)

# Summary table
rows=[]
for sk,sl,icon,_ in STAGES:
    _,sizes=stage_data[sk]
    if sizes:
        r={"Stage":f"{icon} {sl}"}
        for sz in SIZES: r[sz]=sizes.get(sz,0) or ""
        r["TOTAL"]=sum(sizes.values())
        rows.append(r)
if rows:
    st.markdown("""
    <div class='summary-box'>
      <div class='summary-hdr'>📐 Size-wise Summary — All Stages</div>
    """, unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows).set_index("Stage"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Export
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📤 Export</div>", unsafe_allow_html=True)
e1,e2,_=st.columns(3)

def build_report(style, sd):
    rows=""
    for sk,sl,icon,_ in STAGES:
        inf,szs=sd.get(sk,({},{}))
        total=sum(szs.values())
        sc="".join(f"<td>{szs.get(s,0) or ''}</td>" for s in SIZES)
        rows+=f"<tr style='background:#f8f9fa'><td colspan='14' style='padding:8px 12px;font-weight:700'>{icon} {sl} | CH:{inf.get('challan','—')} | Vendor:{inf.get('vendor','—')} | Issue:{inf.get('i_date','—')} | Rcvd:{inf.get('r_date','—')} | Del:{inf.get('del_date','—')}</td></tr><tr>{sc}<td><b>{total}</b></td></tr>"
    ths="".join(f"<th>{s}</th>" for s in SIZES)
    return f"<html><head><style>body{{font-family:Arial;font-size:11px;margin:24px;color:#2c3e50}}h2{{color:#875A7B}}table{{width:100%;border-collapse:collapse;margin-top:16px}}th,td{{border:1px solid #ddd;padding:5px 8px;text-align:center}}th{{background:#875A7B;color:white;font-size:10px}}</style></head><body><h2>🏭 Production Report — {style}</h2><p style='color:#7f8c8d;font-size:12px'>Generated: {date.today()}</p><table><tr><th>Stage</th>{ths}<th>TOTAL</th></tr>{rows}</table></body></html>"

with e1:
    st.download_button("🖨️ Print-Ready HTML Report", build_report(style_input, stage_data),
        file_name=f"report_{style_input}_{date.today()}.html", mime="text/html", use_container_width=True)
with e2:
    if rows:
        xl=io.BytesIO(); pd.DataFrame(rows).to_excel(xl,index=False)
        st.download_button("📊 Excel Summary", xl.getvalue(),
            file_name=f"summary_{style_input}_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

st.markdown("""
<div style='text-align:center;color:#bdc3c7;font-size:0.72rem;padding:24px 0 8px'>
  Production Tracker &nbsp;•&nbsp; Data aapki Excel files se aata hai &nbsp;•&nbsp; Koi data server pe save nahi hota
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
