from datetime import datetime
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from sqlalchemy.exc import SQLAlchemyError
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import pandas as pd
import re
import tempfile
import shutil
import os
import mysql.connector
import google.generativeai as genai
import sqlite3
import pyodbc
from pyodbc import ProgrammingError
from st_chat_message import message
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import nbformat as nbf
import io
from contextlib import redirect_stdout
import json
import plotly.io as pio
import duckdb
from code_editor import code_editor
import time
st.set_page_config(
    page_title="Data Chat",
    # layout="wide"
)


# Initialize session state variables

# SQLite connection function



# MySQL connection function




# SQL Server connection function




# Load CSV or Excel file










# Query Interface page


       





# Helper functions























# def execute_code(code, df):
#     local_namespace = {"df": df}
#     try:
#         exec(code, globals(), local_namespace)
#         # Capture printed output
#         import io
#         from contextlib import redirect_stdout
#         with io.StringIO() as buf, redirect_stdout(buf):
#             exec(code, globals(), local_namespace)
#             output = buf.getvalue()

#         # Return the captured output or the result of the last expression
#         if output:
#             return output, None
#         else:
#             return local_namespace.get('result', None), None
#     except Exception as e:
#         error_msg = f"Error executing code: {type(e).__name__}: {str(e)}"
#         return None, error_msg





# def create_dashboard_html(figures_list, dashboard_title='Dashboard', fig_titles=None, dashboard_name='Dashboard'):
#     """
#     Generates an enhanced HTML dashboard containing all the plots from the figures_list.

#     Parameters:
#     - figures_list: List of Plotly figure objects.
#     - dashboard_title: Title of the dashboard (default is 'Dashboard').
#     - fig_titles: Optional list of titles for each figure.

#     Returns:
#     - HTML string of the dashboard.
#     """
#     # Prepare data for each figure using to_html instead of to_json
#     figures_html = []
#     for fig in figures_list:
#         fig_html = pio.to_html(fig, include_plotlyjs=False, full_html=False)  # Convert figure to HTML
#         figures_html.append(fig_html)

#     # Determine if the number of figures is odd
#     total_figures = len(figures_list)
#     is_odd = total_figures % 2 != 0

