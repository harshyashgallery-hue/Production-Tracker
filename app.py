import streamlit as st
import pandas as pd
from html.parser import HTMLParser
import base64
import os
import json
import zipfile
import io
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Yash Gallery – Style Tracking",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #0d1b6e 0%, #1a237e 50%, #283593 100%);
        color: white; padding: 22px 28px; border-radius: 14px;
        text-align: center; margin-bottom: 24px;
        box-shadow: 0 6px 20px rgba(26,35,126,0.35);
    }
    .main-header h2 { margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 0.5px; }
    .main-header p  { margin: 6px 0 0 0; opacity: 0.85; font-size: 14px; }
    .section-title {
        background: linear-gradient(90deg, #e3f2fd, #f5f5f5);
        border-left: 5px solid #1565c0;
        padding: 9px 16px; font-weight: 700; font-size: 14px;
        margin: 18px 0 10px 0; border-radius: 6px; color: #1a237e;
    }
    .metric-box {
        background: white; border: 1px solid #e8e8e8; border-radius: 12px;
        padding: 16px 12px; text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.07);
        transition: transform 0.15s;
    }
    .metric-box:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.12); }
    .metric-val { font-size: 28px; font-weight: 800; }
    .metric-lbl { font-size: 11px; color: #888; margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-sub { font-size: 11px; color: #aaa; margin-top: 2px; }
    .no-photo {
        background: #f9f9f9; border: 2px dashed #ccc; border-radius: 10px;
        padding: 32px 16px; text-align: center; color: #aaa; font-size: 13px;
    }
    .upload-success {
        background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 8px;
        padding: 10px 14px; color: #2e7d32; font-size: 13px; margin-top: 8px;
    }
    .alert-box {
        border-radius: 10px; padding: 12px 16px; margin: 6px 0; font-size: 13px; font-weight: 600;
    }
    .alert-red    { background: #ffebee; border-left: 4px solid #c62828; color: #c62828; }
    .alert-orange { background: #fff3e0; border-left: 4px solid #e65100; color: #e65100; }
    .alert-green  { background: #e8f5e9; border-left: 4px solid #2e7d32; color: #2e7d32; }
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 700; margin: 2px;
    }
    .badge-red    { background: #ffcdd2; color: #c62828; }
    .badge-green  { background: #c8e6c9; color: #2e7d32; }
    .badge-blue   { background: #bbdefb; color: #1565c0; }
    .badge-orange { background: #ffe0b2; color: #e65100; }
    div[data-testid="stTabs"] button { font-weight: 600; font-size: 13px; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Persistent Storage ─────────────────────────────────────────────────────
DATA_DIR   = "/tmp/yash_gallery_data"
EXCEL_PATH = os.path.join(DATA_DIR, "report.xls")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
META_PATH  = os.path.join(DATA_DIR, "meta.json")
NOTES_PATH = os.path.join(DATA_DIR, "notes.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def save_meta(excel_name, img_count):
    with open(META_PATH, 'w') as f:
        json.dump({"excel_name": excel_name, "img_count": img_count,
                   "uploaded_at": datetime.now().strftime("%d %b %Y %H:%M")}, f)

def load_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH) as f:
            return json.load(f)
    return None

def load_notes():
    if os.path.exists(NOTES_PATH):
        with open(NOTES_PATH) as f:
            return json.load(f)
    return {}

def save_notes(notes):
    with open(NOTES_PATH, 'w') as f:
        json.dump(notes, f)

# ── HTML Parser ─────────────────────────────────────────────────────────────
class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.current_row, self.current_cell, self.in_td = [], [], '', False
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.current_row = []
        elif tag == 'td': self.in_td, self.current_cell = True, ''
    def handle_endtag(self, tag):
        if tag == 'tr' and self.current_row: self.rows.append(self.current_row)
        elif tag == 'td':
            self.in_td = False
            self.current_row.append(self.current_cell.strip())
    def handle_data(self, data):
        if self.in_td: self.current_cell += data

@st.cache_data(show_spinner="📊 Data load ho raha hai…")
def load_data(file_bytes):
    content = file_bytes.decode('utf-8', errors='ignore')
    parser = TableParser()
    parser.feed(content)
    headers = ['JONo','JODate','SONo','SODate','Karigar','IssueNo','IssueDate',
               'Process','Design','Size','NoColour_MI','NoColour_MR','NoColour_BAL',
               'Mix_MI','Mix_MR','Mix_BAL']
    records = []
    for row in parser.rows[2:]:
        if len(row) >= 10 and row[0].strip() and row[8].strip():
            r = {h: (row[i].strip() if i < len(row) else '') for i, h in enumerate(headers)}
            records.append(r)
    df = pd.DataFrame(records)
    for col in ['NoColour_MI','NoColour_MR','NoColour_BAL','Mix_MI','Mix_MR','Mix_BAL']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['IssueDate'] = df['IssueDate'].str.lstrip("'")
    df['JODate']    = df['JODate'].str.lstrip("'")
    df['Total_MI']  = df['NoColour_MI'] + df['Mix_MI']
    df['Total_MR']  = df['NoColour_MR'] + df['Mix_MR']
    df['Total_BAL'] = df['Total_MI'] - df['Total_MR']
    df['StyleCode'] = df['Design']
    SIZE_ORDER = ['XS','S','S-M','S-M-L','M','L','L-XL','L-XL-XXL','XL','XL-XXL',
                  'XL-XXL-3XL','XXL','XXL-3XL','3XL','3XL-4XL','4XL','4XL-5XL',
                  '5XL','5XL-6XL','6XL','7XL','7XL-8XL','8XL','Free Size','Mix',
                  '7 -8 Years','9 -10 Years','11 -12 Years','13 -14 Years']
    df['Size_order'] = df['Size'].apply(lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else 999)
    # Parse issue date for days calc
    def parse_date(s):
        s = str(s).strip().lstrip("'")
        for fmt in ["%d-%m-%Y","%Y-%m-%d","%d/%m/%Y"]:
            try: return datetime.strptime(s, fmt).date()
            except: pass
        return None
    df['IssueDateParsed'] = df['IssueDate'].apply(parse_date)
    today = date.today()
    df['DaysPending'] = df['IssueDateParsed'].apply(
        lambda d: (today - d).days if d else 0)
    return df

def get_style_image(style_code):
    exts = ['.jpg','.jpeg','.png','.jfif','.webp','.bmp']
    for sc in [style_code, style_code.upper(), style_code.lower()]:
        for ext in exts:
            p = os.path.join(IMAGES_DIR, sc + ext)
            if os.path.exists(p): return p
    return None

def aging_bucket(days):
    if days <= 7:    return "🟢 0-7 days"
    elif days <= 15: return "🟡 8-15 days"
    elif days <= 30: return "🟠 16-30 days"
    else:            return "🔴 30+ days"

# ── CONSTANTS ─────────────────────────────────────────────────────────────
PROCESS_ORDER = [
    'Modal Shout','Dyeing','Printing','Fabric Check','Re Process',
    'Cutting','Gola Cutting','Embroidary','5 Threads','Stitching',
    'Alteration','Kaaz Button','Fabric Button','Handwork','Finishing',
    'Stitch to Pack','Washing','Consume Item','Consine Bobin Elastic','Partchange',
]
SIZE_ORDER_LIST = ['XS','S','S-M','S-M-L','M','L','L-XL','L-XL-XXL','XL','XL-XXL',
                   'XL-XXL-3XL','XXL','XXL-3XL','3XL','3XL-4XL','4XL','4XL-5XL',
                   '5XL','5XL-6XL','6XL','7XL','7XL-8XL','8XL','Free Size','Mix',
                   '7 -8 Years','9 -10 Years','11 -12 Years','13 -14 Years']

def process_sort_key(p):
    p_lower = p.strip().lower()
    for i, op in enumerate(PROCESS_ORDER):
        if op.lower() == p_lower: return i
    return len(PROCESS_ORDER)

def color_balance(val):
    if isinstance(val, (int, float)):
        if val > 0:   return 'color:#c62828;font-weight:bold'
        elif val < 0: return 'color:#2e7d32;font-weight:bold'
    return ''

def highlight_days(val):
    try:
        v = int(val)
        if v > 30: return 'color:#c62828;font-weight:bold'
        elif v > 15: return 'color:#e65100;font-weight:bold'
        elif v > 7:  return 'color:#f57f17'
    except: pass
    return ''

def color_aging(val):
    if '🔴' in str(val): return 'background:#ffebee;color:#c62828;font-weight:bold'
    elif '🟠' in str(val): return 'background:#fff3e0;color:#e65100;font-weight:bold'
    elif '🟡' in str(val): return 'background:#fffde7;color:#f57f17;font-weight:bold'
    elif '🟢' in str(val): return 'background:#e8f5e9;color:#2e7d32;font-weight:bold'
    return ''

def metric_card(col, val, lbl, color, sub=""):
    col.markdown(f"""<div class="metric-box">
        <div class="metric-val" style="color:{color}">{val if isinstance(val,str) else f'{val:,}'}</div>
        <div class="metric-lbl">{lbl}</div>
        {'<div class="metric-sub">'+sub+'</div>' if sub else ''}
    </div>""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h2>👗 Yash Gallery Private Limited</h2>
    <p>Material Issue / Receive — Merchant Style Tracking Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Data Management")
    meta       = load_meta()
    excel_loaded = os.path.exists(EXCEL_PATH)
    imgs_count   = len([f for f in os.listdir(IMAGES_DIR) if not f.startswith('.')])

    if excel_loaded and meta:
        st.markdown(f"""<div class="upload-success">
            ✅ <b>{meta.get('excel_name','report.xls')}</b><br>
            🖼️ {imgs_count} photos &nbsp;|&nbsp; 🕐 {meta.get('uploaded_at','')}
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Replace Data"):
            st.session_state['show_upload'] = True
    else:
        st.session_state['show_upload'] = True

    if st.session_state.get('show_upload', not excel_loaded):
        st.markdown("---")
        st.markdown("**Step 1 — Excel Report**")
        up_excel = st.file_uploader("Upload .xls / .html", type=['xls','html','htm'], key="excel_up")
        if up_excel:
            with open(EXCEL_PATH, 'wb') as f: f.write(up_excel.getvalue())
            save_meta(up_excel.name, imgs_count)
            load_data.clear()
            st.success("✅ Excel saved!")

        st.markdown("**Step 2 — Style Photos (ZIP)**")
        st.caption("Photo naam = Style code (e.g. 1557YKRED.jpg)")
        up_zip = st.file_uploader("Upload images ZIP", type=['zip'], key="zip_up")
        if up_zip:
            z = zipfile.ZipFile(io.BytesIO(up_zip.getvalue()))
            count = 0
            for name in z.namelist():
                basename = os.path.basename(name)
                if basename and not basename.startswith('.'):
                    ext = os.path.splitext(basename)[1].lower()
                    if ext in ['.jpg','.jpeg','.png','.jfif','.webp','.bmp']:
                        with z.open(name) as src, open(os.path.join(IMAGES_DIR, basename), 'wb') as dst:
                            dst.write(src.read())
                        count += 1
            save_meta(meta.get('excel_name','') if meta else '', count)
            st.success(f"✅ {count} images saved!")
            if st.button("✅ Done"):
                st.session_state['show_upload'] = False
                st.rerun()

    st.markdown("---")
    # Quick stats
    if excel_loaded and os.path.exists(EXCEL_PATH):
        with open(EXCEL_PATH, 'rb') as f:
            _df = load_data(f.read())
        pend_total = int(_df[_df['Total_BAL'] > 0]['Total_BAL'].sum())
        crit = int((_df[_df['Total_BAL'] > 0]['DaysPending'] > 30).sum())
        st.markdown(f"**📊 Quick Stats**")
        st.markdown(f"- 🎨 Styles: **{_df['StyleCode'].nunique()}**")
        st.markdown(f"- 👷 Karigars: **{_df['Karigar'].nunique()}**")
        st.markdown(f"- ⚠️ Pending Pcs: **{pend_total:,}**")
        if crit > 0:
            st.markdown(f"""<div class="alert-box alert-red">🔴 {crit} critical lines (30+ days)</div>""",
                        unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────
if not os.path.exists(EXCEL_PATH):
    st.info("👈 Sidebar se **Excel report** aur **Images ZIP** upload karo.")
    st.stop()

with open(EXCEL_PATH, 'rb') as f:
    df = load_data(f.read())

# ── TABS ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Style Tracking",
    "📊 Dashboard",
    "⏳ Pendency",
    "👷 Karigar Report",
    "🔍 Raw Data"
])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — STYLE TRACKING
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    fc1, fc2, fc3 = st.columns([2, 2, 1.5])
    with fc1:
        styles_list = sorted(df['StyleCode'].unique())
        selected_style = st.selectbox("🎨 Style / Design", styles_list)
    with fc2:
        style_df = df[df['StyleCode'] == selected_style]
        jos_list  = sorted(style_df['JONo'].unique())
        selected_jo = st.selectbox("📋 JO Number", ['All JOs'] + jos_list)
    with fc3:
        processes = sorted(df['Process'].unique())
        selected_proc = st.selectbox("⚙️ Process", ['All Processes'] + processes)

    view_df = df[df['StyleCode'] == selected_style].copy()
    if selected_jo != 'All JOs':    view_df = view_df[view_df['JONo'] == selected_jo]
    if selected_proc != 'All Processes': view_df = view_df[view_df['Process'] == selected_proc]

    if view_df.empty:
        st.warning("❌ No data for selected filters.")
        st.stop()

    meta_row  = view_df.iloc[0]
    img_path  = get_style_image(selected_style)
    notes     = load_notes()
    style_note = notes.get(selected_style, "")

    # Header card
    hc1, hc2 = st.columns([3, 1])
    with hc1:
        completion_pct = 0
        total_issued = view_df['Total_MI'].sum()
        total_recd   = view_df['Total_MR'].sum()
        if total_issued > 0:
            completion_pct = min(int(total_recd / total_issued * 100), 100)

        pend_pcs  = int(view_df['Total_BAL'].sum())
        max_days  = int(view_df[view_df['Total_BAL']>0]['DaysPending'].max()) if pend_pcs > 0 else 0
        alert_html = ""
        if pend_pcs > 0 and max_days > 30:
            alert_html = f'<div class="badge badge-red">🔴 {max_days} days pending</div>'
        elif pend_pcs > 0 and max_days > 15:
            alert_html = f'<div class="badge badge-orange">🟠 {max_days} days pending</div>'
        elif pend_pcs == 0:
            alert_html = '<div class="badge badge-green">✅ Fully Clear</div>'

        st.markdown(f"""
        <div style="background:#f8f9ff;border-radius:12px;padding:18px 22px;
                    border:1px solid #dde;height:100%">
            <div style="font-size:20px;font-weight:800;color:#1a237e;margin-bottom:4px">
                {selected_style} {alert_html}
            </div>
            <table style="font-size:13px;border-collapse:collapse;margin-top:8px">
                <tr>
                    <td style="color:#888;padding:3px 20px 3px 0;font-weight:600">📋 JO No.</td>
                    <td><b>{meta_row['JONo']}</b></td>
                    <td style="color:#888;padding:3px 20px 3px 20px;font-weight:600">📅 JO Date</td>
                    <td><b>{meta_row['JODate']}</b></td>
                </tr>
                <tr>
                    <td style="color:#888;padding:3px 20px 3px 0;font-weight:600">🧾 SO No.</td>
                    <td><b>{meta_row['SONo']}</b></td>
                    <td style="color:#888;padding:3px 20px 3px 20px;font-weight:600">📅 SO Date</td>
                    <td><b>{meta_row['SODate']}</b></td>
                </tr>
            </table>
            <div style="margin-top:12px">
                <div style="font-size:11px;color:#888;font-weight:600;margin-bottom:4px">
                    COMPLETION — {completion_pct}%
                </div>
                <div style="background:#e0e0e0;border-radius:8px;height:10px">
                    <div style="background:{'#2e7d32' if completion_pct==100 else '#1565c0'};
                                width:{completion_pct}%;height:10px;border-radius:8px;
                                transition:width 0.5s"></div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Notes
        with st.expander("📝 Merchant Notes (is style ke liye)"):
            new_note = st.text_area("Note likhein:", value=style_note, height=80,
                                     placeholder="e.g. Urgent order, dispatch by 20 March…")
            if st.button("💾 Save Note"):
                notes[selected_style] = new_note
                save_notes(notes)
                st.success("Note saved!")

    with hc2:
        if img_path:
            st.image(img_path, use_container_width=True, caption=selected_style)
        else:
            st.markdown('<div class="no-photo">📷<br>No photo<br>available</div>',
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    metric_card(m1, int(total_issued),  "Total Issued (MI)",       "#1565c0")
    metric_card(m2, int(total_recd),    "Total Received (MR)",     "#2e7d32")
    metric_card(m3, abs(pend_pcs),      "Balance (Pending)",       "#c62828" if pend_pcs > 0 else "#2e7d32")
    metric_card(m4, f"{completion_pct}%", "Completion",            "#6a1b9a")
    metric_card(m5, view_df['Process'].nunique(), "Active Processes", "#e65100")

    st.markdown("<br>", unsafe_allow_html=True)

    # Process-wise breakdown
    all_procs = view_df['Process'].unique()
    for process in sorted(all_procs, key=process_sort_key):
        proc_df = view_df[view_df['Process'] == process].copy().sort_values('Size_order')
        proc_mi  = int(proc_df['Total_MI'].sum())
        proc_bal = int(proc_df['Total_BAL'].sum())
        badge = f'<span class="badge badge-red">Pending: {proc_bal}</span>' if proc_bal > 0 \
                else '<span class="badge badge-green">Clear ✅</span>'
        st.markdown(f'<div class="section-title">⚙️ {process} &nbsp; {badge} &nbsp; <small style="color:#888">Issued: {proc_mi}</small></div>',
                    unsafe_allow_html=True)

        pivot_rows = []
        for karigar_name, kg_df in proc_df.groupby('Karigar'):
            kg_df = kg_df.sort_values('Size_order')
            for issue_no, iss_df in kg_df.groupby('IssueNo', sort=False):
                iss_df = iss_df.sort_values('Size_order')
                issue_date = iss_df['IssueDate'].iloc[0]
                days_pend  = int(iss_df['DaysPending'].iloc[0])
                so_no = iss_df['SONo'].iloc[0]
                jo_no = iss_df['JONo'].iloc[0]
                row_data = {'SO No.': so_no, 'JO No.': jo_no, 'Issue Date': issue_date,
                            'Days': days_pend, 'CH. NO.': issue_no,
                            'Karigar': karigar_name, 'Type': 'Issued (MI)'}
                for _, r in iss_df.iterrows():
                    row_data[r['Size']] = int(r['Total_MI']) if r['Total_MI'] else ''
                pivot_rows.append(row_data)

                if iss_df['Total_MR'].sum() > 0:
                    rec_row = {'SO No.':'','JO No.':'','Issue Date':'','Days':'',
                               'CH. NO.': issue_no,'Karigar': karigar_name,'Type': 'Received (MR)'}
                    for _, r in iss_df.iterrows():
                        rec_row[r['Size']] = int(r['Total_MR']) if r['Total_MR'] else ''
                    pivot_rows.append(rec_row)

                    bal_sum = int(iss_df['Total_BAL'].sum())
                    bal_row = {'SO No.':'','JO No.':'','Issue Date':'','Days':'',
                               'CH. NO.': issue_no,'Karigar': karigar_name,
                               'Type': '🔴 Balance' if bal_sum > 0 else '✅ Balance'}
                    for _, r in iss_df.iterrows():
                        bal = int(r['Total_BAL'])
                        bal_row[r['Size']] = bal if bal != 0 else ''
                    pivot_rows.append(bal_row)

        if pivot_rows:
            pv_df = pd.DataFrame(pivot_rows)
            base_cols = ['SO No.','JO No.','Issue Date','Days','CH. NO.','Karigar','Type']
            size_cols  = [s for s in SIZE_ORDER_LIST if s in pv_df.columns]
            other_cols = [c for c in pv_df.columns if c not in base_cols and c not in SIZE_ORDER_LIST]
            pv_df = pv_df.reindex(columns=base_cols + size_cols + other_cols).fillna('')
            all_sz = size_cols + other_cols
            pv_df['TOTAL'] = pv_df[all_sz].apply(
                lambda row: sum(int(v) for v in row if str(v).lstrip('-').isdigit()), axis=1)
            pv_df.loc[pv_df['TOTAL'] == 0, 'TOTAL'] = ''

            def style_rows(row):
                if 'Balance' in str(row.get('Type','')):
                    c = '#ffebee' if '🔴' in str(row.get('Type','')) else '#e8f5e9'
                    return [f'background:{c};font-weight:bold'] * len(row)
                elif 'Received' in str(row.get('Type','')):
                    return ['background:#e3f2fd'] * len(row)
                return ['background:#fffde7'] * len(row)

            st.dataframe(pv_df.style.apply(style_rows, axis=1),
                         use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📊 Business Overview Dashboard")

    total_styles    = df['StyleCode'].nunique()
    total_jos       = df['JONo'].nunique()
    total_karigars  = df['Karigar'].nunique()
    total_issued    = int(df['Total_MI'].sum())
    total_recd      = int(df['Total_MR'].sum())
    total_pending   = int(df[df['Total_BAL']>0]['Total_BAL'].sum())
    overall_pct     = int(total_recd/total_issued*100) if total_issued > 0 else 0

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    metric_card(m1, total_styles,   "Total Styles",       "#1565c0")
    metric_card(m2, total_jos,      "Total JOs",          "#2e7d32")
    metric_card(m3, total_karigars, "Total Karigars",     "#6a1b9a")
    metric_card(m4, total_issued,   "Total Issued (pcs)", "#e65100")
    metric_card(m5, total_recd,     "Total Received",     "#00838f")
    metric_card(m6, total_pending,  "Pending Pcs",        "#c62828")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown('<div class="section-title">📈 Top 10 Styles — Issued vs Received</div>',
                    unsafe_allow_html=True)
        top10 = df.groupby('StyleCode').agg(
            Issued=('Total_MI','sum'), Received=('Total_MR','sum')
        ).reset_index().sort_values('Issued', ascending=False).head(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Issued', x=top10['StyleCode'], y=top10['Issued'],
                             marker_color='#1565c0'))
        fig.add_trace(go.Bar(name='Received', x=top10['StyleCode'], y=top10['Received'],
                             marker_color='#43a047'))
        fig.update_layout(barmode='group', height=320, margin=dict(l=10,r=10,t=10,b=40),
                          plot_bgcolor='white', paper_bgcolor='white',
                          legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="section-title">🔄 Process-wise Pending Qty</div>',
                    unsafe_allow_html=True)
        proc_pend = df[df['Total_BAL']>0].groupby('Process')['Total_BAL'].sum().reset_index()
        proc_pend = proc_pend.sort_values('Total_BAL', ascending=True).tail(10)
        fig2 = px.bar(proc_pend, x='Total_BAL', y='Process', orientation='h',
                      color='Total_BAL', color_continuous_scale='Reds',
                      labels={'Total_BAL':'Pending Pcs'})
        fig2.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10),
                           plot_bgcolor='white', paper_bgcolor='white',
                           showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Charts row 2
    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown('<div class="section-title">🥧 Aging Bucket Distribution</div>',
                    unsafe_allow_html=True)
        pend_df2 = df[df['Total_BAL']>0].copy()
        pend_df2['Aging'] = pend_df2['DaysPending'].apply(aging_bucket)
        age_counts = pend_df2.groupby('Aging')['Total_BAL'].sum().reset_index()
        colors = {'🟢 0-7 days':'#4caf50','🟡 8-15 days':'#ffc107',
                  '🟠 16-30 days':'#ff9800','🔴 30+ days':'#f44336'}
        age_counts['color'] = age_counts['Aging'].map(colors)
        fig3 = px.pie(age_counts, values='Total_BAL', names='Aging',
                      color='Aging', color_discrete_map=colors,
                      hole=0.45)
        fig3.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=10))
        fig3.update_traces(textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)

    with ch4:
        st.markdown('<div class="section-title">👷 Top 10 Karigars — Pending Pcs</div>',
                    unsafe_allow_html=True)
        kar_pend_chart = df[df['Total_BAL']>0].groupby('Karigar')['Total_BAL'].sum()\
                           .reset_index().sort_values('Total_BAL', ascending=False).head(10)
        fig4 = px.bar(kar_pend_chart, x='Karigar', y='Total_BAL',
                      color='Total_BAL', color_continuous_scale='Oranges',
                      labels={'Total_BAL':'Pending Pcs'})
        fig4.update_layout(height=300, margin=dict(l=10,r=10,t=10,b=60),
                           plot_bgcolor='white', paper_bgcolor='white',
                           showlegend=False, coloraxis_showscale=False,
                           xaxis_tickangle=-30)
        st.plotly_chart(fig4, use_container_width=True)

    # Style Summary Table
    st.markdown('<div class="section-title">📋 Style-wise Summary</div>', unsafe_allow_html=True)
    style_sum = df.groupby('StyleCode').agg(
        JOs=('JONo','nunique'), Processes=('Process','nunique'),
        Issued=('Total_MI','sum'), Received=('Total_MR','sum'), Balance=('Total_BAL','sum')
    ).reset_index()
    style_sum.columns = ['Style','JOs','Processes','Issued','Received','Balance']
    style_sum['Balance'] = style_sum['Balance'].astype(int)
    style_sum['%Done'] = (style_sum['Received']/style_sum['Issued']*100).fillna(0).round(1)
    style_sum['Photo'] = style_sum['Style'].apply(lambda s: '✅' if get_style_image(s) else '❌')
    style_sum = style_sum.sort_values('Balance', ascending=False)
    st.dataframe(style_sum.style.applymap(color_balance, subset=['Balance']),
                 use_container_width=True, hide_index=True)

    # Process Summary
    st.markdown('<div class="section-title">⚙️ Process-wise Summary</div>', unsafe_allow_html=True)
    proc_sum = df.groupby('Process').agg(
        Styles=('StyleCode','nunique'), Karigars=('Karigar','nunique'),
        Issued=('Total_MI','sum'), Received=('Total_MR','sum'), Balance=('Total_BAL','sum')
    ).reset_index()
    proc_sum.columns = ['Process','Styles','Karigars','Issued','Received','Balance']
    proc_sum = proc_sum.sort_values('Balance', ascending=False)
    st.dataframe(proc_sum.style.applymap(color_balance, subset=['Balance']),
                 use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — PENDENCY REPORT
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("⏳ Pendency Report — Critical Action Required")

    pend_df = df[df['Total_BAL'] > 0].copy()
    pend_df['Aging'] = pend_df['DaysPending'].apply(aging_bucket)

    if pend_df.empty:
        st.success("🎉 Koi pendency nahi! Sab clear hai.")
    else:
        # Critical alerts at top
        crit_count  = int((pend_df['DaysPending'] > 30).sum())
        orange_count = int(((pend_df['DaysPending'] > 15) & (pend_df['DaysPending'] <= 30)).sum())
        if crit_count > 0:
            st.markdown(f'<div class="alert-box alert-red">🔴 URGENT: {crit_count} SKU lines 30+ days pending — Immediate action needed!</div>',
                        unsafe_allow_html=True)
        if orange_count > 0:
            st.markdown(f'<div class="alert-box alert-orange">🟠 WARNING: {orange_count} SKU lines 15-30 days pending — Follow up required</div>',
                        unsafe_allow_html=True)

        # Filters
        f1, f2, f3, f4 = st.columns(4)
        with f1: p_proc  = st.multiselect("⚙️ Process", sorted(pend_df['Process'].unique()), key="pp")
        with f2: p_kar   = st.multiselect("👷 Karigar", sorted(pend_df['Karigar'].unique()), key="pk")
        with f3: p_aging = st.multiselect("⏱️ Aging",
                               ["🟢 0-7 days","🟡 8-15 days","🟠 16-30 days","🔴 30+ days"], key="pa")
        with f4: p_style = st.multiselect("🎨 Style", sorted(pend_df['StyleCode'].unique()), key="ps")

        filt = pend_df.copy()
        if p_proc:  filt = filt[filt['Process'].isin(p_proc)]
        if p_kar:   filt = filt[filt['Karigar'].isin(p_kar)]
        if p_aging: filt = filt[filt['Aging'].isin(p_aging)]
        if p_style: filt = filt[filt['StyleCode'].isin(p_style)]

        # Metrics
        m1,m2,m3,m4 = st.columns(4)
        metric_card(m1, int(filt['Total_BAL'].sum()),  "Total Pending Pcs",   "#c62828")
        metric_card(m2, len(filt),                      "Pending SKU Lines",   "#e65100")
        metric_card(m3, int(filt['DaysPending'].max()) if len(filt)>0 else 0, "Max Days", "#6a1b9a")
        metric_card(m4, int((filt['DaysPending']>30).sum()), "Critical Lines", "#b71c1c")

        st.markdown("<br>", unsafe_allow_html=True)

        # Stage summary
        st.markdown('<div class="section-title">📊 Stage-wise Pendency</div>', unsafe_allow_html=True)
        stage_sum = filt.groupby('Process').agg(
            Karigars=('Karigar','nunique'), Styles=('StyleCode','nunique'),
            Pending_Pcs=('Total_BAL','sum'), Avg_Days=('DaysPending','mean'),
            Max_Days=('DaysPending','max'),
            Critical=('DaysPending', lambda x: (x>30).sum())
        ).reset_index()
        stage_sum.columns = ['Process','Karigars','Styles','Pending Pcs','Avg Days','Max Days','Critical (30+)']
        stage_sum['Avg Days'] = stage_sum['Avg Days'].round(1)
        stage_sum = stage_sum.sort_values('Pending Pcs', ascending=False)
        st.dataframe(stage_sum.style.applymap(highlight_days, subset=['Max Days','Avg Days']),
                     use_container_width=True, hide_index=True)

        # Karigar summary
        st.markdown('<div class="section-title">👷 Karigar-wise Pendency</div>', unsafe_allow_html=True)
        kar_sum = filt.groupby(['Karigar','Process']).agg(
            Styles=('StyleCode','nunique'), Pending=('Total_BAL','sum'),
            Avg_Days=('DaysPending','mean'), Max_Days=('DaysPending','max'),
            Critical=('DaysPending', lambda x: (x>30).sum())
        ).reset_index()
        kar_sum.columns = ['Karigar','Process','Styles','Pending Pcs','Avg Days','Max Days','Critical (30+)']
        kar_sum['Avg Days'] = kar_sum['Avg Days'].round(1)
        kar_sum = kar_sum.sort_values('Pending Pcs', ascending=False)
        st.dataframe(kar_sum.style.applymap(highlight_days, subset=['Max Days','Avg Days']),
                     use_container_width=True, hide_index=True)

        # Detail table
        st.markdown('<div class="section-title">📋 Detailed — Style × Size × Karigar</div>',
                    unsafe_allow_html=True)
        det = filt[['SONo','JONo','IssueNo','IssueDate','Process','Karigar',
                    'StyleCode','Size','Total_MI','Total_MR','Total_BAL',
                    'DaysPending','Aging']].copy()
        det = det.rename(columns={
            'SONo':'SO No.','JONo':'JO No.','IssueNo':'Issue No.',
            'IssueDate':'Issue Date','StyleCode':'Style',
            'Total_MI':'Issued','Total_MR':'Received',
            'Total_BAL':'Balance','DaysPending':'Days Pending'
        })
        det = det.sort_values('Days Pending', ascending=False)
        st.dataframe(
            det.style.applymap(color_aging, subset=['Aging'])
                     .applymap(highlight_days, subset=['Days Pending']),
            use_container_width=True, hide_index=True
        )

        csv_pend = det.to_csv(index=False)
        col1, col2 = st.columns(2)
        col1.download_button("⬇️ Download Pendency CSV", csv_pend,
                             f"pendency_{date.today()}.csv", "text/csv")

        # WhatsApp-style text report
        with col2:
            if st.button("📱 Generate WhatsApp Summary"):
                lines = [f"*Yash Gallery — Pendency Alert* 📅 {date.today().strftime('%d %b %Y')}",
                         f"Total Pending: *{int(filt['Total_BAL'].sum()):,} pcs*",
                         f"Critical (30+ days): *{int((filt['DaysPending']>30).sum())} lines*",
                         ""]
                for _, row in stage_sum.iterrows():
                    lines.append(f"⚙️ *{row['Process']}* — {int(row['Pending Pcs'])} pcs | Max {row['Max Days']} days")
                lines += ["", "_Please follow up with respective karigars._"]
                wa_text = "\n".join(lines)
                st.text_area("WhatsApp Message (copy karo):", value=wa_text, height=220)

# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — KARIGAR REPORT
# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("👷 Karigar Performance Report")

    kar_list = sorted(df['Karigar'].unique())
    sel_kar  = st.selectbox("👷 Select Karigar", kar_list)
    kar_df   = df[df['Karigar'] == sel_kar].copy()

    k1, k2, k3, k4 = st.columns(4)
    k_issued  = int(kar_df['Total_MI'].sum())
    k_recd    = int(kar_df['Total_MR'].sum())
    k_bal     = int(kar_df['Total_BAL'].sum())
    k_pct     = int(k_recd/k_issued*100) if k_issued > 0 else 0
    metric_card(k1, k_issued,  "Total Issued",   "#1565c0")
    metric_card(k2, k_recd,    "Total Received", "#2e7d32")
    metric_card(k3, k_bal,     "Balance Pcs",    "#c62828" if k_bal>0 else "#2e7d32")
    metric_card(k4, f"{k_pct}%", "Completion",   "#6a1b9a")

    st.markdown("<br>", unsafe_allow_html=True)

    # Process-wise for karigar
    st.markdown('<div class="section-title">⚙️ Process-wise Status</div>', unsafe_allow_html=True)
    kp_sum = kar_df.groupby('Process').agg(
        Styles=('StyleCode','nunique'),
        Issued=('Total_MI','sum'), Received=('Total_MR','sum'), Balance=('Total_BAL','sum'),
        Max_Days=('DaysPending','max')
    ).reset_index()
    kp_sum['%Done'] = (kp_sum['Received']/kp_sum['Issued']*100).fillna(0).round(1)
    kp_sum = kp_sum.sort_values('Balance', ascending=False)
    st.dataframe(kp_sum.style.applymap(color_balance, subset=['Balance'])
                           .applymap(highlight_days, subset=['Max_Days']),
                 use_container_width=True, hide_index=True)

    # Style-wise for karigar
    st.markdown('<div class="section-title">🎨 Style-wise Pendency</div>', unsafe_allow_html=True)
    pend_kar = kar_df[kar_df['Total_BAL']>0].copy()
    pend_kar['Aging'] = pend_kar['DaysPending'].apply(aging_bucket)
    if pend_kar.empty:
        st.success(f"✅ {sel_kar} ke paas koi pending item nahi hai!")
    else:
        det_cols = ['JONo','IssueDate','Process','StyleCode','Size',
                    'Total_MI','Total_MR','Total_BAL','DaysPending','Aging']
        disp = pend_kar[det_cols].rename(columns={
            'JONo':'JO No.','IssueDate':'Issue Date','StyleCode':'Style',
            'Total_MI':'Issued','Total_MR':'Received',
            'Total_BAL':'Balance','DaysPending':'Days Pending'
        }).sort_values('Days Pending', ascending=False)
        st.dataframe(
            disp.style.applymap(color_aging, subset=['Aging'])
                      .applymap(highlight_days, subset=['Days Pending']),
            use_container_width=True, hide_index=True
        )
        csv_kar = disp.to_csv(index=False)
        st.download_button(f"⬇️ Download {sel_kar} Report", csv_kar,
                           f"{sel_kar}_pendency.csv", "text/csv")

    # All karigar comparison
    st.markdown('<div class="section-title">📊 All Karigar Comparison</div>', unsafe_allow_html=True)
    all_kar = df.groupby('Karigar').agg(
        Styles=('StyleCode','nunique'), Issued=('Total_MI','sum'),
        Received=('Total_MR','sum'), Balance=('Total_BAL','sum')
    ).reset_index()
    all_kar['%Done'] = (all_kar['Received']/all_kar['Issued']*100).fillna(0).round(1)
    all_kar = all_kar.sort_values('Balance', ascending=False)
    st.dataframe(all_kar.style.applymap(color_balance, subset=['Balance']),
                 use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 5 — RAW DATA
# ══════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🔍 Raw Data Explorer")

    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1: f_style   = st.multiselect("🎨 Style",   sorted(df['StyleCode'].unique()), key="rs")
    with rc2: f_process = st.multiselect("⚙️ Process", sorted(df['Process'].unique()),  key="rp")
    with rc3: f_karigar = st.multiselect("👷 Karigar", sorted(df['Karigar'].unique()),  key="rk")
    with rc4:
        bal_filter = st.radio("Balance Filter", ["All", "Pending Only", "Clear Only"],
                              horizontal=True, key="rbf")

    raw = df.copy()
    if f_style:   raw = raw[raw['StyleCode'].isin(f_style)]
    if f_process: raw = raw[raw['Process'].isin(f_process)]
    if f_karigar: raw = raw[raw['Karigar'].isin(f_karigar)]
    if bal_filter == "Pending Only": raw = raw[raw['Total_BAL'] > 0]
    if bal_filter == "Clear Only":   raw = raw[raw['Total_BAL'] <= 0]

    display_cols = ['JONo','JODate','SONo','Karigar','IssueNo','IssueDate',
                    'Process','Design','Size','NoColour_MI','NoColour_MR',
                    'Mix_MI','Mix_MR','Total_MI','Total_MR','Total_BAL','DaysPending']
    st.markdown(f"**{len(raw):,} records** | Total Issued: **{int(raw['Total_MI'].sum()):,}** | Pending: **{int(raw[raw['Total_BAL']>0]['Total_BAL'].sum()):,}**")
    st.dataframe(raw[display_cols].sort_values(['Design','Process']),
                 use_container_width=True, hide_index=True)
    csv_raw = raw[display_cols].to_csv(index=False)
    st.download_button("⬇️ Download Filtered CSV", csv_raw,
                       f"yash_gallery_data_{date.today()}.csv", "text/csv")

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#aaa;font-size:12px">'
    'Yash Gallery Private Limited — Merchant Team Dashboard &nbsp;|&nbsp; '
    f'Data as of {date.today().strftime("%d %b %Y")}'
    '</div>',
    unsafe_allow_html=True
)
