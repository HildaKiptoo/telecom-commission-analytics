import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Telecom Agent Performance", layout="wide", initial_sidebar_state="expanded")


# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/telecom_data.csv")
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error("Please ensure 'telecom_data.csv' is inside the 'data/' folder.")
    st.stop()

# --- 3. Interactive Sidebar Slicers ---
st.sidebar.header("Filter Dashboard")

# County Filter
county_list = df['County'].unique().tolist()
selected_counties = st.sidebar.multiselect("Select County", county_list, default=county_list)

# Category Filter
category_list = df['Category'].unique().tolist()
selected_categories = st.sidebar.multiselect("Select Product Category", category_list, default=category_list)

# Apply Filters to Dataframe
filtered_df = df[(df['County'].isin(selected_counties)) & (df['Category'].isin(selected_categories))]

# --- 4. Calculate KPIs (Using Filtered Data) ---
total_revenue = filtered_df['Gross_Revenue'].sum()
total_commission = filtered_df['Commission'].sum()
active_agents = filtered_df['Agent_Name'].nunique()
mom_growth = "5.60%"

# --- 5. KPI Banner ---
st.markdown("<h2 style='text-align: center; color: #FFC107;'>Telecom Agent Performance & Commission Analytics</h2>",
            unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Gross Revenue", f"{total_revenue / 1e9:.2f}bn")
col2.metric("Total Commission Paid", f"{total_commission / 1e6:.2f}M")
col3.metric("MoM Growth %", mom_growth)
col4.metric("Active Agent Count", active_agents)

st.markdown("---")

# --- 6. Charts: Row 1 (Trends & Categories) ---
row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    # Group by month for the line chart
    trend_data = filtered_df.groupby(filtered_df['Date'].dt.to_period('M')).sum(numeric_only=True).reset_index()
    trend_data['Date'] = trend_data['Date'].astype(str)

    fig_trend = px.line(trend_data, x='Date', y=['Gross_Revenue', 'Commission'],
                        title="Revenue & Commission Trends",
                        color_discrete_sequence=['#3B7FB3', '#FFC107'],
                        template="plotly_dark")
    fig_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", legend_title_text='')
    st.plotly_chart(fig_trend, width="stretch")

with row1_col2:
    cat_data = filtered_df.groupby('Category')['Gross_Revenue'].sum().reset_index()
    fig_cat = px.pie(cat_data, values='Gross_Revenue', names='Category', hole=0.6,
                     title="Revenue by Product Category",
                     color_discrete_sequence=['#3B7FB3', '#FFC107', '#444444'],
                     template="plotly_dark")
    fig_cat.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_cat, width="stretch")

# --- 7. Charts: Row 2 (County Waterfall & Top Agents) ---
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    county_data = filtered_df.groupby('County')['Gross_Revenue'].sum().sort_values().reset_index()

    fig_waterfall = go.Figure(go.Waterfall(
        name="2026", orientation="v",
        measure=["relative"] * len(county_data) + ["total"],
        x=county_data['County'].tolist() + ["Total"],
        y=county_data['Gross_Revenue'].tolist() + [county_data['Gross_Revenue'].sum()],
        decreasing={"marker": {"color": "#444444"}},
        increasing={"marker": {"color": "#3B7FB3"}},
        totals={"marker": {"color": "#FFC107"}}
    ))
    fig_waterfall.update_layout(title="Regional Revenue Distribution",
                                template="plotly_dark",
                                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_waterfall, width="stretch")

with row2_col2:
    top_agents = filtered_df.groupby('Agent_Name')['Gross_Revenue'].sum().nlargest(10).sort_values().reset_index()
    fig_agents = px.bar(top_agents, x='Gross_Revenue', y='Agent_Name', orientation='h',
                        title="Top 10 Agents by Revenue",
                        color_discrete_sequence=['#3B7FB3'],
                        template="plotly_dark")
    fig_agents.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_agents, width="stretch")