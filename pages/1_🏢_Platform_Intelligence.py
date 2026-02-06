import streamlit as st
import pandas as pd
import plotly.express as px

# Setup page
st.set_page_config(page_title="Platform Intelligence", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    /* Reuse sleek CSS from main page */
    .stApp { background-color: #f4f6f8; }
    .stMetric { background-color: white; border: 1px solid #dfe1e6; }
    h1, h2, h3 { color: #172b4d !important; }
</style>
""", unsafe_allow_html=True)

st.title("Platform Intelligence")

# Check for data
if 'data' not in st.session_state or st.session_state.data is None:
    st.warning("⚠️ No data found. Please upload a file on the Main Page.")
    st.stop()

df = st.session_state.data
filter_df = df.copy()

# Sidebar Filters specific to this page
st.sidebar.header("Platform Context")
selected_platforms = st.sidebar.multiselect(
    "Compare Platforms",
    options=sorted(df['Platform'].dropna().unique()),
    default=sorted(df['Platform'].dropna().unique())[:3] # Default first 3
)

if selected_platforms:
    filter_df = filter_df[filter_df['Platform'].isin(selected_platforms)]

# --- MAIN CONTENT ---

# 1. Platform Performance Matrix (Bubble Chart)
# X: Quantity, Y: Revenue, Size: AOV, Color: Platform
st.subheader("Performance Matrix")
st.caption("Revenue vs. Volume vs. Average Order Value")

platform_metrics = filter_df.groupby('Platform').agg({
    'Net Revenue': 'sum',
    'Net Quantity': 'sum',
    'Final Order date': 'count' # Orders
}).reset_index()
platform_metrics['AOV'] = platform_metrics['Net Revenue'] / platform_metrics['Final Order date']

fig_bubble = px.scatter(
    platform_metrics,
    x="Net Quantity",
    y="Net Revenue",
    size="AOV",
    color="Platform",
    hover_name="Platform",
    text="Platform",
    size_max=60,
    template="plotly_white",
    title=""
)
fig_bubble.update_traces(textposition='top center')
fig_bubble.update_layout(height=500)
st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue Distribution (Treemap)")
    # Hierarchical view: Platform -> Category
    # Need to group by Platform AND Category
    tree_data = filter_df.groupby(['Platform', 'Category'])['Net Revenue'].sum().reset_index()
    # Filter out small values for cleaner chart
    tree_data = tree_data[tree_data['Net Revenue'] > 0]
    
    fig_tree = px.treemap(
        tree_data,
        path=[px.Constant("All Platforms"), 'Platform', 'Category'],
        values='Net Revenue',
        color='Net Revenue',
        color_continuous_scale='Blues',
        template="plotly_white"
    )
    fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=500)
    st.plotly_chart(fig_tree, use_container_width=True)

with col2:
    st.subheader("Return Rate Analysis")
    # Calculate return rate per platform
    return_data = filter_df.groupby('Platform').agg({
        'Sale (Amt.)': 'sum',
        'Sale Return (Amt.)': 'sum'
    }).reset_index()
    
    return_data['Return Rate (%)'] = (return_data['Sale Return (Amt.)'] / return_data['Sale (Amt.)']) * 100
    return_data = return_data.sort_values('Return Rate (%)', ascending=True) # Best first
    
    fig_bar = px.bar(
        return_data,
        x='Return Rate (%)',
        y='Platform',
        orientation='h',
        color='Return Rate (%)',
        color_continuous_scale='RdYlGn_r', # Red is high return (bad), Green is low
        text_auto='.1f'
    )
    fig_bar.update_layout(height=500)
    st.plotly_chart(fig_bar, use_container_width=True)

st.info("💡 **Insight**: High volume platforms with low return rates are your most efficient channels.")
