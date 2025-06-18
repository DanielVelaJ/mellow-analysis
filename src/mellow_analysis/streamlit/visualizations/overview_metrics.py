"""
Overview metrics visualization component.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime


def render_overview_metrics(data_loader):
    """
    Render the overview metrics section.
    
    This component provides high-level KPIs and summary statistics.
    """
    
    st.header("📊 Overview Metrics")
    
    # Important data structure note
    st.warning("""
    🔍 **Important Data Structure Note:**
    This dataset contains **systematic question duplication** - each question appears with 2 different IDs but identical content. 
    This is intentional (for exam structure) and has been accounted for in our analysis. Question difficulty analysis now groups by content, not ID.
    """)
    
    # How it's built explanation
    with st.expander("🔧 How These KPIs Are Calculated & What They Mean"):
        st.markdown("""
        **Executive Summary Metrics - Step by Step:**
        
        Each metric is calculated directly from the raw data to ensure accuracy:
        """)
        
        # Create KPI explanation table
        kpi_data = {
            'Metric': ['Total Responses', 'Unique Users', 'Overall Accuracy', 'Avg Responses/User'],
            'Calculation': [
                'len(responses_df)',
                'responses_df["id_user_hash"].nunique()',
                'responses_df["is_correct"].mean()',
                'total_responses / unique_users'
            ],
            'What It Measures': [
                'Total platform activity volume',
                'Size of active user base',
                'Learning effectiveness rate (unaffected by duplication)',
                'User engagement intensity'
            ],
            'Business Significance': [
                'Scale of platform usage',
                'Market penetration success',
                'Educational effectiveness',
                'User commitment level'
            ],
            'Good vs Bad Values': [
                'Higher = More engagement',
                'Higher = Broader reach',
                '70-85% = Optimal learning',
                '10-30 = Good engagement'
            ]
        }
        
        kpi_df = pd.DataFrame(kpi_data)
        st.table(kpi_df)
        
        st.markdown("""
        **Detailed Statistics Breakdown:**
        """)
        
        # Create detailed stats explanation table
        stats_data = {
            'Category': ['Content Statistics', 'Platform Activity', 'Quality Metrics'],
            'Includes': [
                'Questions, Cases, Categories, Subcategories',
                'Countries, Date Range, Daily Activity',
                'Accuracy Rates, Response Reliability'
            ],
            'Business Use': [
                'Content inventory and coverage assessment',
                'Geographic reach and usage patterns',
                'Learning effectiveness validation'
            ],
            'Key Insights': [
                'Content variety and depth',
                'Platform adoption and consistency',
                'Educational quality and user success'
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.table(stats_df)
        
        st.markdown("""
        **Executive Decision Framework:**
        """)
        
        # Create decision framework table
        decision_data = {
            'If You See...': ['High responses, low users', 'Low accuracy (<60%)', 'High accuracy (>90%)', 'Declining daily activity'],
            'It Means...': [
                'Few power users, not broad adoption',
                'Content too difficult or unclear',
                'Content may be too easy',
                'User engagement dropping'
            ],
            'Action Required': [
                'User acquisition campaign needed',
                'Content review and improvement',
                'Add advanced/complex content',
                'Re-engagement strategy needed'
            ],
            'Success Metrics': [
                'Increase unique user count',
                'Target 70-85% accuracy range',
                'Maintain 75-85% sweet spot',
                'Reverse activity decline trend'
            ]
        }
        
        decision_df = pd.DataFrame(decision_data)
        st.table(decision_df)
        
    
    # Get summary statistics
    stats = data_loader.get_summary_stats()
    
    # Create metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Responses",
            value=f"{stats['total_responses']:,}",
            help="Total number of question responses across all users"
        )
    
    with col2:
        st.metric(
            label="Unique Users",
            value=f"{stats['unique_users']:,}",
            help="Number of distinct users who have taken exams"
        )
    
    with col3:
        st.metric(
            label="Overall Accuracy",
            value=f"{stats['overall_accuracy']:.1%}",
            help="Percentage of questions answered correctly across all responses"
        )
    
    with col4:
        avg_per_user = stats['total_responses'] / stats['unique_users']
        st.metric(
            label="Avg Responses/User",
            value=f"{avg_per_user:.1f}",
            help="Average number of questions answered per user"
        )
    
    # Additional detailed metrics
    st.subheader("📋 Detailed Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Content Statistics:**
        - Question IDs: {stats['unique_questions']:,}
        - Unique Question Texts: {stats['unique_question_texts']:,}
        - Question Duplication Rate: {stats['duplication_rate']:.1%}
        - Clinical Cases: {stats['unique_cases']:,}
        - Categories: {stats['categories']:,}
        - Subcategories: {stats['subcategories']:,}
        """)
    
    with col2:
        date_range = stats['date_range']
        duration = (date_range['end'] - date_range['start']).days
        st.info(f"""
        **Platform Activity:**
        - Countries: {stats['countries']:,}
        - Date Range: {date_range['start'].strftime('%Y-%m-%d')} to {date_range['end'].strftime('%Y-%m-%d')}
        - Duration: {duration} days
        - Avg Responses/Day: {stats['total_responses'] / max(duration, 1):.1f}
        """)

    # ------------------------------------------------------------------
    # Comprehensive Descriptive Statistics for Both Datasets
    # ------------------------------------------------------------------

    st.subheader("🗂️ Dataset Descriptive Statistics")

    # Load full datasets (cached inside the DataLoader)
    cases_df = data_loader.load_cases()
    responses_df = data_loader.load_responses()

    # --------------------------------------------------
    # 1️⃣  Cases / Questions Dataset
    # --------------------------------------------------
    with st.expander("📚 Cases & Questions Dataset Summary", expanded=False):
        cases_metrics = {
            "Total Rows": len(cases_df),
            "Unique Exams": cases_df["id_exam"].nunique(),
            "Unique Cases": cases_df["id_case"].nunique(),
            "Unique Questions": cases_df["id_question"].nunique(),
            "Categories": cases_df["category_name"].nunique(),
            "Sub-Categories": cases_df["subcategory_name"].nunique(),
        }

        cases_stats_df = (
            pd.DataFrame(cases_metrics.items(), columns=["Metric", "Value"])  # type: ignore[arg-type]
            .sort_values("Metric")
            .reset_index(drop=True)
        )

        st.table(cases_stats_df)

    # --------------------------------------------------
    # 2️⃣  User Responses Dataset
    # --------------------------------------------------
    with st.expander("🧑‍⚕️ User Responses Dataset Summary", expanded=False):
        responses_metrics = {
            "Total Responses": len(responses_df),
            "Unique Users": responses_df["id_user_hash"].nunique(),
            "Countries Represented": responses_df["country_user_made_the_exam"].nunique(),
            "Unique Questions Answered": responses_df["id_question"].nunique(),
            "Overall Accuracy": f"{responses_df['is_correct'].mean():.1%}",
            "Date Range": f"{responses_df['exam_created_at'].min().date()} to {responses_df['exam_created_at'].max().date()}",
        }

        responses_stats_df = (
            pd.DataFrame(responses_metrics.items(), columns=["Metric", "Value"])  # type: ignore[arg-type]
            .sort_values("Metric")
            .reset_index(drop=True)
        )

        st.table(responses_stats_df)


