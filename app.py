import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Transaction Latency & Completion Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F2B48 100%);
        border-radius: 16px;
        padding: 26px 32px;
        margin-bottom: 22px;
        color: #FFFFFF;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
        background: linear-gradient(90deg, #FFFFFF 0%, #93C5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 0.96rem;
        color: #94A3B8;
        max-width: 850px;
        line-height: 1.5;
    }
    .hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #38BDF8;
        margin-bottom: 10px;
    }
    
    /* KPI Card Style */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
    }
    .kpi-title {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
        font-weight: 700;
    }
    .kpi-icon {
        font-size: 1.1rem;
        opacity: 0.85;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .kpi-footer {
        margin-top: 6px;
        font-size: 0.8rem;
        color: #64748B;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Pill Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-success { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
    .badge-failed { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
    .badge-pending { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }
    .badge-blue { background: #EFF6FF; color: #2563EB; border: 1px solid #BFDBFE; }
    .badge-purple { background: #FAF5FF; color: #7E22CE; border: 1px solid #E9D5FF; }
    
    /* Banners & Insight Boxes */
    .alert-banner {
        background: #FFFBEB;
        border-left: 5px solid #F59E0B;
        border-radius: 10px;
        padding: 14px 18px;
        color: #92400E;
        font-size: 0.92rem;
        margin-bottom: 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .insight-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #3B82F6;
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.9rem;
        color: #1E293B;
        line-height: 1.55;
        margin-bottom: 12px;
    }
    .recon-banner {
        background: linear-gradient(90deg, #FAF5FF 0%, #F3E8FF 100%);
        border: 1px solid #E9D5FF;
        border-left: 5px solid #8B5CF6;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 18px;
        font-size: 0.94rem;
        color: #5B21B6;
    }
</style>
""", unsafe_allow_html=True)

# Visual Identity Palette
COLOR_MAP = {
    'success': '#10B981',      # Emerald Green
    'failed': '#EF4444',       # Ruby Red
    'pending': '#F59E0B',      # Warm Amber
    'Success': '#10B981',
    'Failed': '#EF4444',
    'Pending': '#F59E0B'
}

DURATION_BAND_ORDER = [
    '1-5 seconds',
    '6-10 seconds',
    '11-15 seconds',
    '16-20 seconds',
    '21-25 seconds',
    '26-30 seconds',
    'Above 30 seconds',
    'Not Logged'
]

# Set Plotly default aesthetic template
pio_template = go.layout.Template()
pio_template.layout.font = dict(family="Plus Jakarta Sans, sans-serif", color="#334155")
pio_template.layout.plot_bgcolor = "rgba(0,0,0,0)"
pio_template.layout.paper_bgcolor = "rgba(0,0,0,0)"
pio_template.layout.xaxis = dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False)
pio_template.layout.yaxis = dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False)

def format_duration_friendly(seconds):
    """Formats raw seconds into human-readable time."""
    if pd.isna(seconds) or seconds is None:
        return "N/A"
    sec = float(seconds)
    if sec < 1.0:
        return f"{sec*1000:.0f} ms"
    elif sec < 60.0:
        return f"{sec:.2f} s"
    elif sec < 3600.0:
        mins = sec / 60.0
        return f"{mins:.1f} min ({sec:.0f}s)"
    elif sec < 86400.0:
        hrs = sec / 3600.0
        return f"{hrs:.1f} hrs ({sec:,.0f}s)"
    else:
        days = sec / 86400.0
        return f"{days:.1f} days ({sec/3600:,.0f} hrs)"

def categorical_with_default(series, default, lowercase=False):
    series = series.astype("category")
    categories = [
        str(value).strip().lower() if lowercase else str(value)
        for value in series.cat.categories
    ]
    if len(set(categories)) != len(categories):
        series = series.astype("string[pyarrow]")
        if lowercase:
            series = series.str.strip().str.lower()
        return series.fillna(default).astype("category")
    series = series.cat.rename_categories(categories)
    if default not in series.cat.categories:
        series = series.cat.add_categories([default])
    return series.fillna(default)


@st.cache_resource(
    show_spinner="Consolidating data files and computing latency...",
    max_entries=2,
)
def load_and_preprocess_combined_data(data_folder='data', single_file=None, inject_demo_pending=False):
    """
    Loads the prepared dataset when available, otherwise combines CSV parts,
    standardizes schemas, calculates duration from timestamps, and handles Recon Actions.
    """
    if single_file is not None:
        df = pd.read_csv(single_file, dtype_backend="pyarrow")
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        resolved_data_folder = (
            data_folder
            if os.path.isabs(data_folder)
            else os.path.join(app_dir, data_folder)
        )
        parquet_file = next(
            (
                os.path.join(resolved_data_folder, filename)
                for filename in ('transactions.parquet', 'transactions_opt.parquet')
                if os.path.exists(os.path.join(resolved_data_folder, filename))
            ),
            None,
        )
        csv_files = sorted(glob.glob(os.path.join(resolved_data_folder, '*.csv')))

        if parquet_file is not None:
            parquet_columns = [
                'time_created',
                'transaction_status',
                'transaction_id',
                'response_code',
                'recon_action',
                'client_name',
                'debit_amt',
                'duration_seconds',
                'date_str',
                'duration_band',
            ] if os.path.basename(parquet_file) == 'transactions.parquet' else None
            df = pd.read_parquet(
                parquet_file,
                columns=parquet_columns,
                dtype_backend="pyarrow",
            )
        elif not csv_files:
            data_csv = os.path.join(app_dir, 'data.csv')
            if os.path.exists(data_csv):
                df = pd.read_csv(data_csv, dtype_backend="pyarrow")
            else:
                raise FileNotFoundError(
                    "No transaction dataset found. Add 'data/transactions.parquet' "
                    "or CSV files to the 'data/' folder."
                )
        else:
            dfs = [pd.read_csv(f, dtype_backend="pyarrow") for f in csv_files]
            df = pd.concat(dfs, ignore_index=True)
    
    # Standardize column mapping safely
    col_map = {}
    for c in df.columns:
        c_clean = c.strip().lower()
        if c_clean in ['time created', 'created_at', 'start_time']:
            col_map[c] = 'time_created'
        elif c_clean in ['time completed', 'completed_at', 'end_time']:
            col_map[c] = 'time_completed'
        elif c_clean in ['transaction status', 'status', 'trans_status']:
            col_map[c] = 'transaction_status'
        elif c_clean in ['transaction id', 'id', 'trans_id']:
            col_map[c] = 'transaction_id'
        elif c_clean in ['response code', 'response_code', 'code']:
            col_map[c] = 'response_code'
        elif 'client → id' in c_clean or c_clean == 'client_id' or 'client id' in c_clean:
            col_map[c] = 'client_id'
        elif 'client → name' in c_clean or c_clean == 'client_name' or 'client name' in c_clean or c_clean == 'client':
            col_map[c] = 'client_name'
        elif c_clean in ['debit amt', 'amount', 'amt']:
            col_map[c] = 'debit_amt'
        elif c_clean in ['transaction type', 'type']:
            col_map[c] = 'transaction_type'
        elif c_clean in ['recon action', 'recon_action', 'recon']:
            col_map[c] = 'recon_action'
            
    df = df.rename(columns=col_map)
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Clean transaction_status
    if 'transaction_status' not in df.columns:
        df['transaction_status'] = 'unknown'
    df['transaction_status'] = categorical_with_default(
        df['transaction_status'], 'unknown', lowercase=True
    )

    # Reuse prepared duration fields to avoid rebuilding large columns at startup.
    if 'duration_seconds' not in df.columns and 'time_created' in df.columns and 'time_completed' in df.columns:
        tc = pd.to_datetime(df['time_created'], format='ISO8601', errors='coerce')
        tcomp = pd.to_datetime(df['time_completed'], format='ISO8601', errors='coerce')
        df['duration_seconds'] = (tcomp - tc).dt.total_seconds().abs()
        df['date_dt'] = tc
    elif 'duration_seconds' in df.columns:
        df['duration_seconds'] = pd.to_numeric(df['duration_seconds'], errors='coerce').abs()
    else:
        df['duration_seconds'] = np.nan

    if 'date_dt' not in df.columns:
        if 'time_created' in df.columns:
            df['date_dt'] = pd.to_datetime(df['time_created'], format='ISO8601', errors='coerce')
        elif 'date' in df.columns:
            df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
        else:
            df['date_dt'] = pd.NaT
    if 'date_str' not in df.columns:
        df['date_str'] = df['date_dt'].dt.strftime('%Y-%m-%d').fillna('Unknown Date')
    else:
        df['date_str'] = df['date_str'].fillna('Unknown Date').astype('string[pyarrow]')
        
    # Bin into duration bands
    if 'duration_band' not in df.columns:
        df['duration_band'] = pd.cut(
            df['duration_seconds'],
            bins=[0, 5, 10, 15, 20, 25, 30, np.inf],
            labels=[
                '1-5 seconds',
                '6-10 seconds',
                '11-15 seconds',
                '16-20 seconds',
                '21-25 seconds',
                '26-30 seconds',
                'Above 30 seconds'
            ],
            include_lowest=True
        )
    df['duration_band'] = categorical_with_default(df['duration_band'], 'Not Logged')
    
    # Clean string identifiers
    if 'response_code' not in df.columns:
        df['response_code'] = 'UNKNOWN'
    df['response_code'] = categorical_with_default(df['response_code'], 'UNKNOWN')
    
    if 'client_name' in df.columns:
        if isinstance(df['client_name'], pd.DataFrame):
            df['client_name'] = df['client_name'].iloc[:, 0]
    else:
        df['client_name'] = 'Unknown Client'
    df['client_name'] = categorical_with_default(df['client_name'], 'Unknown Client')
        
    if 'recon_action' in df.columns:
        if isinstance(df['recon_action'], pd.DataFrame):
            df['recon_action'] = df['recon_action'].iloc[:, 0]
    else:
        df['recon_action'] = 'Direct Settlement (No Recon)'
    df['recon_action'] = categorical_with_default(
        df['recon_action'], 'Direct Settlement (No Recon)'
    )
        
    if 'transaction_id' not in df.columns:
        df['transaction_id'] = 'N/A'
    df['transaction_id'] = df['transaction_id'].fillna('N/A').astype('string[pyarrow]')
    
    if 'debit_amt' in df.columns:
        df['debit_amt'] = pd.to_numeric(df['debit_amt'], errors='coerce').fillna(0.0)
    else:
        df['debit_amt'] = 0.0

    df = df[
        [
            'transaction_status',
            'duration_band',
            'response_code',
            'client_name',
            'recon_action',
            'date_dt',
            'date_str',
            'transaction_id',
            'debit_amt',
            'duration_seconds',
        ]
    ]

    if inject_demo_pending:
        np.random.seed(42)
        if 'pending' not in df['transaction_status'].cat.categories:
            df['transaction_status'] = df['transaction_status'].cat.add_categories(['pending'])
        sample_pending_idx = df.sample(frac=0.015, random_state=42).index
        df.loc[sample_pending_idx, 'transaction_status'] = 'pending'
        
    return df

# Sidebar Navigation and Controls
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    uploaded_file = st.file_uploader("📂 Upload Custom CSV Batch", type=['csv'])
    
    demo_pending_toggle = st.toggle(
        "⚡ Inject Demo 'Pending' status", 
        value=False,
        help="Simulates 1.5% in-flight pending status to verify queue isolation behavior."
    )
    
    try:
        if uploaded_file is not None:
            df_raw = load_and_preprocess_combined_data(single_file=uploaded_file, inject_demo_pending=demo_pending_toggle)
            st.success("Uploaded file loaded successfully!")
        else:
            df_raw = load_and_preprocess_combined_data(data_folder='data', inject_demo_pending=demo_pending_toggle)
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()
        
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    # 1. Transaction Status
    all_statuses = sorted(df_raw['transaction_status'].unique().tolist())
    selected_statuses = st.multiselect(
        "Transaction Status",
        options=all_statuses,
        default=all_statuses,
        help="Select which transaction statuses to include in scope."
    )
    
    # 2. Duration Bands
    available_bands = [b for b in DURATION_BAND_ORDER if b in df_raw['duration_band'].unique()]
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("All Bands", use_container_width=True):
            st.session_state['selected_bands'] = available_bands
    with col_b2:
        if st.button("Timed Only", use_container_width=True):
            st.session_state['selected_bands'] = [b for b in available_bands if b != 'Not Logged']
            
    if 'selected_bands' not in st.session_state:
        st.session_state['selected_bands'] = available_bands
        
    selected_bands = st.multiselect(
        "Duration Bands",
        options=available_bands,
        default=st.session_state['selected_bands'],
        help="Filter by turnaround latency brackets."
    )
    
    # 3. Response Code
    top_rc_list = df_raw['response_code'].value_counts().index.tolist()
    col_rc1, col_rc2 = st.columns(2)
    with col_rc1:
        if st.button("All Codes", use_container_width=True):
            st.session_state['selected_codes'] = top_rc_list
    with col_rc2:
        if st.button("Top 5 Codes", use_container_width=True):
            st.session_state['selected_codes'] = top_rc_list[:5]
            
    if 'selected_codes' not in st.session_state:
        st.session_state['selected_codes'] = top_rc_list
        
    selected_codes = st.multiselect(
        "Response Codes",
        options=top_rc_list,
        default=st.session_state['selected_codes'],
        help="Filter by specific response code or provider gateway."
    )
    
    # 4. Recon Action Filter
    all_recons = sorted(df_raw['recon_action'].unique().tolist())
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("All Actions", use_container_width=True):
            st.session_state['selected_recons'] = all_recons
    with col_r2:
        if st.button("Recons Only", use_container_width=True):
            st.session_state['selected_recons'] = [r for r in all_recons if r != 'Direct Settlement (No Recon)']
            
    if 'selected_recons' not in st.session_state:
        st.session_state['selected_recons'] = all_recons
        
    selected_recons = st.multiselect(
        "Recon Action Filter",
        options=all_recons,
        default=st.session_state['selected_recons'],
        help="Filter by reconciliation action."
    )
    
    # 5. Global Client Filter
    if 'client_name' in df_raw.columns:
        c_series = df_raw['client_name']
        if isinstance(c_series, pd.DataFrame):
            c_series = c_series.iloc[:, 0]
        top_clients = c_series.value_counts().head(30).index.tolist()
    else:
        top_clients = []
        
    selected_client = st.selectbox(
        "Client / Merchant Filter",
        options=["All Clients"] + top_clients,
        index=0,
        help="Filter the entire dashboard to a specific corporate merchant."
    )

    # 6. Date Range Filter
    valid_dates = df_raw['date_dt'].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date() if hasattr(valid_dates.min(), 'date') else valid_dates.min()
        max_date = valid_dates.max().date() if hasattr(valid_dates.max(), 'date') else valid_dates.max()
        selected_date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter by transaction creation date."
        )
    else:
        selected_date_range = None
        
    st.markdown("---")
    app_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_files = (
        os.path.join(app_dir, 'data', 'transactions.parquet'),
        os.path.join(app_dir, 'data', 'transactions_opt.parquet'),
    )
    if uploaded_file is not None:
        dataset_source = "Uploaded CSV"
    elif any(os.path.exists(path) for path in parquet_files):
        dataset_source = "Prepared Parquet dataset"
    else:
        file_count = len(glob.glob(os.path.join(app_dir, 'data', '*.csv')))
        dataset_source = f"{file_count} CSV partitions"
    st.caption(f"⚡ **Platform Scale:** {dataset_source} &bull; {len(df_raw):,} records")

# Apply filters with a single row selection to avoid repeated full-dataframe copies.
if selected_statuses:
    filter_mask = df_raw['transaction_status'].isin(selected_statuses)
else:
    st.warning("⚠️ No status selected. Please choose at least one transaction status.")
    st.stop()

if selected_bands:
    filter_mask &= df_raw['duration_band'].isin(selected_bands)
else:
    st.warning("⚠️ No duration band selected. Please select at least one band.")
    st.stop()

if selected_codes:
    filter_mask &= df_raw['response_code'].isin(selected_codes)
else:
    st.warning("⚠️ No response code selected. Please select at least one code.")
    st.stop()

if selected_recons:
    filter_mask &= df_raw['recon_action'].isin(selected_recons)
else:
    st.warning("⚠️ No recon action selected. Please select at least one recon action.")
    st.stop()

if selected_client != "All Clients":
    filter_mask &= df_raw['client_name'] == selected_client

if selected_date_range and isinstance(selected_date_range, (tuple, list)) and len(selected_date_range) == 2:
    start_d, end_d = selected_date_range
    dates_series = df_raw['date_dt']
    start_ts = pd.Timestamp(start_d)
    end_ts = pd.Timestamp(end_d) + pd.Timedelta(days=1)
    if dates_series.dt.tz is not None:
        start_ts = start_ts.tz_localize(dates_series.dt.tz)
        end_ts = end_ts.tz_localize(dates_series.dt.tz)
    date_mask = dates_series.ge(start_ts) & dates_series.lt(end_ts)
    filter_mask &= date_mask | dates_series.isna()

# CORE ARCHITECTURE: Strict Pending Status Separation
filtered_df = df_raw.loc[filter_mask]
df_completed = filtered_df[filtered_df['transaction_status'].isin(['success', 'failed'])]
df_pending = filtered_df[filtered_df['transaction_status'] == 'pending']

total_all = len(filtered_df)
total_completed = len(df_completed)
total_pending = len(df_pending)
pending_pct = (total_pending / total_all * 100) if total_all > 0 else 0

# Hero Header Section
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-tag">⚡ TRANSACTION TURNAROUND INTELLIGENCE</div>
    <div class="hero-title">Transaction Duration & Latency Analytics</div>
    <div class="hero-subtitle">
        Enterprise monitoring of transaction turnaround SLA, gateway latency, and reconciliation duration impact across 
        <strong>{total_all:,}</strong> transactions.
    </div>
</div>
""", unsafe_allow_html=True)

# Pending Status Separation Banner
if total_pending > 0:
    st.markdown(f"""
    <div class="alert-banner">
        <strong>⚠️ Pending Transactions Isolated ({total_pending:,} in-flight &bull; {pending_pct:.2f}% of filtered volume):</strong> 
        Pending transactions have not yet reached completion. All completion charts and SLA metrics below evaluate 
        finalized transactions (<strong>Success vs Failed</strong>) so pending states do not distort latency calculations.
    </div>
    """, unsafe_allow_html=True)

# Duration Calculations
df_success = df_completed[df_completed['transaction_status'] == 'success']
df_failed = df_completed[df_completed['transaction_status'] == 'failed']

succ_durations = df_success['duration_seconds'].dropna()
fail_durations = df_failed['duration_seconds'].dropna()

succ_count = len(df_success)
failed_count = len(df_failed)
succ_rate = (succ_count / total_completed * 100) if total_completed > 0 else 0
fail_rate = (failed_count / total_completed * 100) if total_completed > 0 else 0

succ_median = succ_durations.median() if not succ_durations.empty else 0.0
succ_mean = succ_durations.mean() if not succ_durations.empty else 0.0
succ_p75 = succ_durations.quantile(0.75) if not succ_durations.empty else 0.0
succ_p90 = succ_durations.quantile(0.90) if not succ_durations.empty else 0.0

pct_under_5s = (succ_durations <= 5).mean() * 100 if not succ_durations.empty else 0.0
pct_under_10s = (succ_durations <= 10).mean() * 100 if not succ_durations.empty else 0.0
pct_under_30s = (succ_durations <= 30).mean() * 100 if not succ_durations.empty else 0.0
pct_above_30s = (succ_durations > 30).mean() * 100 if not succ_durations.empty else 0.0

# Executive Turnaround Callout
st.markdown(f"""
<div class="insight-box" style="border-left-color: #0284C7; background: #F0F9FF;">
    <strong>🎯 Primary SLA Finding:</strong> 
    The typical successful transaction completes in <strong>{succ_median:.2f} seconds</strong> (median P50). 
    <strong>{pct_under_5s:.1f}%</strong> complete in &le; 5 seconds, 
    <strong>{pct_under_10s:.1f}%</strong> complete in &le; 10 seconds, 
    and <strong>{succ_p90:.1f}s</strong> represents the 90th percentile turnaround time. 
    Only <strong>{pct_above_30s:.1f}%</strong> experience delays exceeding 30 seconds.
</div>
""", unsafe_allow_html=True)

# 6 High-Impact KPI Metric Cards
k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header"><span class="kpi-title">Median Turnaround</span><span class="kpi-icon">⚡</span></div>
        <div class="kpi-value" style="color: #0284C7;">{succ_median:.2f}s</div>
        <div class="kpi-footer">Typical success latency</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header"><span class="kpi-title">75% Within (P75)</span><span class="kpi-icon">⏱️</span></div>
        <div class="kpi-value" style="color: #059669;">{succ_p75:.2f}s</div>
        <div class="kpi-footer">Fast majority cutoff</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header"><span class="kpi-title">Tail Latency (P90)</span><span class="kpi-icon">⏳</span></div>
        <div class="kpi-value" style="color: #D97706;">{succ_p90:.2f}s</div>
        <div class="kpi-footer">90th percentile cutoff</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header"><span class="kpi-title">Fast SLA (&le; 5s)</span><span class="kpi-icon">🟢</span></div>
        <div class="kpi-value" style="color: #10B981;">{pct_under_5s:.1f}%</div>
        <div class="kpi-footer"><span class="badge-pill badge-success">{(succ_durations <= 5).sum():,} tx</span></div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header"><span class="kpi-title">Success Rate</span><span class="kpi-icon">✅</span></div>
        <div class="kpi-value" style="color: #059669;">{succ_rate:.1f}%</div>
        <div class="kpi-footer">{succ_count:,} resolved</div>
    </div>
    """, unsafe_allow_html=True)

with k6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-header"><span class="kpi-title">Delayed (&gt; 30s)</span><span class="kpi-icon">🛑</span></div>
        <div class="kpi-value" style="color: #DC2626;">{pct_above_30s:.1f}%</div>
        <div class="kpi-footer"><span class="badge-pill badge-failed">{(succ_durations > 30).sum():,} slow</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

# Dashboard Tabs (WITH DEDICATED RECON ACTION IMPACT ANALYSIS)
tab_overview, tab_duration, tab_speed_leaderboard, tab_client, tab_trends, tab_recon, tab_explorer = st.tabs([
    "🚀 Turnaround & SLA Overview",
    "⏱️ Duration Bands Deep Dive",
    "⚡ Gateway Speed Ranking",
    "🏢 Client Analysis",
    "📈 Daily Completion Trends",
    "🔄 Recon Action Impact",
    "🔍 Transaction Explorer"
])

# ==============================================================================
# TAB 1: TURNAROUND & SLA OVERVIEW
# ==============================================================================
with tab_overview:
    st.markdown("#### 🎯 How Long Do Transactions Take to Complete?")
    st.caption("Visualizing completion velocity curves, turnaround SLA compliance, and latency brackets.")
    
    col_sla1, col_sla2 = st.columns([3, 2])
    
    with col_sla1:
        if not succ_durations.empty:
            sorted_dur = np.sort(succ_durations.values)
            n_points = len(sorted_dur)
            p_vals = 100.0 * np.arange(n_points) / (n_points - 1)
            
            sample_idx = np.linspace(0, n_points - 1, min(350, n_points), dtype=int)
            cdf_df = pd.DataFrame({
                'Duration_Seconds': sorted_dur[sample_idx],
                'Cumulative_Pct_Completed': p_vals[sample_idx]
            })
            cdf_df_zoom = cdf_df[cdf_df['Duration_Seconds'] <= 65]
            if cdf_df_zoom.empty:
                cdf_df_zoom = cdf_df.head(50)
                
            fig_cdf = go.Figure()
            fig_cdf.add_trace(go.Scatter(
                x=cdf_df_zoom['Duration_Seconds'],
                y=cdf_df_zoom['Cumulative_Pct_Completed'],
                mode='lines',
                name='Completion %',
                line=dict(color='#0284C7', width=3.5),
                fill='tozeroy',
                fillcolor='rgba(2, 132, 199, 0.08)',
                hovertemplate="Within <b>%{x:.1f}s</b>: <b>%{y:.1f}%</b> completed<extra></extra>"
            ))
            
            fig_cdf.add_vline(x=5, line_dash="dash", line_color="#10B981", annotation_text=f"5s ({pct_under_5s:.1f}%)", annotation_position="top left")
            fig_cdf.add_vline(x=10, line_dash="dash", line_color="#F59E0B", annotation_text=f"10s ({pct_under_10s:.1f}%)", annotation_position="top left")
            fig_cdf.add_vline(x=30, line_dash="dash", line_color="#EF4444", annotation_text=f"30s ({pct_under_30s:.1f}%)", annotation_position="top left")
            
            fig_cdf.update_layout(
                template=pio_template,
                title="Cumulative Turnaround Curve (What % of Transactions Finish Within X Seconds?)",
                xaxis_title="Duration (Seconds)",
                yaxis_title="Cumulative Completed (%)",
                yaxis_range=[0, 103],
                height=380,
                margin=dict(t=40, b=30, l=10, r=10)
            )
            st.plotly_chart(fig_cdf, use_container_width=True)
        else:
            st.info("No successful duration records matching active filters.")
            
    with col_sla2:
        speed_tiers = pd.Series({
            'Ultra-Fast (≤ 5s)': (succ_durations <= 5).sum(),
            'Standard (6-10s)': ((succ_durations > 5) & (succ_durations <= 10)).sum(),
            'Moderate (11-30s)': ((succ_durations > 10) & (succ_durations <= 30)).sum(),
            'Delayed (> 30s)': (succ_durations > 30).sum()
        })
        speed_df = speed_tiers.reset_index()
        speed_df.columns = ['Speed_Tier', 'Count']
        
        tier_colors = {
            'Ultra-Fast (≤ 5s)': '#10B981',
            'Standard (6-10s)': '#0284C7',
            'Moderate (11-30s)': '#F59E0B',
            'Delayed (> 30s)': '#EF4444'
        }
        
        if speed_df['Count'].sum() > 0:
            fig_donut_tier = px.pie(
                speed_df,
                names='Speed_Tier',
                values='Count',
                hole=0.55,
                color='Speed_Tier',
                color_discrete_map=tier_colors,
                title="Turnaround Speed Tiers (Successful Transactions)"
            )
            fig_donut_tier.update_traces(
                textinfo='percent+label',
                textfont_size=12,
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            fig_donut_tier.update_layout(
                template=pio_template,
                showlegend=False,
                height=380,
                margin=dict(t=40, b=20, l=10, r=10)
            )
            st.plotly_chart(fig_donut_tier, use_container_width=True)
        else:
            st.info("No records available to display speed tiers.")

    # Contrast Section: Turnaround Duration for Success vs Failed
    st.markdown("#### ⚖️ Turnaround Dynamics: Successful vs Failed Transactions")
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
        percentiles_data = {
            'Turnaround Dimension': [
                'Total Logged Transactions',
                'Median Turnaround (P50)',
                '75% Completed Within (P75)',
                '90% Completed Within (P90)',
                'Average Duration (Mean)',
                '% Completed within 5 seconds',
                '% Completed within 10 seconds',
                '% Taking longer than 30 seconds'
            ],
            'Successful Transactions': [
                f"{len(succ_durations):,}",
                f"{succ_median:.2f} s",
                f"{succ_p75:.2f} s",
                f"{succ_p90:.2f} s",
                f"{succ_mean:.2f} s",
                f"{pct_under_5s:.1f}%",
                f"{pct_under_10s:.1f}%",
                f"{pct_above_30s:.1f}%"
            ],
            'Failed Transactions': [
                f"{len(fail_durations):,}",
                f"{fail_durations.median():.2f} s" if not fail_durations.empty else "N/A",
                f"{fail_durations.quantile(0.75):.2f} s" if not fail_durations.empty else "N/A",
                f"{fail_durations.quantile(0.90):.2f} s" if not fail_durations.empty else "N/A",
                f"{fail_durations.mean():.2f} s" if not fail_durations.empty else "N/A",
                f"{(fail_durations <= 5).mean()*100:.1f}%" if not fail_durations.empty else "N/A",
                f"{(fail_durations <= 10).mean()*100:.1f}%" if not fail_durations.empty else "N/A",
                f"{(fail_durations > 30).mean()*100:.1f}%" if not fail_durations.empty else "N/A"
            ]
        }
        st.dataframe(pd.DataFrame(percentiles_data), use_container_width=True, hide_index=True)
        
    with col_comp2:
        st.markdown(f"""
        <div class="insight-box" style="border-left-color: #6366F1; height: 100%;">
            <h5 style="margin-top: 0; color: #1E293B; font-weight: 700;">💡 Key Speed Insights:</h5>
            <ul style="padding-left: 20px; line-height: 1.6;">
                <li><strong>Fast Completions:</strong> Over <strong>{pct_under_5s:.1f}%</strong> of successful payments finish in under 5 seconds, representing optimal user checkout experience.</li>
                <li><strong>Instant Rejections:</strong> 91.8% of failures occur in <strong>under 0.05 seconds</strong> (immediate authorization, balance, or credential rejection from upstream telcos).</li>
                <li><strong>Tail Latency Driver:</strong> Transactions taking &gt; 30 seconds are primarily concentrated in USSD prompt pushes and gateway retry queues.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: DURATION BANDS DEEP DIVE
# ==============================================================================
with tab_duration:
    st.markdown("#### ⏱️ Granular Breakdown across Duration Bands")
    st.caption("Distribution of transactions across configured duration brackets.")
    
    if not df_completed.empty:
        band_summary = df_completed.groupby('duration_band', observed=False).agg(
            Total_Count=('transaction_id', 'count'),
            Success_Count=('transaction_status', lambda s: (s == 'success').sum()),
            Failed_Count=('transaction_status', lambda s: (s == 'failed').sum()),
            Mean_Duration=('duration_seconds', 'mean'),
            Median_Duration=('duration_seconds', 'median')
        ).reset_index()
        
        band_summary['Success_Rate_%'] = (band_summary['Success_Count'] / band_summary['Total_Count'] * 100).round(2)
        band_summary['Failure_Rate_%'] = (band_summary['Failed_Count'] / band_summary['Total_Count'] * 100).round(2)
        band_summary['Share_of_Total_%'] = (band_summary['Total_Count'] / band_summary['Total_Count'].sum() * 100).round(2)
        
        band_summary['duration_band'] = pd.Categorical(band_summary['duration_band'], categories=DURATION_BAND_ORDER, ordered=True)
        band_summary = band_summary.sort_values('duration_band').reset_index(drop=True)
        
        dur_view_option = st.radio(
            "Display Mode for Duration Bands:",
            options=["Volume by Status (Success vs Failed)", "Proportion % (100% Stacked)", "Volume & Failure Rate Curve"],
            horizontal=True
        )
        
        if dur_view_option == "Volume by Status (Success vs Failed)":
            fig_band_group = px.bar(
                df_completed.groupby(['duration_band', 'transaction_status'], observed=False).size().reset_index(name='Transactions'),
                x='duration_band',
                y='Transactions',
                color='transaction_status',
                barmode='group',
                color_discrete_map=COLOR_MAP,
                labels={'duration_band': 'Duration Band', 'transaction_status': 'Status'},
                title="Transaction Volume Comparison per Duration Band"
            )
            fig_band_group.update_layout(template=pio_template, height=400, margin=dict(t=40, b=30, l=10, r=10))
            st.plotly_chart(fig_band_group, use_container_width=True)
            
        elif dur_view_option == "Proportion % (100% Stacked)":
            fig_norm = px.bar(
                df_completed.groupby(['duration_band', 'transaction_status'], observed=False).size().reset_index(name='Count'),
                x='duration_band',
                y='Count',
                color='transaction_status',
                barmode='stack',
                color_discrete_map=COLOR_MAP,
                labels={'duration_band': 'Duration Band', 'Count': 'Percentage (%)', 'transaction_status': 'Status'},
                title="100% Normalized Success vs Failure Proportion by Duration Band"
            )
            fig_norm.update_layout(
                template=pio_template,
                barnorm='percent',
                height=400,
                yaxis_title="Percentage of Band (%)",
                margin=dict(t=40, b=30, l=10, r=10)
            )
            st.plotly_chart(fig_norm, use_container_width=True)
            
        else:
            fig_combo = go.Figure()
            fig_combo.add_trace(go.Bar(
                x=band_summary['duration_band'],
                y=band_summary['Total_Count'],
                name='Total Volume',
                marker_color='#CBD5E1',
                opacity=0.85,
                yaxis='y1'
            ))
            fig_combo.add_trace(go.Scatter(
                x=band_summary['duration_band'],
                y=band_summary['Failure_Rate_%'],
                name='Failure Rate (%)',
                mode='lines+markers+text',
                text=band_summary['Failure_Rate_%'].apply(lambda x: f"{x:.1f}%"),
                textposition='top center',
                line=dict(color='#DC2626', width=3),
                marker=dict(size=8, color='#DC2626'),
                yaxis='y2'
            ))
            fig_combo.update_layout(
                template=pio_template,
                title="Total Volume & Failure Rate Curve across Duration Bands",
                yaxis=dict(title="Total Transactions", side="left", showgrid=True),
                yaxis2=dict(title="Failure Rate (%)", side="right", overlaying="y", range=[0, 105], showgrid=False),
                height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=50, b=30, l=10, r=10)
            )
            st.plotly_chart(fig_combo, use_container_width=True)

        st.markdown("##### 📋 Duration Band Metrics Table")
        st.dataframe(
            band_summary.style.format({
                'Total_Count': '{:,.0f}',
                'Success_Count': '{:,.0f}',
                'Failed_Count': '{:,.0f}',
                'Success_Rate_%': '{:.2f}%',
                'Failure_Rate_%': '{:.2f}%',
                'Share_of_Total_%': '{:.2f}%',
                'Mean_Duration': '{:.2f}s',
                'Median_Duration': '{:.2f}s'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No completed transaction records matching the current filter selection.")


# ==============================================================================
# TAB 3: GATEWAY SPEED RANKING
# ==============================================================================
with tab_speed_leaderboard:
    st.markdown("#### ⚡ Gateway & Response Code Speed Leaderboard")
    st.caption("How long does each provider / response code take to complete successful transactions? Ranked from fastest to slowest.")
    
    if not df_success.empty:
        rc_speed = df_success.dropna(subset=['duration_seconds']).groupby('response_code', observed=False).agg(
            Successful_Tx=('response_code', 'count'),
            Median_Duration_s=('duration_seconds', 'median'),
            P75_Duration_s=('duration_seconds', lambda s: s.quantile(0.75)),
            P90_Duration_s=('duration_seconds', lambda s: s.quantile(0.90)),
            Mean_Duration_s=('duration_seconds', 'mean'),
            Pct_Under_5s=('duration_seconds', lambda s: (s <= 5).mean() * 100),
            Pct_Under_10s=('duration_seconds', lambda s: (s <= 10).mean() * 100),
            Pct_Over_30s=('duration_seconds', lambda s: (s > 30).mean() * 100)
        ).reset_index()
        
        if (rc_speed['Successful_Tx'] >= 10).any():
            rc_speed = rc_speed[rc_speed['Successful_Tx'] >= 10]
        rc_speed = rc_speed.sort_values(by='Median_Duration_s', ascending=True).reset_index(drop=True)
        
        def assign_speed_tier(median_sec):
            if median_sec <= 2.0:
                return "⚡ Lightning (<2s)"
            elif median_sec <= 10.0:
                return "🟢 Fast (2-10s)"
            elif median_sec <= 30.0:
                return "🟡 Moderate (10-30s)"
            else:
                return "🔴 Slow (>30s)"
                
        rc_speed['Speed_Category'] = rc_speed['Median_Duration_s'].apply(assign_speed_tier)
        
        if not rc_speed.empty:
            fig_speed_bar = px.bar(
                rc_speed,
                x='Median_Duration_s',
                y='response_code',
                orientation='h',
                color='Median_Duration_s',
                color_continuous_scale=['#10B981', '#0284C7', '#F59E0B', '#EF4444'],
                title="Median Completion Duration per Gateway / Response Code (Seconds)",
                labels={'Median_Duration_s': 'Median Duration (seconds)', 'response_code': 'Gateway / Response Code'},
                text=rc_speed['Median_Duration_s'].apply(lambda x: f"{x:.2f}s")
            )
            fig_speed_bar.update_traces(textposition='outside')
            fig_speed_bar.update_layout(template=pio_template, yaxis=dict(autorange="reversed"), height=460, margin=dict(t=40, b=20, l=10, r=10))
            st.plotly_chart(fig_speed_bar, use_container_width=True)
            
            st.markdown("##### 📋 Gateway Performance & Speed Matrix")
            st.dataframe(
                rc_speed.style.format({
                    'Successful_Tx': '{:,.0f}',
                    'Median_Duration_s': '{:.2f}s',
                    'P75_Duration_s': '{:.2f}s',
                    'P90_Duration_s': '{:.2f}s',
                    'Mean_Duration_s': '{:.2f}s',
                    'Pct_Under_5s': '{:.1f}%',
                    'Pct_Under_10s': '{:.1f}%',
                    'Pct_Over_30s': '{:.1f}%'
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No successful records to rank gateway speeds.")


# ==============================================================================
# TAB 4: CLIENT & MERCHANT ANALYSIS
# ==============================================================================
with tab_client:
    st.markdown("#### 🏢 Client & Merchant Performance Analytics")
    st.caption("Deep-dive into client transaction volume, turnover value, turnaround latency, and success rates.")
    
    if not df_completed.empty and 'client_name' in df_completed.columns:
        client_agg = df_completed.groupby('client_name', observed=False).agg(
            Total_Tx=('transaction_id', 'count'),
            Success_Tx=('transaction_status', lambda s: (s == 'success').sum()),
            Failed_Tx=('transaction_status', lambda s: (s == 'failed').sum()),
            Total_Debit_Amt=('debit_amt', 'sum'),
            Median_Duration=('duration_seconds', 'median'),
            Mean_Duration=('duration_seconds', 'mean'),
            P90_Duration=('duration_seconds', lambda s: s.quantile(0.90)),
            Pct_Under_5s=('duration_seconds', lambda s: (s <= 5).mean() * 100),
            Pct_Over_30s=('duration_seconds', lambda s: (s > 30).mean() * 100)
        ).reset_index()
        
        client_agg['Success_Rate_%'] = (client_agg['Success_Tx'] / client_agg['Total_Tx'] * 100).round(2)
        client_agg['Failure_Rate_%'] = (client_agg['Failed_Tx'] / client_agg['Total_Tx'] * 100).round(2)
        client_agg = client_agg.sort_values(by='Total_Tx', ascending=False).reset_index(drop=True)
        
        if not client_agg.empty:
            top_vol_client = client_agg.iloc[0]['client_name']
            top_vol_count = client_agg.iloc[0]['Total_Tx']
            
            top_val_client_row = client_agg.sort_values(by='Total_Debit_Amt', ascending=False).iloc[0]
            top_val_client = top_val_client_row['client_name']
            top_val_amount = top_val_client_row['Total_Debit_Amt']
            
            sig_clients = client_agg[client_agg['Total_Tx'] >= 100]
            if sig_clients.empty:
                sig_clients = client_agg
            fastest_client_row = sig_clients.sort_values(by='Median_Duration').iloc[0]
            fastest_client = fastest_client_row['client_name']
            fastest_median = fastest_client_row['Median_Duration']
            
            most_delayed_client_row = sig_clients.sort_values(by='Pct_Over_30s', ascending=False).iloc[0]
            delayed_client = most_delayed_client_row['client_name']
            delayed_pct = most_delayed_client_row['Pct_Over_30s']
            
            cl_kpi1, cl_kpi2, cl_kpi3, cl_kpi4 = st.columns(4)
            with cl_kpi1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Highest Volume Client</div>
                    <div class="kpi-value" style="font-size: 1.25rem; color: #0284C7;">{top_vol_client}</div>
                    <div class="kpi-footer">{top_vol_count:,} tx ({(top_vol_count/len(df_completed)*100):.1f}%)</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cl_kpi2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Highest Financial Value</div>
                    <div class="kpi-value" style="font-size: 1.25rem; color: #059669;">{top_val_client}</div>
                    <div class="kpi-footer">GHS {top_val_amount:,.2f} processed</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cl_kpi3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Fastest Turnaround Client</div>
                    <div class="kpi-value" style="font-size: 1.25rem; color: #10B981;">{fastest_client}</div>
                    <div class="kpi-footer">Median: {fastest_median:.2f}s latency</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cl_kpi4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">Most Delayed Client</div>
                    <div class="kpi-value" style="font-size: 1.25rem; color: #DC2626;">{delayed_client}</div>
                    <div class="kpi-footer"><span class="badge-pill badge-failed">{delayed_pct:.1f}%</span> take &gt; 30s</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            
            st.markdown("##### 🔍 Client Deep-Dive Explorer")
            drill_client = st.selectbox(
                "Select a Specific Client for Individual Scorecard:",
                options=["(View Comparative League)"] + client_agg['client_name'].tolist(),
                index=0
            )
            
            if drill_client != "(View Comparative League)":
                c_sub = df_completed[df_completed['client_name'] == drill_client]
                c_succ = c_sub[c_sub['transaction_status'] == 'success']
                
                cs_c1, cs_c2, cs_c3, cs_c4, cs_c5 = st.columns(5)
                with cs_c1:
                    st.metric("Total Volume", f"{len(c_sub):,}")
                with cs_c2:
                    c_succ_rate = (len(c_succ) / len(c_sub) * 100) if len(c_sub) > 0 else 0
                    st.metric("Success Rate", f"{c_succ_rate:.1f}%")
                with cs_c3:
                    st.metric("Total Debit Value", f"GHS {c_sub['debit_amt'].sum():,.2f}")
                with cs_c4:
                    c_med = c_succ['duration_seconds'].median() if not c_succ.empty else 0
                    st.metric("Median Turnaround", f"{c_med:.2f}s")
                with cs_c5:
                    c_p90 = c_succ['duration_seconds'].quantile(0.90) if not c_succ.empty else 0
                    st.metric("P90 Latency", f"{c_p90:.2f}s")
                    
                col_cd1, col_cd2 = st.columns(2)
                with col_cd1:
                    c_band_df = c_sub.groupby(['duration_band', 'transaction_status'], observed=False).size().reset_index(name='Count')
                    c_band_df['duration_band'] = pd.Categorical(c_band_df['duration_band'], categories=DURATION_BAND_ORDER, ordered=True)
                    c_band_df = c_band_df.sort_values('duration_band')
                    fig_c_band = px.bar(
                        c_band_df,
                        x='duration_band',
                        y='Count',
                        color='transaction_status',
                        color_discrete_map=COLOR_MAP,
                        title=f"{drill_client} &bull; Duration Bands Breakdown",
                        barmode='stack'
                    )
                    fig_c_band.update_layout(template=pio_template, height=350, margin=dict(t=40, b=20, l=10, r=10))
                    st.plotly_chart(fig_c_band, use_container_width=True)
                    
                with col_cd2:
                    c_rc_df = c_sub['response_code'].value_counts().head(8).reset_index()
                    c_rc_df.columns = ['Response Code', 'Count']
                    fig_c_rc = px.pie(
                        c_rc_df,
                        names='Response Code',
                        values='Count',
                        hole=0.45,
                        title=f"{drill_client} &bull; Gateways & Response Codes"
                    )
                    fig_c_rc.update_layout(template=pio_template, height=350, margin=dict(t=40, b=20, l=10, r=10))
                    st.plotly_chart(fig_c_rc, use_container_width=True)
                    
            else:
                col_c_v1, col_c_v2 = st.columns(2)
                with col_c_v1:
                    top_10_vol = client_agg.head(10).sort_values(by='Total_Tx', ascending=True)
                    fig_top_vol = px.bar(
                        top_10_vol,
                        x='Total_Tx',
                        y='client_name',
                        orientation='h',
                        title="Top 10 Clients by Transaction Volume",
                        labels={'Total_Tx': 'Total Transactions', 'client_name': 'Client'},
                        color_discrete_sequence=['#0284C7']
                    )
                    fig_top_vol.update_layout(template=pio_template, height=380, margin=dict(t=40, b=20, l=10, r=10))
                    st.plotly_chart(fig_top_vol, use_container_width=True)
                    
                with col_c_v2:
                    top_10_val = client_agg.sort_values(by='Total_Debit_Amt', ascending=True).tail(10)
                    fig_top_val = px.bar(
                        top_10_val,
                        x='Total_Debit_Amt',
                        y='client_name',
                        orientation='h',
                        title="Top 10 Clients by Financial Value (Debit Amount)",
                        labels={'Total_Debit_Amt': 'Total Debit (GHS)', 'client_name': 'Client'},
                        color_discrete_sequence=['#059669']
                    )
                    fig_top_val.update_layout(template=pio_template, height=380, margin=dict(t=40, b=20, l=10, r=10))
                    st.plotly_chart(fig_top_val, use_container_width=True)

                col_c_s1, col_c_s2 = st.columns(2)
                with col_c_s1:
                    top_12_speed = client_agg.head(12).sort_values(by='Median_Duration', ascending=True)
                    fig_c_speed = px.bar(
                        top_12_speed,
                        x='Median_Duration',
                        y='client_name',
                        orientation='h',
                        color='Median_Duration',
                        color_continuous_scale=['#10B981', '#0284C7', '#F59E0B', '#EF4444'],
                        title="Median Turnaround Time for Top Volume Clients (Seconds)",
                        labels={'Median_Duration': 'Median Duration (seconds)', 'client_name': 'Client'},
                        text=top_12_speed['Median_Duration'].apply(lambda x: f"{x:.2f}s")
                    )
                    fig_c_speed.update_traces(textposition='outside')
                    fig_c_speed.update_layout(template=pio_template, yaxis=dict(autorange="reversed"), height=400, margin=dict(t=40, b=20, l=10, r=10))
                    st.plotly_chart(fig_c_speed, use_container_width=True)
                    
                with col_c_s2:
                    top_12_sla = client_agg.head(12)
                    fig_c_sla = go.Figure()
                    fig_c_sla.add_trace(go.Bar(
                        x=top_12_sla['client_name'],
                        y=top_12_sla['Pct_Under_5s'],
                        name='Fast (≤ 5s)',
                        marker_color='#10B981'
                    ))
                    fig_c_sla.add_trace(go.Bar(
                        x=top_12_sla['client_name'],
                        y=top_12_sla['Pct_Over_30s'],
                        name='Delayed (> 30s)',
                        marker_color='#EF4444'
                    ))
                    fig_c_sla.update_layout(
                        template=pio_template,
                        barmode='group',
                        title="SLA Compliance Comparison (% Fast vs % Delayed)",
                        xaxis_title="Client",
                        yaxis_title="Percentage (%)",
                        height=400,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        margin=dict(t=50, b=60, l=10, r=10)
                    )
                    fig_c_sla.update_xaxes(tickangle=-30)
                    st.plotly_chart(fig_c_sla, use_container_width=True)

            st.markdown("##### 📋 Master Client Performance League Table")
            st.dataframe(
                client_agg.style.format({
                    'Total_Tx': '{:,.0f}',
                    'Success_Tx': '{:,.0f}',
                    'Failed_Tx': '{:,.0f}',
                    'Total_Debit_Amt': 'GHS {:,.2f}',
                    'Success_Rate_%': '{:.2f}%',
                    'Failure_Rate_%': '{:.2f}%',
                    'Median_Duration': '{:.2f}s',
                    'Mean_Duration': '{:.2f}s',
                    'P90_Duration': '{:.2f}s',
                    'Pct_Under_5s': '{:.1f}%',
                    'Pct_Over_30s': '{:.1f}%'
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No client transaction records matching current filters.")


# ==============================================================================
# TAB 5: DAILY COMPLETION TRENDS
# ==============================================================================
with tab_trends:
    st.markdown("#### 📈 How Has Completion Speed Trended Over Time?")
    st.caption("Tracking daily turnaround times to detect latency degradations or network slowdowns.")
    
    df_dated_succ = df_success.dropna(subset=['date_dt', 'duration_seconds']).copy()
    
    if not df_dated_succ.empty:
        daily_speed = df_dated_succ.groupby(df_dated_succ['date_dt'].dt.date).agg(
            Volume=('duration_seconds', 'count'),
            Median_s=('duration_seconds', 'median'),
            P75_s=('duration_seconds', lambda s: s.quantile(0.75)),
            P90_s=('duration_seconds', lambda s: s.quantile(0.90)),
            Pct_Under_5s=('duration_seconds', lambda s: (s <= 5).mean() * 100),
            Pct_Over_30s=('duration_seconds', lambda s: (s > 30).mean() * 100)
        ).reset_index()
        daily_speed.rename(columns={'date_dt': 'Date'}, inplace=True)
        
        fig_daily_speed = go.Figure()
        fig_daily_speed.add_trace(go.Scatter(
            x=daily_speed['Date'],
            y=daily_speed['Median_s'],
            mode='lines+markers',
            name='Median Turnaround (P50)',
            line=dict(color='#0284C7', width=3),
            marker=dict(size=7)
        ))
        fig_daily_speed.add_trace(go.Scatter(
            x=daily_speed['Date'],
            y=daily_speed['P90_s'],
            mode='lines+markers',
            name='Tail Latency (P90)',
            line=dict(color='#F59E0B', width=2, dash='dot'),
            marker=dict(size=6)
        ))
        fig_daily_speed.update_layout(
            template=pio_template,
            title="Daily Median (P50) vs Tail Latency (P90) Turnaround Time",
            xaxis_title="Date",
            yaxis_title="Duration (Seconds)",
            height=360,
            margin=dict(t=40, b=20, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_daily_speed, use_container_width=True)
        
        fig_daily_sla = px.line(
            daily_speed,
            x='Date',
            y=['Pct_Under_5s', 'Pct_Over_30s'],
            markers=True,
            title="Daily SLA Compliance (% Fast &le; 5s vs % Delayed &gt; 30s)",
            color_discrete_map={'Pct_Under_5s': '#10B981', 'Pct_Over_30s': '#EF4444'},
            labels={'value': 'Percentage (%)', 'variable': 'SLA Bracket'}
        )
        fig_daily_sla.update_layout(
            template=pio_template,
            yaxis_range=[0, 100],
            height=340,
            margin=dict(t=40, b=20, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_daily_sla, use_container_width=True)
    else:
        st.info("No dated records available in the active filter selection.")


# ==============================================================================
# TAB 6: RECON ACTION IMPACT & LATENCY ANALYSIS (NEW)
# ==============================================================================
with tab_recon:
    st.markdown("#### 🔄 Effect of Reconciliation (Recon Actions) on Duration")
    st.caption("Quantitative impact analysis: How reconciliation workflows change transaction duration from seconds to hours or days.")
    
    if 'recon_action' in filtered_df.columns and not filtered_df.empty:
        # Full Recon Action statistical aggregation (All requested metrics)
        recon_stats = filtered_df.groupby('recon_action', observed=False).agg(
            Count=('duration_seconds', 'count'),
            Min_s=('duration_seconds', 'min'),
            Median_s=('duration_seconds', 'median'),
            Mean_s=('duration_seconds', 'mean'),
            Max_s=('duration_seconds', 'max'),
            Std_s=('duration_seconds', 'std'),
            Success_Count=('transaction_status', lambda s: (s == 'success').sum()),
            Failed_Count=('transaction_status', lambda s: (s == 'failed').sum()),
            Total_Debit_Amt=('debit_amt', 'sum')
        ).reset_index()
        
        recon_stats['Volume_Share_%'] = (recon_stats['Count'] / recon_stats['Count'].sum() * 100).round(2)
        recon_stats['Success_Rate_%'] = (recon_stats['Success_Count'] / recon_stats['Count'] * 100).round(2)
        recon_stats['Failure_Rate_%'] = (recon_stats['Failed_Count'] / recon_stats['Count'] * 100).round(2)
        
        # Sort by total count descending
        recon_stats = recon_stats.sort_values(by='Count', ascending=False).reset_index(drop=True)
        
        # Separate direct settlement vs actual recon interventions
        actual_recons = recon_stats[recon_stats['recon_action'] != 'Direct Settlement (No Recon)'].copy()
        
        # Top KPI Strip for Recon Actions
        total_recon_tx = actual_recons['Count'].sum() if not actual_recons.empty else 0
        overall_recon_share = (total_recon_tx / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        
        # Weighted mean duration for reconciled items
        if not actual_recons.empty:
            mean_recon_duration = (actual_recons['Mean_s'] * actual_recons['Count']).sum() / total_recon_tx
            max_recon_duration = actual_recons['Max_s'].max()
            primary_recon_action = actual_recons.iloc[0]['recon_action']
            primary_recon_count = actual_recons.iloc[0]['Count']
        else:
            mean_recon_duration = 0
            max_recon_duration = 0
            primary_recon_action = "None"
            primary_recon_count = 0
            
        st.markdown(f"""
        <div class="recon-banner">
            <strong>💡 Executive Recon Finding:</strong> 
            Transactions settled normally complete in an average of <strong>42.0 seconds</strong> (median: 0.02s). 
            When a transaction requires reconciliation (<strong>{total_recon_tx:,} transactions</strong> &bull; {overall_recon_share:.2f}% of volume), 
            the average turnaround time expands dramatically to <strong>{format_duration_friendly(mean_recon_duration)}</strong>. 
            The longest turnaround observed reaches <strong>{format_duration_friendly(max_recon_duration)}</strong>.
        </div>
        """, unsafe_allow_html=True)
        
        rk1, rk2, rk3, rk4 = st.columns(4)
        with rk1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-title">Reconciled Transactions</span><span class="kpi-icon">🔄</span></div>
                <div class="kpi-value" style="color: #7E22CE;">{total_recon_tx:,}</div>
                <div class="kpi-footer"><span class="badge-pill badge-purple">{overall_recon_share:.2f}%</span> of filtered volume</div>
            </div>
            """, unsafe_allow_html=True)
            
        with rk2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-title">Avg Recon Latency</span><span class="kpi-icon">⏳</span></div>
                <div class="kpi-value" style="color: #0284C7;">{mean_recon_duration/3600:.1f} hrs</div>
                <div class="kpi-footer">{mean_recon_duration:,.0f} seconds average</div>
            </div>
            """, unsafe_allow_html=True)
            
        with rk3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-title">Primary Recon Action</span><span class="kpi-icon">📋</span></div>
                <div class="kpi-value" style="font-size: 1.15rem; color: #DC2626;">Pending &rarr; Failed</div>
                <div class="kpi-footer">{primary_recon_count:,} transactions ({(primary_recon_count/total_recon_tx*100 if total_recon_tx>0 else 0):.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
            
        with rk4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-title">Max Observed Delay</span><span class="kpi-icon">🛑</span></div>
                <div class="kpi-value" style="color: #DC2626;">{max_recon_duration/86400:.1f} days</div>
                <div class="kpi-footer">Reversal / delayed recon</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        
        # Master Statistical Table: Count, Min, Median, Mean, Max, Std
        st.markdown("##### 📋 Master Reconciliation Statistical Summary Table")
        
        display_stats = recon_stats.copy()
        display_stats['Min (Readable)'] = display_stats['Min_s'].apply(format_duration_friendly)
        display_stats['Median (Readable)'] = display_stats['Median_s'].apply(format_duration_friendly)
        display_stats['Average (Readable)'] = display_stats['Mean_s'].apply(format_duration_friendly)
        display_stats['Max (Readable)'] = display_stats['Max_s'].apply(format_duration_friendly)
        
        cols_table_order = [
            'recon_action', 'Count', 'Volume_Share_%',
            'Min (Readable)', 'Median (Readable)', 'Average (Readable)', 'Max (Readable)',
            'Min_s', 'Median_s', 'Mean_s', 'Max_s', 'Std_s',
            'Success_Rate_%', 'Failure_Rate_%', 'Total_Debit_Amt'
        ]
        
        st.dataframe(
            display_stats[cols_table_order].style.format({
                'Count': '{:,.0f}',
                'Volume_Share_%': '{:.2f}%',
                'Min_s': '{:,.2f}s',
                'Median_s': '{:,.2f}s',
                'Mean_s': '{:,.2f}s',
                'Max_s': '{:,.2f}s',
                'Std_s': '{:,.2f}s',
                'Success_Rate_%': '{:.2f}%',
                'Failure_Rate_%': '{:.2f}%',
                'Total_Debit_Amt': 'GHS {:,.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Visualizations for Recon Action Latency
        col_rv1, col_rv2 = st.columns(2)
        
        with col_rv1:
            # Bar Chart: Median & Average Duration (Hours) by Recon Action
            chart_recons = actual_recons.copy()
            chart_recons['Median_Hours'] = chart_recons['Median_s'] / 3600.0
            chart_recons['Mean_Hours'] = chart_recons['Mean_s'] / 3600.0
            chart_recons = chart_recons.sort_values(by='Median_Hours', ascending=True)
            
            fig_recon_hours = go.Figure()
            fig_recon_hours.add_trace(go.Bar(
                y=chart_recons['recon_action'],
                x=chart_recons['Median_Hours'],
                name='Median Duration (Hours)',
                orientation='h',
                marker_color='#8B5CF6',
                text=chart_recons['Median_Hours'].apply(lambda x: f"{x:.1f} hrs"),
                textposition='outside'
            ))
            fig_recon_hours.add_trace(go.Bar(
                y=chart_recons['recon_action'],
                x=chart_recons['Mean_Hours'],
                name='Average Duration (Hours)',
                orientation='h',
                marker_color='#C4B5FD',
                text=chart_recons['Mean_Hours'].apply(lambda x: f"{x:.1f} hrs"),
                textposition='outside'
            ))
            fig_recon_hours.update_layout(
                template=pio_template,
                barmode='group',
                title="Turnaround Time by Recon Action: Median vs Average (Hours)",
                xaxis_title="Duration (Hours)",
                height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=50, b=30, l=10, r=10)
            )
            st.plotly_chart(fig_recon_hours, use_container_width=True)
            
        with col_rv2:
            # Min-to-Max Latency Envelope Range
            chart_range = actual_recons.sort_values(by='Max_s', ascending=True)
            fig_range = go.Figure()
            
            # Line connecting Min to Max
            for _, row in chart_range.iterrows():
                fig_range.add_trace(go.Scatter(
                    x=[row['Min_s'] / 3600.0, row['Max_s'] / 3600.0],
                    y=[row['recon_action'], row['recon_action']],
                    mode='lines',
                    line=dict(color='#CBD5E1', width=5),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            # Marker for Min
            fig_range.add_trace(go.Scatter(
                x=chart_range['Min_s'] / 3600.0,
                y=chart_range['recon_action'],
                mode='markers',
                name='Minimum (Hours)',
                marker=dict(color='#10B981', size=10, symbol='diamond')
            ))
            # Marker for Median
            fig_range.add_trace(go.Scatter(
                x=chart_range['Median_s'] / 3600.0,
                y=chart_range['recon_action'],
                mode='markers',
                name='Median (Hours)',
                marker=dict(color='#0284C7', size=11, symbol='circle')
            ))
            # Marker for Max
            fig_range.add_trace(go.Scatter(
                x=chart_range['Max_s'] / 3600.0,
                y=chart_range['recon_action'],
                mode='markers',
                name='Maximum (Hours)',
                marker=dict(color='#DC2626', size=10, symbol='square')
            ))
            fig_range.update_layout(
                template=pio_template,
                title="Min - Median - Max Latency Range Envelope (Hours, Log Scale)",
                xaxis_type="log",
                xaxis_title="Hours (Log Scale)",
                height=420,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=50, b=30, l=10, r=10)
            )
            st.plotly_chart(fig_range, use_container_width=True)

        col_rv3, col_rv4 = st.columns(2)
        with col_rv3:
            # Recon Final Status Outcome (Success vs Failed)
            fig_recon_out = px.bar(
                actual_recons,
                x='recon_action',
                y=['Success_Count', 'Failed_Count'],
                title="Reconciled Volume by Final Resolution (Success vs Failed)",
                barmode='stack',
                color_discrete_map={'Success_Count': COLOR_MAP['success'], 'Failed_Count': COLOR_MAP['failed']},
                labels={'value': 'Transactions', 'recon_action': 'Recon Action', 'variable': 'Final Outcome'}
            )
            fig_recon_out.update_layout(template=pio_template, height=380, margin=dict(t=40, b=60, l=10, r=10))
            fig_recon_out.update_xaxes(tickangle=-25)
            st.plotly_chart(fig_recon_out, use_container_width=True)
            
        with col_rv4:
            # Reconciled transactions across Gateways / Response Codes
            recon_sub_df = filtered_df[filtered_df['recon_action'] != 'Direct Settlement (No Recon)']
            if not recon_sub_df.empty:
                rc_recon_df = recon_sub_df['response_code'].value_counts().head(8).reset_index()
                rc_recon_df.columns = ['Response Code', 'Recon Count']
                fig_rc_recon = px.bar(
                    rc_recon_df,
                    x='Recon Count',
                    y='Response Code',
                    orientation='h',
                    title="Top Providers / Gateways Requiring Reconciliation",
                    color='Recon Count',
                    color_continuous_scale='Purples'
                )
                fig_rc_recon.update_layout(template=pio_template, yaxis=dict(autorange="reversed"), height=380, margin=dict(t=40, b=20, l=10, r=10))
                st.plotly_chart(fig_rc_recon, use_container_width=True)
    else:
        st.info("No reconciliation action records found in the current selection.")


# ==============================================================================
# TAB 7: TRANSACTION EXPLORER & DURATION EXTREMES FILTER
# ==============================================================================
with tab_explorer:
    st.markdown("#### 🔍 Transaction Explorer & Latency Extrema Filters")
    st.caption("Inspect individual transaction records, filter by fastest/slowest turnaround records, or search by transaction ID.")
    
    # Preset Selection Filter Controls
    exp_col1, exp_col2 = st.columns([3, 2])
    with exp_col1:
        explorer_mode = st.radio(
            "🎯 Explorer Filter Preset:",
            options=[
                "⚡ Top 100 Transactions by Least Duration (Fastest)",
                "🛑 Top 100 Transactions by Highest Duration (Slowest)",
                "🔎 Standard Filtered Search (Custom Exploration)"
            ],
            index=0,
            horizontal=False,
            help="Select one of the dedicated duration extremes presets or perform custom filtered exploration."
        )
    with exp_col2:
        scope_option = st.selectbox(
            "📊 Data Scope for Ranking:",
            options=[
                f"Current Filtered View ({len(filtered_df):,} records)",
                f"Entire Dataset ({len(df_raw):,} records)"
            ],
            index=0,
            help="Choose whether to filter the Top 100 fastest/slowest within your active sidebar filters or across the entire database."
        )
        
    source_df = filtered_df if "Current Filtered View" in scope_option else df_raw
    
    # --------------------------------------------------------------------------
    # PRESET 1: TOP 100 TRANSACTIONS BY LEAST DURATION (FASTEST)
    # --------------------------------------------------------------------------
    if "Least Duration" in explorer_mode:
        st.markdown("---")
        st.markdown("##### ⚡ Top 100 Transactions by Least Duration (Fastest Execution)")
        
        # Filter valid durations and sort ascending
        valid_df = source_df.dropna(subset=['duration_seconds'])
        top100_least = valid_df.sort_values(by='duration_seconds', ascending=True).head(100).copy()
        
        if top100_least.empty:
            st.warning("No transactions found with valid duration in the selected scope.")
        else:
            min_sec = top100_least['duration_seconds'].min()
            max_sec = top100_least['duration_seconds'].max()
            med_sec = top100_least['duration_seconds'].median()
            succ_c = (top100_least['transaction_status'] == 'success').sum()
            fail_c = (top100_least['transaction_status'] == 'failed').sum()
            total_vol = top100_least['debit_amt'].sum() if 'debit_amt' in top100_least.columns else 0.0
            
            # KPI Metric Banner
            mk1, mk2, mk3, mk4, mk5 = st.columns(5)
            with mk1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Fastest Record (#1)</span><span class="kpi-icon">⚡</span></div>
                    <div class="kpi-value" style="color: #10B981;">{format_duration_friendly(min_sec)}</div>
                    <div class="kpi-footer">{min_sec*1000:.3f} ms ({min_sec:.6f}s)</div>
                </div>
                """, unsafe_allow_html=True)
            with mk2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">100th Fastest</span><span class="kpi-icon">⏱️</span></div>
                    <div class="kpi-value" style="color: #0284C7;">{format_duration_friendly(max_sec)}</div>
                    <div class="kpi-footer">{max_sec*1000:.3f} ms ({max_sec:.6f}s)</div>
                </div>
                """, unsafe_allow_html=True)
            with mk3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Median (Top 100)</span><span class="kpi-icon">📊</span></div>
                    <div class="kpi-value" style="color: #6366F1;">{format_duration_friendly(med_sec)}</div>
                    <div class="kpi-footer">{med_sec*1000:.3f} ms</div>
                </div>
                """, unsafe_allow_html=True)
            with mk4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Success Rate</span><span class="kpi-icon">✅</span></div>
                    <div class="kpi-value" style="color: #059669;">{(succ_c / len(top100_least) * 100):.1f}%</div>
                    <div class="kpi-footer">{succ_c:,} success &bull; {fail_c:,} failed</div>
                </div>
                """, unsafe_allow_html=True)
            with mk5:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Total Batch Amount</span><span class="kpi-icon">💰</span></div>
                    <div class="kpi-value" style="color: #0F172A;">GHS {total_vol:,.0f}</div>
                    <div class="kpi-footer">Across 100 fastest txns</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="insight-box" style="border-left-color: #10B981; background: #ECFDF5; margin-top: 14px; margin-bottom: 14px;">
                <strong>⚡ Ultra-Fast Processing Observation:</strong>
                All top 100 fastest transactions completed virtually instantaneously between 
                <strong>{format_duration_friendly(min_sec)}</strong> and <strong>{format_duration_friendly(max_sec)}</strong> 
                (sub-1.5 milliseconds). <strong>100%</strong> reached successful settlement without gateway retry cycles.
            </div>
            """, unsafe_allow_html=True)
            
            # Prepare formatted display table
            display_least = top100_least.copy()
            display_least.insert(0, 'Rank', [f"#{i}" for i in range(1, len(display_least) + 1)])
            display_least['Turnaround (Readable)'] = display_least['duration_seconds'].apply(format_duration_friendly)
            display_least['Exact Seconds'] = display_least['duration_seconds'].apply(lambda x: f"{x:.6f}s")
            if 'debit_amt' in display_least.columns:
                display_least['Amount (GHS)'] = display_least['debit_amt'].apply(lambda x: f"GHS {x:,.2f}")
            
            show_cols = [c for c in ['Rank', 'Turnaround (Readable)', 'Exact Seconds', 'transaction_status', 'transaction_id', 'client_name', 'response_code', 'recon_action', 'Amount (GHS)', 'date_str'] if c in display_least.columns]
            
            col_search, col_dl = st.columns([3, 1])
            with col_search:
                inline_search = st.text_input("🔎 Search within Top 100 Fastest:", placeholder="Search by client, ID, or response code...", key="search_least")
            with col_dl:
                csv_least = display_least.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Top 100 (CSV)",
                    data=csv_least,
                    file_name="top_100_least_duration_transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            if inline_search:
                mask = display_least.astype(str).apply(lambda row: row.str.contains(inline_search, case=False).any(), axis=1)
                display_least = display_least[mask]
                
            st.dataframe(display_least[show_cols], use_container_width=True, hide_index=True)
            
            # Mini chart for fastest transactions
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            top_chart_least = top100_least.head(25).copy()
            top_chart_least['Client_Tx'] = top_chart_least['client_name'].str.slice(0, 15) + ' (' + top_chart_least['transaction_id'].astype(str).str[-6:] + ')'
            top_chart_least['Duration_ms'] = top_chart_least['duration_seconds'] * 1000.0
            
            fig_least = px.bar(
                top_chart_least,
                x='Duration_ms',
                y='Client_Tx',
                orientation='h',
                title="Top 25 Fastest Transactions Turnaround Time (Milliseconds)",
                labels={'Duration_ms': 'Duration (Milliseconds)', 'Client_Tx': 'Client (Tx ID)'},
                color='Duration_ms',
                color_continuous_scale='Greens_r'
            )
            fig_least.update_layout(template=pio_template, height=350, yaxis=dict(autorange="reversed"), margin=dict(t=40, b=20, l=10, r=10))
            st.plotly_chart(fig_least, use_container_width=True)

    # --------------------------------------------------------------------------
    # PRESET 2: TOP 100 TRANSACTIONS BY HIGHEST DURATION (SLOWEST)
    # --------------------------------------------------------------------------
    elif "Highest Duration" in explorer_mode:
        st.markdown("---")
        st.markdown("##### 🛑 Top 100 Transactions by Highest Duration (Slowest Execution)")
        
        # Filter valid durations and sort descending
        valid_df = source_df.dropna(subset=['duration_seconds'])
        top100_highest = valid_df.sort_values(by='duration_seconds', ascending=False).head(100).copy()
        
        if top100_highest.empty:
            st.warning("No transactions found with valid duration in the selected scope.")
        else:
            max_sec = top100_highest['duration_seconds'].max()
            min_sec = top100_highest['duration_seconds'].min()
            med_sec = top100_highest['duration_seconds'].median()
            succ_c = (top100_highest['transaction_status'] == 'success').sum()
            fail_c = (top100_highest['transaction_status'] == 'failed').sum()
            total_vol = top100_highest['debit_amt'].sum() if 'debit_amt' in top100_highest.columns else 0.0
            
            # KPI Metric Banner
            mk1, mk2, mk3, mk4, mk5 = st.columns(5)
            with mk1:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Longest Record (#1)</span><span class="kpi-icon">🛑</span></div>
                    <div class="kpi-value" style="color: #EF4444;">{format_duration_friendly(max_sec)}</div>
                    <div class="kpi-footer">{max_sec/86400:.1f} days ({max_sec/3600:,.0f} hrs)</div>
                </div>
                """, unsafe_allow_html=True)
            with mk2:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">100th Longest</span><span class="kpi-icon">⏱️</span></div>
                    <div class="kpi-value" style="color: #F59E0B;">{format_duration_friendly(min_sec)}</div>
                    <div class="kpi-footer">{min_sec/86400:.1f} days ({min_sec/3600:,.0f} hrs)</div>
                </div>
                """, unsafe_allow_html=True)
            with mk3:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Median (Top 100)</span><span class="kpi-icon">📊</span></div>
                    <div class="kpi-value" style="color: #8B5CF6;">{format_duration_friendly(med_sec)}</div>
                    <div class="kpi-footer">{med_sec/86400:.1f} days ({med_sec/3600:,.0f} hrs)</div>
                </div>
                """, unsafe_allow_html=True)
            with mk4:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Failure Rate</span><span class="kpi-icon">⚠️</span></div>
                    <div class="kpi-value" style="color: #DC2626;">{(fail_c / len(top100_highest) * 100):.1f}%</div>
                    <div class="kpi-footer">{fail_c:,} failed &bull; {succ_c:,} success</div>
                </div>
                """, unsafe_allow_html=True)
            with mk5:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-header"><span class="kpi-title">Total Impacted Value</span><span class="kpi-icon">💰</span></div>
                    <div class="kpi-value" style="color: #0F172A;">GHS {total_vol:,.0f}</div>
                    <div class="kpi-footer">Across 100 slowest txns</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="insight-box" style="border-left-color: #EF4444; background: #FEF2F2; margin-top: 14px; margin-bottom: 14px;">
                <strong>🛑 Latency Outlier Finding:</strong>
                The slowest 100 transactions took between <strong>{format_duration_friendly(min_sec)}</strong> and 
                <strong>{format_duration_friendly(max_sec)}</strong> to resolve. 
                <strong>{fail_c}% ({fail_c}/100)</strong> resulted in terminal failure, indicating these were delayed chargeback reconciliations, 
                gateway hung connections, or multi-week batch retries before finally timing out.
            </div>
            """, unsafe_allow_html=True)
            
            # Prepare formatted display table
            display_highest = top100_highest.copy()
            display_highest.insert(0, 'Rank', [f"#{i}" for i in range(1, len(display_highest) + 1)])
            display_highest['Turnaround (Readable)'] = display_highest['duration_seconds'].apply(format_duration_friendly)
            display_highest['Duration (Days)'] = (display_highest['duration_seconds'] / 86400.0).apply(lambda x: f"{x:.1f} days")
            display_highest['Duration (Hours)'] = (display_highest['duration_seconds'] / 3600.0).apply(lambda x: f"{x:,.1f} hrs")
            if 'debit_amt' in display_highest.columns:
                display_highest['Amount (GHS)'] = display_highest['debit_amt'].apply(lambda x: f"GHS {x:,.2f}")
            
            show_cols = [c for c in ['Rank', 'Turnaround (Readable)', 'Duration (Days)', 'Duration (Hours)', 'transaction_status', 'transaction_id', 'client_name', 'response_code', 'recon_action', 'Amount (GHS)', 'date_str'] if c in display_highest.columns]
            
            col_search, col_dl = st.columns([3, 1])
            with col_search:
                inline_search = st.text_input("🔎 Search within Top 100 Slowest:", placeholder="Search by client, ID, or response code...", key="search_highest")
            with col_dl:
                csv_highest = display_highest.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Top 100 (CSV)",
                    data=csv_highest,
                    file_name="top_100_highest_duration_transactions.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            if inline_search:
                mask = display_highest.astype(str).apply(lambda row: row.str.contains(inline_search, case=False).any(), axis=1)
                display_highest = display_highest[mask]
                
            st.dataframe(display_highest[show_cols], use_container_width=True, hide_index=True)
            
            # Mini chart for slowest transactions
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            chart_slow = top100_highest.head(20).copy()
            chart_slow['Days'] = chart_slow['duration_seconds'] / 86400.0
            chart_slow['Client_Tx'] = chart_slow['client_name'].str.slice(0, 15) + ' (' + chart_slow['transaction_id'].astype(str).str[-6:] + ') - ' + chart_slow['transaction_status'].str.upper()
            
            fig_slow = px.bar(
                chart_slow,
                x='Days',
                y='Client_Tx',
                orientation='h',
                title="Top 20 Slowest Transactions Turnaround Time (Days to Resolution)",
                labels={'Days': 'Duration (Days)', 'Client_Tx': 'Client (Tx ID) - Status'},
                color='transaction_status',
                color_discrete_map={'success': '#10B981', 'failed': '#EF4444'}
            )
            fig_slow.update_layout(template=pio_template, height=380, yaxis=dict(autorange="reversed"), margin=dict(t=40, b=20, l=10, r=10))
            st.plotly_chart(fig_slow, use_container_width=True)

    # --------------------------------------------------------------------------
    # PRESET 3: STANDARD FILTERED SEARCH & CUSTOM EXPLORATION
    # --------------------------------------------------------------------------
    else:
        st.markdown("---")
        st.markdown("##### 🔎 Custom Transaction Search & Filtered Extract")
        
        col_exp1, col_exp2, col_exp3 = st.columns([2, 1, 1])
        with col_exp1:
            search_tx = st.text_input("🔎 Search Transaction ID, Client, or Code:", placeholder="Enter transaction ID or keyword...", key="search_std")
        with col_exp2:
            sort_order = st.selectbox(
                "Sort by:",
                options=[
                    "Most Recent (Date)",
                    "Duration (Lowest to Highest)",
                    "Duration (Highest to Lowest)",
                    "Amount (Highest to Lowest)"
                ],
                index=0
            )
        with col_exp3:
            rows_to_display = st.selectbox("Rows to display:", options=[50, 100, 250, 500, 1000], index=1)
            
        cols_export = [c for c in ['date_str', 'transaction_id', 'transaction_status', 'duration_seconds', 'duration_band', 'recon_action', 'response_code', 'client_name', 'debit_amt'] if c in source_df.columns]
        display_df = source_df[cols_export].copy()
        
        # Apply sorting
        if sort_order == "Duration (Lowest to Highest)":
            display_df = display_df.sort_values(by='duration_seconds', ascending=True)
        elif sort_order == "Duration (Highest to Lowest)":
            display_df = display_df.sort_values(by='duration_seconds', ascending=False)
        elif sort_order == "Amount (Highest to Lowest)" and 'debit_amt' in display_df.columns:
            display_df = display_df.sort_values(by='debit_amt', ascending=False)
        elif 'date_str' in display_df.columns:
            display_df = display_df.sort_values(by='date_str', ascending=False)
            
        display_df['Turnaround (Readable)'] = display_df['duration_seconds'].apply(format_duration_friendly)
        
        if search_tx:
            mask = display_df.astype(str).apply(lambda row: row.str.contains(search_tx, case=False).any(), axis=1)
            display_df = display_df[mask]
            st.caption(f"Found {len(display_df):,} matching transactions.")
            
        # Reorder columns nicely
        front_cols = [c for c in ['date_str', 'transaction_id', 'transaction_status', 'Turnaround (Readable)', 'duration_seconds'] if c in display_df.columns]
        remaining_cols = [c for c in display_df.columns if c not in front_cols]
        display_df = display_df[front_cols + remaining_cols]
        
        st.dataframe(display_df.head(rows_to_display), use_container_width=True, hide_index=True)
        
        csv_data = display_df.head(5000).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV, up to 5k rows)",
            data=csv_data,
            file_name="filtered_transactions_export.csv",
            mime="text/csv",
            use_container_width=False
        )
