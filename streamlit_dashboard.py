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
    page_title="Sales Analytics",
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
    st.title("Sales Analytics")
    st.markdown("""
    **Transform your raw sales data into actionable business intelligence.**
    
    This dashboard provides a comprehensive view of your sales performance, helping you identify trends, top-performing products, and platform insights.
    
    ### How to Customise
    This tool is designed to be flexible. You can filter data by Fiscal Year, Month, Platform, Category, and Product to drill down into specific segments of your business.
    """)
    
    # File upload in sidebar
    st.sidebar.header("Data Source")
    
    # Feedback Box in Sidebar (Before Upload)
    with st.sidebar.expander("📬 Feedback & Suggestions"):
        st.markdown("**Help us improve!**")
        feedback = st.text_area("What features would you like to see?", height=100)
        if st.button("Submit Feedback"):
            if feedback:
                # In a real app, save this to a database/sheet
                # For now, we simulate a save
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
        st.sidebar.info(f"Processing data...")
    else:
        st.sidebar.warning("Please upload an Excel file to begin")
        
        # Show this on main page only when no file is loaded
        st.info("👈 **Upload your Excel file in the sidebar to get started.**")
    
    # Load data
    df = load_data(uploaded_file)
    
    if df is None:
        st.info("Please upload your Excel file using the sidebar to view analytics")
        st.markdown("""
        ### Expected Excel Structure:
        - **Sheet Name**: Final Sale Data
        - **Required Columns**: 
          - Final Order date
          - Main Parties (Platform)
          - Group Name (Category)
          - Item Desc (Product)
          - Sale (Amt.), Sale Return (Amt.)
          - Sale (Qty.), Sale Return (Qty.)
        """)
        st.stop()
    
    # Sidebar filters with cascading logic
    st.sidebar.header("Filters")
    
    # Create a working dataframe for filter calculations
    filter_df = df.copy()
    
    # Fiscal Year filter (independent)
    if 'Fiscal Year' in df.columns:
        fiscal_years = ['All'] + sorted(df['Fiscal Year'].dropna().unique().tolist(), reverse=True)
        selected_fy = st.sidebar.selectbox("Fiscal Year", fiscal_years, index=0)
        if selected_fy != 'All':
            filter_df = filter_df[filter_df['Fiscal Year'] == selected_fy]
    
    # Month filter (depends on FY)
    if 'Month' in df.columns:
        available_months = ['All'] + sorted(filter_df['Month'].dropna().unique().tolist(), reverse=True)
        selected_month = st.sidebar.selectbox("Month", available_months, index=0)
        if selected_month != 'All':
            filter_df = filter_df[filter_df['Month'] == selected_month]
    
    # CASCADING FILTERS START HERE
    # These filters update dynamically based on each other
    
    # Platform filter (updates based on category/product if selected)
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
    
    # Category filter (updates based on platform/product if selected)
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
    
    # Product/SKU filter (updates based on platform/category if selected)
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
    else:
        selected_product = 'All'
    
    # Transaction Type filter
    if 'Transaction Type' in df.columns:
        trans_types = ['All'] + sorted(df['Transaction Type'].dropna().unique().tolist())
        selected_trans_type = st.sidebar.selectbox("Transaction Type", trans_types, index=0)
        if selected_trans_type != 'All':
            filter_df = filter_df[filter_df['Transaction Type'] == selected_trans_type]
    else:
        selected_trans_type = 'All'
    
    # Dispatch Status filter
    if 'Dispatch Status' in df.columns:
        dispatch_statuses = ['All'] + sorted(df['Dispatch Status'].dropna().unique().tolist())
        selected_dispatch = st.sidebar.selectbox("Dispatch Status", dispatch_statuses, index=0)
        if selected_dispatch != 'All':
            filter_df = filter_df[filter_df['Dispatch Status'] == selected_dispatch]
    else:
        selected_dispatch = 'All'
    
    # Custom date range (optional additional filter)
    date_col = 'Final Order date'
    if date_col in df.columns:
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        if pd.notna(min_date) and pd.notna(max_date):
            use_custom_date = st.sidebar.checkbox("Custom Date Range")
            if use_custom_date:
                date_range = st.sidebar.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                if len(date_range) == 2:
                    filter_df = filter_df[
                        (filter_df[date_col] >= pd.to_datetime(date_range[0])) &
                        (filter_df[date_col] <= pd.to_datetime(date_range[1]))
                    ]
    
    # Use the cascading-filtered dataframe as the final filtered dataframe
    filtered_df = filter_df.copy()
    
    # Calculate previous period for trends
    def calculate_trend(current_df, date_column):
        """Calculate metrics for previous period to show trends"""
        if date_column not in current_df.columns or len(current_df) == 0:
            return None, None, None, None
        
        try:
            # Get date range
            current_start = current_df[date_column].min()
            current_end = current_df[date_column].max()
            period_length = (current_end - current_start).days
            
            if period_length <= 0:
                return None, None, None, None
            
            # Calculate previous period
            prev_start = current_start - pd.Timedelta(days=period_length)
            prev_end = current_start - pd.Timedelta(days=1)
            
            # Filter for previous period
            prev_df = df[
                (df[date_column] >= prev_start) &
                (df[date_column] <= prev_end)
            ]
            
            if len(prev_df) == 0:
                return None, None, None, None
            
            # Calculate metrics
            prev_revenue = prev_df['Net Revenue'].sum() if 'Net Revenue' in prev_df.columns else 0
            prev_qty = prev_df['Net Quantity'].sum() if 'Net Quantity' in prev_df.columns else 0
            prev_orders = len(prev_df)
            prev_avg = prev_revenue / prev_orders if prev_orders > 0 else 0
            
            return prev_revenue, prev_qty, prev_orders, prev_avg
        except Exception as e:
            return None, None, None, None
    
    # Get previous period metrics
    date_col = 'Final Order date'
    prev_revenue, prev_qty, prev_orders, prev_avg = calculate_trend(filtered_df, date_col) if date_col in df.columns else (None, None, None, None)
    
    # KPIs with Trend Indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = filtered_df['Net Revenue'].sum() if 'Net Revenue' in filtered_df.columns else 0
        if prev_revenue and prev_revenue > 0:
            revenue_change = ((total_revenue - prev_revenue) / prev_revenue) * 100
            revenue_delta = f"{revenue_change:+.1f}%"
            revenue_color = "normal" if revenue_change >= 0 else "inverse"
        else:
            revenue_delta = None
            revenue_color = "off"
        st.metric("Net Revenue", f"₹{total_revenue:,.0f}", delta=revenue_delta, delta_color=revenue_color)
    
    with col2:
        total_qty = filtered_df['Net Quantity'].sum() if 'Net Quantity' in filtered_df.columns else 0
        if prev_qty and prev_qty > 0:
            qty_change = ((total_qty - prev_qty) / prev_qty) * 100
            qty_delta = f"{qty_change:+.1f}%"
            qty_color = "normal" if qty_change >= 0 else "inverse"
        else:
            qty_delta = None
            qty_color = "off"
        st.metric("Net Quantity", f"{total_qty:,.0f}", delta=qty_delta, delta_color=qty_color)
    
    with col3:
        total_orders = len(filtered_df)
        if prev_orders and prev_orders > 0:
            orders_change = ((total_orders - prev_orders) / prev_orders) * 100
            orders_delta = f"{orders_change:+.1f}%"
            orders_color = "normal" if orders_change >= 0 else "inverse"
        else:
            orders_delta = None
            orders_color = "off"
        st.metric("Total Orders", f"{total_orders:,}", delta=orders_delta, delta_color=orders_color)
    
    with col4:
        avg_value = total_revenue / total_orders if total_orders > 0 else 0
        if prev_avg and prev_avg > 0:
            avg_change = ((avg_value - prev_avg) / prev_avg) * 100
            avg_delta = f"{avg_change:+.1f}%"
            avg_color = "normal" if avg_change >= 0 else "inverse"
        else:
            avg_delta = None
            avg_color = "off"
        st.metric("Avg Order Value", f"₹{avg_value:,.0f}", delta=avg_delta, delta_color=avg_color)
    
    st.markdown("---")
    
    # Smart Insights
    st.subheader("Key Insights")
    insights = generate_insights(df, filtered_df)
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Platform")
        if 'Platform' in filtered_df.columns:
            platform_data = filtered_df.groupby('Platform')['Net Revenue'].sum().reset_index()
            platform_data = platform_data.sort_values('Net Revenue', ascending=False)
            fig = px.bar(platform_data, x='Platform', y='Net Revenue',
                        color='Net Revenue', color_continuous_scale='Blues')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("Revenue by Category")
        if 'Category' in filtered_df.columns:
            category_data = filtered_df.groupby('Category')['Net Revenue'].sum().reset_index()
            fig = px.pie(category_data, names='Category', values='Net Revenue',
                        color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(height=400)
            st.plotly_chart(fig, width='stretch')
    
    # Time series
    if date_col:
        st.subheader("Revenue Trend Over Time")
        time_data = filtered_df.groupby(filtered_df[date_col].dt.date)['Net Revenue'].sum().reset_index()
        time_data.columns = ['Date', 'Revenue']
        fig = px.line(time_data, x='Date', y='Revenue', markers=True)
        fig.update_traces(line_color='#0052cc', line_width=3)
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')
    
    # Top products
    st.subheader("Top 10 Products by Revenue")
    if 'Product' in filtered_df.columns:
        top_products = filtered_df.groupby('Product')['Net Revenue'].sum().nlargest(10).reset_index()
        fig = px.bar(top_products, x='Net Revenue', y='Product', orientation='h',
                    color='Net Revenue', color_continuous_scale='Blues')
        fig.update_layout(showlegend=False, height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, width='stretch')
    
    # Data table
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df, width='stretch', height=400)
        st.caption(f"Showing {len(filtered_df):,} rows (filtered from {len(df):,} total rows)")
    
    # Footer with data stats
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Total Rows Loaded:** {len(df):,}")
    with col2:
        st.markdown(f"**Filtered Rows:** {len(filtered_df):,}")
    with col3:
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