#     # Build the HTML
#     html_parts = []
#     html_parts.append('<!DOCTYPE html>')
#     html_parts.append('<html lang="en">')
#     html_parts.append('<head>')
#     html_parts.append('<meta charset="UTF-8">')
#     html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
#     html_parts.append(f'<title>{dashboard_title}</title>')
#     # Include Plotly.js from CDN
#     html_parts.append('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
#     # Include Google Fonts and Font Awesome
#     html_parts.append('<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">')
#     html_parts.append('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">')
#     # Include custom CSS for styling
#     html_parts.append('<style>')
#     # Include the full CSS styling here
#     html_parts.append('''
#     :root {
#         --primary-color: #4e54c8;
#         --secondary-color: #8f94fb;
#         --background-color: #f0f2f5;
#         --text-color: #333;
#         --header-height: 60px;
#         --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
#     }
#     [data-theme="dark"] {
#         --primary-color: #232526;
#         --secondary-color: #414345;
#         --background-color: #181818;
#         --text-color: #e0e0e0;
#         --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
#     }
#     body {
#         font-family: 'Roboto', sans-serif;
#         margin: 0;
#         padding: 0;
#         color: var(--text-color);
#         background-color: var(--background-color);
#         transition: background-color 0.3s, color 0.3s;
#     }
#     .header {
#         background: var(--gradient);
#         padding: 0 20px;
#         display: flex;
#         align-items: center;
#         justify-content: space-between;
#         color: white;
#         position: sticky;
#         top: 0;
#         height: var(--header-height);
#         z-index: 100;
#         box-shadow: 0 2px 5px rgba(0,0,0,0.1);
#     }
#     .header .logo {
#         font-size: 1.8em;
#         font-weight: bold;
#     }
#     .header .toggle-button {
#         background: none;
#         border: none;
#         color: white;
#         font-size: 1.5em;
#         cursor: pointer;
#         margin-left: 15px;
#         transition: transform 0.3s, color 0.3s;
#     }
#     .header .toggle-button:hover {
#         transform: scale(1.2);
#         color: #ffd700;
#     }
#     .sidebar {
#         position: fixed;
#         top: var(--header-height);
#         left: -260px;
#         width: 240px;
#         background: var(--gradient);
#         padding-top: 20px;
#         height: calc(100% - var(--header-height));
#         overflow-x: hidden;
#         transition: left 0.4s ease;
#         z-index: 99;
#         box-shadow: 2px 0 5px rgba(0,0,0,0.1);
#     }
#     .sidebar.active {
#         left: 0;
#     }
#     .sidebar .toggle-sidebar {
#         position: absolute;
#         top: 20px;
#         right: -35px;
#         background: var(--gradient);
#         color: white;
#         padding: 12px;
#         border-radius: 50%;
#         cursor: pointer;
#         box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
#         transition: transform 0.3s;
#     }
#     .sidebar .toggle-sidebar:hover {
#         transform: rotate(90deg);
#     }
#     .sidebar a {
#         padding: 15px 20px;
#         text-decoration: none;
#         font-size: 1em;
#         color: white;
#         display: flex;
#         align-items: center;
#         transition: background-color 0.2s, padding-left 0.3s;
#     }
#     .sidebar a:hover {
#         background-color: rgba(255, 255, 255, 0.1);
#         padding-left: 30px;
#     }
#     .sidebar a i {
#         margin-right: 10px;
#     }
#     .content {
#         margin-left: 20px;
#         padding: 80px 30px 30px 30px;
#         transition: margin-left 0.4s ease;
#     }
#     .content.shifted {
#         margin-left: 260px;
#     }
#     .figure {
#         margin-bottom: 50px;
#         background-color: white;
#         padding: 20px;
#         border-radius: 15px;
#         box-sizing: border-box;
#         box-shadow: 0 5px 15px rgba(0,0,0,0.1);
#         transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s;
#     }
#     [data-theme="dark"] .figure {
#         background-color: #1e1e1e;
#     }
#     .figure:hover {
#         box-shadow: 0 8px 25px rgba(0,0,0,0.2);
#         transform: translateY(-5px);
#     }
#     .figure-title {
#         text-align: center;
#         font-weight: bold;
#         margin-bottom: 20px;
#         font-size: 1.5em;
#         color: var(--text-color);
#     }
#     .footer {
#         text-align: center;
#         padding: 20px;
#         background: var(--gradient);
#         color: white;
#         position: relative;
#     }
#     .footer::before {
#         content: "";
#         position: absolute;
#         top: -20px;
#         left: 0;
#         right: 0;
#         height: 20px;
#         background: linear-gradient(to top, rgba(0,0,0,0.1), transparent);
#     }
#     /* Two-column grid for figures */
#     .grid-container {
#         display: grid;
#         grid-template-columns: repeat(2, 1fr);
#         grid-gap: 20px;
#     }
#     /* Make last item span two columns if total number is odd */
#     .grid-container .full-width {
#         grid-column: span 2;
#     }
#     /* Adjust to one column on smaller screens */
#     @media screen and (max-width: 768px) {
#         .header {
#             flex-direction: column;
#             align-items: flex-start;
#             height: auto;
#             padding: 10px 20px;
#         }
#         .header .toggle-buttons {
#             margin-top: 10px;
#             width: 100%;
#             display: flex;
#             justify-content: space-between;
#         }
#         .content {
#             margin-left: 0;
#             padding: 100px 20px 20px 20px;
#         }
#         .sidebar {
#             width: 100%;
#             height: calc(100% - var(--header-height));
#             position: fixed;
#             top: var(--header-height);
#             left: -100%;
#         }
#         .sidebar.active {
#             left: 0;
#         }
#         .content.shifted {
#             margin-left: 0;
#         }
#         /* Change grid to one column on small screens */
#         .grid-container {
#             grid-template-columns: 1fr;
#         }
#         /* Ensure full-width items still occupy full width */
#         .grid-container .full-width {
#             grid-column: span 1;
#         }
#     }
#     ''')
#     html_parts.append('</style>')
#     html_parts.append('</head>')
#     html_parts.append('<body>')

#     # Header
#     html_parts.append(f'''
#     <div class="header">
#         <div class="logo">{dashboard_title}</div>
#         <div class="toggle-buttons">
#             <button class="toggle-button" onclick="toggleDarkMode()" title="Toggle Dark Mode">
#                 <i class="fas fa-adjust"></i>
#             </button>
#             <button class="toggle-button" onclick="toggleSidebar()" title="Toggle Sidebar">
#                 <i class="fas fa-bars"></i>
#             </button>
#         </div>
#     </div>
#     ''')

