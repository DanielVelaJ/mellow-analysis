"""
User progression analysis visualization component.

Provides detailed learning progression analysis with distribution bands,
showing how users improve over time with configurable metrics and insights.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def render_user_progression_analysis(data_loader):
    """
    Render clean learning progression analysis with distribution bands.
    
    Shows the 25th-75th percentile range plus average trend, with optional individual user lines.
    """
    
    st.header("📈 Learning Progression Analysis")
    
    # How it's built explanation - simplified and clear
    with st.expander("🔧 How This Chart Works & What It Shows"):
        st.markdown("""
        **Simple Data Processing Steps:**
        ```python
        # Step 1: Sort by time to track progression
        responses_df = responses_df.sort_values(['id_user_hash', 'exam_created_at'])
        
        # Step 2: Filter users with enough attempts for meaningful analysis
        user_attempt_counts = responses_df.groupby('id_user_hash').size()
        qualified_users = user_attempt_counts[user_attempt_counts >= min_attempts]
        
        # Step 3: Calculate cumulative accuracy for each user
        user_data['cumulative_accuracy'] = user_data['is_correct'].expanding().mean()
        
        # Step 4: Aggregate across all users to show the distribution
        stats_by_attempt = data.groupby('attempt_number')['cumulative_accuracy'].agg([
            'mean',                    # Average performance
            lambda x: x.quantile(0.25), # 25th percentile (bottom quartile)
            lambda x: x.quantile(0.75)  # 75th percentile (top quartile)
        ])
        ```
        
        **What The Chart Shows:**
        """)
        
        # Clear explanation table
        chart_elements = {
            'Element': [
                'Blue Shaded Area',
                'Dark Blue Line', 
                'Individual Gray Lines',
                'X-Axis',
                'Y-Axis'
            ],
            'What It Represents': [
                '25th to 75th percentile range - where most users perform',
                'Average cumulative accuracy across all users',
                'Individual user learning curves (optional)',
                'Attempt number (1st question, 2nd question, etc.)',
                'Cumulative accuracy rate (lifetime average so far)'
            ],
            'How to Interpret': [
                'Wider band = more variation between users',
                'Upward trend = users are learning over time',
                'Each line shows one person\'s learning journey',
                'Shows progression from first attempt onwards',
                'Higher = better overall performance'
            ]
        }
        
        elements_df = pd.DataFrame(chart_elements)
        st.table(elements_df)
        
        st.markdown("""
        **Key Insights to Look For:**
        - **📈 Rising Average Line:** Users are learning and improving over time
        - **📊 Narrowing Blue Band:** Users becoming more consistent as they progress  
        - **📈 Widening Blue Band:** Increasing performance gaps between users
        - **📊 Flat Average Line:** No clear learning happening on average
        - **📉 Declining Trend:** Systematic performance issues (fatigue, content difficulty)
        
        **Business Applications:**
        - **Content Effectiveness:** Rising trends indicate good educational design
        - **User Segmentation:** Wide bands suggest need for personalized approaches
        - **Intervention Timing:** Identify when users typically struggle or succeed
        """)
    
    # Load and prepare data
    responses_df = data_loader.load_responses()
    responses_df = responses_df.sort_values(['id_user_hash', 'exam_created_at'])
    
    # Settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_attempts = st.slider("Minimum attempts per user", 5, 50, 15, 
                                help="Users need multiple attempts to show meaningful progression")
    
    with col2:
        max_users_to_analyze = st.slider("Maximum users to analyze", 20, 200, 100,
                                        help="More users = more reliable statistics but slower processing")
    
    with col3:
        show_individual_lines = st.checkbox("Show individual user lines", value=False,
                                          help="Toggle to see individual learning curves")
    
    # Find qualified users
    user_attempt_counts = responses_df.groupby('id_user_hash').size()
    qualified_users = user_attempt_counts[user_attempt_counts >= min_attempts].index
    
    if len(qualified_users) == 0:
        st.warning(f"No users found with {min_attempts}+ attempts. Try lowering the minimum.")
        return
    
    # Limit to top users for performance
    analyzed_users = qualified_users[:max_users_to_analyze]
    filtered_df = responses_df[responses_df['id_user_hash'].isin(analyzed_users)]
    
    st.info(f"Analyzing {len(analyzed_users)} users with {min_attempts}+ attempts each")
    
    # Calculate progression for each user
    progression_data = []
    
    for user_id in analyzed_users:
        user_data = filtered_df[filtered_df['id_user_hash'] == user_id].copy()
        user_data = user_data.sort_values('exam_created_at')
        
        # Calculate cumulative accuracy
        user_data['cumulative_accuracy'] = user_data['is_correct'].expanding().mean()
        user_data['attempt_number'] = range(1, len(user_data) + 1)
        
        progression_data.append(user_data[['id_user_hash', 'attempt_number', 'cumulative_accuracy']])
    
    if not progression_data:
        st.error("No valid progression data found.")
        return
    
    # Combine all user data
    all_progression = pd.concat(progression_data, ignore_index=True)
    
    # Calculate distribution statistics by attempt number
    distribution_stats = (
        all_progression
        .groupby('attempt_number')['cumulative_accuracy']
        .agg([
            'mean',
            lambda x: x.quantile(0.25),
            lambda x: x.quantile(0.75),
            'count'
        ])
        .rename(columns={
            'mean': 'average',
            '<lambda_0>': 'q25',
            '<lambda_1>': 'q75'
        })
        .reset_index()
    )
    
    # Create the clean visualization
    fig = go.Figure()
    
    # Add the distribution band (25th-75th percentile)
    fig.add_trace(go.Scatter(
        x=distribution_stats['attempt_number'],
        y=distribution_stats['q75'],
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip',
        name='75th percentile'
    ))
    
    fig.add_trace(go.Scatter(
        x=distribution_stats['attempt_number'],
        y=distribution_stats['q25'],
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0, 123, 255, 0.3)',
        showlegend=True,
        name='25th-75th Percentile Range',
        hovertemplate='<b>Attempt %{x}</b><br>' +
                     '25th-75th percentile range<br>' +
                     'Bottom: %{y:.1%}<extra></extra>'
    ))
    
    # Add the average trend line
    fig.add_trace(go.Scatter(
        x=distribution_stats['attempt_number'],
        y=distribution_stats['average'],
        mode='lines+markers',
        line=dict(color='#1f77b4', width=4),
        marker=dict(size=6, color='#1f77b4'),
        name='Average Cumulative Accuracy',
        hovertemplate='<b>Attempt %{x}</b><br>' +
                     'Average accuracy: %{y:.1%}<br>' +
                     '<extra></extra>'
    ))
    
    # Optionally add individual user lines
    if show_individual_lines:
        for user_id in analyzed_users[:min(20, len(analyzed_users))]:  # Limit to 20 for visibility
            user_subset = all_progression[all_progression['id_user_hash'] == user_id]
            if len(user_subset) > 0:
                fig.add_trace(go.Scatter(
                    x=user_subset['attempt_number'],
                    y=user_subset['cumulative_accuracy'],
                    mode='lines',
                    line=dict(color='gray', width=1, dash='dot'),
                    opacity=0.4,
                    showlegend=False,
                    hovertemplate='<b>User: %{text}</b><br>' +
                                 'Attempt %{x}<br>' +
                                 'Accuracy: %{y:.1%}<extra></extra>',
                    text=[user_id[:8] + '...' for _ in range(len(user_subset))]
                ))
    
    # Update layout
    fig.update_layout(
        title='Learning Progression: Cumulative Accuracy Distribution Over Time',
        xaxis_title='Attempt Number',
        yaxis_title='Cumulative Accuracy Rate',
        height=500,
        hovermode='x unified'
    )
    
    fig.update_yaxes(tickformat='.0%', range=[0, 1])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Multi-line progression chart with distribution bands
    - **📈 X-Axis:** Attempt number (1st question, 2nd question, etc.)
    - **📊 Y-Axis:** Cumulative accuracy rate (lifetime average to that point)
    - **🎯 Blue Shaded Area:** Range where 50% of users perform (25th-75th percentile)
    - **📏 Dark Blue Line:** Average performance across all users
    - **📍 Gray Dotted Lines:** Individual user learning curves (if enabled)
    
    **How to Read It:**
    - **Upward trending blue line** = Users are learning over time
    - **Wider blue band** = More variation between high/low performers
    - **Narrower blue band** = Users becoming more consistent
    - **Higher position** = Better overall performance
    - **Steeper slopes** = Faster learning rate
    """)
    
    # Show key progression metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        initial_accuracy = distribution_stats['average'].iloc[0] if len(distribution_stats) > 0 else 0
        st.metric("Initial Accuracy", f"{initial_accuracy:.1%}")
    
    with col2:
        final_accuracy = distribution_stats['average'].iloc[-1] if len(distribution_stats) > 0 else 0
        improvement = final_accuracy - initial_accuracy
        st.metric("Final Accuracy", f"{final_accuracy:.1%}", f"{improvement:+.1%}")
    
    with col3:
        max_attempts = distribution_stats['attempt_number'].max() if len(distribution_stats) > 0 else 0
        st.metric("Max Attempts Tracked", max_attempts)
    
    with col4:
        avg_users_per_attempt = distribution_stats['count'].mean() if len(distribution_stats) > 0 else 0
        st.metric("Avg Users per Attempt", f"{avg_users_per_attempt:.0f}")
    
    # Show detailed progression insights
    st.subheader("📊 Progression Insights")
    
    if len(distribution_stats) > 1:
        learning_trend = final_accuracy - initial_accuracy
        
        if learning_trend > 0.1:
            st.success(f"🚀 **Strong Learning Trend:** Users improve by {learning_trend:.1%} on average from first to last attempt")
        elif learning_trend > 0.05:
            st.info(f"📈 **Moderate Learning:** Users show {learning_trend:.1%} improvement over time")
        elif learning_trend > -0.05:
            st.warning(f"📊 **Stable Performance:** Minimal change ({learning_trend:+.1%}) - users neither improving nor declining")
        else:
            st.error(f"📉 **Concerning Trend:** Performance declining by {abs(learning_trend):.1%} - investigate content difficulty or fatigue")
        
        # Calculate consistency
        final_band_width = distribution_stats['q75'].iloc[-1] - distribution_stats['q25'].iloc[-1]
        initial_band_width = distribution_stats['q75'].iloc[0] - distribution_stats['q25'].iloc[0]
        consistency_change = final_band_width - initial_band_width
        
        if consistency_change < -0.05:
            st.success(f"🎯 **Increasing Consistency:** Performance gap narrowing by {abs(consistency_change):.1%}")
        elif consistency_change > 0.05:
            st.warning(f"📊 **Increasing Variation:** Performance gap widening by {consistency_change:.1%}")
        else:
            st.info("📊 **Stable Variation:** Consistent performance spread maintained")
