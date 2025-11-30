"""
NYS Education Performance & Equity Dashboard
Focus: NYC, Westchester, Nassau, and Suffolk Counties
"""

import streamlit as st 
import pandas as pd 
import plotly.express as px 
import plotly.graph_objects as go 
from pathlib import Path 

#page config
st.set_page_config(
    page_title="NYS Education Dashboard",
    page_icon="📚",
    layout="wide"
)

#load data
@st.cache_data
def load_data():
    data_path = Path('data/processed/master_dataset.csv')
    df = pd.read_csv(data_path)

    #clean and prep data
    df['YEAR'] = df['YEAR'].astype(int)

    #convert percentage columns to numeric
    pct_col = [col for col in df.columns if col.startswith('PER_')]
    for col in pct_col:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['ATTENDANCE_RATE'] = pd.to_numeric(df['ATTENDANCE_RATE'], errors='coerce')
    df['total_enrollment'] = pd.to_numeric(df['total_enrollment'], errors='coerce')

    return df

df = load_data()

#title and intro
st.title("🎓 NYS School District Performance & Equity Dashboard")
st.markdown("""
Analyzing education outcomes across **NYC, Westchester, Nassau, and Suffolk** counties.
Data covers 182 districts from 2022-2024.
 """)

#sidebar filters
st.sidebar.header("📊 Filters")

#year filter
years = sorted(df['YEAR'].unique())
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)

#county filter
counties = sorted(df['county'].dropna().unique())
selected_counties = st.sidebar.multiselect(
    "Select Counties",
    counties,
    default=counties
)

#filter data
df_filtered = df[
    (df['YEAR'] == selected_year) &
    (df['county'].isin(selected_counties))
].copy()

#remove rows where key metrics are all null
df_filtered = df_filtered.dropna(subset=['total_enrollment'], how='all')
st.sidebar.markdown(f"**{len(df_filtered)} districts** in selection")

