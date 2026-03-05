import streamlit as st
import pandas as pd
from html.parser import HTMLParser
from io import StringIO

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
        color: white;
        padding: 18px 24px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-title {
        background: #e3f2fd;
        border-left: 5px solid #1565c0;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 15px;
        margin: 16px 0 8px 0;
        border-radius: 4px;
        color: #1a237e;
    }
    .metric-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .metric-val { font-size: 26px; font-weight: 800; color: #1565c0; }
    .metric-lbl { font-size: 12px; color: #666; margin-top: 4px; }
    .bal-neg  { color: #c62828; font-weight: 700; }
    .bal-pos  { color: #2e7d32; font-weight: 700; }
    .bal-zero { color: #f57f17; font-weight: 700; }
    div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
    .stSelectbox > div { border-radius: 6px; }
    .process-tag {
        display: inline-block;
        background: #e8f5e9;
        border: 1px solid #a5d6a7;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 12px;
        margin: 2px;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)


# ── HTML Parser ─────────────────────────────────────────────────────────────
class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.current_row, self.current_cell, self.in_td = [], [], '', False

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.current_row = []
        elif tag == 'td':
            self.in_td, self.current_cell = True, ''

    def handle_endtag(self, tag):
        if tag == 'tr' and self.current_row:
            self.rows.append(self.current_row)
        elif tag == 'td':
            self.in_td = False
            self.current_row.append(self.current_cell.strip())

    def handle_data(self, data):
        if self.in_td:
            self.current_cell += data


# ── Load data ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading Excel data…")
def load_data(file_bytes):
    content = file_bytes.decode('utf-8', errors='ignore')
    parser = TableParser()
    parser.feed(content)

    headers = ['JONo', 'JODate', 'SONo', 'SODate', 'Karigar',
               'IssueNo', 'IssueDate', 'Process', 'Design', 'Size',
               'NoColour_MI', 'NoColour_MR', 'NoColour_BAL',
               'Mix_MI', 'Mix_MR', 'Mix_BAL']

    data_rows = parser.rows[2:]  # skip title & header rows
    records = []
    for row in data_rows:
        if len(row) >= 10 and row[0].strip() and row[8].strip():
            r = {}
            for i, h in enumerate(headers):
                r[h] = row[i].strip() if i < len(row) else ''
            records.append(r)

    df = pd.DataFrame(records)

    # Numeric columns
    for col in ['NoColour_MI', 'NoColour_MR', 'NoColour_BAL', 'Mix_MI', 'Mix_MR', 'Mix_BAL']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Date cleanup
    df['IssueDate'] = df['IssueDate'].str.lstrip("'")
    df['JODate']    = df['JODate'].str.lstrip("'")

    # Total MI / MR / BAL across both colour types
    df['Total_MI']  = df['NoColour_MI'] + df['Mix_MI']
    df['Total_MR']  = df['NoColour_MR'] + df['Mix_MR']
    df['Total_BAL'] = df['Total_MI'] - df['Total_MR']

    # Style code = Design name
    df['StyleCode'] = df['Design']

    SIZE_ORDER = ['XS','S','S-M','S-M-L','M','L','L-XL','L-XL-XXL',
                  'XL','XL-XXL','XL-XXL-3XL','XXL','XXL-3XL',
                  '3XL','3XL-4XL','4XL','4XL-5XL','5XL','5XL-6XL',
                  '6XL','7XL','7XL-8XL','8XL','Free Size','Mix',
                  '7 -8 Years','9 -10 Years','11 -12 Years','13 -14 Years']
    df['Size_order'] = df['Size'].apply(lambda s: SIZE_ORDER.index(s) if s in SIZE_ORDER else 999)

    return df


# ── Sidebar – upload ─────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h2 style="margin:0">👗 Yash Gallery Private Limited</h2>
    <p style="margin:4px 0 0 0; opacity:0.85">Material Issue / Receive – Style Tracking Dashboard</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 Data Source")
    uploaded = st.file_uploader("Upload report (.xls / .html)", type=['xls','html','htm'])
    st.markdown("---")
    st.markdown("**Quick Guide**")
    st.markdown("1. Upload your report file\n2. Select Style/JO\n3. View size-wise tracking sheet")

if uploaded is None:
    st.info("👈 Please upload your **Material Issue Receive** report (.xls) from the sidebar to get started.")
    st.stop()

df = load_data(uploaded.read())

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Style-wise Tracking Sheet", "📊 Summary Dashboard", "🔍 Raw Data"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – Tracking Sheet (mimics the paper form)
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

    # Apply filters
    view_df = df[df['StyleCode'] == selected_style].copy()
    if selected_jo != 'All JOs':
        view_df = view_df[view_df['JONo'] == selected_jo]
    if selected_proc != 'All Processes':
        view_df = view_df[view_df['Process'] == selected_proc]

    if view_df.empty:
        st.warning("No data found for selected filters.")
        st.stop()

    # ── Header info card ────────────────────────────────────────────────────
    meta = view_df.iloc[0]
    st.markdown(f"""
    <div style="background:#f5f5f5;border-radius:10px;padding:14px 20px;margin-bottom:16px;
                border:1px solid #ddd;display:flex;flex-wrap:wrap;gap:24px">
        <span><b>Style:</b> {selected_style}</span>
        <span><b>JO No:</b> {meta['JONo']}</span>
        <span><b>JO Date:</b> {meta['JODate']}</span>
        <span><b>SO No:</b> {meta['SONo']}</span>
        <span><b>SO Date:</b> {meta['SODate']}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary metrics ──────────────────────────────────────────────────────
    total_mi  = int(view_df['Total_MI'].sum())
    total_mr  = int(view_df['Total_MR'].sum())
    total_bal = int(view_df['Total_BAL'].sum())
    bal_class = 'bal-neg' if total_bal > 0 else ('bal-pos' if total_bal < 0 else 'bal-zero')

    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl, color in [
        (m1, total_mi,  "Total Issued (MI)",   "#1565c0"),
        (m2, total_mr,  "Total Received (MR)", "#2e7d32"),
        (m3, abs(total_bal), "Balance (Pending)", "#c62828" if total_bal > 0 else "#2e7d32"),
        (m4, view_df['Process'].nunique(), "Processes", "#6a1b9a")
    ]:
        col.markdown(f"""
        <div class="metric-box">
            <div class="metric-val" style="color:{color}">{val}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Process-wise sections (like the paper form) ──────────────────────────
    all_processes = view_df['Process'].unique()

    for process in sorted(all_processes):
        proc_df = view_df[view_df['Process'] == process].copy()
        proc_df = proc_df.sort_values('Size_order')

        st.markdown(f'<div class="section-title">⚙️ {process}</div>', unsafe_allow_html=True)

        # Pivot size-wise
        pivot_rows = []
        karigars = proc_df.groupby('Karigar')

        for karigar_name, kg_df in karigars:
            kg_df = kg_df.sort_values('Size_order')
            issues = kg_df.groupby('IssueNo', sort=False)

            for issue_no, iss_df in issues:
                iss_df = iss_df.sort_values('Size_order')
                issue_date = iss_df['IssueDate'].iloc[0]

                # Build a row: one column per size
                row_data = {
                    'Issue Date': issue_date,
                    'CH. NO. (Issue No)': issue_no,
                    'Karigar': karigar_name,
                    'Type': 'Issued (MI)'
                }
                for _, r in iss_df.iterrows():
                    row_data[r['Size']] = int(r['Total_MI']) if r['Total_MI'] else ''
                pivot_rows.append(row_data)

                # Received row if any MR
                if iss_df['Total_MR'].sum() > 0:
                    rec_row = {
                        'Issue Date': '',
                        'CH. NO. (Issue No)': issue_no,
                        'Karigar': karigar_name,
                        'Type': 'Received (MR)'
                    }
                    for _, r in iss_df.iterrows():
                        rec_row[r['Size']] = int(r['Total_MR']) if r['Total_MR'] else ''
                    pivot_rows.append(rec_row)

                    # Balance row
                    bal_row = {
                        'Issue Date': '',
                        'CH. NO. (Issue No)': issue_no,
                        'Karigar': karigar_name,
                        'Type': '🔴 Balance (BAL)' if iss_df['Total_BAL'].sum() > 0 else '✅ Balance (BAL)'
                    }
                    for _, r in iss_df.iterrows():
                        bal = int(r['Total_BAL'])
                        bal_row[r['Size']] = bal if bal != 0 else ''
                    pivot_rows.append(bal_row)

        if pivot_rows:
            pv_df = pd.DataFrame(pivot_rows)

            # Size order in columns
            SIZE_ORDER_LIST = ['XS','S','S-M','S-M-L','M','L','L-XL','L-XL-XXL',
                               'XL','XL-XXL','XL-XXL-3XL','XXL','XXL-3XL',
                               '3XL','3XL-4XL','4XL','4XL-5XL','5XL','5XL-6XL',
                               '6XL','7XL','7XL-8XL','8XL','Free Size','Mix',
                               '7 -8 Years','9 -10 Years','11 -12 Years','13 -14 Years']
            base_cols = ['Issue Date','CH. NO. (Issue No)','Karigar','Type']
            size_cols_present = [s for s in SIZE_ORDER_LIST if s in pv_df.columns]
            other_size_cols = [c for c in pv_df.columns if c not in base_cols and c not in SIZE_ORDER_LIST]
            final_cols = base_cols + size_cols_present + other_size_cols

            pv_df = pv_df.reindex(columns=final_cols).fillna('')

            # Total column
            size_only_cols = size_cols_present + other_size_cols
            pv_df['TOTAL'] = pv_df[size_only_cols].apply(
                lambda row: sum(int(v) for v in row if str(v).lstrip('-').isdigit()), axis=1
            )
            pv_df.loc[pv_df['TOTAL'] == 0, 'TOTAL'] = ''

            # Color rows
            def style_rows(row):
                if 'Balance' in str(row.get('Type', '')):
                    if '🔴' in str(row.get('Type', '')):
                        return ['background-color: #ffebee; font-weight: bold'] * len(row)
                    else:
                        return ['background-color: #e8f5e9; font-weight: bold'] * len(row)
                elif 'Received' in str(row.get('Type', '')):
                    return ['background-color: #e3f2fd'] * len(row)
                else:
                    return ['background-color: #fff8e1'] * len(row)

            styled = pv_df.style.apply(style_rows, axis=1)
            st.dataframe(styled, use_container_width=True, hide_index=True)


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
        col.markdown(f"""
        <div class="metric-box">
            <div class="metric-val" style="color:{color}">{val:,}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Style-wise summary table
    st.markdown('<div class="section-title">📋 Style-wise Issue / Receive Summary</div>', unsafe_allow_html=True)

    style_summary = df.groupby('StyleCode').agg(
        JO_Count=('JONo', 'nunique'),
        Process_Count=('Process', 'nunique'),
        Total_Issued=('Total_MI', 'sum'),
        Total_Received=('Total_MR', 'sum'),
        Balance=('Total_BAL', 'sum')
    ).reset_index()
    style_summary.columns = ['Style/Design', 'JOs', 'Processes', 'Total Issued', 'Total Received', 'Balance']
    style_summary['Balance'] = style_summary['Balance'].astype(int)

    def color_balance(val):
        if val > 0:  return 'color: #c62828; font-weight: bold'
        elif val < 0: return 'color: #2e7d32; font-weight: bold'
        return 'color: #f57f17; font-weight: bold'

    st.dataframe(
        style_summary.style.applymap(color_balance, subset=['Balance']),
        use_container_width=True, hide_index=True
    )

    # Process-wise summary
    st.markdown('<div class="section-title">⚙️ Process-wise Summary</div>', unsafe_allow_html=True)
    proc_summary = df.groupby('Process').agg(
        Styles=('StyleCode', 'nunique'),
        Total_Issued=('Total_MI', 'sum'),
        Total_Received=('Total_MR', 'sum'),
        Balance=('Total_BAL', 'sum')
    ).reset_index()
    proc_summary.columns = ['Process', 'Styles', 'Total Issued', 'Total Received', 'Balance']
    st.dataframe(
        proc_summary.sort_values('Total Issued', ascending=False).style.applymap(color_balance, subset=['Balance']),
        use_container_width=True, hide_index=True
    )

    # Karigar-wise
    st.markdown('<div class="section-title">👷 Karigar-wise Summary</div>', unsafe_allow_html=True)
    kar_summary = df.groupby('Karigar').agg(
        Styles=('StyleCode', 'nunique'),
        Total_Issued=('Total_MI', 'sum'),
        Total_Received=('Total_MR', 'sum'),
        Balance=('Total_BAL', 'sum')
    ).reset_index()
    kar_summary.columns = ['Karigar', 'Styles', 'Total Issued', 'Total Received', 'Balance']
    st.dataframe(
        kar_summary.sort_values('Balance', ascending=False).style.applymap(color_balance, subset=['Balance']),
        use_container_width=True, hide_index=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – Raw Data
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔍 Raw Data Explorer")

    col1, col2, col3 = st.columns(3)
    with col1:
        f_style = st.multiselect("Style", sorted(df['StyleCode'].unique()))
    with col2:
        f_process = st.multiselect("Process", sorted(df['Process'].unique()))
    with col3:
        f_karigar = st.multiselect("Karigar", sorted(df['Karigar'].unique()))

    raw = df.copy()
    if f_style:   raw = raw[raw['StyleCode'].isin(f_style)]
    if f_process: raw = raw[raw['Process'].isin(f_process)]
    if f_karigar: raw = raw[raw['Karigar'].isin(f_karigar)]

    display_cols = ['JONo','JODate','SONo','Karigar','IssueNo','IssueDate',
                    'Process','Design','Size','NoColour_MI','NoColour_MR',
                    'Mix_MI','Mix_MR','Total_MI','Total_MR','Total_BAL']

    st.write(f"**{len(raw):,} records**")
    st.dataframe(raw[display_cols].sort_values(['Design','Process','Size_order']),
                 use_container_width=True, hide_index=True)

    # Download
    csv = raw[display_cols].to_csv(index=False)
    st.download_button("⬇️ Download Filtered CSV", csv, "filtered_data.csv", "text/csv")
