# Interactive Data Visualization Dashboard

A powerful and user-friendly data visualization dashboard built with Streamlit. This application allows users to upload, analyze, and visualize data with various chart types and advanced analytics features.

## Features

- **Data Upload**: Support for CSV, Excel, TSV, and JSON files
- **Data Processing**: 
  - Automatic data type detection
  - Missing value handling
  - Data transformation options
- **Visualizations**:
  - Geospatial mapping
  - Time series analysis
  - Categorical data analysis
  - Numeric data analysis
  - Correlation analysis
  - Advanced clustering
- **Export Options**:
  - Export processed data in multiple formats
  - Export visualizations as HTML

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Upload your data file or use the default dataset
3. Use the sidebar to configure visualization settings
4. Explore different visualization types and analytics

## Data Requirements

The application can handle various data types:
- Numeric columns for statistical analysis
- Categorical columns for distribution analysis
- Date columns for time series analysis
- Latitude/Longitude columns for geospatial visualization

## Visualization Types

### Geospatial Analysis
- Circle Markers
- Marker Clusters
- Interactive maps with multiple layers

### Categorical Analysis
- Bar Charts
- Pie Charts
- Donut Charts

### Numeric Analysis
- Histograms
- Box Plots
- Violin Plots
- Correlation Heatmaps

### Advanced Analytics
- K-Means Clustering
- Cross-tabulation Analysis
- Scatter Plots with Trend Lines

## Error Handling

The application includes comprehensive error handling for:
- File upload issues
- Data processing errors
- Visualization generation problems
- Invalid user inputs

## Performance Optimization

- Data caching for improved performance
- Lazy loading for large datasets
- Efficient data processing

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 