#main metrics section
st.header("📈 Key Metrics Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    total_students = df_filtered['total_enrollment'].sum()
    st.metric("Total Students", f"{total_students:,.0f}")

with col2:
    avg_attendance = df_filtered['ATTENDANCE_RATE'].mean()
    st.metric("Avg Attendance Rate", f"{avg_attendance:.1f}%")

with col3:
    avg_ecdis = df_filtered['PER_ECDIS'].mean()
    st.metric("Avg Econ. Disadvantaged", f"{avg_ecdis:.1f}%")

with col4:
    avg_suspension = df_filtered['PER_SUSPENSIONS'].mean()
    st.metric("Avg Suspension Rate", f"{avg_suspension:.1f}%")

with col5:
    avg_grad = df_filtered['graduation_rate'].mean()
    st.metric("Avg Graduation Rate", f"{avg_grad:.1f}%")

with col6:
    avg_dropout = df_filtered['dropout_rate'].mean()
    st.metric("Avg Dropout Rate", f"{avg_dropout:.1f}")

#summary statistics
st.header("📊 Summary Statistics")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.subheader("Key Metrics Distribution")

    metrics_for_summary = {
        'Graduation Rate': 'graduation_rate',
        'Dropout Rate': 'dropout_rate',
        'Attendance Rate': 'ATTENDANCE_RATE',
        'Ecomonically Disadvantaged': 'PER_ECDIS',
        'Free Lunch Eligible': 'PER_FREE_LUNCH',
        'Suspension Rate': 'PER_SUSPENSIONS'
    }

    summary_data = []
    for label, col in metrics_for_summary.items():
        if col in df_filtered.columns:
            data = df_filtered[col].dropna()
            if len(data) > 0:
                summary_data.append({
                    'Metric': label,
                    "Mean": f"{data.mean():.1f}%",
                    'Median': f"{data.median():.1f}%",
                    'Min': f"{data.min():.1f}%",
                    'Max': f"{data.max():.1f}%",
                    'Std Dev': f"{data.std():.1f}%"
                })
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

with summary_col2:
    st.subheader("Demographics Distribution")

    demo_metrics = {
        'White': 'PER_WHITE',
        'Black': 'PER_BLACK',
        'Hispanic': 'PER_HISP',
        'Asian': 'PER_ASIAN',
        'English Language Learners': 'PER_ELL',
        'Student with Disabilities': 'PER_SWD'
    }
    demo_summary = []
    for label, col in demo_metrics.items():
        if col in df_filtered.columns:
            data = df_filtered[col].dropna()
            if len(data) > 0:
                demo_summary.append({
                    'Group': label,
                    'Mean': f"{data.mean():.1f}%",
                    'Median': f"{data.median():.1f}%"
                })
    demo_summary_df = pd.DataFrame(demo_summary)
    st.dataframe(demo_summary_df, use_container_width=True)

#export button for summary stats
col_export1, col_export2 = st.columns(2)
with col_export1:
    summary_csv = summary_df.to_csv(index=False)
    st.download_button(
        label='📥 Download Metrics Summary',
        data=summary_csv,
        file_name=f"metrics_summary_{selected_year}.csv",
        mime='text/csv'
    )

with col_export2:
    demo_csv = demo_summary_df.to_csv(index=False)
    st.download_button(
        label='📥 Download Demographics Summary',
        data=demo_csv,
        file_name=f"demographics_summary_{selected_year}.csv",
        mime='text/csv'
    )

#visualizations
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Student Enrollment by County")

    enrollment_by_county = df_filtered.groupby('county')['total_enrollment'].sum().reset_index()
    enrollment_by_county = enrollment_by_county.sort_values('total_enrollment', ascending=False)

    fig = px.bar(
        enrollment_by_county,
        x='county',
        y='total_enrollment',
        title=f'Total Enrollment by County ({selected_year})',
        labels={'total_enrollment': 'Students', 'county': 'County'},
        color='total_enrollment',
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader("Demographics Breakdown")

    demo_cols = {
        'PER_WHITE': 'White',
        'PER_BLACK': 'Black',
        'PER_HISP': 'Hispanic',
        'PER_ASIAN': 'Asian'
    }

    demo_data = []
    for col, label in demo_cols.items():
        avg_val = df_filtered[col].mean()
        demo_data.append({'Race/Ethnicity': label, 'Percentage': avg_val})
    
    demo_df = pd.DataFrame(demo_data)

    fig = px.pie(
        demo_df,
        values='Percentage',
        names='Race/Ethnicity',
        title=f'Average Demographics Across Districts ({selected_year})',
        color_discrete_sequence=px.colors.qualitative.Set3 
    )
    st.plotly_chart(fig, use_container_width=True)

#equity analysis
st.header("⚖️ Equity Analysis")

equity_col1, equity_col2 = st.columns(2)

with equity_col1:
    st.subheader("Ecomonic Disadvantage vs Attendance")
    scatter_df = df_filtered[['ENTITY_NAME', 'county', 'PER_ECDIS', 'ATTENDANCE_RATE']].dropna()

    fig = px.scatter(
        scatter_df,
        x='PER_ECDIS',
        y='ATTENDANCE_RATE',
        color='county',
        hover_data=['ENTITY_NAME'],
        title='Does Economic Disadvantage Correlate with Attendance?',
        labels={
            'PER_ECDIS': 'Economically Disadvantage (%)',
            'ATTENDANCE_RATE': 'Attendance Rate (%)'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

with equity_col2:
    st.subheader("Free Lunch vs. Suspension Rates")

    scatter_df2 = df_filtered[['ENTITY_NAME', 'county', 'PER_FREE_LUNCH', 'PER_SUSPENSIONS']].dropna()
    fig = px.scatter(
        scatter_df2,
        x='PER_FREE_LUNCH',
        y='PER_SUSPENSIONS',
        color='county', 
        hover_data=['ENTITY_NAME'],
        title='Free Lunch Eligibility vs Suspensions',
        labels={
            'PER_FREE_LUNCH': 'Free Lunch Eligible (%)',
            'PER_SUSPENSIONS': 'Suspension Rate (%)'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

#district comparison
st.header("🔍 District Comparison Tool")

st.markdown("Select districts to compare side-by-side:")

#multi-select for districts
district_options = sorted(df_filtered['ENTITY_NAME'].unique())
selected_districts = st.multiselect(
    "Choose districts to compare",
    district_options,
    default=district_options[:3] if len(district_options) >=3 else district_options
)

if selected_districts:
    comparsion_df = df_filtered[df_filtered['ENTITY_NAME'].isin(selected_districts)]

    metrics_to_compare = {
        'total_enrollment': 'Total Enrollment',
        'graduation_rate': 'Graduation Rate (%)',
        'dropout_rate': 'Dropout Rate (%)',
        'PER_ECDIS': 'Economically Disadvantaged (%)',
        'PER_FREE_LUNCH': 'Free Lunch Eligible (%)',
        'ATTENDANCE_RATE': 'Attendance Rate (%)',
        'PER_SUSPENSIONS': 'Suspension Rate (%)',
        'PER_ELL': 'English Language Learners (%)',
        'PER_SWD': 'Students with Disabilities (%)'
    }

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        metric = st.selectbox('Select Metric 1', list(metrics_to_compare.keys()),
        format_func=lambda x: metrics_to_compare[x])

        fig = px.bar(
            comparsion_df,
            x='ENTITY_NAME',
            y=metric,
            title=metrics_to_compare[metric],
            labels={'ENTITY_NAME': 'District', metric: metrics_to_compare[metric]},
            color='county'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with comp_col2:
        metric2 = st.selectbox("Select Metric 2", list(metrics_to_compare.keys()),
        index=1,
        format_func=lambda x: metrics_to_compare[x])

        fig = px.bar(
            comparsion_df,
            x='ENTITY_NAME',
            y=metric2,
            title=metrics_to_compare[metric],
            labels={'ENTITY_NAME': 'District', metric2: metrics_to_compare[metric2]},
            color='county'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detailed Comparison")
    display_cols = ['ENTITY_NAME', 'county'] + list(metrics_to_compare.keys())
    display_df = comparsion_df[display_cols].copy()

    for col in metrics_to_compare.keys():
        if col in display_df.columns:
            display_df[col] = display_df[col].round(1)

    st.dataframe(display_df, use_container_width=True)

#trends over time
st.header("📊 Trends Over Time")

#allow user to select districts for trend analysis
trend_districts = st.multiselect(
    "Select districts to see trends",
    district_options,
    default=[district_options[0]] if district_options else []
)

if trend_districts:
    trend_df = df[df['ENTITY_NAME'].isin(trend_districts)].copy()

    trend_col1, trend_col2, trend_col3, trend_col4 = st.columns(4)

    with trend_col1:
        fig = px.line(
            trend_df,
            x='YEAR',
            y='ATTENDANCE_RATE',
            color='ENTITY_NAME',
            title='Attendance Rate Trend',
            labels={'ATTENDANCE_RATE': 'Attendance Rate (%)', 'YEAR': 'Year'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with trend_col2:
        fig = px.line(
            trend_df,
            x='YEAR',
            y='total_enrollment',
            color='ENTITY_NAME',
            title='Enrollment Trend',
            labels={'total_enrollemnt': 'Total Enrollment', 'YEAR': 'Year'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with trend_col3:
        fig = px.line(
            trend_df,
            x='YEAR',
            y='graduation_rate',
            color='ENTITY_NAME',
            title='Graduation Rate Trend',
            labels={'graduation_rate': 'Graduation Rate (%)', 'YEAR': 'Year'},
            markers=True 
        )
        st.plotly_chart(fig, use_container_width=True)

    with trend_col4:
        fig = px.line(
            trend_df,
            x='YEAR',
            y='dropout_rate',
            color='ENTITY_NAME',
            title='Dropout Rate Trend',
            labels={'dropout_rate': 'Dropout Rate (%)', 'YEAR': 'Year'},
            markers=True 
        )
        st.plotly_chart(fig, use_container_width=True) 

#data explorer
with st.expander("🔍 Explore Raw Data"):
    st.subheader("Filtered Dataset")
    st.markdown(f"Showing {len(df_filtered)} districts for {selected_year}")

    all_cols = df_filtered.columns.tolist()
    default_cols = ['ENTITY_NAME', 'county', 'total_enrollment', 'graduation_rate', 'dropout_rate', 'ATTENDANCE_RATE',
                    'PER_ECDIS', 'PER_FREE_LUNCH']

    selected_cols = st.multiselect(
        "Select columns to display",
        all_cols,
        default=[col for col in default_cols if col in all_cols]
    )

    if selected_cols:
        st.dataframe(df_filtered[selected_cols], use_container_width=True)

#footer
st.markdown("---")
st.markdown("""
**Data Source:** New York State Education Department (data.nysed.gov)
**Years Covered:** 2022-2024
**Regions:** NYC, Westchester, Nassau, and Suffolk Counties
 """)