#     # Sidebar with navigation links
#     html_parts.append('<div class="sidebar" id="sidebar">')
#     html_parts.append('<div class="toggle-sidebar" onclick="toggleSidebar()" title="Close Sidebar"><i class="fas fa-times"></i></div>')
#     if fig_titles:
#         for i, title in enumerate(fig_titles):
#             html_parts.append(f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> {title}</a>')
#     else:
#         for i in range(len(figures_list)):
#             html_parts.append(f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> Figure {i+1}</a>')
#     html_parts.append('</div>')

#     # Main content
#     html_parts.append('<div class="content" id="content">')
#     html_parts.append('<div class="grid-container">')
#     for i in range(len(figures_html)):
#         # Determine if this is the last item and if total figures are odd
#         last_item = (i == total_figures - 1) and is_odd
#         figure_class = "figure"
#         if last_item:
#             figure_class += " full-width"
#         html_parts.append(f'<div class="{figure_class}" id="figure-{i}">')
#         if fig_titles and i < len(fig_titles):
#             html_parts.append(f'<div class="figure-title">{fig_titles[i]}</div>')
#         else:
#             html_parts.append(f'<div class="figure-title">Figure {i+1}</div>')
#         # Insert the figure HTML
#         html_parts.append(figures_html[i])
#         html_parts.append('</div>')
#     html_parts.append('</div>')  # Close grid-container
#     html_parts.append('</div>')  # Close content

#     # Footer
#     html_parts.append('<div class="footer">&copy; 2023 Your Company</div>')

#     # JavaScript for dark mode toggle and sidebar interactions
#     html_parts.append('''
#     <script>
#     // Function to toggle dark mode
#     function toggleDarkMode() {
#         var body = document.body;
#         if (body.getAttribute('data-theme') === 'dark') {
#             body.removeAttribute('data-theme');
#             localStorage.removeItem('theme');
#         } else {
#             body.setAttribute('data-theme', 'dark');
#             localStorage.setItem('theme', 'dark');
#         }
#     }

#     // Sidebar toggle
#     function toggleSidebar() {
#         var sidebar = document.getElementById('sidebar');
#         var content = document.getElementById('content');
#         sidebar.classList.toggle('active');
#         content.classList.toggle('shifted');
#     }

#     // Remember theme preference
#     window.onload = function() {
#         if (localStorage.getItem('theme') === 'dark') {
#             document.body.setAttribute('data-theme', 'dark');
#         }
#     }
#     </script>
#     ''')

#     html_parts.append('</body>')
#     html_parts.append('</html>')

#     html = '\n'.join(html_parts)

#     # Save HTML to file
#     now = datetime.now()
#     filename_date = now.strftime("%Y-%m-%d_%H-%M-%S")
#     file_name = f"{dashboard_name}_{filename_date}.html"

#     with open(file_name, 'w', encoding='utf-8') as f:
#         f.write(html)

#     return file_name
# def ensure_plot_colors(plot_json: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
#     """
#     Comprehensive function to add default colors to plotly JSON data for all trace types.
    
#     Args:
#         plot_json (Union[str, Dict]): Plotly figure JSON data or dictionary
        
#     Returns:
#         Dict: Modified plotly JSON data with colors added where missing
#     """
#     # Convert string to dict if needed
#     if isinstance(plot_json, str):
#         plot_data = json.loads(plot_json)
#     else:
#         plot_data = plot_data = json.loads(json.dumps(plot_json))  # Deep copy through serialization
    
#     # Default colors list (Plotly's default color sequence)
#     default_colors = [
#         '#1f77b4',  # muted blue
#         '#ff7f0e',  # safety orange
#         '#2ca02c',  # cooked asparagus green
#         '#d62728',  # brick red
#         '#9467bd',  # muted purple
#         '#8c564b',  # chestnut brown
#         '#e377c2',  # raspberry yogurt pink
#         '#7f7f7f',  # middle gray
#         '#bcbd22',  # curry yellow-green
#         '#17becf'   # blue-teal
#     ]
    
#     # Default colorscales for different plot types
#     default_colorscales = {
#         'heatmap': 'Viridis',
#         'contour': 'Viridis',
#         'surface': 'Viridis',
#         'histogram2d': 'Viridis',
#         'histogram2dcontour': 'Viridis',
#         'choropleth': 'Viridis',
#         'densitymapbox': 'Viridis'
#     }
    