def render_performance_trends(data_loader):
    """
    Render performance trends over time.
    """
    
    st.header("📈 Performance Trends")
    
    # How it's built explanation
    with st.expander("🔧 How This Chart Is Built & Data Processing Details"):
        st.markdown("""
        **Step-by-Step Data Processing:**
        ```python
        # Step 1: Extract date from timestamp and group by date
        responses_df['date'] = responses_df['exam_created_at'].dt.date
        
        # Step 2: Calculate daily statistics
        daily_stats = responses_df.groupby('date').agg({
            'is_correct': ['mean', 'count', 'sum'],  # Accuracy, volume, correct count
            'id_user_hash': 'nunique'                # Unique users per day
        })
        ```
        
        **What Each Aggregation Calculates:**
        """)
        
        # Create aggregation explanation table
        agg_data = {
            'Column': ['is_correct', 'is_correct', 'is_correct', 'id_user_hash'],
            'Function': ['mean', 'count', 'sum', 'nunique'],
            'Result': ['Daily Accuracy %', 'Total Responses', 'Correct Responses', 'Unique Users'],
            'Formula': [
                'Sum of correct / Total responses per day',
                'Number of responses submitted per day',
                'Count of responses where is_correct = 1',
                'Count of distinct users active per day'
            ],
            'Business Use': [
                'Track learning effectiveness over time',
                'Monitor platform usage and engagement',
                'Calculate absolute success metrics',
                'Measure user base activity'
            ]
        }
        
        agg_df = pd.DataFrame(agg_data)
        st.table(agg_df)
        
        st.markdown("""
        **Chart Construction & Interpretation:**
        """)
        
        # Create chart explanation table
        chart_data = {
            'Element': ['Line Graph', 'Dual Y-Axis', 'Time Series', 'Trend Line', 'Volume Bars'],
            'What It Shows': [
                'Daily accuracy rate progression',
                'Accuracy % (left) + Response count (right)',
                'Chronological progression over time',
                'Overall direction of improvement',
                'Daily platform usage volume'
            ],
            'Why Important': [
                'Shows if users are learning over time',
                'Reveals relationship between usage and performance',
                'Identifies patterns and seasonality',
                'Validates platform effectiveness',
                'Indicates user engagement levels'
            ],
            'Interpretation': [
                'Upward = Users improving, Flat = No progress',
                'High volume + high accuracy = Optimal',
                'Consistent patterns = Predictable behavior',
                'Positive slope = Effective learning',
                'Spikes = Marketing campaigns or events'
            ]
        }
        
        chart_df = pd.DataFrame(chart_data)
        st.table(chart_df)
        
        st.markdown("""
        **Key Patterns to Look For:**
        - 📈 **Learning Curve:** Gradually increasing accuracy suggests effective teaching
        - 📊 **Volume Correlation:** High usage days with maintained accuracy = good user experience
        - 🔄 **Seasonality:** Regular patterns help predict resource needs
        - ⚠️ **Warning Signs:** Declining accuracy or sudden drops in usage
        """)
        
    
    # Load and process data
    responses_df = data_loader.load_responses()
    
    # Calculate daily statistics
    daily_stats = responses_df.groupby('date').agg({
        'is_correct': ['mean', 'count', 'sum'],
        'id_user_hash': 'nunique'
    }).reset_index()
    
    # Flatten column names
    daily_stats.columns = ['date', 'accuracy', 'total_responses', 'correct_responses', 'unique_users']
    
    # Sort by date
    daily_stats = daily_stats.sort_values('date')
    
    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add accuracy trend
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['accuracy'],
            mode='lines+markers',
            name='Daily Accuracy',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='<b>Date:</b> %{x}<br><b>Accuracy:</b> %{y:.1%}<extra></extra>'
        ),
        secondary_y=False,
    )
    
    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=daily_stats['date'],
            y=daily_stats['total_responses'],
            name='Daily Responses',
            opacity=0.7,
            marker_color='#ff7f0e',
            hovertemplate='<b>Date:</b> %{x}<br><b>Responses:</b> %{y}<extra></extra>'
        ),
        secondary_y=True,
    )
    
    # Update layout
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Accuracy Rate", secondary_y=False, tickformat='.0%')
    fig.update_yaxes(title_text="Number of Responses", secondary_y=True)
    
    fig.update_layout(
        title="Performance and Volume Trends Over Time",
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Line chart with bars (dual-axis visualization)
    - **📈 X-Axis:** Date (chronological time progression)
    - **📊 Left Y-Axis (Blue Line):** Daily accuracy rate (0% to 100%)
    - **📊 Right Y-Axis (Orange Bars):** Number of responses per day
    - **🎯 Blue Line with Dots:** Shows accuracy trend over time
    - **🟧 Orange Bars:** Shows daily platform usage volume
    
    **How to Read It:**
    - **Line going UP** = Users improving over time (learning happening!)
    - **Line going DOWN** = Performance declining (needs attention)
    - **TALL orange bars** = High usage days (busy periods)
    - **Short orange bars** = Low usage days (quiet periods)
    - **Line + bars moving together** = More practice leads to better performance
    - **Flat line** = Stable performance (no improvement or decline)
    """)
    
    # Show summary insights
    latest_accuracy = daily_stats['accuracy'].iloc[-7:].mean()  # Last week average
    overall_accuracy = daily_stats['accuracy'].mean()
    
    if latest_accuracy > overall_accuracy:
        st.success(f"📈 Recent performance is above average! Last week: {latest_accuracy:.1%} vs Overall: {overall_accuracy:.1%}")
    else:
        st.warning(f"📉 Recent performance is below average. Last week: {latest_accuracy:.1%} vs Overall: {overall_accuracy:.1%}")


def render_user_engagement(data_loader):
    """
    Render user engagement patterns.
    """
    
    st.header("👥 User Engagement Patterns")
    
    # How it's built explanation
    with st.expander("🔧 How This Chart Is Built"):
        st.markdown("""
        **Data Processing:**
        ```python
        # Extract hour from timestamp and count responses
        hourly_activity = responses_df.groupby('hour').size()
        ```
        
        **Visualization Method:**
        - **Bar Chart:** Shows distribution of responses across 24 hours
        - **Color Coding:** Different colors for different time periods (morning, afternoon, evening)
        
        **Business Intuition:**
        Understanding when users are most active helps:
        - Optimize server resources and maintenance windows
        - Schedule content releases and notifications
        - Identify user behavior patterns (e.g., studying after work)
        
        **Key Insights:**
        - Peak hours reveal when medical professionals prefer to study
        - Low activity periods are good for system maintenance
        - Patterns might differ by geography or user type
        """)
    
    responses_df = data_loader.load_responses()
    
    # Calculate hourly activity
    hourly_activity = responses_df.groupby('hour').size().reset_index()
    hourly_activity.columns = ['hour', 'responses']
    
    # Add time period labels
    def get_period(hour):
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'
    
    hourly_activity['period'] = hourly_activity['hour'].apply(get_period)
    
    # Create bar chart
    fig = px.bar(
        hourly_activity, 
        x='hour', 
        y='responses',
        color='period',
        title='User Activity by Hour of Day',
        labels={'hour': 'Hour of Day', 'responses': 'Number of Responses'},
        color_discrete_map={
            'Morning': '#2E8B57',    # Sea Green
            'Afternoon': '#4682B4',   # Steel Blue  
            'Evening': '#8A2BE2',     # Blue Violet
            'Night': '#2F4F4F'        # Dark Slate Gray
        }
    )
    
    fig.update_layout(height=400)
    fig.update_xaxes(dtick=2)  # Show every 2 hours
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Bar chart (vertical bars)
    - **📈 X-Axis:** Hour of day (0 = midnight, 12 = noon, 23 = 11 PM)
    - **📊 Y-Axis:** Number of responses during that hour
    - **🎯 Each Bar:** Represents total activity for one hour across all days
    - **🌈 Bar Colors:** Green = Morning, Blue = Afternoon, Purple = Evening, Gray = Night
    - **📏 Bar Height:** Taller bars = More active hours
    
    **How to Read It:**
    - **TALL bars** = Peak usage times (users prefer studying then)
    - **Short bars** = Low activity periods (good for maintenance)
    - **Color patterns** = Shows which time periods are most popular
    - **Multiple peaks** = Different user groups with different schedules
    """)
    
    # Show peak hours
    peak_hour = hourly_activity.loc[hourly_activity['responses'].idxmax(), 'hour']
    peak_responses = hourly_activity['responses'].max()
    
    st.info(f"🕐 **Peak Activity:** {peak_hour}:00 with {peak_responses} responses") 