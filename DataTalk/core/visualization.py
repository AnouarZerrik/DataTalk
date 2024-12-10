import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
from core.utils import *
from core.execution import *
import streamlit as st
import json




def generate_fig(code_python, external_data):
    code = extract_code_without_blocks(code_python)
    fig, error = execute_python_code_plotly(code, external_data)
    return fig, error


def create_dashboard_html(figures_list, dashboard_title='Dashboard', fig_titles=None, dashboard_name='Dashboard'):
    """
    Generates an enhanced HTML dashboard containing all the plots from the figures_list.

    Parameters:
    - figures_list: List of Plotly figure objects.
    - dashboard_title: Title of the dashboard (default is 'Dashboard').
    - fig_titles: Optional list of titles for each figure.

    Returns:
    - HTML string of the dashboard.
    """
    # Prepare data for each figure
    figures_data = []
    for fig in figures_list:
        fig_json_str = fig.to_json()  # Serialize the figure to JSON string
        # Convert JSON string to Python dict
        fig_json = json.loads(fig_json_str)
        figures_data.append(fig_json)

    # Determine if the number of figures is odd
    total_figures = len(figures_list)
    is_odd = total_figures % 2 != 0

    # Build the HTML
    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html lang="en">')
    html_parts.append('<head>')
    html_parts.append('<meta charset="UTF-8">')
    html_parts.append(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append(f'<title>{dashboard_title}</title>')
    # Include Plotly.js from CDN
    html_parts.append(
        '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
    # Include Google Fonts and Font Awesome
    html_parts.append(
        '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">')
    html_parts.append(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">')
    # Include custom CSS for styling
    html_parts.append('<style>')
    # Include the full CSS styling here
    html_parts.append('''
    :root {
        --primary-color: #4e54c8;
        --secondary-color: #8f94fb;
        --background-color: #f0f2f5;
        --text-color: #333;
        --header-height: 60px;
        --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    }
    [data-theme="dark"] {
        --primary-color: #232526;
        --secondary-color: #414345;
        --background-color: #181818;
        --text-color: #e0e0e0;
        --gradient: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    }
    body {
        font-family: 'Roboto', sans-serif;
        margin: 0;
        padding: 0;
        color: var(--text-color);
        background-color: var(--background-color);
        transition: background-color 0.3s, color 0.3s;
    }
    .header {
        background: var(--gradient);
        padding: 0 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        position: sticky;
        top: 0;
        height: var(--header-height);
        z-index: 100;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .header .logo {
        font-size: 1.8em;
        font-weight: bold;
    }
    .header .toggle-button {
        background: none;
        border: none;
        color: white;
        font-size: 1.5em;
        cursor: pointer;
        margin-left: 15px;
        transition: transform 0.3s, color 0.3s;
    }
    .header .toggle-button:hover {
        transform: scale(1.2);
        color: #ffd700;
    }
    .sidebar {
        position: fixed;
        top: var(--header-height);
        left: -260px;
        width: 240px;
        background: var(--gradient);
        padding-top: 20px;
        height: calc(100% - var(--header-height));
        overflow-x: hidden;
        transition: left 0.4s ease;
        z-index: 99;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
    }
    .sidebar.active {
        left: 0;
    }
    .sidebar .toggle-sidebar {
        position: absolute;
        top: 20px;
        right: -35px;
        background: var(--gradient);
        color: white;
        padding: 12px;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: transform 0.3s;
    }
    .sidebar .toggle-sidebar:hover {
        transform: rotate(90deg);
    }
    .sidebar a {
        padding: 15px 20px;
        text-decoration: none;
        font-size: 1em;
        color: white;
        display: flex;
        align-items: center;
        transition: background-color 0.2s, padding-left 0.3s;
    }
    .sidebar a:hover {
        background-color: rgba(255, 255, 255, 0.1);
        padding-left: 30px;
    }
    .sidebar a i {
        margin-right: 10px;
    }
    .content {
        margin-left: 20px;
        padding: 80px 30px 30px 30px;
        transition: margin-left 0.4s ease;
    }
    .content.shifted {
        margin-left: 260px;
    }
    .figure {
        margin-bottom: 50px;
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-sizing: border-box;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s;
    }
    [data-theme="dark"] .figure {
        background-color: #1e1e1e;
    }
    .figure:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        transform: translateY(-5px);
    }
    .figure-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        font-size: 1.5em;
        color: var(--text-color);
    }
    .footer {
        text-align: center;
        padding: 20px;
        background: var(--gradient);
        color: white;
        position: relative;
    }
    .footer::before {
        content: "";
        position: absolute;
        top: -20px;
        left: 0;
        right: 0;
        height: 20px;
        background: linear-gradient(to top, rgba(0,0,0,0.1), transparent);
    }
    /* Two-column grid for figures */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        grid-gap: 20px;
    }
    /* Make last item span two columns if total number is odd */
    .grid-container .full-width {
        grid-column: span 2;
    }
    /* Adjust to one column on smaller screens */
    @media screen and (max-width: 768px) {
        .header {
            flex-direction: column;
            align-items: flex-start;
            height: auto;
            padding: 10px 20px;
        }
        .header .toggle-buttons {
            margin-top: 10px;
            width: 100%;
            display: flex;
            justify-content: space-between;
        }
        .content {
            margin-left: 0;
            padding: 100px 20px 20px 20px;
        }
        .sidebar {
            width: 100%;
            height: calc(100% - var(--header-height));
            position: fixed;
            top: var(--header-height);
            left: -100%;
        }
        .sidebar.active {
            left: 0;
        }
        .content.shifted {
            margin-left: 0;
        }
        /* Change grid to one column on small screens */
        .grid-container {
            grid-template-columns: 1fr;
        }
        /* Ensure full-width items still occupy full width */
        .grid-container .full-width {
            grid-column: span 1;
        }
    }
    ''')
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    # Header
    html_parts.append(f'''
    <div class="header">
        <div class="logo">{dashboard_title}</div>
        <div class="toggle-buttons">
            <button class="toggle-button" onclick="toggleDarkMode()" title="Toggle Dark Mode">
                <i class="fas fa-adjust"></i>
            </button>
            <button class="toggle-button" onclick="toggleSidebar()" title="Toggle Sidebar">
                <i class="fas fa-bars"></i>
            </button>
        </div>
    </div>
    ''')
    # Sidebar with navigation links
    html_parts.append('<div class="sidebar" id="sidebar">')
    html_parts.append(
        '<div class="toggle-sidebar" onclick="toggleSidebar()" title="Close Sidebar"><i class="fas fa-times"></i></div>')
    if fig_titles:
        for i, title in enumerate(fig_titles):
            html_parts.append(
                f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> {title}</a>')
    else:
        for i in range(len(figures_list)):
            html_parts.append(
                f'<a href="#figure-{i}"><i class="fas fa-chart-bar"></i> Figure {i+1}</a>')
    html_parts.append('</div>')
    # Main content
    html_parts.append('<div class="content" id="content">')
    html_parts.append('<div class="grid-container">')
    for i in range(len(figures_data)):
        # Determine if this is the last item and if total figures are odd
        last_item = (i == total_figures - 1) and is_odd
        figure_class = "figure"
        if last_item:
            figure_class += " full-width"
        html_parts.append(f'<div class="{figure_class}" id="figure-{i}">')
        if fig_titles and i < len(fig_titles):
            html_parts.append(
                f'<div class="figure-title">{fig_titles[i]}</div>')
        elif not fig_titles:
            html_parts.append(f'<div class="figure-title">Figure {i+1}</div>')
        html_parts.append(f'<div id="plot-{i}"></div>')
        html_parts.append('</div>')
    html_parts.append('</div>')  # Close grid-container
    html_parts.append('</div>')  # Close content
    # Footer
    html_parts.append('<div class="footer">&copy; 2023 Your Company</div>')
    # JavaScript for interactivity and plots
    html_parts.append('<script>')
    # Include the plot data and layout
    html_parts.append('var figures = [];')
    for i, fig_json in enumerate(figures_data):
        fig_json_str = json.dumps(fig_json)
        html_parts.append(f'figures[{i}] = {fig_json_str};')
    html_parts.append('''
    // Function to render all plots
    function renderPlots(template) {
        for (var i = 0; i < figures.length; i++) {
            var fig = figures[i];
            var config = {responsive: true};
            // Apply the template
            if (!fig.layout) fig.layout = {};
            fig.layout.template = template;
            Plotly.newPlot('plot-' + i, fig.data, fig.layout, config);
        }
    }
    // Function to resize all plots
    function resizePlots() {
        for (var i = 0; i < figures.length; i++) {
            Plotly.Plots.resize(document.getElementById('plot-' + i));
        }
    }
    // Initial rendering of plots
    var initialTemplate = (localStorage.getItem('theme') === 'dark') ? 'plotly_dark' : 'plotly';
    renderPlots(initialTemplate);
    // Dark mode toggle
    function toggleDarkMode() {
        var body = document.body;
        var newTemplate = 'plotly';
        if (body.getAttribute('data-theme') === 'dark') {
            body.removeAttribute('data-theme');
            localStorage.removeItem('theme');
            newTemplate = 'plotly';
        } else {
            body.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            newTemplate = 'plotly_dark';
        }
        // Re-render plots with new template
        renderPlots(newTemplate);
    }
    // Remember theme preference
    window.onload = function() {
        if (localStorage.getItem('theme') === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
        }
        var initialTemplate = (localStorage.getItem('theme') === 'dark') ? 'plotly_dark' : 'plotly';
        renderPlots(initialTemplate);
    }
    // Sidebar toggle
    function toggleSidebar() {
        var sidebar = document.getElementById('sidebar');
        var content = document.getElementById('content');
        sidebar.classList.toggle('active');
        content.classList.toggle('shifted');
        // Wait for the CSS transition to finish before resizing plots
        setTimeout(function() {
            resizePlots();
        }, 400);
    }
    // Resize plots on window resize
    window.addEventListener('resize', resizePlots);
    // Smooth scrolling
    document.querySelectorAll('.sidebar a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            if (window.innerWidth <= 768) {
                toggleSidebar(); // Close sidebar on link click for mobile
            }
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    </script>
    ''')
    html_parts.append('</body>')
    html_parts.append('</html>')

    html = '\n'.join(html_parts)
    from datetime import datetime

# Get current date and time
    now = datetime.now()

    # Format it in a suitable way for filenames (e.g., YYYY-MM-DD_HH-MM-SS)
    filename_date = now.strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{dashboard_name}_{filename_date}.html"
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html)

    return file_name












