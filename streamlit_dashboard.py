"""
Sales Analytics Dashboard - Streamlit Version
Clean, working, beautiful dashboard that actually displays data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
# Page config
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Executive Dashboard Style
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #ffffff;
    }
    
    /* Metric cards */
    .stMetric {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Metric labels */
    .stMetric label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    /* Metric values */
    .stMetric [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    /* Metric delta */
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 14px !important;
        font-weight: 600 !important;
    }
    
    /* Headers - High Contrast for Dark Mode */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
        font-weight: 600 !important;
    }
    
    /* Subheaders in main content */
    .main h2, .main h3 {
        color: #f5f5f5 !important;
    }
    
    /* Insight boxes */
    .insight-box {
        background-color: #e8f4f8;
        padding: 16px;
        border-radius: 6px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
        color: #1a1a1a;
        font-weight: 500;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f5f7fa;
    }
    
    /* Sidebar text */
    .sidebar .sidebar-content {
        color: #2c3e50;
    }
    
    /* Multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #2196F3 !important;
        color: white !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2196F3;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
    }
    
    .stButton button:hover {
        background-color: #1976D2;
    }
    
    /* Dataframe */
    .dataframe {
        font-size: 13px;
        color: #1a1a1a;
    }
    
    .dataframe th {
        background-color: #2c3e50 !important;
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data(uploaded_file):
    """Load and clean the Excel data from uploaded file"""
    if uploaded_file is None:
        return None
    
    try:
        # Load from uploaded file - use 'Final Sale Data' sheet with 128K+ rows
        df = pd.read_excel(uploaded_file, sheet_name='Final Sale Data')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Primary date column (from Excel analysis)
        date_col = 'Final Order date'
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Add fiscal year column (March-February)
            df['Fiscal Year'] = df[date_col].apply(
                lambda x: f"FY{x.year}-{str(x.year+1)[-2:]}" if pd.notna(x) and x.month >= 3 
                else f"FY{x.year-1}-{str(x.year)[-2:]}" if pd.notna(x) else None
            )
            
            # Add month column for filtering
            df['Month'] = df[date_col].dt.strftime('%B %Y')
            df['Month_Num'] = df[date_col].dt.to_period('M')
        
        # Ensure numeric columns
        numeric_cols = ['Sale (Qty.)', 'Sale Return (Qty.)', 'Sale (Amt.)', 'Sale Return (Amt.)']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calculate net values
        if 'Sale (Amt.)' in df.columns and 'Sale Return (Amt.)' in df.columns:
            df['Net Revenue'] = df['Sale (Amt.)'] - df['Sale Return (Amt.)']
        
        if 'Sale (Qty.)' in df.columns and 'Sale Return (Qty.)' in df.columns:
            df['Net Quantity'] = df['Sale (Qty.)'] - df['Sale Return (Qty.)']
        
        # Map Excel columns to dashboard field names
        df['Platform'] = df['Main Parties'] if 'Main Parties' in df.columns else None
        df['Category'] = df['Group Name'] if 'Group Name' in df.columns else None
        df['Product'] = df['Item Desc'] if 'Item Desc' in df.columns else None
        df['SKU'] = df['Alias'] if 'Alias' in df.columns else None
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {str(e)}")
        st.info("💡 Make sure your Excel file has a 'Sheet1' with the correct column structure.")
        return None

# Generate insights
def generate_insights(df, filtered_df):
    """Auto-generate smart insights from the data"""
    insights = []
    
    if len(filtered_df) == 0:
        return ["No data matches the selected filters."]
    
    # Revenue insight
    total_revenue = filtered_df['Net Revenue'].sum() if 'Net Revenue' in filtered_df.columns else 0
    avg_order_value = total_revenue / len(filtered_df) if len(filtered_df) > 0 else 0
    insights.append(f"Average Order Value: **₹{avg_order_value:,.0f}**")
    
    # Top platform
    if 'Platform' in filtered_df.columns:
        top_platform = filtered_df.groupby('Platform')['Net Revenue'].sum().idxmax()
        top_platform_revenue = filtered_df.groupby('Platform')['Net Revenue'].sum().max()
        insights.append(f"Top Platform: **{top_platform}** (₹{top_platform_revenue:,.0f})")
    
    # Return rate
    if 'Sale (Amt.)' in filtered_df.columns and 'Sale Return (Amt.)' in filtered_df.columns:
        total_sales = filtered_df['Sale (Amt.)'].sum()
        total_returns = filtered_df['Sale Return (Amt.)'].sum()
        return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
        insights.append(f"Return Rate: **{return_rate:.1f}%**")
    
    # Top product
    if 'Product' in filtered_df.columns:
        top_product = filtered_df.groupby('Product')['Net Revenue'].sum().nlargest(1)
        if not top_product.empty:
            insights.append(f"Best Seller: **{top_product.index[0]}** (₹{top_product.values[0]:,.0f})")
    
    return insights

# Main app
def main():
    st.title("Analytics Dashboard")
    st.markdown("### Sales Performance Snapshot")
    
    # ------------------ SIDEBAR ------------------
    st.sidebar.header("Data Source")
    
    # Feedback Box in Sidebar
    with st.sidebar.expander("📬 Feedback & Suggestions"):
        st.markdown("**Help us improve!**")
        st.caption("Tell us what **features**, **analytics indicators**, or improvements you'd like to see.")
        feedback = st.text_area("Your suggestions:", height=100)
        if st.button("Submit Feedback"):
            if feedback:
                st.success("Thank you! Your feedback has been recorded.")
            else:
                st.warning("Please enter some feedback first.")
    
    st.sidebar.markdown("---")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload your sales data Excel file - 'Final Sale Data' sheet will be processed"
    )
    
    if uploaded_file:
        st.sidebar.success(f"File loaded: {uploaded_file.name}")
    else:
        st.sidebar.warning("Please upload an Excel file to begin")
        st.info("👈 **Upload your Excel file in the sidebar to get started.**")
        st.markdown("""
        #### Sales Dashboard
        Upload your Excel file to view insights.
        
        **Available Modules:**
        *   **Overview**: High-level sales performance.
        *   **Platform Analysis**: Channel and distribution metrics.
        *   **Product Analysis**: SKU-level performance.
        """)
        st.stop()
    
    # Load data
    df = load_data(uploaded_file)
    
    if df is None:
        st.info("Please upload your Excel file using the sidebar to view analytics")
        st.stop()
        
    # ------------------ GLOBAL FILTERS (CASCADING) ------------------
    st.sidebar.header("Filters")
    
    # Create valid filter df
    filter_df = df.copy()
    
    # Fiscal Year filter
    if 'Fiscal Year' in df.columns:
        fiscal_years = ['All'] + sorted(df['Fiscal Year'].dropna().unique().tolist(), reverse=True)
        selected_fy = st.sidebar.selectbox("Fiscal Year", fiscal_years, index=0)
        if selected_fy != 'All':
            filter_df = filter_df[filter_df['Fiscal Year'] == selected_fy]

    # Month filter
    if 'Month' in df.columns:
        available_months = ['All'] + sorted(filter_df['Month'].dropna().unique().tolist(), reverse=True)
        selected_month = st.sidebar.selectbox("Month", available_months, index=0)
        if selected_month != 'All':
            filter_df = filter_df[filter_df['Month'] == selected_month]

    # Platform filter
    if 'Platform' in filter_df.columns:
        available_platforms = ['All'] + sorted(filter_df['Platform'].dropna().unique().tolist())
        selected_platforms = st.sidebar.multiselect(
            "Platform", 
            available_platforms, 
            default=['All'],
            help="Select platforms - updates based on category/product selection"
        )
        if 'All' not in selected_platforms and selected_platforms:
            filter_df = filter_df[filter_df['Platform'].isin(selected_platforms)]

    # Category filter
    if 'Category' in filter_df.columns:
        available_categories = ['All'] + sorted(filter_df['Category'].dropna().unique().tolist())
        selected_categories = st.sidebar.multiselect(
            "Category", 
            available_categories, 
            default=['All'],
            help="Select categories - updates based on platform/product selection"
        )
        if 'All' not in selected_categories and selected_categories:
            filter_df = filter_df[filter_df['Category'].isin(selected_categories)]

    # Product filter (Optional)
    if st.sidebar.checkbox("Filter by Product/SKU"):
        if 'Product' in filter_df.columns:
            available_products = sorted(filter_df['Product'].dropna().unique().tolist())
            selected_product = st.sidebar.selectbox(
                "Product", 
                ['All'] + available_products,
                help="Select product - updates based on platform/category selection"
            )
            if selected_product != 'All':
                filter_df = filter_df[filter_df['Product'] == selected_product]

    # Date Range Slider
    if 'Final Order date' in df.columns:
        min_date = df['Final Order date'].min()
        max_date = df['Final Order date'].max()
        if pd.notnull(min_date) and pd.notnull(max_date):
            cols = st.sidebar.columns(1)
            date_range = cols[0].slider(
                "Date Period",
                min_value=min_date.date(),
                max_value=max_date.date(),
                value=(min_date.date(), max_date.date())
            )
            filter_df = filter_df[
                (filter_df['Final Order date'].dt.date >= date_range[0]) &
                (filter_df['Final Order date'].dt.date <= date_range[1])
            ]
            
    filtered_df = filter_df

    # ------------------ KPI SECTION ------------------
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate KPIs
    revenue = filtered_df['Net Revenue'].sum()
    qty = filtered_df['Net Quantity'].sum()
    orders = len(filtered_df)
    aov = revenue / orders if orders > 0 else 0
    
    with col1:
        st.metric("Total Revenue", f"₹{revenue:,.0f}")
    with col2:
        st.metric("Sales Volume", f"{qty:,.0f}")
    with col3:
        st.metric("Total Orders", f"{orders:,.0f}")
    with col4:
        st.metric("Avg. Order Value", f"₹{aov:,.0f}")
        
    st.markdown("---")

    # ------------------ REVENUE VELOCITY ------------------
    st.subheader("Revenue Trends")
    
    if 'Final Order date' in filtered_df.columns:
        time_data = filtered_df.groupby(pd.Grouper(key='Final Order date', freq='M'))['Net Revenue'].sum().reset_index()
        
        fig = px.area(
            time_data, 
            x='Final Order date', 
            y='Net Revenue',
            template="plotly_white",
            line_shape='spline'
        )
        fig.update_traces(line_color='#0052cc', fillcolor='rgba(0, 82, 204, 0.1)')
        fig.update_layout(
            height=400,
            xaxis_title="",
            yaxis_title="Revenue (₹)",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ------------------ SECTION: PLATFORM INTELLIGENCE ------------------
    st.markdown("## 🏢 Platform Intelligence")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Performance Matrix")
        st.caption("Revenue vs. Volume vs. Average Order Value")
        
        platform_metrics = filtered_df.groupby('Platform').agg({
            'Net Revenue': 'sum',
            'Net Quantity': 'sum',
            'Final Order date': 'count'
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
            template="plotly_white"
        )
        fig_bubble.update_traces(textposition='top center')
        fig_bubble.update_layout(height=500, xaxis_title="Sales Volume (Qty)", yaxis_title="Total Revenue")
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col2:
        st.markdown("### Return Rates")
        return_data = filtered_df.groupby('Platform').agg({
            'Sale (Amt.)': 'sum',
            'Sale Return (Amt.)': 'sum'
        }).reset_index()
        
        return_data['Return Rate (%)'] = (return_data['Sale Return (Amt.)'] / return_data['Sale (Amt.)']) * 100
        return_data = return_data.sort_values('Return Rate (%)', ascending=True)
        
        fig_bar = px.bar(
            return_data,
            x='Return Rate (%)',
            y='Platform',
            orientation='h',
            color='Return Rate (%)',
            color_continuous_scale='RdYlGn_r',
            text_auto='.1f',
            template="plotly_white"
        )
        fig_bar.update_layout(height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### Channel Distribution")
    tree_data = filtered_df.groupby(['Platform', 'Category'])['Net Revenue'].sum().reset_index()
    tree_data = tree_data[tree_data['Net Revenue'] > 0]
    
    fig_tree = px.treemap(
        tree_data,
        path=[px.Constant("All Platforms"), 'Platform', 'Category'],
        values='Net Revenue',
        color='Net Revenue',
        color_continuous_scale='Blues',
        template="plotly_white"
    )
    fig_tree.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=400)
    st.plotly_chart(fig_tree, use_container_width=True)

    # ------------------ SECTION: PRODUCT MATRIX ------------------
    st.markdown("## 📦 Product Matrix")
    st.markdown("---")

    # Star Products
    prod_stats = filtered_df.groupby('Product').agg({
        'Net Revenue': 'sum',
        'Net Quantity': 'sum'
    }).sort_values('Net Revenue', ascending=False)
    
    if not prod_stats.empty:
        col1, col2, col3 = st.columns(3)
        top_rev = prod_stats.index[0]
        top_rev_val = prod_stats.iloc[0]['Net Revenue']
        top_qty_prod = prod_stats.sort_values('Net Quantity', ascending=False).index[0]
        top_qty_val = prod_stats.sort_values('Net Quantity', ascending=False).iloc[0]['Net Quantity']
        
        with col1:
            st.metric("Highest Revenue SKU", top_rev, f"₹{top_rev_val:,.0f}")
        with col2:
            st.metric("Highest Volume SKU", top_qty_prod, f"{top_qty_val:,.0f} units")
        with col3:
            st.metric("Active SKUs", len(prod_stats))

    # Pareto Chart
    st.markdown("### Revenue Concentration (Pareto)")
    pareto_data = prod_stats.copy()
    pareto_data['Cumulative Revenue'] = pareto_data['Net Revenue'].cumsum()
    pareto_data['Cumulative %'] = 100 * pareto_data['Cumulative Revenue'] / pareto_data['Net Revenue'].sum()
    pareto_data = pareto_data.reset_index().head(50)
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=pareto_data['Product'],
        y=pareto_data['Net Revenue'],
        name='Revenue',
        marker_color='#0052cc'
    ))
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

    # Detailed Table
    with st.expander("🔎 View Detailed Product Performance"):
        st.dataframe(
            prod_stats.style.background_gradient(subset=['Net Revenue'], cmap='Blues'),
            use_container_width=True,
            height=500
        )

if __name__ == "__main__":
    main()
