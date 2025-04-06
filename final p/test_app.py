import unittest
import pandas as pd
import numpy as np
from app import (
    detect_columns,
    is_date_column,
    detect_date_columns,
    get_color_palette,
    validate_file_upload
)

class TestDataVisualizationApp(unittest.TestCase):
    def setUp(self):
        # Create sample data for testing
        self.sample_df = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=5),
            'Latitude': [37.7, 37.8, 37.9, 38.0, 38.1],
            'Longitude': [-122.5, -122.4, -122.3, -122.2, -122.1],
            'Category': ['A', 'B', 'C', 'D', 'E'],
            'Value': [1, 2, 3, 4, 5]
        })

    def test_detect_columns(self):
        # Test latitude detection
        lat_col = detect_columns(self.sample_df, ['Latitude', 'latitude', 'LAT'])
        self.assertEqual(lat_col, 'Latitude')

        # Test longitude detection
        lon_col = detect_columns(self.sample_df, ['Longitude', 'longitude', 'LON'])
        self.assertEqual(lon_col, 'Longitude')

        # Test non-existent column
        non_existent = detect_columns(self.sample_df, ['NonExistent'])
        self.assertIsNone(non_existent)

    def test_is_date_column(self):
        # Test date column
        self.assertTrue(is_date_column(self.sample_df['Date']))
        
        # Test non-date column
        self.assertFalse(is_date_column(self.sample_df['Value']))

    def test_detect_date_columns(self):
        # Test date column detection
        date_cols = detect_date_columns(self.sample_df)
        self.assertIn('Date', date_cols)
        self.assertEqual(len(date_cols), 1)

    def test_get_color_palette(self):
        # Test categorical palette
        cat_palette = get_color_palette('categorical', 5)
        self.assertIsNotNone(cat_palette)

        # Test sequential palette
        seq_palette = get_color_palette('sequential')
        self.assertIsNotNone(seq_palette)

    def test_validate_file_upload(self):
        # This test would require mocking the file upload
        # For now, we'll just test the None case
        self.assertIsNone(validate_file_upload(None))

if __name__ == '__main__':
    unittest.main() 