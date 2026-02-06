"""
Unit tests for Data Visualizer module.
"""

import unittest
from src.visualization.data_visualizer import generate_bar_chart, generate_line_chart, generate_pie_chart, visualize_osint_summary
import os

class TestVisualization(unittest.TestCase):
    def test_generate_bar_chart(self):
        data = {"A": 10, "B": 20, "C": 30}
        generate_bar_chart(data, save_path="test_bar_chart.png")
        self.assertTrue(os.path.exists("test_bar_chart.png"))
        os.remove("test_bar_chart.png")

    def test_generate_line_chart(self):
        x_values = [0, 1, 2]
        y_values = [5, 15, 10]
        generate_line_chart(x_values, y_values, save_path="test_line_chart.png")
        self.assertTrue(os.path.exists("test_line_chart.png"))
        os.remove("test_line_chart.png")

    def test_generate_pie_chart(self):
        labels = ["X", "Y", "Z"]
        sizes = [40, 35, 25]
        generate_pie_chart(labels, sizes, save_path="test_pie_chart.png")
        self.assertTrue(os.path.exists("test_pie_chart.png"))
        os.remove("test_pie_chart.png")

    def test_visualize_osint_summary(self):
        summary = "Test OSINT summary with repeated words test test test."
        paths = visualize_osint_summary(summary, output_dir="./test_visualizations")
        self.assertIn("bar_chart", paths)
        # Clean up created files
        for file in paths.values():
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists("./test_visualizations"):
            os.rmdir("./test_visualizations")

if __name__ == "__main__":
    unittest.main()