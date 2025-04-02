import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from folium.plugins import MarkerCluster
from io import StringIO
from streamlit.components.v1 import html
import tempfile

# Function to detect column names dynamically
def detect_columns(df, candidates):
    return next((col for col in candidates if col in df.columns), None)

# Function to load default data if no file is uploaded
def load_default_data():
    return pd.read_csv("assets/healthcare.csv")

# Function to convert multiple figures to HTML
def convert_figs_to_html(figs):
    buffer = StringIO()
    for fig in figs:
        fig.write_html(buffer, full_html=False, include_plotlyjs='cdn')
    return buffer.getvalue()

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
df = pd.read_csv(uploaded_file) if uploaded_file else load_default_data()

# Detect latitude and longitude columns dynamically
lat_col = detect_columns(df, ['Latitude', 'latitude', 'LAT', 'lat'])
lon_col = detect_columns(df, ['Longitude', 'longitude', 'LON', 'lon'])

# Geospatial Mapping with user selection
geo_map_type = st.radio("Select Geospatial Map Type", ["Circle Markers", "Marker Cluster"], index=0)

if lat_col and lon_col:
    st.write("### Geospatial Map of Patient Locations")
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=12)
    
    if geo_map_type == "Circle Markers":
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=5, color='blue', fill=True, fill_color='blue', fill_opacity=0.6
            ).add_to(m)
    else:
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in df.iterrows():
            folium.Marker(
                location=[row[lat_col], row[lon_col]],
                popup=row.get('Medical Condition', 'Unknown')
            ).add_to(marker_cluster)
    
    # Use tempfile to save the map
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        m.save(tmp_file.name)
        tmp_file.seek(0)
        with open(tmp_file.name, 'r') as f:
            map_html = f.read()
        html(map_html, height=500)
else:
    st.warning("Latitude and Longitude columns not found in the dataset, but other visualizations are still available.")

# Display dataset overview
st.write("### Dataset Overview")
st.write(f"Total Records: {len(df)}")

if 'Billing Amount' in df.columns:
    st.write(f"Average Billing Amount: ${df['Billing Amount'].mean():,.2f}")

# Store all visualizations
figs = []

# Generate colorful visualizations dynamically
for col in df.columns:
    # Skip latitude and longitude columns
    if 'lat' in col.lower() or 'lon' in col.lower():
        continue
        
    # Skip Billing Amount column (removed distribution section)
    if col == 'Billing Amount':
        continue

    if df[col].dtype == 'object' and df[col].nunique() < 20:
        st.write(f"### Distribution of {col}")
        chart_type = st.selectbox(f"Select Chart Type for {col}", ["Bar Chart", "Pie Chart"], key=col)
        color_palette = px.colors.qualitative.Set1  # Vibrant colors
        
        # Fix: Create value counts and properly name the columns
        value_counts = df[col].value_counts().reset_index()
        value_counts.columns = [col, 'Count']  # Rename columns to avoid using 'index'
        
        if chart_type == "Bar Chart":
            fig = px.bar(value_counts, x=col, y='Count', 
                         title=f"Distribution of {col}", color=col, 
                         color_discrete_sequence=color_palette)
        else:
            fig = px.pie(value_counts, names=col, values='Count', 
                         title=f"Distribution of {col}", color=col, 
                         color_discrete_sequence=color_palette)
        st.plotly_chart(fig)
        figs.append(fig)  # Store the visualization

    elif df[col].dtype in ['int64', 'float64'] and col != 'Billing Amount':
        # Special handling for Age column
        if col.lower() == 'age':
            st.write(f"### Age Distribution")
            chart_type = st.selectbox(f"Select Chart Type for {col}", ["Bar Chart", "Pie Chart"], key=col + "_num")
            color_palette = px.colors.qualitative.Set2  # Another vibrant color palette
            
            # Fix: Create age counts with proper column names
            age_counts = df[col].value_counts().reset_index()
            age_counts.columns = ['Age', 'Count']  # Rename columns for clarity
            
            if chart_type == "Bar Chart":
                fig = px.bar(age_counts, x='Age', y='Count', 
                             title=f"Age Distribution", color='Age', 
                             color_discrete_sequence=color_palette)
            else:
                fig = px.pie(age_counts, names='Age', values='Count', 
                             title=f"Age Distribution", color='Age', 
                             color_discrete_sequence=color_palette)
            st.plotly_chart(fig)
            figs.append(fig)  # Store the visualization
        else:
            st.write(f"### Distribution of {col}")
            chart_type = st.selectbox(f"Select Chart Type for {col}", ["Bar Chart", "Pie Chart"], key=col + "_num")
            color_palette = px.colors.qualitative.Set2  # Another vibrant color palette
            
            # Create proper value counts for numeric columns
            num_counts = df[col].value_counts().reset_index()
            num_counts.columns = [col, 'Count']
            
            if chart_type == "Bar Chart":
                # Use the column directly with properly named dataframe
                fig = px.bar(num_counts, x=col, y='Count', 
                             title=f"Distribution of {col}", color=col,
                             color_discrete_sequence=color_palette)
            else:
                fig = px.pie(num_counts, names=col, values='Count', 
                             title=f"Distribution of {col}", color=col,
                             color_discrete_sequence=color_palette)
            st.plotly_chart(fig)
            figs.append(fig)  # Store the visualization

# Handle medical condition filtering and time series visualization
if 'Date of Admission' in df.columns and 'Medical Condition' in df.columns:
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    selected_condition = st.selectbox("Select Medical Condition", df['Medical Condition'].unique())
    chart_type = st.radio("Select Chart Type", ["Bar Chart", "Line Chart"], key="admission_chart")
    admissions_by_date = df[df['Medical Condition'] == selected_condition].groupby('Date of Admission').size().reset_index(name='Count')
    
    color_palette = px.colors.qualitative.Dark24
    if chart_type == "Bar Chart":
        fig = px.bar(admissions_by_date, x='Date of Admission', y='Count', 
                     title=f"Admissions for {selected_condition}", 
                     color='Count', color_continuous_scale=color_palette)
    else:
        fig = px.line(admissions_by_date, x='Date of Admission', y='Count', 
                      title=f"Admissions for {selected_condition}", 
                      line_shape="linear", markers=True)
    
    st.plotly_chart(fig)
    figs.append(fig)  # Store the visualization

# Billing amount histogram with filtering (Keeping only the histogram)
if 'Billing Amount' in df.columns:
    min_val, max_val = df['Billing Amount'].min(), df['Billing Amount'].max()
    billing_range = st.slider("Select Billing Amount Range", float(min_val), float(max_val), (float(min_val), float(max_val)))
    df_filtered_billing = df[(df['Billing Amount'] >= billing_range[0]) & (df['Billing Amount'] <= billing_range[1])]
    
    # Histogram - keep only this
    st.write(f"### Billing Amount Distribution (Histogram)")
    blue_palette = ['#0d47a1', '#1565c0', '#1976d2', '#1e88e5', '#2196f3', '#42a5f5', '#64b5f6']
    fig_hist = px.histogram(df_filtered_billing, x='Billing Amount', 
                            title="Billing Amount Distribution - Histogram", 
                            color_discrete_sequence=blue_palette)
    st.plotly_chart(fig_hist)
    figs.append(fig_hist)  # Store the visualization

# Button to download all visualizations as colorful HTML
if st.button("Download Colorful Visualizations as HTML"):
    html_content = convert_figs_to_html(figs)
    st.download_button(
        label="Download All Visualizations",
        data=html_content,
        file_name="colorful_visualizations.html",
        mime="text/html"
    )

st.success("Data loaded and processed successfully!")