def format_indian_currency(num):
    num = int(num)
    s = str(num)

    if len(s) <= 3:
        return s

    last3 = s[-3:]
    rest = s[:-3]

    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return ",".join(parts) + "," + last3

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import random
import os

def spacer(h=15):
    st.markdown(f"<div style='margin-top:{h}px'></div>", unsafe_allow_html=True)

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="EquiFund Dashboard", layout="wide")

# -----------------------------
# DARK THEME
# -----------------------------  
st.markdown("""
<style>

/* ================= GLOBAL ================= */
.stApp {
    background: linear-gradient(135deg, #0b1220, #111827);
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

/* ================= UNIVERSAL CARD STYLE ================= */
.card-style {
    border-radius: 16px;
    border: 1px solid rgba(148,163,184,0.25);
    box-shadow: 
        0 6px 16px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

/* ================= SIDEBAR ================= */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #020617);
    border-right: 1px solid rgba(148,163,184,0.2);
}

/* ================= KPI CARDS ================= */
.metric-card {
    background: linear-gradient(145deg, #1e293b, #334155);
    border-radius: 16px;
    padding: 22px;

    border: 1px solid rgba(148,163,184,0.25);
    box-shadow:
        0 6px 16px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04);

    transition: all 0.25s ease;
}

/* hover polish */
.metric-card:hover {
    border: 1px solid rgba(59,130,246,0.4);
    box-shadow:
        0 10px 24px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.05);
}

/* ================= KPI TEXT ================= */
.metric-label {
    font-size: 13px;
    color: #9ca3af;
}

.metric-value {
    font-size: clamp(16px, 1.6vw, 22px);
    font-weight: 700;
    color: #f9fafb;
}

/* ================= ST.METRIC ================= */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1f2937, #111827);
    border-radius: 16px;
    padding: 16px;

    border: 1px solid rgba(148,163,184,0.25);
    box-shadow:
        0 6px 14px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

/* ================= BUTTON ================= */
/* ================= CLEAN BUTTON STYLE ================= */
.stButton>button {
    background: linear-gradient(145deg, #1e293b, #0f172a);  /* dark like cards */

    border-radius: 12px;
    border: 1px solid rgba(148,163,184,0.25);  /* light border */

    color: #e2e8f0;
    padding: 10px 18px;
    font-weight: 600;

    box-shadow:
        0 4px 10px rgba(0,0,0,0.3),
        inset 0 1px 0 rgba(255,255,255,0.05);

    transition: all 0.25s ease;
}

.stButton>button:hover {
    border: 1px solid rgba(96,165,250,0.5);  /* slight highlight */
    
    background: linear-gradient(145deg, #1e293b, #1e3a8a);  /* very subtle */
    
    box-shadow:
        0 6px 16px rgba(0,0,0,0.4);
}

/* ================= DROPDOWN ================= */
div[data-baseweb="select"] > div {
    background: #111827 !important;
    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 10px;
}

/* ================= TABLE ================= */
div[data-testid="stDataFrame"] > div {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 14px;

    border: 1px solid rgba(148,163,184,0.25);
    box-shadow:
        0 6px 16px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

/* ================= CHART ================= */
.js-plotly-plot {
    background: linear-gradient(145deg, #020617, #111827);
    border-radius: 14px;

    border: 1px solid rgba(148,163,184,0.2);
    box-shadow:
        0 6px 16px rgba(0,0,0,0.4);

    padding: 10px;
}

/* ================= ALERT ================= */
.stAlert {
    background: #111827;
    border-left: 4px solid #3b82f6;
    border-radius: 10px;

    border: 1px solid rgba(148,163,184,0.2);
}

/* ================= SCROLL ================= */
::-webkit-scrollbar-thumb {
    background: #374151;
}

/* ================= CUSTOM ALERT ================= */
.custom-alert {
    padding: 16px 20px;
    border-radius: 14px;
    font-weight: 600;
    margin-top: 10px;

    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid rgba(148,163,184,0.25);

    box-shadow:
        0 6px 16px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04);
    color: #ffffff !important;
}

/* high risk */
.alert-high {
    border-left: 4px solid #ef4444;
    color: #fca5a5;
}

/* medium risk */
.alert-medium {
    border-left: 4px solid #f59e0b;
    color: #fde68a;
}

/* low risk */
.alert-low {
    border-left: 4px solid #10b981;
    color: #86efac;
}

/* ================= TAB BOX STYLE ================= */

/* tab container spacing */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

/* each tab = box */
.stTabs [data-baseweb="tab"] {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 10px;

    border: 1px solid rgba(148,163,184,0.25);  /* light border */
    
    padding: 8px 16px;
    transition: all 0.25s ease;

    color: #cbd5f5;  /* light text */
}

/* active tab (clean, no blue fill) */
.stTabs [aria-selected="true"] {
    background: linear-gradient(145deg, #1e293b, #0f172a);  /* same as others */
    
    border: 1px solid rgba(96,165,250,0.6);  /* highlight border only */
    
    color: #ffffff;

    box-shadow:
        0 0 0 1px rgba(96,165,250,0.2),
        0 4px 12px rgba(0,0,0,0.4);
}
            
/* ================= AI OUTPUT BOX ================= */
.ai-output-box {
    background: linear-gradient(145deg, #1e293b, #0f172a);

    border-radius: 16px;
    padding: 20px;

    border: 1px solid rgba(255,255,255,0.25);  /* white border */

    box-shadow:
        0 8px 20px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.05);

    color: #ffffff;

    line-height: 1.6;
}

/* spacing for text inside */
.ai-output-box p {
    margin-bottom: 10px;
}
            
/* ================= INPUT BLOCK STYLE ================= */

/* DROPDOWN BOX (closed state) */
div[data-baseweb="select"] > div {
    background: linear-gradient(145deg, #1e293b, #0f172a) !important;

    border: 1px solid rgba(148,163,184,0.25) !important;
    border-radius: 10px;

    box-shadow:
        0 4px 10px rgba(0,0,0,0.3),
        inset 0 1px 0 rgba(255,255,255,0.05);

    color: #e2e8f0 !important;
}

/* DROPDOWN MENU (open list) */
div[data-baseweb="menu"] {
    background: #0f172a !important;
    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 10px;
}

/* DROPDOWN OPTIONS */
div[data-baseweb="menu"] div {
    color: #e2e8f0 !important;
}

/* HOVER OPTION */
div[data-baseweb="menu"] div:hover {
    background: #1e293b !important;
}

/* KEEP ARROW VISIBLE */
div[data-baseweb="select"] svg {
    fill: #cbd5f5 !important;
}

/* DOWNLOAD BUTTON (SIDEBAR) */
section[data-testid="stSidebar"] button {
    background: linear-gradient(145deg, #1e293b, #0f172a);

    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 10px;

    width: 100%;
    color: #e2e8f0;

    box-shadow:
        0 4px 10px rgba(0,0,0,0.3);
}

/* HOVER (ALL INPUTS SAME STYLE) */
div[data-baseweb="select"]:hover,
section[data-testid="stSidebar"] button:hover,
div[data-testid="stFileUploader"] button:hover {
    border: 1px solid rgba(96,165,250,0.5) !important;
}
            
/* ================= SMALL TOP ADJUSTMENT ================= */

/* reduce top padding slightly (not too much) */
.block-container {
    padding-top: 2rem !important;
}

/* slight lift for title */
h1 {
    margin-top: -10px !important;
}

/* keep tabs aligned nicely */
.stTabs {
    margin-top: 5px;
}
            
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():

        df_alloc = pd.read_excel("EquiFund_Realistic_Final.xlsx", sheet_name="FactAllocations")
        df_util = pd.read_excel("EquiFund_Realistic_Final.xlsx", sheet_name="FactUtilization")
        df_regions = pd.read_excel("EquiFund_Realistic_Final.xlsx", sheet_name="DimRegions")
        df_schemes = pd.read_excel("EquiFund_Realistic_Final.xlsx", sheet_name="DimSchemes")
        df_audit = pd.read_excel("EquiFund_Realistic_Final.xlsx", sheet_name="FactAuditFlags")

        return df_alloc, df_util, df_regions, df_schemes, df_audit

# -----------------------------
# DATA PROCESSING (ADD THIS)
# -----------------------------
def preprocess_data(df_alloc, df_util, df_regions, df_schemes, df_audit):

    # 1. Remove duplicates
    df_alloc = df_alloc.drop_duplicates()
    df_util = df_util.drop_duplicates()
    df_regions = df_regions.drop_duplicates()
    df_schemes = df_schemes.drop_duplicates()
    df_audit = df_audit.drop_duplicates()

    # 2. Handle missing values
    df_alloc['AmountAllocated'] = df_alloc['AmountAllocated'].fillna(0)
    df_util['AmountSpent'] = df_util['AmountSpent'].fillna(0)

    df_regions['Population'] = df_regions['Population'].fillna(0)
    df_regions['PovertyRate'] = df_regions['PovertyRate'].fillna(0)

    # 3. Fix negative values
    df_alloc['AmountAllocated'] = df_alloc['AmountAllocated'].clip(lower=0)
    df_util['AmountSpent'] = df_util['AmountSpent'].clip(lower=0)

    # 4. Convert types
    df_alloc['AmountAllocated'] = pd.to_numeric(df_alloc['AmountAllocated'], errors='coerce').fillna(0)
    df_util['AmountSpent'] = pd.to_numeric(df_util['AmountSpent'], errors='coerce').fillna(0)

    # 5. Fix: Spent should not exceed allocated
    df_util = df_util.merge(
        df_alloc[['AllocationID', 'AmountAllocated']],
        on='AllocationID',
        how='left'
    )
    df_util['AmountSpent'] = df_util[['AmountSpent', 'AmountAllocated']].min(axis=1)
    # ✅ ADD THIS (IMPORTANT)
    df_util['AmountSpent'] = df_util['AmountSpent'].fillna(0)
    df_util = df_util.drop(columns=['AmountAllocated'])

    # 6. Date cleaning
    df_alloc['DateAllocated'] = pd.to_datetime(df_alloc['DateAllocated'], errors='coerce')
    df_util['DateRecorded'] = pd.to_datetime(df_util['DateRecorded'], errors='coerce')

    # 7. Text cleaning
    df_regions['State'] = df_regions['State'].str.strip().str.upper()
    df_regions['RegionName'] = df_regions['RegionName'].str.strip()
    df_schemes['SchemeName'] = df_schemes['SchemeName'].str.strip()

    # 8. Department safe handling
    if 'Department' in df_alloc.columns:
        df_alloc['Department'] = df_alloc['Department'].str.strip()

    if 'Department' in df_schemes.columns:
        df_schemes['Department'] = df_schemes['Department'].str.strip()

    return df_alloc, df_util, df_regions, df_schemes, df_audit
    
def get_ai_insights(summary):

    API_KEY = os.getenv("GROQ_API_KEY")   # your Groq key

    variation = random.randint(1, 100000)

    prompt = f"""
    You are a SENIOR GOVERNMENT AUDITOR reviewing public welfare fund data.
    
    STRICT RULES:
    - Use ONLY the provided dataset
    - DO NOT give generic financial or investment advice
    - Output must be audit-focused and data-specific
    
    ========================
    DATA CONTEXT
    ========================
    {summary}
    
    ========================
    OUTPUT FORMAT
    ========================
    
    Use clear headings (NO numbering).
    Use bullet points (-) only.
    Keep everything concise and professional.
    
    ----------------------------------------
    
    FILTER SUMMARY:
    - Mention State, Year, Date Range clearly
    
    ----------------------------------------
    
    REGION INSIGHTS:
    - Identify regions with:
      • High allocation but low utilization
      • High leakage
    - Mention actual region names
    - Highlight imbalance across regions
    
    ----------------------------------------
    
    DEPARTMENT ANALYSIS:
    - Identify top departments by allocation
    - Highlight departments with:
      • Low utilization
      • High leakage
    - Mention department names clearly
    
    ----------------------------------------
    
    SCHEME ANALYSIS:
    - Identify key schemes receiving highest funds
    - Highlight schemes with:
      • Poor utilization
      • High leakage
    - Mention scheme names clearly
    
    ----------------------------------------
    
    TIME INSIGHTS:
    - Identify trends across dates/months
    - Mention increase/decrease in utilization or leakage
    
    ----------------------------------------
    
    KEY AUDIT RISKS:
    - Regional imbalance
    - Inefficient departments
    - Underperforming schemes
    - Delayed utilization
    
    ----------------------------------------
    
    RECOMMENDATIONS (VERY IMPORTANT):
    
    - Keep each recommendation VERY SHORT (one line only)
    - MUST include State / Region / Department / Scheme name
    - Focus on audit actions only
    
    Examples:
    - Increase audit monitoring in [Region] due to high leakage
    - Review [Department] for low utilization efficiency
    - Reallocate funds from underperforming schemes like [SchemeName]
    - Prioritize audits in [State] high-risk regions
    
    ----------------------------------------
    
    IMPORTANT:
    - DO NOT write long paragraphs
    - DO NOT give general advice
    - MUST mention Region, Department, Scheme names
    - Keep recommendations brief and actionable
    """
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 1.2
        }
    )

    if response.status_code != 200:
        return f"❌ Request Failed ({response.status_code})\n{response.text}"

    data = response.json()

    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    else:
        return f"❌ API Error:\n{data}"

st.title("EquiFund Analytics: Welfare Distribution and Efficiency Tracking")

# ================= LANDING SCREEN =================

if "start_app" not in st.session_state:
    st.session_state.start_app = False

if not st.session_state.start_app:

    st.markdown("""
    <div class="metric-card" style="text-align:center; padding:40px;">
        <h2>👋 Welcome to EquiFund Dashboard</h2>
        <p style="color:#9ca3af;">
        Analyze government fund allocation, utilization, leakage, and equity insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    spacer(20)

    if st.button("🚀 Explore Dashboard"):
        st.session_state.start_app = True
        st.rerun()

    st.stop()


# ✅ LOAD DATA
df_alloc, df_util, df_regions, df_schemes, df_audit = load_data()
df_alloc, df_util, df_regions, df_schemes, df_audit = preprocess_data(
    df_alloc, df_util, df_regions, df_schemes, df_audit
)


# -----------------------------
# KPI CARD
# -----------------------------
def kpi_card(title, value):
   return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# -----------------------------
# MERGE
# -----------------------------
df = df_alloc.merge(df_regions, on="RegionID", how="left")
df = df.merge(df_schemes, on="SchemeID", how="left")
df_util_clean = df_util.groupby("AllocationID", as_index=False).agg({
    "AmountSpent": "sum"
})
df = df.merge(df_util_clean, on="AllocationID", how="left")

df_clean = df.drop_duplicates(subset=["AllocationID"])

st.sidebar.header("Filters")

# ✅ CREATE STATE LIST FIRST (IMPORTANT FIX)
state_list = sorted(df['State'].dropna().unique())

# ✅ STATE DROPDOWN
state = st.sidebar.selectbox(
    "State",
    ["All States"] + state_list
)

# ✅ YEAR LIST
year_list = sorted(df['DateAllocated'].dt.year.dropna().unique())

# ✅ YEAR DROPDOWN
year = st.sidebar.selectbox("Year", year_list)

# -----------------------------
# APPLY FILTERS (FINAL FIX)
# -----------------------------
filtered_df = df.copy()

# Year filter
filtered_df = filtered_df[
    filtered_df['DateAllocated'].dt.year == year
]

# State filter
if state != "All States":
    filtered_df = filtered_df[filtered_df['State'] == state]

# ✅ AFTER FILTERING
st.sidebar.markdown("---")

st.sidebar.download_button(
    "⬇️ Download Filtered Data",
    filtered_df.to_csv(index=False),
    file_name="filtered_data.csv"
)

# -----------------------------
# KPI CALCULATIONS
# ----------------------------
total_alloc = filtered_df['AmountAllocated'].sum()
total_util = filtered_df['AmountSpent'].sum()

leakage = total_alloc - total_util
leakage_pct = (leakage / total_alloc) if total_alloc else 0
util_rate = (total_util / total_alloc) if total_alloc else 0

# Equity
df_regions['PovertyCount'] = df_regions['Population'] * df_regions['PovertyRate']
total_poverty = df_regions['PovertyCount'].sum()

regional_poverty = df_regions.groupby('RegionID')['PovertyCount'].sum()
region_alloc = filtered_df.groupby('RegionID')['AmountAllocated'].sum()

equity = (region_alloc / total_alloc) - (regional_poverty / total_poverty)
equity = equity.reset_index()

equity = equity.merge(df_regions[['RegionID', 'RegionName']], on='RegionID')
equity.columns = ['RegionID', 'EquityVariance', 'Region']

# -----------------------------
# TABS
# -----------------------------
tabs = st.tabs([
    "📊 Executive",
    "⚠️ Audit",
    "🌍 Equity",
    "🧠 AI Insights",
    "📦 Scheme Analysis",
    "📍 Regional Analysis"
])

with tabs[0]:
    spacer(20)

    # ✅ KPI HORIZONTAL
    col1, col2, col3 = st.columns(3)

    col1.markdown(kpi_card("Total Allocated", f"₹ {format_indian_currency(total_alloc)}"), unsafe_allow_html=True)

    col2.markdown(kpi_card("Total Utilized", f"₹ {format_indian_currency(total_util)}"), unsafe_allow_html=True)

    col3.markdown(kpi_card("Leakage %", f"{leakage_pct:.2%}"), unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)

    if leakage_pct > 0.15:
        st.markdown("""
        <div class="custom-alert alert-high">
            🚨 High Leakage Detected! Immediate action required
        </div>
        """, unsafe_allow_html=True)

    elif leakage_pct > 0.08:
        st.markdown("""
        <div class="custom-alert alert-medium">
            ⚠️ Moderate Leakage Detected
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="custom-alert alert-low">
            ✅ Funds are efficiently utilized
        </div>
        """, unsafe_allow_html=True)
    
    spacer(20)
    st.markdown("---")
    spacer(20)


    # ✅ AREA CHART
    st.subheader("Total Allocated vs Utilized")

    time_df = filtered_df.groupby(filtered_df['DateAllocated'].dt.to_period("M")).agg({
        'AmountAllocated': 'sum',
        'AmountSpent': 'sum'
    }).reset_index()

    time_df['DateAllocated'] = time_df['DateAllocated'].astype(str)

    time_df["Allocated_fmt"] = time_df["AmountAllocated"].apply(
        lambda x: "₹ " + format_indian_currency(x)
    )

    time_df["Spent_fmt"] = time_df["AmountSpent"].apply(
        lambda x: "₹ " + format_indian_currency(x)
    )

    fig = px.area(
        time_df,
        x="DateAllocated",
        y=["AmountAllocated", "AmountSpent"]
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )

    fig.update_traces(
        customdata=time_df[["Allocated_fmt", "Spent_fmt"]],
        hovertemplate="Date: %{x}<br>Amount: %{customdata[0]}<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    spacer(20)

    # ✅ DONUT
    st.subheader("Total Allocated by Department")

    dept_df = filtered_df.groupby("Department")["AmountAllocated"].sum().reset_index()

    # ✅ ADD THIS LINE (FORMAT)
    dept_df["Amount_fmt"] = dept_df["AmountAllocated"].apply(
        lambda x: "₹ " + format_indian_currency(x)
    )

    # ✅ MODIFY CHART
    fig2 = px.pie(
        dept_df,
        names="Department",
        values="AmountAllocated",
        hole=0.5
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )

    fig2.update_traces(
        hovertemplate="Department: %{label}<br>Amount: %{customdata}<extra></extra>",
        customdata=dept_df["Amount_fmt"]
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    spacer(20)


    # =========================
    # 🟢 Department vs Utilization
    # =========================
    st.markdown("###  Department vs Utilization")
    
    dept_util = filtered_df.groupby("Department").agg({
        "AmountAllocated": "sum",
        "AmountSpent": "sum"
    }).reset_index()
    
    # utilization %
    dept_util["UtilRate"] = dept_util["AmountSpent"] / dept_util["AmountAllocated"]
    
    # sort
    dept_util = dept_util.sort_values("UtilRate", ascending=False)
    
    # label (₹ + %)
    dept_util["Util_full"] = dept_util.apply(
        lambda x: f"{x['UtilRate']*100:.2f}% (₹ {format_indian_currency(x['AmountSpent'])})",
        axis=1
    )
    
    # chart
    fig_util = px.bar(
        dept_util,
        x="UtilRate",
        y="Department",
        orientation="h",
        color="UtilRate",
        color_continuous_scale="Greens",
        title="Department Utilization Ranking"
    )
    
    fig_util.update_traces(
        hovertemplate="Department: %{y}<br>%{customdata}<extra></extra>",
        customdata=dept_util["Util_full"]
    )
    
    fig_util.update_layout(
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        xaxis_title="Utilization Rate",
        yaxis_title="Department"
    )
    
    st.plotly_chart(fig_util, use_container_width=True)

    st.markdown("---")
    spacer(20)

    
    # =========================
    # 🔴 Department Leakage (Waterfall)
    # =========================
    st.markdown("###  Department Leakage ")
    
    dept_leak = filtered_df.groupby("Department").agg({
        "AmountAllocated": "sum",
        "AmountSpent": "sum"
    }).reset_index()
    
    dept_leak["Leakage"] = dept_leak["AmountAllocated"] - dept_leak["AmountSpent"]
    
    total_leak = dept_leak["Leakage"].sum()
    
    # % contribution
    dept_leak["Leak_pct"] = dept_leak["Leakage"] / total_leak
    
    # labels
    dept_leak["Leak_full"] = dept_leak.apply(
        lambda x: f"₹ {format_indian_currency(x['Leakage'])} ({x['Leak_pct']*100:.2f}%)",
        axis=1
    )
    
    fig_waterfall = go.Figure(go.Waterfall(
        x=dept_leak["Department"],
        y=dept_leak["Leakage"],
        text=dept_leak["Leak_full"],
        textposition="outside"
    ))
    
    fig_waterfall.update_layout(
        height=500,
        title="Leakage Contribution by Department",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        yaxis_title="Leakage (₹)"
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)

    underfunded = equity[equity["EquityVariance"] < 0].shape[0]
    st.markdown("---")
    spacer(20)


    st.subheader("Executive Summary & Key Insights")

    st.markdown(f"""
    <div class="custom-alert alert-medium">
    • Total Allocation: ₹ {format_indian_currency(total_alloc)}<br>
    • Utilization Rate: {util_rate:.2%}<br>
    • Leakage is {leakage_pct:.2%}, indicating inefficiency<br><br>
    👉 Higher leakage suggests poor fund tracking or delays.
    </div>
    """, unsafe_allow_html=True)

with tabs[1]:

    spacer(20)

    # =========================
    # CREATE SCATTER DATA FIRST
    # =========================
    scatter_df = filtered_df.groupby("RegionName").agg({
        "AmountAllocated": "sum",
        "AmountSpent": "sum",
        "DateAllocated": "max"
    }).reset_index()

    scatter_df["Leakage"] = scatter_df["AmountAllocated"] - scatter_df["AmountSpent"]

    # 👉 ADD RISK SCORE BACK
    audit_region = df_audit.merge(
        df_alloc[['AllocationID', 'RegionID']], on='AllocationID'
    ).merge(
        df_regions[['RegionID', 'RegionName']], on='RegionID'
    )

    risk_region = audit_region.groupby("RegionName")["RiskScore"].mean().reset_index()

    scatter_df = scatter_df.merge(risk_region, on="RegionName", how="left")

    # format date
    scatter_df["DateAllocated"] = scatter_df["DateAllocated"].dt.strftime("%d-%b-%Y")

    # =========================
    # SCATTER PLOT
    # =========================
    st.subheader("Leakage vs Risk")
    scatter_df["RiskScore"] = scatter_df["RiskScore"].fillna(0)

    # ✅ CREATE REQUIRED COLUMNS (MISSING FIX)

    scatter_df["Leakage_fmt"] = scatter_df["Leakage"].apply(
        lambda x: "₹ " + format_indian_currency(x)
    )
    
    scatter_df["Risk_pct"] = scatter_df["RiskScore"].fillna(0) * 100

    fig3 = px.scatter(
        scatter_df,
        x="Leakage",
        y="Risk_pct",
        color="RegionName",
        hover_name="RegionName"
    )
    
    fig3.update_traces(
        hovertemplate=
        "Region: %{hovertext}<br>" +
        "Leakage: %{customdata[0]}<br>" +
        "Risk: %{customdata[1]:.2f}%<extra></extra>",
        customdata=scatter_df[["Leakage_fmt", "Risk_pct"]]
    )
    
    fig3.update_layout(
        yaxis_title="Risk Score (%)",
        xaxis_title="Leakage (₹)"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    spacer(20)


    # =========================
    # TOP & BOTTOM TABLES
    # =========================
    top = scatter_df.sort_values("Leakage", ascending=False).head(5).copy().reset_index(drop=True)
    bottom = scatter_df.sort_values("Leakage").head(5).copy().reset_index(drop=True)

    top.index = top.index + 1
    bottom.index = bottom.index + 1

    top["Leakage"] = top["Leakage"].apply(lambda x: "₹ " + format_indian_currency(x))
    bottom["Leakage"] = bottom["Leakage"].apply(lambda x: "₹ " + format_indian_currency(x))

    st.markdown("###  Top Leakage Regions")
    st.dataframe(top[["RegionName", "Leakage", "DateAllocated"]])

    st.markdown("---")

    st.markdown("###  Best Performing Regions")
    st.dataframe(bottom[["RegionName", "Leakage", "DateAllocated"]])

    st.markdown("---")
    spacer(20)

    # =========================
    # LEAKAGE OVERVIEW (GAUGE)
    # =========================
    st.subheader("Leakage Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=leakage_pct * 100,
            title={'text': "Leakage %"},
            gauge={
                'axis': {'range': [0, 30]},
                'bar': {'color': "green"}
            }
        ))
    
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0")
        )
    
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.metric("Leakage Amount", f"₹ {format_indian_currency(leakage)}")
    
    st.markdown("---")
    spacer(20)


    # =========================
    # AUDIT FLAGS TABLE
    # =========================
    st.subheader("Audit Flags")

    audit_table = df_audit.merge(
        filtered_df[['AllocationID', 'RegionID', 'DateAllocated']],
        on='AllocationID',
        how='inner'
    ).merge(
        df_regions[['RegionID', 'RegionName']],
        on='RegionID',
        how='left'
    )

    audit_table["DateAllocated"] = audit_table["DateAllocated"].dt.strftime("%d-%b-%Y")

    high_risk_df = audit_table[audit_table['RiskScore'] > 0.7][
        ['RegionName', 'AuditID', 'Status', 'RiskScore', 'DateAllocated']
    ]

    high_risk_df = high_risk_df.reset_index(drop=True)
    high_risk_df.index = high_risk_df.index + 1

    st.dataframe(high_risk_df)

    high_risk_count = high_risk_df.shape[0]

    st.markdown("---")
    spacer(20)


    # =========================
    # SUMMARY
    # =========================
    st.subheader("Audit Findings & Risk Analysis")

    st.markdown(f"""
    <div class="custom-alert alert-high">
    • Regions with high leakage tend to have higher risk scores<br><br>
    👉 Focus audit on top leakage regions first.
    </div>
    """, unsafe_allow_html=True)
with tabs[2]:

    spacer(20)

    # ================================
    # 🌍 EQUITY VARIANCE MAP
    # ================================
    st.subheader("🌍 Equity Variance Map")

    with open("india_states.geojson") as f:
        india_geo = json.load(f)

    map_df = equity.merge(
        df_regions[['RegionName', 'State']],
        left_on='Region',
        right_on='RegionName'
    )

    map_df = map_df.groupby("State", as_index=False)["EquityVariance"].mean()
    map_df['State'] = map_df['State'].str.strip().str.upper()

    geo_key = "NAME_1"

    geo_states = []
    for feature in india_geo["features"]:
        name = str(feature["properties"][geo_key]).strip().upper()
        feature["properties"][geo_key] = name
        geo_states.append(name)

    full_map = pd.DataFrame({"State": geo_states})
    full_map = full_map.merge(map_df, on="State", how="left")

    # 👉 better than 0 → use neutral mid value
    full_map["EquityVariance"] = full_map["EquityVariance"].fillna(0)

    fig_map = px.choropleth(
        full_map,
        geojson=india_geo,
        locations="State",
        featureidkey="properties.NAME_1",
        color="EquityVariance",
        color_continuous_scale="RdYlGn_r",
        title="Equity Distribution Across India"
    )

    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )                                                               

    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(height=650)

    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    spacer(20)


    # ================================
    # 📊 TORNADO CHART
    # ================================
  
    st.markdown("Comparing **Population Poverty %** vs **Budget Allocation %** per region")

    poverty_df = df_regions.copy()
    poverty_df["PovertyCount"] = poverty_df["Population"] * poverty_df["PovertyRate"]

    alloc_df = filtered_df.groupby("RegionID")["AmountAllocated"].sum().reset_index()

    merged = poverty_df.merge(alloc_df, on="RegionID")

    merged["Poverty %"] = merged["PovertyCount"] / merged["PovertyCount"].sum()
    merged["Allocation %"] = merged["AmountAllocated"] / merged["AmountAllocated"].sum()

    # 🔥 Better tornado style (horizontal)
    fig_tornado = px.bar(
        merged.sort_values("Poverty %"),
        y="RegionName",
        x=["Poverty %", "Allocation %"],
        barmode="group",
        orientation="h",
        title="Population Poverty % vs Budget Allocation %"
    )

    fig_tornado.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )

    fig_tornado.update_layout(
        yaxis_title="Region",
        xaxis_title="Percentage"
    )

    st.plotly_chart(fig_tornado, use_container_width=True)

    st.markdown("---")
    spacer(20)


    # ================================
    # 🌳 DECOMPOSITION (DRILLDOWN)
    # ================================
    st.markdown("Drill down from **Department → Scheme → Region** to analyze fund flow")

    col1, col2 = st.columns(2)

    with col1:
        dept_sel = st.selectbox("Select Department", df["Department"].unique())

        scheme_df = filtered_df[filtered_df["Department"] == dept_sel]

    with col2:
        scheme_sel = st.selectbox("Select Scheme", scheme_df["SchemeName"].unique())

    region_df = scheme_df[scheme_df["SchemeName"] == scheme_sel]

    # ✅ ADD THIS LINE BEFORE CHART
    region_df["Amount_fmt"] = region_df["AmountAllocated"].apply(
        lambda x: "₹ " + format_indian_currency(x)
    )

    fig_drill = px.bar(
        region_df,
        x="RegionName",
        y="AmountAllocated",
        title="Fund Allocation by Region"
    )

    fig_drill.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )

    fig_drill.update_traces(
        hovertemplate="Region: %{x}<br>Amount: %{customdata}",
        customdata=region_df["Amount_fmt"]
    )

    fig_drill.update_layout(
        xaxis_title="Region",
        yaxis_title="Amount (₹)"
    )

    st.plotly_chart(fig_drill, use_container_width=True)
    st.markdown("---")
    spacer(20)

    st.subheader("Equity Analysis & Distribution Insights")

    st.markdown(f"""
    <div class="custom-alert alert-low">
    • Underfunded Regions: {underfunded}<br>
    • Some regions receive less than required allocation<br><br>
    👉 Redistribution can improve fairness.
    </div>
    """, unsafe_allow_html=True)

