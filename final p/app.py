import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px
from folium.plugins import MarkerCluster
from io import StringIO
from streamlit.components.v1 import html
import tempfile
import os
import plotly.graph_objects as go
from io import BytesIO, StringIO
import logging
from datetime import datetime
import traceback
from streamlit_folium import st_folium
import io
import zipfile
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import threading
from queue import Queue
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Constants
MAX_FILE_SIZE_MB = 200
SUPPORTED_FILE_TYPES = ['csv', 'xlsx', 'xls', 'tsv', 'json']
MAX_CATEGORIES = 30
DEFAULT_CHART_HEIGHT = 500

# Configure Streamlit page
st.set_page_config(
    page_title="Data Visualization Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better appearance and accessibility
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    h1, h2, h3 {
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    /* Metric styling */
    .css-1l4firl, .css-1wivap2, [data-testid="stMetricValue"] {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #1E88E5 !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #4CAF50 !important;
    }
    /* Metric container */
    .css-1xarl3l {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Accessibility improvements */
    .stSelectbox, .stMultiselect, .stSlider {
        margin-bottom: 1rem;
    }
    .stSelectbox label, .stMultiselect label, .stSlider label {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    /* High contrast mode */
    .high-contrast {
        background-color: #000;
    }
    .high-contrast [data-testid="stMetricValue"] {
        color: #ffffff !important;
        background-color: #000000 !important;
    }
    .high-contrast [data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }
    /* Loading spinner */
    .stSpinner {
        margin: 2rem auto;
    }
</style>
""", unsafe_allow_html=True)

# Error handling decorator
def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = "An error occurred: {}".format(str(e))
            logging.error("{}\n{}".format(error_msg, traceback.format_exc()))
            st.error(error_msg)
            return None
    return wrapper

# Function to validate file upload
@handle_errors
def validate_file_upload(uploaded_file):
    if uploaded_file is None:
        return None
    
    # Check file size
    file_size = uploaded_file.size / (1024 * 1024)  # Convert to MB
    if file_size > MAX_FILE_SIZE_MB:
        st.error("File size exceeds the maximum limit of {}MB".format(MAX_FILE_SIZE_MB))
        return None
    
    # Check file type
    file_type = uploaded_file.name.split('.')[-1].lower()
    if file_type not in SUPPORTED_FILE_TYPES:
        st.error("Unsupported file type. Please upload one of: {}".format(', '.join(SUPPORTED_FILE_TYPES)))
        return None
    
    return uploaded_file

# Function to detect column names dynamically
@handle_errors
def detect_columns(df, candidates):
    for col in df.columns:
        if any(candidate.lower() == col.lower() for candidate in candidates):
            return col
    return None

# Function to load default data if no file is uploaded
@handle_errors
@st.cache_data
def load_default_data():
    try:
        return pd.read_csv("assets/healthcare.csv")
    except FileNotFoundError:
        logging.info("Default dataset not found, creating sample data")
        data = {
            'Age': np.random.randint(18, 85, 50),
            'Gender': np.random.choice(['Male', 'Female', 'Other'], 50),
            'Medical Condition': np.random.choice(['Diabetes', 'Hypertension', 'Asthma', 'Arthritis'], 50),
            'Billing Amount': np.random.uniform(100, 5000, 50).round(2),
            'Date of Admission': pd.date_range(start='2023-01-01', periods=50),
            'Latitude': np.random.uniform(37.7, 37.8, 50),
            'Longitude': np.random.uniform(-122.5, -122.4, 50)
        }
        return pd.DataFrame(data)

# Function to convert multiple figures to HTML
@handle_errors
def convert_figs_to_html(figs):
    buffer = StringIO()
    for fig in figs:
        fig.write_html(buffer, full_html=False, include_plotlyjs='cdn')
    return buffer.getvalue()

# Upload CSV file
@handle_errors
def read_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return None
        
    file_type = uploaded_file.name.split('.')[-1].lower()

    try:
        if file_type in ['csv']:
            for encoding in ['utf-8', 'latin1', 'cp1252']:
                try:
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    uploaded_file.seek(0)  # Reset file pointer
                    return df
                except UnicodeDecodeError:
                    uploaded_file.seek(0)  # Reset for next try
                    continue
            st.error("Could not decode CSV file. Please check the encoding.")
            return None

        elif file_type in ['tsv']:
            return pd.read_csv(uploaded_file, sep='\t')

        elif file_type in ['xlsx', 'xls']:
            return pd.read_excel(uploaded_file)

        elif file_type in ['json']:
            return pd.read_json(uploaded_file)

        else:
            st.error("Unsupported file type. Please upload CSV, TSV, Excel, or JSON.")
            return None

    except Exception as e:
        st.error("Error reading file: {}".format(e))
        return None

# Function to determine if a column has date-like values
@handle_errors
def is_date_column(series):
    try:
        pd.to_datetime(series)
        return True
    except:
        return False

# Function to detect date columns
@handle_errors
def detect_date_columns(df):
    if df is None:
        return []
    date_cols = []
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['date', 'time', 'day', 'month', 'year']):
            if is_date_column(df[col]):
                date_cols.append(col)
        elif df[col].dtype == 'object' and is_date_column(df[col]):
            date_cols.append(col)
    return date_cols

# Function to get appropriate color palette based on data type
@handle_errors
def get_color_palette(data_type, num_categories=None):
    if data_type == 'categorical':
        palettes = [
            px.colors.qualitative.Plotly,
            px.colors.qualitative.Set1,
            px.colors.qualitative.Dark24,
            px.colors.qualitative.Pastel
        ]
        if num_categories and num_categories > 10:
            return px.colors.qualitative.Dark24
        return px.colors.qualitative.Set1
    elif data_type == 'sequential':
        return px.colors.sequential.Blues
    else:
        return px.colors.qualitative.Plotly

@st.cache_data
def process_data(df):
    """Process and cache data to improve performance"""
    if df is None:
        return None
    try:
        # Convert date columns
        date_cols = detect_date_columns(df)
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Fill missing values for numeric columns with mean
        for col in df.select_dtypes(include=['number']).columns:
            df[col] = df[col].fillna(df[col].mean())
        
        # Fill missing values for categorical columns with mode
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna(df[col].mode()[0])
        
        return df
    except Exception as e:
        logging.error("Error processing data: {}".format(e))
        st.error("Error processing data. Please check your data format.")
        return df

def create_popup_content(row):
    """Create informative popup content for map markers"""
    popup_content = "<div style='width: 200px;'>"
    for col in row.index:
        if col not in ['latitude', 'longitude', 'lat', 'lon', 'LAT', 'LON']:
            popup_content += f"<b>{col}:</b> {row[col]}<br>"
    popup_content += "</div>"
    return folium.Popup(popup_content, max_width=300)

@st.cache_data(ttl=3600)
def process_coordinates(df, lat_col, lon_col):
    """Process and validate coordinate data"""
    try:
        # Convert coordinates to numeric, handling any non-numeric values
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        
        # Filter out rows with invalid coordinates
        valid_coords = df.dropna(subset=[lat_col, lon_col])
        valid_coords = valid_coords[
            (valid_coords[lat_col] >= -90) & (valid_coords[lat_col] <= 90) &
            (valid_coords[lon_col] >= -180) & (valid_coords[lon_col] <= 180)
        ]
        
        if len(valid_coords) == 0:
            st.warning("No valid coordinates found in the dataset. Please ensure your latitude values are between -90 and 90, and longitude values are between -180 and 180.")
            return None
            
        return valid_coords
    except Exception as e:
        st.error(f"Error processing coordinates: {str(e)}")
        logging.error(f"Coordinate processing error: {str(e)}\n{traceback.format_exc()}")
        return None

# Add background processing function
def process_map_in_background(queue, valid_coords, lat_col, lon_col, map_type, map_style):
    """Process map creation in background thread"""
    try:
        # Create a simpler map with fewer features for better performance
        center_lat = valid_coords[lat_col].mean()
        center_lon = valid_coords[lon_col].mean()
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=map_style,
            prefer_canvas=True  # Use canvas renderer for better performance
        )
        
        # Use clustering by default for large datasets
        if len(valid_coords) > 1000:
            marker_cluster = MarkerCluster().add_to(m)
        
        # Process in smaller batches
        BATCH_SIZE = 500
        total_rows = len(valid_coords)
        
        if map_type == "Heat Map":
            from folium.plugins import HeatMap
            # Downsample data for heat map if too large
            if len(valid_coords) > 5000:
                sample_size = 5000
                valid_coords = valid_coords.sample(n=sample_size)
            heat_data = [[row[lat_col], row[lon_col]] for _, row in valid_coords.iterrows()]
            HeatMap(heat_data, min_opacity=0.2).add_to(m)
        
        elif map_type == "Circle Markers":
            for i in range(0, total_rows, BATCH_SIZE):
                batch = valid_coords.iloc[i:i+BATCH_SIZE]
                for _, row in batch.iterrows():
                    folium.CircleMarker(
                        location=[row[lat_col], row[lon_col]],
                        radius=3,  # Smaller radius
                        color='blue',
                        fill=True,
                        fill_opacity=0.4,
                        popup=None  # Remove popups for better performance
                    ).add_to(m if len(valid_coords) <= 1000 else marker_cluster)
        
        else:  # Marker Cluster
            for i in range(0, total_rows, BATCH_SIZE):
                batch = valid_coords.iloc[i:i+BATCH_SIZE]
                for _, row in batch.iterrows():
                    folium.Marker(
                        location=[row[lat_col], row[lon_col]],
                        popup=None  # Remove popups for better performance
                    ).add_to(marker_cluster)
        
        queue.put(("success", m))
    except Exception as e:
        queue.put(("error", str(e)))

def reset_map_state():
    """Reset the map processing state"""
    if 'map_processing' in st.session_state:
        st.session_state.map_processing = {
            'started': False,
            'completed': False,
            'map': None,
            'error': None,
            'settings': None
        }

def init_session_state():
    """Initialize session state variables"""
    if "map_processing" not in st.session_state:
        st.session_state.map_processing = {
            'started': False,
            'completed': False,
            'map': None,
            'error': None,
            'settings': None,
            'queue': None,
            'last_valid_map': None
        }
    if "load_visualizations" not in st.session_state:
        st.session_state.load_visualizations = {
            'geospatial': True,
            'time_series': True,
            'categorical': True,
            'numeric': True,
            'advanced': True
        }
    if "map_key" not in st.session_state:
        st.session_state.map_key = 0
    if "last_processed_df" not in st.session_state:
        st.session_state.last_processed_df = None

def create_simple_map(valid_coords, lat_col, lon_col, map_style="OpenStreetMap"):
    """Create a simple map without complex features for better performance"""
    try:
        center_lat = valid_coords[lat_col].mean()
        center_lon = valid_coords[lon_col].mean()
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=map_style
        )
        
        # Add markers in a single batch
        for _, row in valid_coords.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=3,
                color='blue',
                fill=True,
                fill_opacity=0.4
            ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None

def main():
    # Initialize session state
    init_session_state()
    
    st.title("📊 Interactive Data Visualization Dashboard")
    
    # Initialize df as None
    df = None
    
    # Sidebar for file upload and options
    with st.sidebar:
        st.header("Data Source")
        uploaded_file = st.file_uploader(
            "Upload your data file", 
            type=SUPPORTED_FILE_TYPES,
            help="Supported formats: CSV, Excel, TSV, JSON"
        )
        use_default = st.checkbox("Use default dataset", value=False)
        
        if uploaded_file:
            uploaded_file = validate_file_upload(uploaded_file)
            if uploaded_file:
                st.success("✅ File uploaded successfully!")
                df = read_uploaded_file(uploaded_file)
        elif use_default:
            st.info("ℹ️ Using default dataset")
            df = load_default_data()
            
        # Add accessibility options
        st.header("Accessibility Options")
        high_contrast = st.checkbox("High Contrast Mode", value=False)
        large_text = st.checkbox("Large Text Mode", value=False)
        
        # Section Visibility
        st.subheader("Show/Hide Sections")
        show_geospatial = st.checkbox("Show Geospatial Analysis", value=True)
        show_time_series = st.checkbox("Show Time Series Analysis", value=True)
        show_categorical = st.checkbox("Show Categorical Analysis", value=True)
        show_numeric = st.checkbox("Show Numeric Analysis", value=True)
        show_advanced = st.checkbox("Show Advanced Analysis", value=True)
        
        # Dashboard Settings
        st.header("Dashboard Settings")
        theme = st.selectbox(
            "Select Dashboard Theme",
            ["Default", "Dark", "Light", "Colorful"],
            help="Choose a theme for the dashboard"
        )
        
        # Layout customization
        st.subheader("Dashboard Layout")
        layout_option = st.radio(
            "Layout Style",
            ["Standard", "Wide", "Compact"],
            help="Choose the layout style for the dashboard"
        )
        
        # Export Options
        st.subheader("Export Options")
        if st.button("Export as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
    
    # Apply theme
    if theme == "Dark":
        st.markdown("""
        <style>
            .main {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            .stButton button {
                background-color: #4CAF50;
                color: white;
            }
            h1, h2, h3 {
                color: #00BFFF;
            }
            .css-1d391kg {
                background-color: #2E2E2E;
            }
        </style>
        """, unsafe_allow_html=True)
    elif theme == "Light":
        st.markdown("""
        <style>
            .main {
                background-color: #F5F5F5;
                color: #333333;
            }
            .stButton button {
                background-color: #2196F3;
                color: white;
            }
            h1, h2, h3 {
                color: #1976D2;
            }
        </style>
        """, unsafe_allow_html=True)
    elif theme == "Colorful":
        st.markdown("""
        <style>
            .main {
                background-color: #FFFACD;
                color: #333333;
            }
            .stButton button {
                background-color: #FF6347;
                color: white;
            }
            h1 {
                color: #FF4500;
            }
            h2 {
                color: #9932CC;
            }
            h3 {
                color: #008B8B;
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Apply accessibility settings
    if high_contrast:
        st.markdown("""
        <style>
        .stApp {
            background-color: black;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    if large_text:
        st.markdown("""
        <style>
        .stApp {
            font-size: 120%;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Check if we have data to work with
    if df is None:
        st.info("Please upload a file or use the default dataset to begin")
        return
    
    if df.empty:
        st.error("The dataset is empty. Please upload a valid file.")
        return
    
    # Process data
    with st.spinner("Processing data..."):
        df = process_data(df)
    
    # Store the processed dataframe in session state
    st.session_state.processed_df = df
    
    # Data overview
    st.header("Dataset Overview")
    overview_cols = st.columns([1, 1, 1])
    with overview_cols[0]:
        st.metric(label="Total Records", value=len(df), help="Total number of rows in the dataset")
    with overview_cols[1]:
        st.metric(label="Total Columns", value=len(df.columns), help="Total number of columns in the dataset")
    with overview_cols[2]:
        num_cols = len(df.select_dtypes(include=['number']).columns)
        st.metric(label="Numeric Fields", value=num_cols, help="Number of numeric columns in the dataset")
    
    # Preview data
    st.subheader("Data Preview")
    st.dataframe(
        df.head(10).style.set_properties(**{
            'background-color': '#f0f2f6',
            'color': 'black',
            'border-color': 'white',
            'padding': '0.5em'
        }),
        use_container_width=True,
        height=300
    )
    
    # Column information in a clean table
    st.subheader("Column Information")
    info_df = pd.DataFrame({
        'Column': df.columns,
        'Data Type': df.dtypes.values,
        'Non-Null Count': df.count().values,
        'Null Count': df.isna().sum().values
    })
    st.dataframe(
        info_df.style.set_properties(**{
            'background-color': '#f0f2f6',
            'color': 'black',
            'border-color': 'white',
            'padding': '0.5em'
        }),
        use_container_width=True,
        height=200
    )
    
    # Store all visualizations
    figs = []
    
    # Data Filtering
    st.header("Data Filtering")
    with st.expander("Filter Data"):
        # Create filters based on column types
        filter_cols = st.multiselect("Select columns to filter by", df.columns.tolist())
        
        filtered_df = df.copy()
        should_continue = True
        
        for col in filter_cols:
            if not should_continue:
                break
                
            if df[col].dtype == 'object' or df[col].nunique() < 10:  # Categorical
                unique_values = ['All'] + list(df[col].dropna().unique())
                selected_value = st.selectbox(f"Filter by {col}", unique_values)
                if selected_value != 'All':
                    filtered_df = filtered_df[filtered_df[col] == selected_value]
            elif is_date_column(df[col]):  # Date column
                try:
                    min_date = pd.to_datetime(df[col]).min().date()
                    max_date = pd.to_datetime(df[col]).max().date()
                    date_range = st.date_input(
                        f"Filter by {col} range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        filtered_df = filtered_df[(pd.to_datetime(filtered_df[col]).dt.date >= start_date) & 
                                              (pd.to_datetime(filtered_df[col]).dt.date <= end_date)]
                except:
                    st.warning(f"Could not filter by {col} as date conversion failed")
            else:  # Numeric
                min_val, max_val = float(df[col].min()), float(df[col].max())
                range_vals = st.slider(f"Filter by {col} range", min_val, max_val, (min_val, max_val))
                filtered_df = filtered_df[(filtered_df[col] >= range_vals[0]) & (filtered_df[col] <= range_vals[1])]
            
            # Check if we have any records after applying this filter
            if len(filtered_df) == 0:
                st.warning("No records match the filter criteria.")
                should_continue = False
        
        # Update the dataframe for visualizations if filters are applied
        if len(filter_cols) > 0 and len(filtered_df) > 0:
            df = filtered_df
            st.session_state.processed_df = df  # Update session state
            st.success(f"✅ Applied filters. Showing {len(df)} records.")
    
    # Continue with visualizations only if we have data
    if len(df) > 0:
        # Time series analysis
        if st.session_state.load_visualizations.get('time_series', False):
            st.header("Time Series Analysis")
            date_cols = detect_date_columns(df)
            if date_cols:
                selected_date_col = st.selectbox("Select Date Column", date_cols)
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    selected_metric = st.selectbox("Select Metric to Plot", numeric_cols)
                    df[selected_date_col] = pd.to_datetime(df[selected_date_col])
                    fig_time = px.line(df, x=selected_date_col, y=selected_metric)
                    st.plotly_chart(fig_time, use_container_width=True)
        
        # Categorical analysis
        if st.session_state.load_visualizations.get('categorical', False):
            st.header("Categorical Analysis")
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            if categorical_cols:
                selected_cat = st.selectbox("Select Categorical Column", categorical_cols)
                # Create value counts and properly format for plotting
                value_counts_df = df[selected_cat].value_counts().reset_index()
                value_counts_df.columns = ['Category', 'Count']  # Rename columns
                fig_cat = px.bar(
                    value_counts_df,
                    x='Category',
                    y='Count',
                    title=f'Distribution of {selected_cat}',
                    labels={'Category': selected_cat, 'Count': 'Frequency'},
                    color='Category'  # Add color for better visualization
                )
                # Improve layout
                fig_cat.update_layout(
                    xaxis_title=selected_cat,
                    yaxis_title='Count',
                    showlegend=False  # Hide legend as it's redundant with x-axis
                )
                st.plotly_chart(fig_cat, use_container_width=True)
        
        # Numeric analysis
        if st.session_state.load_visualizations.get('numeric', False):
            st.header("Numeric Analysis")
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                selected_num = st.selectbox("Select Numeric Column", numeric_cols)
                fig_num = px.histogram(df, x=selected_num)
                st.plotly_chart(fig_num, use_container_width=True)
        
        # Advanced analysis
        if st.session_state.load_visualizations.get('advanced', False):
            st.header("Advanced Analysis")
            if len(numeric_cols) >= 2:
                x_col = st.selectbox("Select X axis", numeric_cols)
                y_col = st.selectbox("Select Y axis", numeric_cols)
                fig_scatter = px.scatter(df, x=x_col, y=y_col)
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Geospatial mapping (moved to the end)
        if st.session_state.load_visualizations.get('geospatial', False):
            st.header("Geospatial Visualization")
            
            # Define possible column names for coordinates
            lat_candidates = ['Latitude', 'latitude', 'LAT', 'lat']
            lon_candidates = ['Longitude', 'longitude', 'LON', 'lon']
            
            # Try to detect coordinate columns
            lat_col = None
            lon_col = None
            
            # Simple column detection
            for col in df.columns:
                if any(candidate.lower() == col.lower() for candidate in lat_candidates):
                    lat_col = col
                if any(candidate.lower() == col.lower() for candidate in lon_candidates):
                    lon_col = col
            
            if lat_col and lon_col:
                valid_coords = process_coordinates(df, lat_col, lon_col)
                
                if valid_coords is not None and not valid_coords.empty:
                    st.success(f"Found {len(valid_coords)} valid coordinates")
                    
                    # Simple map creation
                    with st.spinner("Creating map..."):
                        m = create_simple_map(valid_coords, lat_col, lon_col)
                        if m:
                            st_folium(m, width=800, height=500)
                            
                    # Show basic stats
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Latitude Range", 
                                f"{valid_coords[lat_col].min():.2f} to {valid_coords[lat_col].max():.2f}")
                    with col2:
                        st.metric("Longitude Range", 
                                f"{valid_coords[lon_col].min():.2f} to {valid_coords[lon_col].max():.2f}")

    # Add lazy loading for other visualizations
    if "load_visualizations" not in st.session_state:
        st.session_state.load_visualizations = False

    if st.button("Load Other Visualizations"):
        st.session_state.load_visualizations = True

    if st.session_state.load_visualizations:
        # Your existing visualization code here...
        pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("Application error: {}\n{}".format(e, traceback.format_exc()))
        st.error(f"An unexpected error occurred: {str(e)}. Please check the logs for more details.")