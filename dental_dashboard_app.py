import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import plotly.express as px # Charts ke liye Plotly Express
import io # Download button ke liye

# --- Configuration ---
DATA_FILE = 'dental_data.csv'

# --- Page Settings ---
st.set_page_config(
    page_title="Dental Clinic Dashboard",
    layout="wide", # Page layout ko wide set kiya
    initial_sidebar_state="expanded" # Sidebar shuruat mein khula rahega
)

# --- Custom CSS for Decoration ---
st.markdown(
    """
    <style>
    /* General Body Styling */
    body {
        font-family: 'Segoe UI', sans-serif;
        color: #333333;
        background-color: #f8f9fa;
    }

    /* Main Title Styling */
    .css-fg4ri6 h1, .st-emotion-cache-nahz7x h1 {
        color: #007bff;
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #e0e0e0;
        font-weight: 700;
        font-size: 2.8em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Headers (h2, h3) Styling */
    .st-emotion-cache-1jm692z h2, .st-emotion-cache-1jm692z h3 {
        color: #0056b3;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 15px;
        border-left: 5px solid #007bff;
        padding-left: 10px;
    }

    /* Sidebar Styling */
    .st-emotion-cache-1l0bgz .st-emotion-cache-1l0bgz {
        background-color: #ffffff;
        padding: 25px 20px;
        border-right: 1px solid #e0e0e0;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Metric Cards Styling (KPIs) */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.2s ease-in-out;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }

    [data-testid="stMetric"] label {
        color: #6c757d;
        font-size: 1em;
        margin-bottom: 8px;
        font-weight: 600;
    }

    [data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #2c3e50;
        font-size: 2.2em;
        font-weight: 800;
    }

    /* Streamlit widgets (selectboxes, multiselects etc.) */
    .st-emotion-cache-135a507 {
        margin-bottom: 15px;
    }

    /* Dataframe Styling (for preview) */
    .st-emotion-cache-nahz7x table {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Main content area padding */
    .st-emotion-cache-nahz7x {
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        background-color: #ffffff;
    }
    
    /* Custom style for the download button to make it look nicer */
    .st-emotion-cache-nahz7x button {
        background-color: #28a745; /* Green color for download */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 1em;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .st-emotion-cache-nahz7x button:hover {
        background-color: #218838; /* Darker green on hover */
    }

    </style>
    """,
    unsafe_allow_html=True
)

