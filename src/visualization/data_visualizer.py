"""
Data Visualizer module.
Provides functions to generate visualizations for OSINT data.
Utilizes matplotlib for generating charts and graphs.
"""

import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from src.utils.logger import get_logger
import random

logger = get_logger(__name__)

def generate_bar_chart(data_dict, title="Bar Chart", xlabel="Categories", ylabel="Values", save_path=None):
    """
    Generates a bar chart from a dictionary of data.
    """
    categories = list(data_dict.keys())
    values = list(data_dict.values())
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories, values, color=[(random.random(), random.random(), random.random()) for _ in categories])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, height, f'{height}', ha='center', va='bottom')
    
    if save_path:
        plt.savefig(save_path)
        logger.info("Bar chart saved to %s", save_path)
    plt.close()

def generate_line_chart(x_values, y_values, title="Line Chart", xlabel="X-axis", ylabel="Y-axis", save_path=None):
    """
    Generates a line chart given x and y values.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    if save_path:
        plt.savefig(save_path)
        logger.info("Line chart saved to %s", save_path)
    plt.close()

def generate_pie_chart(labels, sizes, title="Pie Chart", save_path=None):
    """
    Generates a pie chart.
    """
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    plt.axis('equal')
    
    if save_path:
        plt.savefig(save_path)
        logger.info("Pie chart saved to %s", save_path)
    plt.close()

def visualize_osint_summary(osint_summary, output_dir="./visualizations"):
    """
    Parses OSINT summary data (assuming a dict with keys and numeric values) and creates multiple charts.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Simulate processing: if osint_summary is a string, create dummy data
    if isinstance(osint_summary, str):
        # Create dummy data based on text length and word frequency
        words = osint_summary.split()
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        # Use top 10 words for visualization
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        data_dict = dict(sorted_words)
    elif isinstance(osint_summary, dict):
        data_dict = osint_summary
    else:
        data_dict = {"Data": 1}
    
    # Generate bar chart
    bar_chart_path = os.path.join(output_dir, "bar_chart.png")
    generate_bar_chart(data_dict, title="OSINT Data Bar Chart", save_path=bar_chart_path)
    
    # Generate pie chart
    labels = list(data_dict.keys())
    sizes = list(data_dict.values())
    pie_chart_path = os.path.join(output_dir, "pie_chart.png")
    generate_pie_chart(labels, sizes, title="OSINT Data Pie Chart", save_path=pie_chart_path)
    
    # Generate line chart
    x_values = list(range(len(sizes)))
    line_chart_path = os.path.join(output_dir, "line_chart.png")
    generate_line_chart(x_values, sizes, title="OSINT Data Line Chart", xlabel="Index", ylabel="Frequency", save_path=line_chart_path)
    
    logger.info("Visualizations generated in %s", output_dir)
    return {"bar_chart": bar_chart_path, "pie_chart": pie_chart_path, "line_chart": line_chart_path}

def visualize_progress(iterable, description="Processing"):
    """
    Wraps an iterable with tqdm for progress visualization.
    """
    return tqdm(iterable, desc=description)