import streamlit as st
import pandas as pd
import plotly.express as px

# Setup page
st.set_page_config(page_title="Product Analysis", page_icon="📦", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #172b4d;
    }

    /* Main background */
    .stApp {
        background-color: #f4f6f8;
    }
    
    /* Metric cards */
    .stMetric {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #dfe1e6;
        box-shadow: 0 1px 2px rgba(9, 30, 66, 0.08);
    }
    
    /* Metric labels */
    .stMetric label {
        color: #5e6c84 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Metric values */
    .stMetric [data-testid="stMetricValue"] {
        color: #172b4d !important;
        font-size: 32px !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Headers */
    h1 {
        color: #172b4d !important;
        font-weight: 700 !important;
    }
    
    h2, h3 {
        color: #172b4d !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Product Matrix")

if 'data' not in st.session_state or st.session_state.data is None:
    st.warning("⚠️ No data found. Please upload a file on the Main Page.")
    st.stop()

df = st.session_state.data
filter_df = df.copy()

# Sidebar: Category Focus
cols_side = st.sidebar.columns(1)
selected_cat = st.sidebar.selectbox("Focus Category", ['All'] + sorted(df['Category'].dropna().unique().tolist()))

if selected_cat != 'All':
    filter_df = filter_df[filter_df['Category'] == selected_cat]

# --- MAIN CONTENT ---

# 1. Top Performers Cards
st.subheader("Star Products")
col1, col2, col3 = st.columns(3)

# Group by product
prod_stats = filter_df.groupby('Product').agg({
    'Net Revenue': 'sum',
    'Net Quantity': 'sum'
}).sort_values('Net Revenue', ascending=False)

if not prod_stats.empty:
    top_rev = prod_stats.index[0]
    top_rev_val = prod_stats.iloc[0]['Net Revenue']
    
    top_qty_prod = prod_stats.sort_values('Net Quantity', ascending=False).index[0]
    top_qty_val = prod_stats.sort_values('Net Quantity', ascending=False).iloc[0]['Net Quantity']
    
    with col1:
        st.metric("Highest Revenue SKU", top_rev, f"₹{top_rev_val:,.0f}")
    with col2:
        st.metric("Highest Volume SKU", top_qty_prod, f"{top_qty_val:,.0f} units")
    with col3:
        # Most returned?
        # Requires calculating return rate per product - might be intensive, stay simple for now
        st.metric("Active SKUs", len(prod_stats))

st.markdown("---")

# 2. Pareto Chart (80/20 Rule)
st.subheader("Revenue Concentration (Pareto Analysis)")
# Sort by revenue
pareto_data = prod_stats.copy()
pareto_data['Cumulative Revenue'] = pareto_data['Net Revenue'].cumsum()
pareto_data['Cumulative %'] = 100 * pareto_data['Cumulative Revenue'] / pareto_data['Net Revenue'].sum()
pareto_data = pareto_data.reset_index().head(50) # Top 50 for readability

# Dual axis chart
import plotly.graph_objects as go

fig_pareto = go.Figure()
# Bar for revenue
fig_pareto.add_trace(go.Bar(
    x=pareto_data['Product'],
    y=pareto_data['Net Revenue'],
    name='Revenue',
    marker_color='#0052cc'
))
# Line for cumulative %
fig_pareto.add_trace(go.Scatter(
    x=pareto_data['Product'],
    y=pareto_data['Cumulative %'],
    name='Cumulative %',
    yaxis='y2',
    mode='lines+markers',
    marker_color='#ffab00'
))

fig_pareto.update_layout(
    xaxis_title="Product (Top 50)",
    yaxis_title="Revenue",
    yaxis2=dict(title="Cumulative %", overlaying='y', side='right', range=[0, 110]),
    showlegend=False,
    height=500,
    template="plotly_white"
)
st.plotly_chart(fig_pareto, use_container_width=True)

# 3. Detailed SKU Table with Sparklines (Simulated with simple bars in another column if possible, or just heatmaps)
st.subheader("Detailed SKU Performance")

# Create a rich table
grid_df = prod_stats.reset_index()
grid_df['AOV'] = grid_df['Net Revenue'] / grid_df['Net Quantity']

st.dataframe(
    grid_df.style.background_gradient(subset=['Net Revenue'], cmap='Blues'),
    use_container_width=True,
    height=500
)
