# Dynmic Data visualization Dashboard-
# Healthcare Data Visualization Dashboard

## Overview
This interactive data visualization tool built with Streamlit provides comprehensive insights into healthcare data. It allows users to upload their own CSV data or use the provided sample healthcare dataset to generate dynamic visualizations for patient demographics, medical conditions, geographic distribution, and billing information.

## Features
- **Data Upload**: Upload custom healthcare CSV data or use the included sample dataset
- **Geospatial Visualization**: View patient locations on an interactive map with options for circle markers or clustered markers
- **Dynamic Chart Generation**: Auto-generates appropriate visualizations based on data types
- **Chart Type Selection**: Choose between bar charts and pie charts for categorical data
- **Medical Condition Filtering**: Filter time-series data by specific medical conditions
- **Billing Analysis**: Visualize billing amount distributions with interactive range filtering
- **Exportable Visualizations**: Download all generated visualizations as a single HTML file

## Requirements
- Python 3.7+
- Streamlit
- Pandas
- Folium
- Plotly Express
- Other dependencies listed in requirements.txt

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/healthcare-visualization.git
cd healthcare-visualization

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Upload your healthcare CSV data or use the default dataset

4. Explore the generated visualizations and interact with the filters

## Data Format
The application works best with CSV files that contain the following recommended columns:
- Latitude/Longitude (for geospatial mapping)
- Medical Condition
- Date of Admission
- Billing Amount
- Age
- Other categorical or numerical healthcare data

The application will detect column names dynamically and adapt accordingly.

## Project Structure
```
healthcare-visualization/
├── app.py                # Main Streamlit application
├── assets/               # Contains sample data
│   └── healthcare.csv    # Default dataset
├── requirements.txt      # Project dependencies
└── README.md             # This file
```

## Customization
- **Color Palettes**: The application uses vibrant color schemes from Plotly's qualitative and sequential color palettes
- **Chart Types**: Multiple visualization options are available for different data types
- **Map Styles**: Choose between different marker types for the geospatial visualization

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
[MIT License](LICENSE)

## Acknowledgments
- Streamlit for providing an excellent framework for data applications
- Plotly for the interactive visualization capabilities
- Folium for the geospatial mapping functionality