#     # Properties that might need colors for different trace types
#     color_properties = {
#         'scatter': ['marker.color', 'line.color', 'error_x.color', 'error_y.color'],
#         'scattergl': ['marker.color', 'line.color'],
#         'scatter3d': ['marker.color', 'line.color', 'error_x.color', 'error_y.color', 'error_z.color'],
#         'bar': ['marker.color', 'error_x.color', 'error_y.color'],
#         'box': ['marker.color', 'line.color'],
#         'violin': ['marker.color', 'line.color'],
#         'candlestick': ['increasing.line.color', 'decreasing.line.color'],
#         'ohlc': ['increasing.line.color', 'decreasing.line.color'],
#         'waterfall': ['increasing.marker.color', 'decreasing.marker.color'],
#         'funnel': ['marker.color'],
#         'funnelarea': ['marker.colors'],
#         'pie': ['marker.colors'],
#         'sunburst': ['marker.colors'],
#         'treemap': ['marker.colors'],
#         'sankey': ['node.color', 'link.color'],
#         'indicator': ['marker.color', 'line.color'],
#         'icicle': ['marker.colors'],
#         'carpet': ['aaxis.color', 'baxis.color']
#     }

#     def set_nested_value(obj: Dict, path: str, value: Any) -> None:
#         """Set a value in a nested dictionary using a dot-notation path."""
#         parts = path.split('.')
#         for part in parts[:-1]:
#             if part not in obj:
#                 obj[part] = {}
#             obj = obj[part]
#         if parts[-1] not in obj:
#             obj[parts[-1]] = value

#     def get_nested_value(obj: Dict, path: str) -> Any:
#         """Get a value from a nested dictionary using a dot-notation path."""
#         parts = path.split('.')
#         for part in parts:
#             if part not in obj:
#                 return None
#             obj = obj[part]
#         return obj

#     if 'data' in plot_data:
#         for i, trace in enumerate(plot_data['data']):
#             color_index = i % len(default_colors)
#             trace_type = trace.get('type', 'scatter')  # Default to scatter if type not specified
            
#             # Handle colorscale-based plots
#             if trace_type in default_colorscales and 'colorscale' not in trace:
#                 trace['colorscale'] = default_colorscales[trace_type]
            
#             # Handle special cases for specific plot types
#             if trace_type in ['pie', 'sunburst', 'treemap', 'icicle', 'funnelarea']:
#                 if 'marker' not in trace:
#                     trace['marker'] = {}
#                 if 'colors' not in trace['marker']:
#                     trace['marker']['colors'] = default_colors
            
#             # Handle sankey diagrams
#             elif trace_type == 'sankey':
#                 if 'node' not in trace:
#                     trace['node'] = {}
#                 if 'color' not in trace['node']:
#                     trace['node']['color'] = default_colors[color_index]
#                 if 'link' not in trace:
#                     trace['link'] = {}
#                 if 'color' not in trace['link']:
#                     trace['link']['color'] = default_colors[(color_index + 1) % len(default_colors)]
            
#             # Handle properties for the specific trace type
#             if trace_type in color_properties:
#                 for property_path in color_properties[trace_type]:
#                     if not get_nested_value(trace, property_path):
#                         set_nested_value(trace, property_path, default_colors[color_index])
            
#             # Handle showscale property for applicable traces
#             if trace_type in ['heatmap', 'contour', 'surface']:
#                 if 'showscale' not in trace:
#                     trace['showscale'] = True
            
#             # Handle special line styling
#             if 'line' in trace and isinstance(trace['line'], dict):
#                 if 'width' not in trace['line']:
#                     trace['line']['width'] = 2
            
#             # Handle special marker styling
#             if 'marker' in trace and isinstance(trace['marker'], dict):
#                 if 'size' not in trace['marker']:
#                     trace['marker']['size'] = 6
#                 if 'opacity' not in trace['marker']:
#                     trace['marker']['opacity'] = 1
    
#     # Handle layout colors if present
#     if 'layout' in plot_data:
#         layout = plot_data['layout']
#         if 'paper_bgcolor' not in layout:
#             layout['paper_bgcolor'] = 'white'
#         if 'plot_bgcolor' not in layout:
#             layout['plot_bgcolor'] = 'white'
    
#     return plot_data

# import numpy as np
# def numpy_encoder(obj):
#     """Custom JSON encoder for NumPy types"""
#     if isinstance(obj, np.integer):
#         return int(obj)
#     elif isinstance(obj, np.floating):
#         return float(obj)
#     elif isinstance(obj, np.ndarray):
#         return obj.tolist()
#     elif isinstance(obj, np.bool_):
#         return bool(obj)
#     raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

