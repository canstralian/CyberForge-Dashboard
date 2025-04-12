import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

def parse_timerange(time_range):
    """
    Parse a time range string and return start and end dates.
    
    Args:
        time_range (str): Time range description
        
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    now = datetime.now()
    
    if time_range == "Last 24 Hours":
        start_date = now - timedelta(days=1)
        end_date = now
    elif time_range == "Last 7 Days":
        start_date = now - timedelta(days=7)
        end_date = now
    elif time_range == "Last 30 Days":
        start_date = now - timedelta(days=30)
        end_date = now
    elif time_range == "Last Quarter":
        start_date = now - timedelta(days=90)
        end_date = now
    elif time_range == "Year to Date":
        start_date = datetime(now.year, 1, 1)
        end_date = now
    else:  # Custom or unrecognized
        start_date = now - timedelta(days=30)  # Default to last 30 days
        end_date = now
    
    return start_date, end_date

def filter_alerts_by_severity(alerts_df, severities):
    """
    Filter alerts by severity levels.
    
    Args:
        alerts_df (pd.DataFrame): DataFrame containing alerts
        severities (list): List of severity levels to include
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if not severities:
        return alerts_df
    
    return alerts_df[alerts_df['severity'].isin(severities)]

def filter_alerts_by_timerange(alerts_df, time_range):
    """
    Filter alerts by time range.
    
    Args:
        alerts_df (pd.DataFrame): DataFrame containing alerts
        time_range (str): Time range description
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    start_date, end_date = parse_timerange(time_range)
    
    # Assuming timestamp column is already in datetime format
    # If not, convert it first: alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'])
    
    return alerts_df[(alerts_df['timestamp'] >= start_date) & 
                    (alerts_df['timestamp'] <= end_date)]

def filter_alerts_by_category(alerts_df, categories):
    """
    Filter alerts by categories.
    
    Args:
        alerts_df (pd.DataFrame): DataFrame containing alerts
        categories (list): List of categories to include
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if not categories:
        return alerts_df
    
    return alerts_df[alerts_df['category'].isin(categories)]

def filter_alerts_by_keyword(alerts_df, keyword):
    """
    Filter alerts by a keyword search.
    
    Args:
        alerts_df (pd.DataFrame): DataFrame containing alerts
        keyword (str): Keyword to search for
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if not keyword:
        return alerts_df
    
    # Search in description and any other text columns
    return alerts_df[alerts_df['description'].str.contains(keyword, case=False, na=False)]

def generate_alert_severity_distribution(alerts_df):
    """
    Calculate the distribution of alerts by severity.
    
    Args:
        alerts_df (pd.DataFrame): DataFrame containing alerts
        
    Returns:
        tuple: (labels, values) for severity distribution
    """
    severity_counts = alerts_df['severity'].value_counts()
    labels = severity_counts.index.tolist()
    values = severity_counts.values.tolist()
    
    return labels, values

def generate_alert_category_distribution(alerts_df):
    """
    Calculate the distribution of alerts by category.
    
    Args:
        alerts_df (pd.DataFrame): DataFrame containing alerts
        
    Returns:
        tuple: (labels, values) for category distribution
    """
    category_counts = alerts_df['category'].value_counts()
    labels = category_counts.index.tolist()
    values = category_counts.values.tolist()
    
    return labels, values

def calculate_alert_trends(alerts_df, time_range):
    """
    Calculate alert trends over the specified time range.
    
    Args:
        alerts_df (pd.DataFrame): DataFrame containing alerts
        time_range (str): Time range description
        
    Returns:
        pd.DataFrame: DataFrame with trend data
    """
    start_date, end_date = parse_timerange(time_range)
    
    # Convert timestamps to datetime objects if they aren't already
    if not isinstance(alerts_df['timestamp'].iloc[0], datetime):
        alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'])
    
    # Create date column for grouping
    alerts_df['date'] = alerts_df['timestamp'].dt.date
    
    # Group by date and severity
    grouped = alerts_df.groupby(['date', 'severity']).size().unstack(fill_value=0)
    
    # Ensure all dates in the range are included
    date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
    trend_df = pd.DataFrame(index=date_range)
    trend_df.index.name = 'date'
    
    # Ensure all severity levels are included
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        if severity not in grouped.columns:
            grouped[severity] = 0
    
    # Merge with the grouped data
    trend_df = trend_df.join(grouped, how='left').fillna(0)
    
    # Reset index to make date a column
    trend_df = trend_df.reset_index()
    
    return trend_df

def parse_ioc_data(text, ioc_type):
    """
    Parse text to extract indicators of compromise of the specified type.
    
    Args:
        text (str): Text to parse
        ioc_type (str): Type of IoC to extract (e.g., 'ip', 'domain', 'hash', 'url')
        
    Returns:
        list: Extracted IoCs
    """
    iocs = []
    
    if ioc_type == 'ip':
        # Simple IPv4 regex
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        iocs = re.findall(ip_pattern, text)
    
    elif ioc_type == 'domain':
        # Simple domain regex
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        iocs = re.findall(domain_pattern, text)
    
    elif ioc_type == 'hash':
        # MD5, SHA1, SHA256 regex
        hash_patterns = [
            r'\b[a-fA-F0-9]{32}\b',  # MD5
            r'\b[a-fA-F0-9]{40}\b',  # SHA1
            r'\b[a-fA-F0-9]{64}\b'   # SHA256
        ]
        
        for pattern in hash_patterns:
            iocs.extend(re.findall(pattern, text))
    
    elif ioc_type == 'url':
        # Simple URL regex
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        iocs = re.findall(url_pattern, text)
    
    return iocs

def generate_sample_threat_data():
    """
    Generate sample threat data for demonstration purposes.
    
    Returns:
        pd.DataFrame: DataFrame with sample threat data
    """
    # This function would be replaced with real data sourcing in production
    now = datetime.now()
    
    # Generate sample timestamps
    timestamps = []
    for day in range(14, 0, -1):
        base_date = now - timedelta(days=day)
        for hour in range(0, 24, 2):  # Every 2 hours
            timestamps.append(base_date + timedelta(hours=hour))
    
    # Generate sample severity levels
    severities = []
    counts = []
    
    for _ in range(len(timestamps)):
        rand = np.random.random()
        if rand > 0.7:  # 30% chance of critical
            severity = "Critical"
            count = np.random.randint(1, 4)
        elif rand > 0.5:  # 20% chance of high
            severity = "High"
            count = np.random.randint(1, 6)
        elif rand > 0.3:  # 20% chance of medium
            severity = "Medium"
            count = np.random.randint(1, 8)
        else:  # 30% chance of low
            severity = "Low"
            count = np.random.randint(1, 10)
        
        severities.append(severity)
        counts.append(count)
    
    # Create the dataframe
    return pd.DataFrame({
        'timestamp': timestamps,
        'severity': severities,
        'count': counts
    })
