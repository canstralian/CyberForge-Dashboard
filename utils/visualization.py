import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Color constants based on style guidelines
COLORS = {
    'primary': '#1A1A1A',
    'secondary': '#2C3E50',
    'accent': '#E74C3C',
    'success': '#2ECC71',
    'warning': '#F1C40F',
    'text': '#ECF0F1',
    'critical': '#E74C3C',
    'high': '#F1C40F',
    'medium': '#3498DB',
    'low': '#2ECC71'
}

def create_threat_timeline(data):
    """
    Create a timeline visualization of threats.
    
    Args:
        data (pd.DataFrame): DataFrame with timestamp and severity columns
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    fig = px.scatter(
        data,
        x='timestamp',
        y='severity',
        size='count',
        color='severity',
        color_discrete_map={
            'Critical': COLORS['critical'],
            'High': COLORS['high'],
            'Medium': COLORS['medium'],
            'Low': COLORS['low']
        },
        hover_data=['count'],
        height=400
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(26, 26, 26, 0)',
        plot_bgcolor='rgba(26, 26, 26, 0)',
        xaxis=dict(
            showgrid=False,
            title=None,
            tickfont=dict(color=COLORS['text'])
        ),
        yaxis=dict(
            showgrid=False,
            title=None,
            tickfont=dict(color=COLORS['text']),
            categoryorder='array',
            categoryarray=['Low', 'Medium', 'High', 'Critical']
        ),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    return fig

def create_category_distribution(categories, values):
    """
    Create a pie chart for category distribution.
    
    Args:
        categories (list): List of category names
        values (list): List of corresponding values
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    fig = px.pie(
        names=categories,
        values=values,
        hole=0.6,
        color_discrete_sequence=[COLORS['critical'], COLORS['high'], COLORS['medium'], 
                                COLORS['low'], '#9B59B6', '#E67E22']
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(26, 26, 26, 0)',
        plot_bgcolor='rgba(26, 26, 26, 0)',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="center",
            x=0.5,
            font=dict(color=COLORS['text'])
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=300,
    )
    
    return fig

def create_geo_threat_map(locations, z_values):
    """
    Create a choropleth map of global threats.
    
    Args:
        locations (list): List of country codes
        z_values (list): List of corresponding threat values
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    fig = go.Figure(data=go.Choropleth(
        locations=locations,
        z=z_values,
        colorscale='Reds',
        autocolorscale=False,
        reversescale=False,
        marker_line_color=COLORS['secondary'],
        marker_line_width=0.5,
        colorbar_title='Threat<br>Index',
    ))

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(26, 26, 26, 0)',
            coastlinecolor=COLORS['secondary'],
            landcolor=COLORS['primary'],
            oceancolor=COLORS['secondary'],
        ),
        paper_bgcolor='rgba(26, 26, 26, 0)',
        plot_bgcolor='rgba(26, 26, 26, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
    )
    
    return fig

def create_trend_chart(df, date_col, value_cols, names):
    """
    Create a stacked area chart for trend visualization.
    
    Args:
        df (pd.DataFrame): DataFrame with trend data
        date_col (str): Column name for date values
        value_cols (list): List of column names for values
        names (list): List of names for the legend
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    fig = go.Figure()
    
    colors = [COLORS['critical'], COLORS['high'], COLORS['medium'], COLORS['low']]
    
    for i, col in enumerate(value_cols):
        fig.add_trace(go.Scatter(
            x=df[date_col], y=df[col],
            mode='lines',
            line=dict(width=0.5, color=colors[i % len(colors)]),
            stackgroup='one',
            name=names[i]
        ))
    
    fig.update_layout(
        paper_bgcolor='rgba(26, 26, 26, 0)',
        plot_bgcolor='rgba(26, 26, 26, 0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=COLORS['text'])
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(
            showgrid=False,
            title=None,
            tickfont=dict(color=COLORS['text'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(44, 62, 80, 0.3)',
            title=None,
            tickfont=dict(color=COLORS['text'])
        ),
        height=300
    )
    
    return fig

def create_horizontal_bar(df, x_col, y_col, color_col=None):
    """
    Create a horizontal bar chart.
    
    Args:
        df (pd.DataFrame): DataFrame with bar data
        x_col (str): Column name for x-axis values
        y_col (str): Column name for y-axis categories
        color_col (str, optional): Column name for color values
        
    Returns:
        plotly.graph_objects.Figure: A plotly figure object
    """
    if color_col:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            orientation='h',
            color=color_col,
            color_continuous_scale=[COLORS['low'], COLORS['medium'], COLORS['high'], COLORS['critical']],
            height=300
        )
    else:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            orientation='h',
            height=300
        )
    
    fig.update_layout(
        paper_bgcolor='rgba(26, 26, 26, 0)',
        plot_bgcolor='rgba(26, 26, 26, 0)',
        coloraxis_showscale=False,
        xaxis=dict(
            title=None,
            showgrid=True,
            gridcolor='rgba(44, 62, 80, 0.3)',
            tickfont=dict(color=COLORS['text'])
        ),
        yaxis=dict(
            title=None,
            showgrid=False,
            tickfont=dict(color=COLORS['text'])
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

def generate_mock_trend_data(days=30, categories=4):
    """
    Generate mock trend data for demonstration purposes.
    
    Args:
        days (int): Number of days in the trend
        categories (int): Number of data categories
        
    Returns:
        pd.DataFrame: DataFrame with trend data
    """
    # Generate dates for the specified number of days
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days, 0, -1)]
    
    # Initialize data dictionary with dates
    data = {'Date': dates}
    
    # Category names
    category_names = ['Critical', 'High', 'Medium', 'Low']
    
    # Generate random values for each category
    for i in range(min(categories, len(category_names))):
        # More severe categories have lower counts
        mean_value = 10 * (categories - i)
        std_dev = mean_value * 0.2
        
        # Generate random values with normal distribution
        values = np.random.normal(mean_value, std_dev, days).astype(int)
        
        # Ensure no negative values
        values = np.maximum(values, 0)
        
        # Add to data dictionary
        data[category_names[i]] = values
    
    return pd.DataFrame(data)