with tabs[3]:
    spacer(20)


    st.subheader("🧠 AI Insights & Recommendations")

    col1, col2 = st.columns(2)

    col1.metric("Total Budget", f"₹ {format_indian_currency(total_alloc)}")
    col1.metric("Utilization Rate", f"{util_rate:.2%}")

    col2.metric("Leakage", f"₹ {format_indian_currency(leakage)}")

    st.markdown("---")
    spacer(20)


    # =========================
    # BUILD FILTER-AWARE SUMMARY
    # =========================
    
    # Top regions (by allocation)
    top_regions = filtered_df.groupby("RegionName")["AmountAllocated"].sum().nlargest(5).index.tolist()
    
    # Top departments
    top_departments = filtered_df.groupby("Department")["AmountAllocated"].sum().nlargest(5).index.tolist()
    
    # Top schemes
    top_schemes = filtered_df.groupby("SchemeName")["AmountAllocated"].sum().nlargest(5).index.tolist()
    
    # date range
    date_min = filtered_df["DateAllocated"].min()
    date_max = filtered_df["DateAllocated"].max()
    
    # convert dates
    date_range = f"{date_min.strftime('%d-%b-%Y')} to {date_max.strftime('%d-%b-%Y')}"
    
    # state display
    state_selected = state if state != "All States" else "All States"
    
    summary = f"""
    FILTER CONTEXT:
    - State: {state_selected}
    - Year: {year}
    - Date Range: {date_range}
    
    KEY METRICS:
    - Total Allocation: ₹ {format_indian_currency(total_alloc)}
    - Total Utilization: ₹ {format_indian_currency(total_util)}
    - Leakage: ₹ {format_indian_currency(leakage)}
    - Utilization Rate: {util_rate:.2%}
    
    TOP REGIONS:
    {", ".join(top_regions)}
    
    TOP DEPARTMENTS:
    {", ".join(top_departments)}
    
    TOP SCHEMES:
    {", ".join(top_schemes)}
    
    INSTRUCTION:
    Provide detailed insights, risks, and recommendations 
    based on this filtered dataset.
    Mention:
    - Region-wise observations
    - Department performance
    - Scheme efficiency
    - Time-based patterns
    """

    if st.button("🤖 Generate AI Insights"):

        with st.spinner("Analyzing data..."):
            ai_output = get_ai_insights(summary)


        st.markdown(f"""
        <div class="ai-output-box">
        {ai_output}
        </div>
        """, unsafe_allow_html=True)

