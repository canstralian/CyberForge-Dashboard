"""
Search History and Trends Component

This component provides UI for displaying and analyzing search history and trends.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import json
from typing import Dict, List, Any, Optional
import random

from src.streamlit_database import get_async_session
from src.api.services.search_history_service import (
    get_search_history,
    get_trending_topics,
    get_search_trend_analysis,
    get_popular_searches,
    add_search_history,
    save_search,
    create_saved_search,
    get_saved_searches
)

# For demo/placeholder data when database is not populated
def generate_demo_trends():
    """Generate demo trend data"""
    topics = [
        "ransomware", "databreach", "malware", "phishing", "zeroday",
        "darkmarket", "cryptolocker", "anonymity", "botnet", "exploit",
        "vulnerability", "trojan", "blackmarket", "identity", "creditcard",
        "hacking", "ddos", "credentials", "bitcoin", "monero"
    ]
    
    return [
        {
            "topic": topic,
            "mentions": random.randint(5, 100),
            "growth_rate": random.uniform(0.5, 25.0)
        }
        for topic in random.sample(topics, min(len(topics), 10))
    ]

def generate_demo_search_data(days=30):
    """Generate demo search frequency data"""
    base_date = datetime.now() - timedelta(days=days)
    dates = [base_date + timedelta(days=i) for i in range(days)]
    
    base_count = 10
    trend = [random.randint(max(0, base_count-5), base_count+15) for _ in range(days)]
    # Add a spike for visual interest
    spike_day = random.randint(5, days-5)
    trend[spike_day] = trend[spike_day] * 3
    
    return [
        {"interval": date, "count": count}
        for date, count in zip(dates, trend)
    ]

def generate_demo_search_categories():
    """Generate demo search categories data"""
    categories = [
        "Marketplace", "Forum", "Data Breach", "Hacking Tools", 
        "Credential Dumps", "Crypto", "Scam", "Uncategorized"
    ]
    return [
        {"category": cat, "count": random.randint(10, 100)}
        for cat in categories
    ]

def generate_demo_popular_searches():
    """Generate demo popular searches data"""
    searches = [
        "ransomware as a service", "credit card dumps", "personal data breach",
        "hacking tools", "bank account access", "identity documents", "covid vaccine cards",
        "social security numbers", "corporate credentials", "zero day exploits"
    ]
    return [
        {"query": query, "count": random.randint(5, 50)}
        for query in searches
    ]

async def get_trend_data(days=90, trend_days=7, limit=10):
    """Get trend data from the database"""
    try:
        # Create a session without context manager
        from src.streamlit_database import async_session
        session = async_session()
        
        try:
            data = await get_search_trend_analysis(
                db=session,
                days=days,
                trend_days=trend_days,
                limit=limit
            )
            await session.commit()
            return data
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    except Exception as e:
        st.error(f"Error fetching trend data: {e}")
        # Use demo data as fallback
        return {
            "frequency": generate_demo_search_data(days),
            "popular_searches": generate_demo_popular_searches(),
            "trending_topics": generate_demo_trends(),
            "categories": generate_demo_search_categories(),
            "recent_popular": generate_demo_popular_searches(),
            "velocity": random.uniform(-10, 30),
            "total_searches": {
                "total": 1000,
                "recent": 400,
                "previous": 600
            }
        }

async def save_search_query(query, user_id=None, category=None, tags=None):
    """Save a search query to the database"""
    try:
        # Create a session without context manager
        from src.streamlit_database import async_session
        session = async_session()
        
        try:
            search = await add_search_history(
                db=session,
                query=query,
                user_id=user_id,
                category=category,
                tags=tags,
                result_count=random.randint(5, 100)  # Placeholder
            )
            await session.commit()
            return search
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    except Exception as e:
        st.error(f"Error saving search: {e}")
        return None

async def get_user_searches(user_id=None, limit=50):
    """Get search history for a user"""
    try:
        # Create a session without context manager
        from src.streamlit_database import async_session
        session = async_session()
        
        try:
            searches = await get_search_history(
                db=session,
                user_id=user_id,
                limit=limit
            )
            await session.commit()
            return searches
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    except Exception as e:
        st.error(f"Error fetching search history: {e}")
        return []

async def get_user_saved_searches(user_id=None):
    """Get saved searches for a user"""
    try:
        # Create a session without context manager
        from src.streamlit_database import async_session
        session = async_session()
        
        try:
            searches = await get_saved_searches(
                db=session,
                user_id=user_id
            )
            await session.commit()
            return searches
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    except Exception as e:
        st.error(f"Error fetching saved searches: {e}")
        return []

async def create_new_saved_search(name, query, user_id=None, frequency=24, category=None):
    """Create a new saved search"""
    try:
        async with get_async_session() as session:
            saved_search = await create_saved_search(
                db=session,
                name=name,
                query=query,
                user_id=user_id or 1,  # Default user ID
                frequency=frequency,
                category=category
            )
            return saved_search
    except Exception as e:
        st.error(f"Error creating saved search: {e}")
        return None

def plot_search_trends(frequency_data):
    """Create a plot of search frequency over time"""
    if not frequency_data:
        return None
    
    df = pd.DataFrame(frequency_data)
    if 'interval' in df.columns:
        df['interval'] = pd.to_datetime(df['interval'])
        
        fig = px.line(
            df, 
            x='interval', 
            y='count',
            title='Search Frequency Over Time',
            labels={'interval': 'Date', 'count': 'Number of Searches'},
            template='plotly_dark'
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Searches",
            plot_bgcolor='rgba(17, 17, 17, 0.8)',
            paper_bgcolor='rgba(17, 17, 17, 0)',
            font=dict(color='white')
        )
        
        return fig
    
    return None

def plot_category_distribution(category_data):
    """Create a plot of search categories distribution"""
    if not category_data:
        return None
    
    df = pd.DataFrame(category_data)
    
    fig = px.pie(
        df, 
        values='count', 
        names='category',
        title='Search Categories Distribution',
        template='plotly_dark',
        hole=0.4
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(17, 17, 17, 0.8)',
        paper_bgcolor='rgba(17, 17, 17, 0)',
        font=dict(color='white')
    )
    
    return fig

def plot_trending_topics(trending_data):
    """Create a bar chart of trending topics"""
    if not trending_data:
        return None
    
    df = pd.DataFrame(trending_data)
    if len(df) == 0:
        return None
    
    # Sort by mentions or growth rate
    df = df.sort_values('growth_rate', ascending=False)
    
    fig = px.bar(
        df, 
        y='topic', 
        x='growth_rate',
        title='Trending Topics by Growth Rate',
        labels={'topic': 'Topic', 'growth_rate': 'Growth Rate (%)'},
        orientation='h',
        template='plotly_dark',
        color='growth_rate',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Growth Rate (%)",
        yaxis_title="Topic",
        plot_bgcolor='rgba(17, 17, 17, 0.8)',
        paper_bgcolor='rgba(17, 17, 17, 0)',
        font=dict(color='white'),
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def plot_popular_searches(popular_data):
    """Create a bar chart of popular searches"""
    if not popular_data:
        return None
    
    df = pd.DataFrame(popular_data)
    if len(df) == 0:
        return None
    
    df = df.sort_values('count', ascending=True)
    
    fig = px.bar(
        df, 
        y='query', 
        x='count',
        title='Most Popular Search Terms',
        labels={'query': 'Search Term', 'count': 'Number of Searches'},
        orientation='h',
        template='plotly_dark'
    )
    
    fig.update_layout(
        xaxis_title="Number of Searches",
        yaxis_title="Search Term",
        plot_bgcolor='rgba(17, 17, 17, 0.8)',
        paper_bgcolor='rgba(17, 17, 17, 0)',
        font=dict(color='white'),
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def render_search_box():
    """Render the search box component"""
    st.markdown("### Search Dark Web Content")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Enter search terms", placeholder="Enter keywords to search dark web content...")
    
    with col2:
        categories = ["All Categories", "Marketplace", "Forum", "Paste Site", "Data Breach", "Hacking", "Cryptocurrency"]
        selected_category = st.selectbox("Category", categories, index=0)
        
        if selected_category == "All Categories":
            selected_category = None
    
    advanced_options = st.expander("Advanced Search Options", expanded=False)
    with advanced_options:
        col1, col2 = st.columns(2)
        
        with col1:
            date_range = st.selectbox(
                "Date Range",
                ["All Time", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
            )
            
            include_images = st.checkbox("Include Images", value=False)
            include_code = st.checkbox("Include Code Snippets", value=True)
        
        with col2:
            sources = st.multiselect(
                "Sources",
                ["Dark Forums", "Marketplaces", "Paste Sites", "Leak Sites", "Chat Channels"],
                default=["Dark Forums", "Marketplaces", "Leak Sites"]
            )
            
            sort_by = st.selectbox(
                "Sort Results By",
                ["Relevance", "Date (Newest First)", "Date (Oldest First)"]
            )
    
    tags_input = st.text_input("Tags (comma-separated)", placeholder="Add tags to organize your search...")
    
    search_button = st.button("Search Dark Web")
    
    if search_button and search_query:
        # Save search to history
        user_id = getattr(st.session_state, "user_id", None)
        
        # Process tags
        tags = tags_input.strip() if tags_input else None
        
        # Run the search
        with st.spinner("Searching dark web..."):
            search = asyncio.run(save_search_query(
                query=search_query,
                user_id=user_id,
                category=selected_category,
                tags=tags
            ))
            
            if search:
                st.success(f"Search completed: Found {search.result_count} results for '{search_query}'")
                # In a real application, we would display results here
                
                # Offer to save as a monitored search
                save_col1, save_col2 = st.columns([3, 1])
                with save_col1:
                    search_name = st.text_input(
                        "Save this search for monitoring (enter a name)",
                        placeholder="My saved search"
                    )
                with save_col2:
                    frequency = st.selectbox(
                        "Check frequency",
                        ["Manual only", "Daily", "Every 12 hours", "Every 6 hours", "Hourly"],
                        index=1
                    )
                    
                    # Map to hours
                    freq_mapping = {
                        "Manual only": 0,
                        "Daily": 24,
                        "Every 12 hours": 12,
                        "Every 6 hours": 6,
                        "Hourly": 1
                    }
                    freq_hours = freq_mapping.get(frequency, 24)
                
                if st.button("Save for Monitoring"):
                    if search_name:
                        saved = asyncio.run(create_new_saved_search(
                            name=search_name,
                            query=search_query,
                            user_id=user_id,
                            frequency=freq_hours,
                            category=selected_category
                        ))
                        
                        if saved:
                            st.success(f"Saved search '{search_name}' created successfully!")
                    else:
                        st.error("Please enter a name for your saved search")
            else:
                st.error("Failed to perform search. Please try again.")

def render_search_history():
    """Render the search history component"""
    st.markdown("### Your Search History")
    
    user_id = getattr(st.session_state, "user_id", None)
    
    # Fetch search history
    searches = asyncio.run(get_user_searches(user_id))
    
    if not searches:
        st.info("No search history found. Try searching for dark web content.")
        return
    
    # Convert to DataFrame for display
    search_data = []
    for search in searches:
        search_data.append({
            "ID": search.id,
            "Query": search.query,
            "Date": search.timestamp.strftime("%Y-%m-%d %H:%M"),
            "Results": search.result_count,
            "Category": search.category or "All",
            "Saved": "✓" if search.is_saved else ""
        })
    
    df = pd.DataFrame(search_data)
    
    # Display as table
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "ID": st.column_config.NumberColumn(format="%d"),
            "Query": st.column_config.TextColumn(),
            "Date": st.column_config.DatetimeColumn(),
            "Results": st.column_config.NumberColumn(),
            "Category": st.column_config.TextColumn(),
            "Saved": st.column_config.TextColumn()
        }
    )

def render_saved_searches():
    """Render the saved searches component"""
    st.markdown("### Saved Searches")
    
    user_id = getattr(st.session_state, "user_id", None)
    
    # Fetch saved searches
    saved_searches = asyncio.run(get_user_saved_searches(user_id))
    
    if not saved_searches:
        st.info("No saved searches found. Save a search to monitor for new results.")
        return
    
    # Convert to DataFrame for display
    search_data = []
    for search in saved_searches:
        # Calculate next run time
        if search.last_run_at and search.frequency > 0:
            next_run = search.last_run_at + timedelta(hours=search.frequency)
        else:
            next_run = "Manual only"
        
        search_data.append({
            "ID": search.id,
            "Name": search.name,
            "Query": search.query,
            "Category": search.category or "All",
            "Frequency": f"{search.frequency}h" if search.frequency > 0 else "Manual",
            "Last Run": search.last_run_at.strftime("%Y-%m-%d %H:%M") if search.last_run_at else "Never",
            "Next Run": next_run if isinstance(next_run, str) else next_run.strftime("%Y-%m-%d %H:%M"),
            "Status": "Active" if search.is_active else "Paused"
        })
    
    df = pd.DataFrame(search_data)
    
    # Display as table
    st.dataframe(
        df,
        use_container_width=True
    )
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Run Selected Searches Now"):
            st.info("This would trigger manual execution of selected searches")
    
    with col2:
        if st.button("Pause Selected"):
            st.info("This would pause the selected searches")
    
    with col3:
        if st.button("Delete Selected"):
            st.info("This would delete the selected searches")

def render_trend_dashboard():
    """Render the trend dashboard component"""
    st.markdown("## Search Trends Analysis")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    with col1:
        time_period = st.selectbox(
            "Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year"],
            index=1
        )
        
        # Map to days
        period_mapping = {
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90,
            "Last Year": 365
        }
        days = period_mapping.get(time_period, 30)
    
    with col2:
        st.markdown("")  # Spacing
    
    # Fetch trend data
    with st.spinner("Loading trend data..."):
        trend_data = asyncio.run(get_trend_data(days=days))
    
    # Create layout for visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        search_trend_fig = plot_search_trends(trend_data.get("frequency", []))
        if search_trend_fig:
            st.plotly_chart(search_trend_fig, use_container_width=True)
        else:
            st.error("Failed to load search trend data")
        
        popular_searches_fig = plot_popular_searches(trend_data.get("popular_searches", []))
        if popular_searches_fig:
            st.plotly_chart(popular_searches_fig, use_container_width=True)
        else:
            st.error("Failed to load popular searches data")
    
    with col2:
        trending_topics_fig = plot_trending_topics(trend_data.get("trending_topics", []))
        if trending_topics_fig:
            st.plotly_chart(trending_topics_fig, use_container_width=True)
        else:
            st.error("Failed to load trending topics data")
        
        category_fig = plot_category_distribution(trend_data.get("categories", []))
        if category_fig:
            st.plotly_chart(category_fig, use_container_width=True)
        else:
            st.error("Failed to load category distribution data")
    
    # Display trend insights
    st.markdown("### Trend Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        velocity = trend_data.get("velocity", 0)
        velocity_color = "green" if velocity > 0 else "red"
        velocity_icon = "↗️" if velocity > 0 else "↘️"
        st.markdown(f"""
        ### Search Velocity
        <h2 style="color:{velocity_color}">{velocity_icon} {abs(velocity):.1f}%</h2>
        <p>Change in search volume compared to previous period</p>
        """, unsafe_allow_html=True)
    
    with col2:
        total_searches = trend_data.get("total_searches", {}).get("total", 0)
        st.markdown(f"""
        ### Total Searches
        <h2>{total_searches:,}</h2>
        <p>Total searches in the selected period</p>
        """, unsafe_allow_html=True)
    
    with col3:
        top_topic = "None"
        top_growth = 0
        if trend_data.get("trending_topics"):
            top_item = max(trend_data["trending_topics"], key=lambda x: x.get("growth_rate", 0))
            top_topic = top_item.get("topic", "None")
            top_growth = top_item.get("growth_rate", 0)
        
        st.markdown(f"""
        ### Fastest Growing Topic
        <h2>{top_topic}</h2>
        <p>Growth rate: {top_growth:.1f}%</p>
        """, unsafe_allow_html=True)
    
    # Display emerging themes (if available)
    if trend_data.get("trending_topics"):
        st.markdown("### Emerging Dark Web Themes")
        
        # Group topics by similar growth rates
        topics = trend_data["trending_topics"]
        
        # Display as topic clusters with common themes
        theme_groups = {
            "High Growth": [t for t in topics if t.get("growth_rate", 0) > 15],
            "Moderate Growth": [t for t in topics if 5 <= t.get("growth_rate", 0) <= 15],
            "Stable": [t for t in topics if t.get("growth_rate", 0) < 5]
        }
        
        for theme, items in theme_groups.items():
            if items:
                st.markdown(f"#### {theme}")
                themes_text = ", ".join([f"{t.get('topic')} ({t.get('growth_rate', 0):.1f}%)" for t in items])
                st.markdown(f"<p>{themes_text}</p>", unsafe_allow_html=True)

def render_search_trends():
    """Main function to render the search trends component"""
    st.title("Dark Web Search & Trends")
    
    tabs = st.tabs([
        "Search Dark Web", 
        "Search History", 
        "Saved Searches",
        "Trend Analysis"
    ])
    
    with tabs[0]:
        render_search_box()
    
    with tabs[1]:
        render_search_history()
    
    with tabs[2]:
        render_saved_searches()
    
    with tabs[3]:
        render_trend_dashboard()