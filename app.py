import streamlit as st
import pandas as pd
from html.parser import HTMLParser
import base64
import os
import json
import zipfile
import io

st.set_page_config(
    page_title="Yash Gallery - Style Tracking",
    page_icon="👗",
    layout="wide"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white; padding: 18px 24px; border-radius: 10px;
        text-align: center; margin-bottom: 20px;
    }
    .section-title {
        background: #e3f2fd; border-left: 5px solid #1565c0;
        padding: 8px 16px; font-weight: 700; font-size: 15px;
        margin: 16px 0 8px 0; border-radius: 4px; color: #1a237e;
    }
    .metric-box {
        background: white; border: 1px solid #e0e0e0; border-radius: 8px;
        padding: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .metric-val { font-size: 26px; font-weight: 800; color: #1565c0; }
    .metric-lbl { font-size: 12px; color: #666; margin-top: 4px; }
    .style-photo {
        border-radius: 10px; border: 2px solid #1565c0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); max-height: 220px;
    }
    .no-photo {
        background: #f5f5f5; border: 2px dashed #bdbdbd; border-radius: 10px;
        padding: 30px; text-align: center; color: #9e9e9e; font-size: 13px;
    }
    .upload-success {
        background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 8px;
        padding: 10px 14px; color: #2e7d32; font-size: 13px; margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Persistent storage paths (server-side, Streamlit Cloud safe) ────────────
DATA_DIR = "/tmp/yash_gallery_data"
EXCEL_PATH = os.path.join(DATA_DIR, "report.xls")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
META_PATH  = os.path.join(DATA_DIR, "meta.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def save_meta(excel_name, img_count):
    with open(META_PATH, 'w') as f:
        json.dump({"excel_name": excel_name, "img_count": img_count}, f)

def load_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH) as f:
            return json.load(f)
    return None

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

@st.cache_data(show_spinner="Loading data…")
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
    return df

def get_style_image(style_code):
    """Try to find image for style code with any extension."""
    exts = ['.jpg','.jpeg','.png','.jfif','.webp','.bmp']
    for ext in exts:
        p = os.path.join(IMAGES_DIR, style_code + ext)
        if os.path.exists(p):
            return p
        # Case-insensitive fallback
        p2 = os.path.join(IMAGES_DIR, style_code.upper() + ext)
        if os.path.exists(p2):
            return p2
        p3 = os.path.join(IMAGES_DIR, style_code.lower() + ext)
        if os.path.exists(p3):
            return p3
    return None

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h2 style="margin:0">👗 Yash Gallery Private Limited</h2>
    <p style="margin:4px 0 0 0; opacity:0.85">Material Issue / Receive – Style Tracking Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Data Source")

    meta = load_meta()
    excel_loaded = os.path.exists(EXCEL_PATH)
    imgs_count   = len([f for f in os.listdir(IMAGES_DIR) if not f.startswith('.')])

    if excel_loaded and meta:
        st.markdown(f"""<div class="upload-success">
            ✅ <b>Excel:</b> {meta.get('excel_name','report.xls')}<br>
            🖼️ <b>Images:</b> {imgs_count} photos loaded
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Replace / Upload New Data"):
            st.session_state['show_upload'] = True
    else:
        st.session_state['show_upload'] = True

    if st.session_state.get('show_upload', not excel_loaded):
        st.markdown("---")
        st.markdown("**Step 1: Upload Excel Report**")
        up_excel = st.file_uploader("Report file (.xls)", type=['xls','html','htm'], key="excel_up")
        if up_excel:
            with open(EXCEL_PATH, 'wb') as f:
                f.write(up_excel.getvalue())
            save_meta(up_excel.name, imgs_count)
            st.success("✅ Excel saved!")
            load_data.clear()

        st.markdown("**Step 2: Upload Images (ZIP folder)**")
        st.caption("Apni saari style photos ek ZIP mein dal ke upload karo.\nPhoto naam = Style code (e.g. 1557YKRED.jpg)")
        up_zip = st.file_uploader("Images ZIP file", type=['zip'], key="zip_up")
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
            imgs_count = count
            save_meta(meta.get('excel_name','') if meta else '', count)
            st.success(f"✅ {count} images saved!")
            if st.button("✅ Done, close upload panel"):
                st.session_state['show_upload'] = False
                st.rerun()

    st.markdown("---")
    st.markdown("**Quick Guide**")
    st.markdown("1. Upload Excel + ZIP of images (ek baar)\n2. Agli baar seedha open karo — data ready milega\n3. Style select karo → tracking dekho")

# ── Load data ─────────────────────────────────────────────────────────────────
if not os.path.exists(EXCEL_PATH):
    st.info("👈 Pehle sidebar se **Excel report** aur **Images ZIP** upload karo.")
    st.stop()

with open(EXCEL_PATH, 'rb') as f:
    df = load_data(f.read())

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📋 Style-wise Tracking Sheet", "📊 Summary Dashboard", "🔍 Raw Data", "⏳ Pendency Report"])

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

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Tracking Sheet
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        styles_list = sorted(df['StyleCode'].unique())
        selected_style = st.selectbox("🎨 Select Style / Design", styles_list)
    with col2:
        style_df = df[df['StyleCode'] == selected_style]
        jos_in_style = sorted(style_df['JONo'].unique())
        selected_jo = st.selectbox("📋 Filter by JO No.", ['All JOs'] + jos_in_style)
    with col3:
        processes = sorted(df['Process'].unique())
        selected_proc = st.selectbox("⚙️ Process", ['All Processes'] + processes)

    view_df = df[df['StyleCode'] == selected_style].copy()
    if selected_jo != 'All JOs':
        view_df = view_df[view_df['JONo'] == selected_jo]
    if selected_proc != 'All Processes':
        view_df = view_df[view_df['Process'] == selected_proc]

    if view_df.empty:
        st.warning("No data found for selected filters.")
        st.stop()

    meta_row = view_df.iloc[0]

    # ── Header card with PHOTO ────────────────────────────────────────────────
    img_path = get_style_image(selected_style)
    hcol1, hcol2 = st.columns([3, 1])
    with hcol1:
        st.markdown(f"""
        <div style="background:#f5f5f5;border-radius:10px;padding:16px 20px;
                    border:1px solid #ddd;height:100%">
            <div style="font-size:18px;font-weight:800;color:#1a237e;margin-bottom:10px">
                {selected_style}
            </div>
            <table style="font-size:14px;border-collapse:collapse">
                <tr><td style="color:#666;padding:3px 16px 3px 0">📋 JO No.</td>
                    <td><b>{meta_row['JONo']}</b></td></tr>
                <tr><td style="color:#666;padding:3px 16px 3px 0">📅 JO Date</td>
                    <td><b>{meta_row['JODate']}</b></td></tr>
                <tr><td style="color:#666;padding:3px 16px 3px 0">🧾 SO No.</td>
                    <td><b>{meta_row['SONo']}</b></td></tr>
                <tr><td style="color:#666;padding:3px 16px 3px 0">📅 SO Date</td>
                    <td><b>{meta_row['SODate']}</b></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    with hcol2:
        if img_path:
            st.image(img_path, use_container_width=True, caption=selected_style)
        else:
            st.markdown("""<div class="no-photo">📷<br>No photo<br>available</div>""",
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────────────
    total_mi  = int(view_df['Total_MI'].sum())
    total_mr  = int(view_df['Total_MR'].sum())
    total_bal = int(view_df['Total_BAL'].sum())
    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl, color in [
        (m1, total_mi,  "Total Issued (MI)",   "#1565c0"),
        (m2, total_mr,  "Total Received (MR)", "#2e7d32"),
        (m3, abs(total_bal), "Balance (Pending)", "#c62828" if total_bal > 0 else "#2e7d32"),
        (m4, view_df['Process'].nunique(), "Processes", "#6a1b9a")
    ]:
        col.markdown(f"""<div class="metric-box">
            <div class="metric-val" style="color:{color}">{val}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Process sections ──────────────────────────────────────────────────────
    all_processes = view_df['Process'].unique()
    for process in sorted(all_processes, key=process_sort_key):
        proc_df = view_df[view_df['Process'] == process].copy()
        proc_df = proc_df.sort_values('Size_order')
        st.markdown(f'<div class="section-title">⚙️ {process}</div>', unsafe_allow_html=True)

        pivot_rows = []
        for karigar_name, kg_df in proc_df.groupby('Karigar'):
            kg_df = kg_df.sort_values('Size_order')
            for issue_no, iss_df in kg_df.groupby('IssueNo', sort=False):
                iss_df = iss_df.sort_values('Size_order')
                issue_date = iss_df['IssueDate'].iloc[0]
                so_no  = iss_df['SONo'].iloc[0]
                jo_no  = iss_df['JONo'].iloc[0]
                row_data = {'SO No.': so_no, 'JO No.': jo_no,
                            'Issue Date': issue_date, 'CH. NO.': issue_no,
                            'Karigar': karigar_name, 'Type': 'Issued (MI)'}
                for _, r in iss_df.iterrows():
                    row_data[r['Size']] = int(r['Total_MI']) if r['Total_MI'] else ''
                pivot_rows.append(row_data)
                if iss_df['Total_MR'].sum() > 0:
                    rec_row = {'SO No.': '', 'JO No.': '',
                               'Issue Date': '', 'CH. NO.': issue_no,
                               'Karigar': karigar_name, 'Type': 'Received (MR)'}
                    for _, r in iss_df.iterrows():
                        rec_row[r['Size']] = int(r['Total_MR']) if r['Total_MR'] else ''
                    pivot_rows.append(rec_row)
                    bal_row = {'SO No.': '', 'JO No.': '',
                               'Issue Date': '', 'CH. NO.': issue_no, 'Karigar': karigar_name,
                               'Type': '🔴 Balance' if iss_df['Total_BAL'].sum() > 0 else '✅ Balance'}
                    for _, r in iss_df.iterrows():
                        bal = int(r['Total_BAL'])
                        bal_row[r['Size']] = bal if bal != 0 else ''
                    pivot_rows.append(bal_row)

        if pivot_rows:
            pv_df = pd.DataFrame(pivot_rows)
            base_cols = ['SO No.','JO No.','Issue Date','CH. NO.','Karigar','Type']
            size_cols = [s for s in SIZE_ORDER_LIST if s in pv_df.columns]
            other_cols = [c for c in pv_df.columns if c not in base_cols and c not in SIZE_ORDER_LIST]
            pv_df = pv_df.reindex(columns=base_cols + size_cols + other_cols).fillna('')
            all_size_cols = size_cols + other_cols
            pv_df['TOTAL'] = pv_df[all_size_cols].apply(
                lambda row: sum(int(v) for v in row if str(v).lstrip('-').isdigit()), axis=1)
            pv_df.loc[pv_df['TOTAL'] == 0, 'TOTAL'] = ''

            def style_rows(row):
                if 'Balance' in str(row.get('Type', '')):
                    return ['background-color:#ffebee;font-weight:bold'
                            if '🔴' in str(row.get('Type',''))
                            else 'background-color:#e8f5e9;font-weight:bold'] * len(row)
                elif 'Received' in str(row.get('Type', '')):
                    return ['background-color:#e3f2fd'] * len(row)
                return ['background-color:#fff8e1'] * len(row)

            st.dataframe(pv_df.style.apply(style_rows, axis=1),
                         use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – Summary Dashboard
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📊 Overall Summary")
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl, color in [
        (c1, df['StyleCode'].nunique(), "Total Styles",     "#1565c0"),
        (c2, df['JONo'].nunique(),      "Total JO Numbers", "#2e7d32"),
        (c3, df['Karigar'].nunique(),   "Total Karigars",   "#6a1b9a"),
        (c4, int(df['Total_MI'].sum()), "Total Issued Qty", "#e65100"),
    ]:
        col.markdown(f"""<div class="metric-box">
            <div class="metric-val" style="color:{color}">{val:,}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def color_balance(val):
        if val > 0:   return 'color:#c62828;font-weight:bold'
        elif val < 0: return 'color:#2e7d32;font-weight:bold'
        return 'color:#f57f17;font-weight:bold'

    # Style summary with photos
    st.markdown('<div class="section-title">📋 Style-wise Summary</div>', unsafe_allow_html=True)
    style_summary = df.groupby('StyleCode').agg(
        JOs=('JONo','nunique'), Processes=('Process','nunique'),
        Total_Issued=('Total_MI','sum'), Total_Received=('Total_MR','sum'),
        Balance=('Total_BAL','sum')).reset_index()
    style_summary.columns = ['Style/Design','JOs','Processes','Total Issued','Total Received','Balance']
    style_summary['Balance'] = style_summary['Balance'].astype(int)
    style_summary['📷'] = style_summary['Style/Design'].apply(
        lambda s: '✅' if get_style_image(s) else '❌')
    st.dataframe(style_summary.style.applymap(color_balance, subset=['Balance']),
                 use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">⚙️ Process-wise Summary</div>', unsafe_allow_html=True)
    proc_summary = df.groupby('Process').agg(
        Styles=('StyleCode','nunique'), Total_Issued=('Total_MI','sum'),
        Total_Received=('Total_MR','sum'), Balance=('Total_BAL','sum')).reset_index()
    proc_summary.columns = ['Process','Styles','Total Issued','Total Received','Balance']
    st.dataframe(proc_summary.sort_values('Total Issued', ascending=False)
                 .style.applymap(color_balance, subset=['Balance']),
                 use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">👷 Karigar-wise Summary</div>', unsafe_allow_html=True)
    kar_summary = df.groupby('Karigar').agg(
        Styles=('StyleCode','nunique'), Total_Issued=('Total_MI','sum'),
        Total_Received=('Total_MR','sum'), Balance=('Total_BAL','sum')).reset_index()
    kar_summary.columns = ['Karigar','Styles','Total Issued','Total Received','Balance']
    st.dataframe(kar_summary.sort_values('Balance', ascending=False)
                 .style.applymap(color_balance, subset=['Balance']),
                 use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – Raw Data
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔍 Raw Data Explorer")
    col1, col2, col3 = st.columns(3)
    with col1: f_style   = st.multiselect("Style",   sorted(df['StyleCode'].unique()))
    with col2: f_process = st.multiselect("Process", sorted(df['Process'].unique()))
    with col3: f_karigar = st.multiselect("Karigar", sorted(df['Karigar'].unique()))

    raw = df.copy()
    if f_style:   raw = raw[raw['StyleCode'].isin(f_style)]
    if f_process: raw = raw[raw['Process'].isin(f_process)]
    if f_karigar: raw = raw[raw['Karigar'].isin(f_karigar)]

    display_cols = ['JONo','JODate','SONo','Karigar','IssueNo','IssueDate',
                    'Process','Design','Size','NoColour_MI','NoColour_MR',
                    'Mix_MI','Mix_MR','Total_MI','Total_MR','Total_BAL']
    st.write(f"**{len(raw):,} records**")
    st.dataframe(raw[display_cols].sort_values(['Design','Process']),
                 use_container_width=True, hide_index=True)
    csv = raw[display_cols].to_csv(index=False)
    st.download_button("⬇️ Download Filtered CSV", csv, "filtered_data.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – Pendency Report
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("⏳ Pendency Report — Stage & Karigar Wise")

    from datetime import datetime, date

    # Only rows where balance > 0 (pending)
    pend_df = df[df['Total_BAL'] > 0].copy()

    if pend_df.empty:
        st.success("🎉 Koi pendency nahi hai! Sab clear hai.")
    else:
        # Calculate days pending from IssueDate
        def calc_days(issue_date_str):
            try:
                issue_date_str = str(issue_date_str).strip().lstrip("'")
                for fmt in ["%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        d = datetime.strptime(issue_date_str, fmt).date()
                        return (date.today() - d).days
                    except:
                        continue
            except:
                pass
            return 0

        pend_df['Days Pending'] = pend_df['IssueDate'].apply(calc_days)

        # Aging bucket
        def aging_bucket(days):
            if days <= 7:   return "🟢 0-7 days"
            elif days <= 15: return "🟡 8-15 days"
            elif days <= 30: return "🟠 16-30 days"
            else:            return "🔴 30+ days"

        pend_df['Aging'] = pend_df['Days Pending'].apply(aging_bucket)

        # ── Top filters ──────────────────────────────────────────────────────
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            p_process = st.multiselect("Process / Stage",
                                        sorted(pend_df['Process'].unique()), key="pend_proc")
        with f2:
            p_karigar = st.multiselect("Karigar",
                                        sorted(pend_df['Karigar'].unique()), key="pend_kar")
        with f3:
            p_aging = st.multiselect("Aging",
                                      ["🟢 0-7 days","🟡 8-15 days","🟠 16-30 days","🔴 30+ days"],
                                      key="pend_aging")
        with f4:
            p_style = st.multiselect("Style", sorted(pend_df['StyleCode'].unique()), key="pend_style")

        filtered = pend_df.copy()
        if p_process: filtered = filtered[filtered['Process'].isin(p_process)]
        if p_karigar: filtered = filtered[filtered['Karigar'].isin(p_karigar)]
        if p_aging:   filtered = filtered[filtered['Aging'].isin(p_aging)]
        if p_style:   filtered = filtered[filtered['StyleCode'].isin(p_style)]

        # ── Summary metrics ───────────────────────────────────────────────────
        total_pend_pcs  = int(filtered['Total_BAL'].sum())
        total_pend_sku  = len(filtered)
        max_days        = int(filtered['Days Pending'].max()) if not filtered.empty else 0
        critical_count  = int((filtered['Days Pending'] > 30).sum())

        m1, m2, m3, m4 = st.columns(4)
        for col, val, lbl, color in [
            (m1, total_pend_pcs,  "Total Pending Pcs",    "#c62828"),
            (m2, total_pend_sku,  "Pending SKU Lines",    "#e65100"),
            (m3, max_days,        "Max Days Pending",     "#6a1b9a"),
            (m4, critical_count,  "Critical (30+ days)",  "#b71c1c"),
        ]:
            col.markdown(f"""<div class="metric-box">
                <div class="metric-val" style="color:{color}">{val:,}</div>
                <div class="metric-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Stage-wise Pendency ───────────────────────────────────────────────
        st.markdown('<div class="section-title">📊 Stage-wise Pendency Summary</div>',
                    unsafe_allow_html=True)

        stage_summary = filtered.groupby('Process').agg(
            Karigar_Count=('Karigar', 'nunique'),
            Style_Count=('StyleCode', 'nunique'),
            Pending_Pcs=('Total_BAL', 'sum'),
            Avg_Days=('Days Pending', 'mean'),
            Max_Days=('Days Pending', 'max'),
            Critical_Lines=('Days Pending', lambda x: (x > 30).sum())
        ).reset_index()
        stage_summary.columns = ['Process','Karigars','Styles','Pending Pcs',
                                   'Avg Days','Max Days','Critical (30+)']
        stage_summary['Avg Days'] = stage_summary['Avg Days'].round(1)
        stage_summary = stage_summary.sort_values('Pending Pcs', ascending=False)

        def highlight_critical(val):
            if isinstance(val, (int, float)):
                if val > 30: return 'color:#c62828;font-weight:bold'
                elif val > 15: return 'color:#e65100;font-weight:bold'
            return ''

        st.dataframe(
            stage_summary.style.applymap(highlight_critical, subset=['Max Days','Avg Days']),
            use_container_width=True, hide_index=True
        )

        # ── Karigar-wise Pendency ─────────────────────────────────────────────
        st.markdown('<div class="section-title">👷 Karigar-wise Pendency</div>',
                    unsafe_allow_html=True)

        kar_pend = filtered.groupby(['Karigar','Process']).agg(
            Styles=('StyleCode','nunique'),
            Pending_Pcs=('Total_BAL','sum'),
            Avg_Days=('Days Pending','mean'),
            Max_Days=('Days Pending','max'),
            Critical=('Days Pending', lambda x: (x > 30).sum())
        ).reset_index()
        kar_pend.columns = ['Karigar','Process','Styles','Pending Pcs','Avg Days','Max Days','Critical (30+)']
        kar_pend['Avg Days'] = kar_pend['Avg Days'].round(1)
        kar_pend = kar_pend.sort_values(['Pending Pcs'], ascending=False)

        st.dataframe(
            kar_pend.style.applymap(highlight_critical, subset=['Max Days','Avg Days']),
            use_container_width=True, hide_index=True
        )

        # ── Detailed Pendency Table ───────────────────────────────────────────
        st.markdown('<div class="section-title">📋 Detailed Pendency — Style × Size × Karigar</div>',
                    unsafe_allow_html=True)

        detail_cols = ['SONo','JONo','IssueNo','IssueDate','Process','Karigar',
                       'StyleCode','Size','Total_MI','Total_MR','Total_BAL',
                       'Days Pending','Aging']
        detail_cols = [c for c in detail_cols if c in filtered.columns]

        detail_df = filtered[detail_cols].copy()
        detail_df = detail_df.rename(columns={
            'SONo':'SO No.', 'JONo':'JO No.', 'IssueNo':'Issue No.',
            'IssueDate':'Issue Date', 'StyleCode':'Style',
            'Total_MI':'Issued','Total_MR':'Received','Total_BAL':'Balance Pcs'
        })
        detail_df = detail_df.sort_values(['Days Pending'], ascending=False)

        def color_aging(val):
            if '🔴' in str(val): return 'background-color:#ffebee;font-weight:bold;color:#c62828'
            elif '🟠' in str(val): return 'background-color:#fff3e0;color:#e65100'
            elif '🟡' in str(val): return 'background-color:#fffde7;color:#f57f17'
            elif '🟢' in str(val): return 'background-color:#e8f5e9;color:#2e7d32'
            return ''

        def color_days(val):
            try:
                v = int(val)
                if v > 30: return 'color:#c62828;font-weight:bold'
                elif v > 15: return 'color:#e65100;font-weight:bold'
                elif v > 7: return 'color:#f57f17'
            except: pass
            return ''

        st.dataframe(
            detail_df.style
                .applymap(color_aging, subset=['Aging'])
                .applymap(color_days, subset=['Days Pending']),
            use_container_width=True, hide_index=True
        )

        # ── Download ──────────────────────────────────────────────────────────
        csv_pend = detail_df.to_csv(index=False)
        st.download_button("⬇️ Download Pendency Report", csv_pend,
                           "pendency_report.csv", "text/csv")