with tabs[4]:

    spacer(20)

    # =========================
    # PREP DATA
    # =========================
    scheme_df = filtered_df.groupby(
        "SchemeName", as_index=False
    ).agg({
        "AmountAllocated": "sum",
        "AmountSpent": "sum"
    })
    
    scheme_df["UtilRate"] = (
        scheme_df["AmountSpent"] / scheme_df["AmountAllocated"]
    ).fillna(0)

    scheme_df["Leakage"] = scheme_df["AmountAllocated"] - scheme_df["AmountSpent"]
   

    total_alloc_s = scheme_df["AmountAllocated"].sum()
    total_spent_s = scheme_df["AmountSpent"].sum()
    total_leak_s = scheme_df["Leakage"].sum()

    # =========================
    # 🔵 1. SUNBURST (ALLOCATION)
    # =========================
    st.markdown("###  Scheme-wise Allocation ")

    scheme_df["Alloc_pct"] = scheme_df["AmountAllocated"] / total_alloc_s

    scheme_df["Alloc_full"] = scheme_df.apply(
        lambda x: f"₹ {format_indian_currency(x['AmountAllocated'])} ({x['Alloc_pct']*100:.2f}%)",
        axis=1
    )

    fig_alloc = px.sunburst(
        scheme_df,
        path=["SchemeName"],
        values="AmountAllocated",
        color="AmountAllocated",
        color_continuous_scale="Blues",
        title="Allocation Distribution by Scheme"
    )

    fig_alloc.update_traces(
        textinfo="label+percent entry",
        hovertemplate="Scheme: %{label}<br>%{customdata}<extra></extra>",
        customdata=scheme_df["Alloc_full"]
    )

    fig_alloc.update_layout(
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )

    st.plotly_chart(fig_alloc, use_container_width=True)

    st.markdown("---")
    spacer(20)


    # =========================
    # 🟢 Scheme Utilization (Better Chart)
    # =========================
    st.markdown("###  Scheme Utilization (Allocated vs Utilized)")
    
    util_df = scheme_df.copy()
    
    # calculate unspent
    util_df["Unspent"] = util_df["AmountAllocated"] - util_df["AmountSpent"]
    
    # sort (important for readability)
    util_df = util_df.sort_values("UtilRate", ascending=True)
    
    # create chart
    fig_util_new = go.Figure()
    
    # utilized
    fig_util_new.add_bar(
        y=util_df["SchemeName"],
        x=util_df["AmountSpent"],
        name="Utilized",
        orientation="h"
    )
    
    # unspent
    fig_util_new.add_bar(
        y=util_df["SchemeName"],
        x=util_df["Unspent"],
        name="Unspent",
        orientation="h"
    )
    
    # layout
    fig_util_new.update_layout(
        barmode="stack",
        height=500,
        title="Utilization Efficiency by Scheme",
        xaxis_title="Amount (₹)",
        yaxis_title="Scheme",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )
    
    st.plotly_chart(fig_util_new, use_container_width=True)

    st.markdown("---")
    spacer(20)


    # =========================
    # 🔴 Scheme-wise Leakage (Advanced Ranking)
    # =========================
    st.markdown("###  Scheme-wise Leakage ")
    
    # calculate %
    scheme_df["Leak_pct"] = scheme_df["Leakage"] / total_leak_s
    
    # sort (highest leakage first)
    scheme_df = scheme_df.sort_values("Leakage", ascending=False)
    
    # full label (₹ + %)
    scheme_df["Leak_full"] = scheme_df.apply(
        lambda x: f"₹ {format_indian_currency(x['Leakage'])} ({x['Leak_pct']*100:.2f}%)",
        axis=1
    )
    
    # bar chart
    fig_leak = px.bar(
        scheme_df,
        x="Leakage",
        y="SchemeName",
        orientation="h",
        color="Leakage",
        color_continuous_scale="Reds",
        title="Leakage Ranking by Scheme"
    )
    
    # show ₹ + %
    fig_leak.update_traces(
        hovertemplate="Scheme: %{y}<br>%{customdata}<extra></extra>",
        customdata=scheme_df["Leak_full"]
    )
    
    fig_leak.update_layout(
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        xaxis_title="Leakage (₹)",
        yaxis_title="Scheme"
    )
    
    st.plotly_chart(fig_leak, use_container_width=True)

    st.markdown("---")
    spacer(20)


    # =========================
    # INSIGHTS
    # =========================
    st.subheader("Scheme Performance Insights")

    st.markdown(f"""
    <div class="custom-alert alert-medium">
    • Total Allocation: ₹ {format_indian_currency(total_alloc_s)}<br>
    • Utilization Rate: {(total_spent_s/total_alloc_s):.2%}<br>
    • Total Leakage: ₹ {format_indian_currency(total_leak_s)}<br><br>
    👉 Schemes with high leakage require immediate review.
    </div>
    """, unsafe_allow_html=True)

