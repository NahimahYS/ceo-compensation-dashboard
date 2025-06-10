import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(
    page_title="CEO Compensation Dashboard",
    page_icon="💰",
    layout="wide"
)

# Title
st.title("💰 CEO Compensation Dashboard: The Pay Gap Story")
st.markdown("### Analyzing Fortune 500 CEO compensation across industries")

# Load your data with proper handling
@st.cache_data
def load_data():
    try:
        # Read Excel file
        df = pd.read_excel('Book1.xlsx')
        
        # Clean column names - remove any extra spaces
        df.columns = df.columns.str.strip()
        
        # Create exact column mapping for your data
        column_mapping = {
            'CEO Name': 'CEO_Name',
            'Company': 'Company',
            'Ticker': 'Ticker',
            'Industry': 'Industry',
            'Salary': 'Salary',
            'Pay Ratio': 'Pay_Ratio',
            'Median Worker Pay': 'Median_Worker_Pay',
            'Market Cap (Billions)': 'Market_Cap_Billions',
            'CEO Tenure (Years)': 'CEO_Tenure_Years',
            'Employees': 'Employees',
            'Pay Level': 'Pay_Level'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Convert numeric columns
        numeric_columns = ['Salary', 'Pay_Ratio', 'Market_Cap_Billions', 'CEO_Tenure_Years', 'Employees', 'Median_Worker_Pay']
        
        for col in numeric_columns:
            if col in df.columns:
                if col == 'Pay_Ratio':
                    # Special handling for pay ratio - it's in format "1,447:1"
                    df[col] = df[col].astype(str).str.replace(',', '')
                    df[col] = df[col].str.split(':').str[0]
                elif col in ['Salary', 'Median_Worker_Pay']:
                    # Remove dollar and commas from salary columns
                    df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '')
                else:
                    # For other numeric columns, just remove commas
                    df[col] = df[col].astype(str).str.replace(',', '')
                
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean string columns
        string_columns = ['CEO_Name', 'Company', 'Industry', 'Pay_Level']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Ensure Pay_Level is a category type with the correct order
        if 'Pay_Level' in df.columns:
            df['Pay_Level'] = pd.Categorical(df['Pay_Level'], 
                                             categories=['Minimal', 'Low', 'Medium', 'High', 'Extreme'], 
                                             ordered=True)
        
        # Remove any rows with missing critical data
        df = df.dropna(subset=['CEO_Name', 'Salary'])
        
        return df
        
    except Exception as e:
        st.error(f"Error in load_data: {str(e)}")
        raise e

# Load the data
try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.error("Please ensure 'Book1.xlsx' is in the correct format.")
    st.stop()

# Sidebar with filters
with st.sidebar:
    st.header("🔍 Filters")
    
    # Industry filter
    if 'Industry' in df.columns:
        industries = sorted([ind for ind in df['Industry'].unique() if ind and ind != 'nan'])
        selected_industries = st.multiselect(
            "Select Industries",
            options=industries,
            default=industries
        )
        if selected_industries:
            df_filtered = df[df['Industry'].isin(selected_industries)]
        else:
            df_filtered = df.copy()
    else:
        df_filtered = df.copy()
    
    # Pay level filter
    if 'Pay_Level' in df.columns:
        pay_levels = [level for level in ['Minimal', 'Low', 'Medium', 'High', 'Extreme'] 
                     if level in df['Pay_Level'].cat.categories]
        selected_pay_levels = st.multiselect(
            "Select Pay Levels",
            options=pay_levels,
            default=pay_levels
        )
        if selected_pay_levels:
            df_filtered = df_filtered[df_filtered['Pay_Level'].isin(selected_pay_levels)]
    
    st.markdown("---")
    st.markdown("### 📊 Data Summary")
    st.write(f"Total CEOs: {len(df_filtered)}")
    if len(df_filtered) > 0:
        st.write(f"Avg Salary: ${df_filtered['Salary'].mean()/1000000:.1f}M")

# Color map for pay levels
color_map = {
    'Minimal': '#059669',
    'Low': '#10b981', 
    'Medium': '#3b82f6',
    'High': '#f59e0b',
    'Extreme': '#ef4444'
}

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Summary", "📈 Inequality Analysis", "🏭 Industry Insights", "❓ Performance Question"])