# def ensure_plot_colors(plot_json):
#     """
#     Add default colors to plotly JSON data if colors are not specified.
#     Now handles NumPy arrays properly.
#     """
#     # Convert to dict and handle NumPy arrays
#     if isinstance(plot_json, str):
#         plot_data = json.loads(plot_json)
#     else:
#         try:
#             plot_data = json.loads(json.dumps(plot_json, default=numpy_encoder))
#         except TypeError as e:
#             print(f"Error serializing plot data: {e}")
#             # Fall back to direct copy if serialization fails
#             plot_data = plot_json.copy()
    
#     # Default colors list
#     default_colors = [
#         '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
#         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
#     ]
    
#     if 'data' in plot_data:
#         for i, trace in enumerate(plot_data['data']):
#             color_index = i % len(default_colors)
            
#             # Handle different trace types
#             if 'type' in trace:
#                 if trace['type'] in ['scatter', 'line']:
#                     if 'line' in trace and 'color' not in trace['line']:
#                         trace['line']['color'] = default_colors[color_index]
#                     if 'marker' in trace and 'color' not in trace['marker']:
#                         trace['marker']['color'] = default_colors[color_index]
                
#                 elif trace['type'] in ['bar', 'column']:
#                     if 'marker' not in trace:
#                         trace['marker'] = {}
#                     if 'color' not in trace['marker']:
#                         trace['marker']['color'] = default_colors[color_index]
                
#                 elif trace['type'] == 'pie':
#                     if 'marker' not in trace:
#                         trace['marker'] = {'colors': default_colors}
#                     elif 'colors' not in trace['marker']:
#                         trace['marker']['colors'] = default_colors
            
#             # For traces without specified type
#             elif 'marker' in trace and 'color' not in trace['marker']:
#                 trace['marker']['color'] = default_colors[color_index]
    
#     return plot_data

# def create_enhanced_dashboard(figures_list, dashboard_title='Dashboard', fig_titles=None, dashboard_name='Dashboard'):
#     """
#     Creates a dashboard with automatic color management for all plots.
#     Now handles NumPy arrays properly.
#     """
#     # First, ensure colors for all figures
#     enhanced_figures = []
#     for fig in figures_list:
#         try:
#             # Convert figure to dict
#             fig_dict = fig.to_dict()
#             fig_dict = go.Figure(fig_dict)
            
#             # Apply color enhancement
#             colored_fig_dict = ensure_plot_colors(fig_dict)
            
#             # Convert back to Plotly figure
#             enhanced_fig = go.Figure(colored_fig_dict)
#             enhanced_figures.append(enhanced_fig)
#         except Exception as e:
#             print(f"Error processing figure: {e}")
#             # If enhancement fails, use original figure
#             enhanced_figures.append(fig)
    
#     # Create dashboard with enhanced figures
#     file_name = create_dashboard_html(
#         figures_list=enhanced_figures,
#         dashboard_title=dashboard_title,
#         fig_titles=fig_titles,
#         dashboard_name=dashboard_name
#     )
    
#     return file_name




# def create_enhanced_dashboard(figures_list, dashboard_title='Dashboard', fig_titles=None, dashboard_name='Dashboard'):
#     """
#     Creates a dashboard with automatic color management for all plots.
    
#     Parameters:
#     - figures_list: List of Plotly figure objects
#     - dashboard_title: Title of the dashboard
#     - fig_titles: Optional list of titles for each figure
#     - dashboard_name: Name used for the output file
    
#     Returns:
#     - str: Name of the created HTML file
#     """
#     # First, ensure colors for all figures
#     enhanced_figures = []
#     for fig in figures_list:
#         # Convert figure to dict
#         fig_dict = fig.to_dict()
        
#         # Apply color enhancement
#         colored_fig_dict = ensure_plot_colors(fig_dict)
        
#         # Convert back to Plotly figure
#         enhanced_fig = go.Figure(colored_fig_dict)
#         enhanced_figures.append(enhanced_fig)
    
#     # Create dashboard with enhanced figures
#     file_name = create_dashboard_html(
#         figures_list=enhanced_figures,
#         dashboard_title=dashboard_title,
#         fig_titles=fig_titles,
#         dashboard_name=dashboard_name
#     )
    
#     return file_name




# Main app logic


def main():
    init_session_state()

    if st.session_state.page == "page1":
        connection_page()
    elif st.session_state.page == "page2":
        query_interface_page()


if __name__ == "__main__":
    main()