with tabs[5]:

    spacer(20)

    region_sel = st.selectbox(
        "Select Region",
        filtered_df["RegionName"].unique()
    )

    region_data = df_clean[df_clean["RegionName"] == region_sel]
    
    total_alloc_r = region_data["AmountAllocated"].sum()
    total_spent_r = region_data["AmountSpent"].sum()

    col1, col2 = st.columns(2)

    col1.metric("Allocated", f"₹ {format_indian_currency(total_alloc_r)}")
    col2.metric("Utilized", f"₹ {format_indian_currency(total_spent_r)}")

    st.markdown("---")
    spacer(20)

    st.markdown("### 📊 Department-wise Allocation")

    dept_region = region_data.groupby("Department", as_index=False).agg({
        "AmountAllocated": "sum"
    })

    fig_region = px.bar(
        dept_region,
        x="Department",
        y="AmountAllocated",
        color="Department",
        title="Department Allocation"
    )

    dept_region["Amount_fmt"] = dept_region["AmountAllocated"].apply(
        lambda x: "₹ " + format_indian_currency(x)
    )

    fig_region.update_traces(
        hovertemplate="Department: %{x}<br>Amount: %{customdata}<extra></extra>",
        customdata=dept_region["Amount_fmt"]
    )

    fig_region.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )

    st.plotly_chart(fig_region, use_container_width=True)

    st.markdown("---")
    spacer(20)


   # =========================
    # 🟢 Department Utilization (Advanced)
    # =========================
    st.markdown("###  Department Utilization ")
    
    col1, col2 = st.columns(2)
    
    # -------------------------
    # GAUGE (Overall Utilization)
    # -------------------------
    with col1:
    
        total_alloc_r = region_data["AmountAllocated"].sum()
        total_spent_r = region_data["AmountSpent"].sum()
    
        overall_util = (total_spent_r / total_alloc_r) * 100 if total_alloc_r else 0
    
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_util,
            number={'suffix': "%"},
            title={'text': "Overall Utilization %"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 50], 'color': "#7f1d1d"},
                    {'range': [50, 75], 'color': "#f59e0b"},
                    {'range': [75, 100], 'color': "#10b981"}
                ]
            }
        ))
    
        fig_gauge.update_layout(
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0")
        )
    
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    
    # -------------------------
    # RANKING BAR CHART
    # -------------------------
    with col2:
    
        dept_util = region_data.groupby("Department").agg({
            "AmountAllocated": "sum",
            "AmountSpent": "sum"
        }).reset_index()
    
        dept_util["UtilizationRate"] = dept_util["AmountSpent"] / dept_util["AmountAllocated"]
    
        # sort
        dept_util = dept_util.sort_values("UtilizationRate", ascending=False)
    
        # full label
        dept_util["Util_full"] = dept_util.apply(
            lambda x: f"{x['UtilizationRate']*100:.2f}% (₹ {format_indian_currency(x['AmountSpent'])})",
            axis=1
        )
    
        fig_util_adv = px.bar(
            dept_util,
            x="UtilizationRate",
            y="Department",
            orientation="h",
            color="UtilizationRate",
            color_continuous_scale="Greens",
            title="Department Utilization Ranking"
        )
    
        fig_util_adv.update_traces(
            hovertemplate="Department: %{y}<br>%{customdata}<extra></extra>",
            customdata=dept_util["Util_full"]
        )
    
        fig_util_adv.update_layout(
            height=400,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
            xaxis_title="Utilization Rate",
            yaxis_title="Department"
        )
    
        st.plotly_chart(fig_util_adv, use_container_width=True)

    st.markdown("---")
    spacer(20)

    # =========================
    # 🔴 Department-wise Leakage (Treemap)
    # =========================
    st.markdown("###  Department-wise Leakage")
    
    dept_leak = region_data.groupby("Department").agg({
        "AmountAllocated": "sum",
        "AmountSpent": "sum"
    }).reset_index()
    
    # calculate leakage
    dept_leak["Leakage"] = dept_leak["AmountAllocated"] - dept_leak["AmountSpent"]
    
    # total leakage
    total_leakage = dept_leak["Leakage"].sum()
    
    # percentage
    dept_leak["Leak_pct"] = dept_leak["Leakage"] / total_leakage
    
    # combined display
    dept_leak["Leak_full"] = dept_leak.apply(
        lambda x: f"₹ {format_indian_currency(x['Leakage'])} ({x['Leak_pct']*100:.2f}%)",
        axis=1
    )
    
    # treemap
    fig_tree = px.treemap(
        dept_leak,
        path=["Department"],
        values="Leakage",
        color="Leakage",
        color_continuous_scale="Reds",
        title="Leakage Distribution by Department"
    )
    
    fig_tree.update_traces(
        textinfo="label+percent entry",
        hovertemplate="Department: %{label}<br>Leakage: %{customdata}<extra></extra>",
        customdata=dept_leak["Leak_full"]
    )
    
    fig_tree.update_layout(
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0")
    )
    
    st.plotly_chart(fig_tree, use_container_width=True)

    util_rate_r = (total_spent_r / total_alloc_r) if total_alloc_r else 0
    leakage_r = total_alloc_r - total_spent_r

    st.markdown("---")
    spacer(20)

    st.subheader("Regional Performance Analysis & Insights")


    st.markdown(f"""
    <div class="custom-alert alert-medium">
    • Total Allocation: ₹ {format_indian_currency(total_alloc_r)}<br>
    • Utilization Rate: {util_rate_r:.2%}<br>
    • Estimated Leakage: ₹ {format_indian_currency(leakage_r)}<br><br>
    👉 Regions with lower utilization may indicate inefficiencies or delays in fund deployment.
    </div>
    """, unsafe_allow_html=True)
spacer(20)
st.warning("Disclaimer: This Streamlit app may occasionally produce inaccurate or incomplete results and should not be solely relied upon for critical decisions.")