# TAB 1: Executive Summary
with tab1:
    st.header("Executive Summary: The Shocking Truth")
    
    if len(df_filtered) > 0:
        # Calculate KPIs
        max_salary = df_filtered['Salary'].max()
        min_salary = df_filtered['Salary'].min()
        pay_gap = max_salary / min_salary if min_salary > 0 else 0
        avg_salary = df_filtered['Salary'].mean()
        
        # Pay ratio stats
        if 'Pay_Ratio' in df_filtered.columns:
            valid_ratios = df_filtered['Pay_Ratio'].dropna()
            if len(valid_ratios) > 0:
                max_ratio = valid_ratios.max()
                min_ratio = valid_ratios.min()
                ratio_gap = max_ratio / min_ratio if min_ratio > 0 else 0
            else:
                max_ratio = min_ratio = ratio_gap = 0
        else:
            max_ratio = min_ratio = ratio_gap = 0
            
        num_industries = df_filtered['Industry'].nunique()
        
        # Display KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="CEO Pay Gap",
                value=f"{pay_gap:.0f}x",
                delta="Highest to Lowest"
            )
        
        with col2:
            st.metric(
                label="Average CEO Pay",
                value=f"${avg_salary/1000000:.1f}M",
                delta=f"Across {len(df_filtered)} CEOs"
            )
        
        with col3:
            st.metric(
                label="Pay Ratio Gap",
                value=f"{ratio_gap:.0f}x" if ratio_gap > 0 else "N/A",
                delta=f"{min_ratio:.0f}:1 to {max_ratio:.0f}:1" if min_ratio > 0 else "N/A"
            )
        
        with col4:
            st.metric(
                label="Industries",
                value=num_industries,
                delta="Diverse sectors"
            )
        
        # CEO Salary Bar Chart
        st.subheader("CEO Compensation Ranking")
        
        # Sort by salary and take top 20
        df_chart = df_filtered.nlargest(20, 'Salary')[['CEO_Name', 'Company', 'Salary', 'Pay_Level']]
        df_chart = df_chart.sort_values('Salary', ascending=True)
        
        fig_bar = px.bar(
            df_chart, 
            x='Salary', 
            y='CEO_Name',
            orientation='h',
            color='Pay_Level',
            color_discrete_map=color_map,
            title="Top 20 CEO Total Compensation",
            hover_data={'Company': True, 'Salary': ':$,.0f'},
            category_orders={'Pay_Level': ['Minimal', 'Low', 'Medium', 'High', 'Extreme']}
        )
        
        fig_bar.update_layout(
            height=600,
            xaxis_title="Total Compensation ($)",
            yaxis_title="CEO",
            xaxis=dict(tickformat='$,.0f')
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Insight box
        highest_paid = df_filtered.loc[df_filtered['Salary'].idxmax()]
        lowest_paid = df_filtered.loc[df_filtered['Salary'].idxmin()]
        
        st.info(f"💡 **Key Insight:** {highest_paid['CEO_Name']} earns {pay_gap:.0f}x more than {lowest_paid['CEO_Name']}!")
    else:
        st.warning("No data available with current filters.")

# TAB 2: Inequality Analysis
with tab2:
    st.header("The Inequality Story")
    
    if len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Scatter plot: Salary vs Pay Ratio
            if 'Pay_Ratio' in df_filtered.columns:
                df_scatter = df_filtered[df_filtered['Pay_Ratio'].notna()]
                
                if len(df_scatter) > 0:
                    fig_scatter = px.scatter(
                        df_scatter,
                        x='Salary',
                        y='Pay_Ratio',
                        size='Employees' if 'Employees' in df_scatter.columns else None,
                        color='Industry',
                        hover_data=['CEO_Name', 'Company'],
                        title="CEO Salary vs Worker Pay Ratio"
                    )
                    
                    fig_scatter.update_layout(
                        height=450,
                        xaxis=dict(tickformat='$,.0f', title="CEO Salary ($)"),
                        yaxis=dict(title="Pay Ratio (CEO:Worker)")
                    )
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.info("No valid pay ratio data available")
            else:
                st.info("Pay ratio data not available")
        
        with col2:
            # Distribution of pay ratios
            if 'Pay_Ratio' in df_filtered.columns:
                df_hist = df_filtered[df_filtered['Pay_Ratio'].notna()]
                
                if len(df_hist) > 0:
                    fig_hist = px.histogram(
                        df_hist,
                        x='Pay_Ratio',
                        nbins=20,
                        title='Distribution of CEO-to-Worker Pay Ratios'
                    )
                    
                    fig_hist.update_layout(
                        height=450,
                        xaxis=dict(title="Pay Ratio"),
                        yaxis=dict(title="Number of Companies")
                    )
                    
                    st.plotly_chart(fig_hist, use_container_width=True)
        
        # Industry comparison table
        if 'Industry' in df_filtered.columns:
            st.subheader("Pay Inequality by Industry")
            
            industry_stats = []
            for industry in df_filtered['Industry'].unique():
                if industry and industry != 'nan':
                    ind_data = df_filtered[df_filtered['Industry'] == industry]
                    
                    stats = {
                        'Industry': industry,
                        'Number of CEOs': len(ind_data),
                        'Avg CEO Pay': f"${ind_data['Salary'].mean()/1000000:.1f}M",
                        'Max CEO Pay': f"${ind_data['Salary'].max()/1000000:.1f}M",
                        'Min CEO Pay': f"${ind_data['Salary'].min()/1000000:.1f}M"
                    }
                    
                    if 'Pay_Ratio' in ind_data.columns:
                        valid_ratios = ind_data['Pay_Ratio'].dropna()
                        if len(valid_ratios) > 0:
                            stats['Avg Pay Ratio'] = f"{valid_ratios.mean():.0f}:1"
                            stats['Max Pay Ratio'] = f"{valid_ratios.max():.0f}:1"
                    
                    industry_stats.append(stats)
            
            if industry_stats:
                st.dataframe(pd.DataFrame(industry_stats), use_container_width=True, hide_index=True)
    else:
        st.warning("No data available with current filters.")

# TAB 3: Industry Insights
with tab3:
    st.header("Industry Deep Dive")
    
    if len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Industry averages bar chart
            if 'Industry' in df_filtered.columns:
                industry_avg = df_filtered.groupby('Industry')['Salary'].mean().sort_values(ascending=True)
                industry_avg = industry_avg[industry_avg.index != 'nan']
                
                if len(industry_avg) > 0:
                    fig_industry = px.bar(
                        x=industry_avg.values,
                        y=industry_avg.index,
                        orientation='h',
                        title='Average CEO Compensation by Industry',
                        color=industry_avg.values,
                        color_continuous_scale='Viridis'
                    )
                    
                    fig_industry.update_layout(
                        height=500, 
                        showlegend=False,
                        xaxis=dict(tickformat='$,.0f', title="Average Salary ($)"),
                        yaxis=dict(title="Industry")
                    )
                    
                    st.plotly_chart(fig_industry, use_container_width=True)
        
        with col2:
            # Pay level distribution by industry
            if 'Pay_Level' in df_filtered.columns and 'Industry' in df_filtered.columns:
                df_stack = df_filtered[df_filtered['Industry'] != 'nan']
                
                if len(df_stack) > 0:
                    pay_level_counts = df_stack.groupby(['Industry', 'Pay_Level']).size().reset_index(name='count')
                    
                    fig_stacked = px.bar(
                        pay_level_counts,
                        x='Industry',
                        y='count',
                        color='Pay_Level',
                        title='Pay Level Distribution by Industry',
                        color_discrete_map=color_map,
                        category_orders={'Pay_Level': ['Minimal', 'Low', 'Medium', 'High', 'Extreme']}
                    )
                    
                    fig_stacked.update_layout(
                        height=500, 
                        xaxis_tickangle=-45,
                        yaxis=dict(title="Number of CEOs")
                    )
                    
                    st.plotly_chart(fig_stacked, use_container_width=True)
        
        # Top companies by industry
        st.subheader("Top Paid CEOs by Industry")
        
        if 'Industry' in df_filtered.columns:
            valid_industries = sorted([ind for ind in df_filtered['Industry'].unique() if ind and ind != 'nan'])
            
            if valid_industries:
                industry_selection = st.selectbox("Select an industry:", valid_industries)
                
                industry_data = df_filtered[df_filtered['Industry'] == industry_selection].nlargest(10, 'Salary')
                
                if len(industry_data) > 0:
                    display_cols = ['CEO_Name', 'Company', 'Salary']
                    display_data = industry_data[display_cols].copy()
                    display_data['Salary'] = display_data['Salary'].apply(lambda x: f"${x/1000000:.1f}M")
                    
                    if 'Pay_Ratio' in industry_data.columns:
                        display_data['Pay Ratio'] = industry_data['Pay_Ratio'].apply(
                            lambda x: f"{x:.0f}:1" if pd.notna(x) else "N/A"
                        )
                    
                    st.dataframe(display_data, use_container_width=True, hide_index=True)
    else:
        st.warning("No data available with current filters.")

# TAB 4: Performance Question
with tab4:
    st.header("The Performance Question: Does Pay Equal Performance?")
    
    if len(df_filtered) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Tenure vs Salary scatter
            if 'CEO_Tenure_Years' in df_filtered.columns:
                df_tenure = df_filtered[df_filtered['CEO_Tenure_Years'].notna()]
                
                if len(df_tenure) > 0:
                    fig_tenure = px.scatter(
                        df_tenure,
                        x='CEO_Tenure_Years',
                        y='Salary',
                        size='Market_Cap_Billions' if 'Market_Cap_Billions' in df_tenure.columns else None,
                        color='Pay_Level',
                        color_discrete_map=color_map,
                        hover_data=['CEO_Name', 'Company'],
                        title='CEO Experience vs Compensation'
                    )
                    
                    fig_tenure.update_layout(
                        height=450,
                        xaxis=dict(title="Years as CEO"),
                        yaxis=dict(tickformat='$,.0f', title="Total Compensation ($)")
                    )
                    
                    st.plotly_chart(fig_tenure, use_container_width=True)
                else:
                    st.info("No tenure data available")
            else:
                st.info("CEO tenure data not available")
        
        with col2:
            # Company size vs pay
            if 'Employees' in df_filtered.columns:
                df_employees = df_filtered[df_filtered['Employees'].notna()]
                
                if len(df_employees) > 0:
                    fig_employees = px.scatter(
                        df_employees,
                        x='Employees',
                        y='Salary',
                        size='Market_Cap_Billions' if 'Market_Cap_Billions' in df_employees.columns else None,
                        color='Industry',
                        hover_data=['CEO_Name', 'Company'],
                        title='Company Size vs CEO Pay',
                        log_x=True
                    )
                    
                    fig_employees.update_layout(
                        height=450,
                        xaxis=dict(title="Number of Employees (log scale)"),
                        yaxis=dict(tickformat='$,.0f', title="CEO Compensation ($)")
                    )
                    
                    st.plotly_chart(fig_employees, use_container_width=True)
                else:
                    st.info("No employee data available")
            else:
                st.info("Employee count data not available")
        
        # Correlation analysis
        st.subheader("Correlation Analysis: What Drives CEO Pay?")
        
        numeric_cols = ['Salary']
        if 'Market_Cap_Billions' in df_filtered.columns:
            numeric_cols.append('Market_Cap_Billions')
        if 'Employees' in df_filtered.columns:
            numeric_cols.append('Employees')
        if 'CEO_Tenure_Years' in df_filtered.columns:
            numeric_cols.append('CEO_Tenure_Years')
        if 'Pay_Ratio' in df_filtered.columns:
            numeric_cols.append('Pay_Ratio')
        
        if len(numeric_cols) > 1:
            df_corr = df_filtered[numeric_cols].dropna()
            
            if len(df_corr) > 1:
                corr_matrix = df_corr.corr()
                
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    title='Correlation Matrix: Pay vs Performance Metrics',
                    color_continuous_scale='RdBu',
                    zmin=-1,
                    zmax=1
                )
                
                fig_corr.update_layout(height=500)
                st.plotly_chart(fig_corr, use_container_width=True)
        
        # The Buffett comparison
        st.subheader("The Buffett Model: A Different Approach")
        
        lowest_paid = df_filtered.loc[df_filtered['Salary'].idxmin()]
        lowest_salary = lowest_paid['Salary']
        
        total_actual = df_filtered['Salary'].sum()
        total_if_lowest = lowest_salary * len(df_filtered)
        savings = total_actual - total_if_lowest
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total CEO Compensation",
                value=f"${total_actual/1000000:.1f}M",
                delta=f"Across {len(df_filtered)} companies"
            )
        
        with col2:
            st.metric(
                label="If All Paid Like Lowest",
                value=f"${total_if_lowest/1000000:.1f}M",
                delta=f"At ${lowest_salary:,.0f} each"
            )
        
        with col3:
            st.metric(
                label="Potential Savings",
                value=f"${savings/1000000:.1f}M",
                delta=f"{(savings/total_actual)*100:.1f}% reduction"
            )
        
        st.warning(f"📊 **Conclusion:** If all CEOs were paid like {lowest_paid['CEO_Name']} ({lowest_paid['Company']}), " +
                  f"companies could save ${savings/1000000:.1f}M annually!")
    else:
        st.warning("No data available with current filters.")

# Footer
st.markdown("---")
st.markdown("*Data visualization created with Streamlit and Plotly*")