# --- Data Loading Function ---
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"Error: Data file not found at {file_path}. Please make sure '{DATA_FILE}' is in the same directory.")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)

        numeric_cols = ['Patient Age', 'Duration (minutes)', 'Billing Amount ($)']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df.dropna(subset=[col], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        return pd.DataFrame()

# --- Main Dashboard Logic ---
st.title('🦷 Private Dental Clinic Dashboard')

df = load_data(DATA_FILE)

if df.empty:
    st.warning("Dashboard run nahi ho sakta kyunki data load nahi hua ya empty hai. Please generate 'dental_data.csv' first using 'generate_dental_data.py'.")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Filter Appointments")

    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    selected_start_date, selected_end_date = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    all_doctors = sorted(df['Doctor Name'].unique().tolist())
    selected_doctors = st.sidebar.multiselect(
        "Select Doctor(s)",
        options=all_doctors,
        default=all_doctors
    )

    all_procedures = sorted(df['Procedure Type'].unique().tolist())
    selected_procedures = st.sidebar.multiselect(
        "Select Procedure Type(s)",
        options=all_procedures,
        default=all_procedures
    )

    all_statuses = sorted(df['Appointment Status'].unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "Select Appointment Status(es)",
        options=all_statuses,
        default=all_statuses
    )

    df_filtered = df[
        (df['Date'].dt.date >= selected_start_date) & 
        (df['Date'].dt.date <= selected_end_date) &
        (df['Doctor Name'].isin(selected_doctors)) &
        (df['Procedure Type'].isin(selected_procedures)) &
        (df['Appointment Status'].isin(selected_statuses))
    ]

    # --- Display KPIs ---
    st.header("Key Performance Indicators (KPIs)")

    if df_filtered.empty:
        st.info("No data available for the selected filters. Please adjust your filters.")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric(label="Total Appointments", value="0")
        with col2: st.metric(label="Total Revenue", value="$0.00")
        with col3: st.metric(label="No-Show Rate", value="0.00%")
        with col4: st.metric(label="Appointments Today", value="0")
    else:
        total_appointments = df_filtered.shape[0]
        total_revenue = df_filtered['Billing Amount ($)'].sum()
        
        # Only consider 'Scheduled' or 'No-show' for no-show rate calculation, not 'Completed' if filtering
        # To avoid confusion, for no-show rate, it's typically (no-shows / (scheduled + no-shows)) for selected filters
        # Or you might want to calculate it globally before filtering by status.
        # For simplicity, using filtered data to calculate no-show rate:
        no_shows = df_filtered[df_filtered['Appointment Status'] == 'No-show'].shape[0]
        total_appointments_for_rate = df_filtered.shape[0] # Total filtered appointments
        no_show_rate = (no_shows / total_appointments_for_rate * 100) if total_appointments_for_rate > 0 else 0
        
        today = datetime.now().date()
        appointments_today = df_filtered[df_filtered['Date'].dt.date == today].shape[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="Total Appointments", value=f"{total_appointments:,}")
        
        with col2:
            st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
        
        with col3:
            st.metric(label="No-Show Rate", value=f"{no_show_rate:.2f}%")
        
        with col4:
            st.metric(label="Appointments Today", value=f"{appointments_today:,}")

        # --- Charts Section ---
        st.header("Key Performance Visualizations")

        chart_row1_col1, chart_row1_col2 = st.columns(2)
        
        with chart_row1_col1:
            st.subheader("Revenue by Procedure Type")
            revenue_by_procedure = df_filtered.groupby('Procedure Type')['Billing Amount ($)'].sum().sort_values(ascending=False).reset_index()
            fig_revenue_procedure = px.bar(
                revenue_by_procedure, 
                x='Billing Amount ($)', 
                y='Procedure Type', 
                orientation='h',
                title='Total Revenue per Procedure',
                labels={'Billing Amount ($)':'Total Revenue', 'Procedure Type':'Procedure'},
                color='Billing Amount ($)',
                color_continuous_scale=px.colors.sequential.Bluyl
            )
            fig_revenue_procedure.update_layout(yaxis_title='', xaxis_title='Total Revenue ($)')
            fig_revenue_procedure.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_revenue_procedure, use_container_width=True)

        with chart_row1_col2:
            st.subheader("Revenue by Doctor")
            revenue_by_doctor = df_filtered.groupby('Doctor Name')['Billing Amount ($)'].sum().sort_values(ascending=False).reset_index()
            fig_revenue_doctor = px.bar(
                revenue_by_doctor, 
                x='Billing Amount ($)', 
                y='Doctor Name', 
                orientation='h',
                title='Total Revenue per Doctor',
                labels={'Billing Amount ($)':'Total Revenue', 'Doctor Name':'Doctor'},
                color='Billing Amount ($)',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig_revenue_doctor.update_layout(yaxis_title='', xaxis_title='Total Revenue ($)')
            fig_revenue_doctor.update_yaxes(categoryorder='total ascending')
            st.plotly_chart(fig_revenue_doctor, use_container_width=True)

        chart_row2_col1, chart_row2_col2 = st.columns(2)

        with chart_row2_col1:
            st.subheader("Appointment Status Breakdown")
            status_counts = df_filtered['Appointment Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.pie(
                status_counts, 
                values='Count', 
                names='Status', 
                title='Distribution of Appointment Status',
                hole=0.4, # Donut chart ke liye
                color_discrete_sequence=px.colors.qualitative.D3 # Color palette
            )
            fig_status.update_traces(textinfo='percent+label', pull=[0.05, 0, 0]) # Completed ko thoda bahar pull karein
            st.plotly_chart(fig_status, use_container_width=True)

        with chart_row2_col2:
            st.subheader("Appointments Over Time")
            # Daily appointments count karein
            daily_appointments = df_filtered.groupby(df_filtered['Date'].dt.date).size().reset_index(name='Count')
            daily_appointments.columns = ['Date', 'Appointments'] # Column rename
            fig_appts_time = px.line(
                daily_appointments, 
                x='Date', 
                y='Appointments', 
                title='Daily Appointments Trend',
                labels={'Date':'Date', 'Appointments':'Number of Appointments'},
                markers=True # Data points par markers dikhayen
            )
            fig_appts_time.update_layout(xaxis_title='Date', yaxis_title='Appointments')
            st.plotly_chart(fig_appts_time, use_container_width=True)


        # --- Filtered Data Table & Download ---
        st.header("Filtered Appointment Details")
        st.dataframe(df_filtered.sort_values(by='Date', ascending=False), use_container_width=True)

        # Download button
        csv_file = df_filtered.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_file,
            file_name="filtered_dental_data.csv",
            mime="text/csv",
            help="Download the currently displayed filtered data."
        )
