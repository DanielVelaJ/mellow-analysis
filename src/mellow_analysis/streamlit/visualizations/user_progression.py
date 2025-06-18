"""
User progression analysis visualization component.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def render_user_progression_analysis(data_loader):
    """
    Render enhanced user learning progression analysis with dual-metric support.
    
    IMPORTANT: This analysis only works for users with multiple attempts.
    Features both cumulative accuracy and rolling window accuracy for comprehensive learning assessment.
    """
    
    st.header("📈 Enhanced Learning Progression Analysis")
    
    # How it's built explanation - enhanced for dual metrics
    with st.expander("🔧 How This Chart Is Built & The Mathematics of Dual-Metric Learning Progression"):
        st.markdown("""
        **Critical Data Processing Steps:**
        ```python
        # Step 1: Ensure chronological order (ESSENTIAL for progression)
        responses_df = responses_df.sort_values(['id_user_hash', 'exam_created_at'])
        
        # Step 2: Filter users with sufficient data for meaningful analysis
        user_attempt_counts = responses_df.groupby('id_user_hash').size()
        multi_attempt_users = user_attempt_counts[user_attempt_counts >= min_attempts]
        
        # Step 3: Calculate BOTH metrics
        # Cumulative accuracy (expanding mean)
        user_data['cumulative_accuracy'] = user_data['is_correct'].expanding().mean()
        
        # Rolling window accuracy (recent performance)
        user_data['rolling_accuracy'] = user_data['is_correct'].rolling(window_size, min_periods=1).mean()
        ```
        
        **Understanding Both Metrics - The Complete Learning Picture:**
        """)
        
        # Create dual metric comparison table
        comparison_data = {
            'Aspect': ['Purpose', 'Time Sensitivity', 'Volatility', 'Best For', 'Weakness'],
            'Cumulative Accuracy': [
                'Overall learning trajectory',
                'Early attempts heavily weighted',
                'Stable, dampened',
                'Long-term assessment',
                'Poor at recent changes'
            ],
            'Rolling Window Accuracy': [
                'Current performance level',
                'Recent attempts only',
                'More volatile',
                'Immediate coaching decisions',
                'Can miss overall progress'
            ],
            'When to Use': [
                'Progress reports, certification',
                'Intervention decisions, support',
                'Academic transcripts',
                'Real-time feedback',
                'Historical analysis'
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.table(comparison_df)
        
        st.markdown("""
        **Mathematical Example - Same User, Different Insights:**
        """)
        
        # Create detailed mathematical example
        example_data = {
            'Attempt': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Response': ['✓', '✗', '✗', '✓', '✓', '✓', '✓', '✗', '✓', '✓'],
            'Score': [1, 0, 0, 1, 1, 1, 1, 0, 1, 1],
            'Cumulative Accuracy': ['100%', '50%', '33%', '50%', '60%', '67%', '71%', '63%', '67%', '70%'],
            'Rolling (3-attempt)': ['100%', '50%', '33%', '33%', '67%', '100%', '100%', '67%', '67%', '67%'],
            'Insight Difference': [
                'Same',
                'Same', 
                'Same',
                'Cumulative: steady growth',
                'Rolling: rapid improvement',
                'Rolling: mastery achieved',
                'Cumulative: gradual progress',
                'Rolling: immediate impact visible',
                'Different volatility levels',
                'Cumulative: stable, Rolling: current'
            ]
        }
        
        example_df = pd.DataFrame(example_data)
        st.table(example_df)
        
        st.markdown("""
        **Pattern Recognition - What Each Metric Reveals:**
        """)
        
        # Create pattern analysis table
        pattern_data = {
            'Learning Pattern': ['Early Struggle → Mastery', 'Quick Start → Plateau', 'Consistent Progress', 'Recent Decline'],
            'Cumulative Shows': [
                'Gradual overall improvement',
                'High early performance maintained',
                'Steady upward trend',
                'Slight recent dip in average'
            ],
            'Rolling Shows': [
                'Clear recent mastery',
                'Current performance plateau',
                'Consistent current performance',
                'Sharp recent performance drop'
            ],
            'Coaching Action': [
                'Celebrate breakthrough',
                'Introduce advanced content',
                'Continue current approach',
                'Immediate intervention needed'
            ]
        }
        
        pattern_df = pd.DataFrame(pattern_data)
        st.table(pattern_df)
        
        st.markdown("""
        **Advanced Analytics - Trend Detection:**
        - **Performance Surge:** Rolling > Cumulative by >10pp (recent improvement)
        - **Performance Decline:** Rolling < Cumulative by >10pp (recent problems)
        - **Consistency:** Rolling ≈ Cumulative (stable performance)
        - **Volatility Index:** Standard deviation of rolling accuracy
        """)
    
    # Load data
    responses_df = data_loader.load_responses()
    
    # Ensure data is sorted chronologically
    responses_df = responses_df.sort_values(['id_user_hash', 'exam_created_at'])
    
    # Enhanced filter settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_attempts = st.slider("Minimum attempts per user", 5, 50, 15, 
                                help="Users need multiple attempts to show meaningful progression")
    
    with col2:
        rolling_window = st.slider("Rolling window size", 3, 15, 7,
                                 help="Number of recent attempts for rolling accuracy")
    
    with col3:
        analysis_mode = st.radio(
            "Analysis Mode",
            ["Cumulative Accuracy", "Rolling Accuracy", "Both (Comparison)"],
            help="Choose which metrics to display"
        )
    
    # Find users with sufficient attempts
    user_attempt_counts = responses_df.groupby('id_user_hash').size()
    multi_attempt_users = user_attempt_counts[user_attempt_counts >= min_attempts].index
    
    if len(multi_attempt_users) == 0:
        st.warning(f"No users found with {min_attempts}+ attempts. Try lowering the minimum.")
        return
    
    # Filter to users with multiple attempts
    filtered_df = responses_df[responses_df['id_user_hash'].isin(multi_attempt_users)]
    
    st.info(f"Analyzing {len(multi_attempt_users)} users with {min_attempts}+ attempts each (Rolling window: {rolling_window} attempts)")
    
    # Calculate progression for each user with both metrics
    progression_data = []
    trend_analysis = []
    
    for user_id in multi_attempt_users[:20]:  # Limit to top 20 for visibility
        user_data = filtered_df[filtered_df['id_user_hash'] == user_id].copy()
        user_data = user_data.sort_values('exam_created_at')
        
        # Calculate both metrics
        user_data['cumulative_accuracy'] = user_data['is_correct'].expanding().mean()
        user_data['rolling_accuracy'] = user_data['is_correct'].rolling(rolling_window, min_periods=1).mean()
        user_data['attempt_number'] = range(1, len(user_data) + 1)
        
        # Trend analysis for this user
        final_cumulative = user_data['cumulative_accuracy'].iloc[-1]
        final_rolling = user_data['rolling_accuracy'].iloc[-1]
        performance_gap = final_rolling - final_cumulative
        
        # Volatility calculation
        rolling_volatility = user_data['rolling_accuracy'].std() if len(user_data) > rolling_window else 0
        
        trend_analysis.append({
            'user_id': user_id,
            'final_cumulative': final_cumulative,
            'final_rolling': final_rolling,
            'performance_gap': performance_gap,
            'rolling_volatility': rolling_volatility,
            'total_attempts': len(user_data),
            'trend_type': 'Recent Surge' if performance_gap > 0.1 else 
                         'Recent Decline' if performance_gap < -0.1 else 'Stable'
        })
        
        progression_data.append(user_data[['id_user_hash', 'attempt_number', 'cumulative_accuracy', 'rolling_accuracy']])
    
    # Combine all user data
    if progression_data:
        all_progression = pd.concat(progression_data, ignore_index=True)
        
        # Create visualization based on selected mode
        if analysis_mode == "Both (Comparison)":
            # Side-by-side comparison
            fig = go.Figure()
            
            # Add cumulative accuracy lines
            for user_id in multi_attempt_users[:20]:
                user_subset = all_progression[all_progression['id_user_hash'] == user_id]
                fig.add_trace(go.Scatter(
                    x=user_subset['attempt_number'],
                    y=user_subset['cumulative_accuracy'],
                    mode='lines',
                    name=f'User {user_id[:8]} (Cumulative)',
                    line=dict(dash='dot'),
                    legendgroup='cumulative',
                    legendgrouptitle_text="Cumulative Accuracy"
                ))
                
                fig.add_trace(go.Scatter(
                    x=user_subset['attempt_number'],
                    y=user_subset['rolling_accuracy'],
                    mode='lines',
                    name=f'User {user_id[:8]} (Rolling)',
                    line=dict(dash='solid'),
                    legendgroup='rolling',
                    legendgrouptitle_text="Rolling Accuracy"
                ))
            
            # Add trend lines
            overall_cumulative = all_progression.groupby('attempt_number')['cumulative_accuracy'].mean().reset_index()
            overall_rolling = all_progression.groupby('attempt_number')['rolling_accuracy'].mean().reset_index()
            
            fig.add_trace(go.Scatter(
                x=overall_cumulative['attempt_number'],
                y=overall_cumulative['cumulative_accuracy'],
                mode='lines',
                name='Average Cumulative Trend',
                line=dict(color='red', width=4, dash='dash'),
                legendgroup='trends'
            ))
            
            fig.add_trace(go.Scatter(
                x=overall_rolling['attempt_number'],
                y=overall_rolling['rolling_accuracy'],
                mode='lines',
                name='Average Rolling Trend',
                line=dict(color='blue', width=4, dash='solid'),
                legendgroup='trends'
            ))
            
            fig.update_layout(
                title=f'Learning Progression: Cumulative vs Rolling Accuracy Comparison (Window: {rolling_window})',
                xaxis_title='Attempt Number',
                yaxis_title='Accuracy Rate',
                height=600,
                showlegend=True
            )
            
        elif analysis_mode == "Cumulative Accuracy":
            # Cumulative only
            fig = px.line(
                all_progression,
                x='attempt_number',
                y='cumulative_accuracy',
                color='id_user_hash',
                title=f'Learning Progression: Cumulative Accuracy Over Time (Top 20 Users)',
                labels={
                    'attempt_number': 'Attempt Number',
                    'cumulative_accuracy': 'Cumulative Accuracy Rate',
                    'id_user_hash': 'User ID'
                }
            )
            
            # Add overall trend line
            overall_trend = all_progression.groupby('attempt_number')['cumulative_accuracy'].mean().reset_index()
            
            fig.add_scatter(
                x=overall_trend['attempt_number'],
                y=overall_trend['cumulative_accuracy'],
                mode='lines',
                name='Average Cumulative Trend',
                line=dict(color='red', width=4, dash='dash')
            )
            
        else:  # Rolling Accuracy
            fig = px.line(
                all_progression,
                x='attempt_number',
                y='rolling_accuracy',
                color='id_user_hash',
                title=f'Learning Progression: Rolling Accuracy Over Time (Window: {rolling_window} attempts)',
                labels={
                    'attempt_number': 'Attempt Number',
                    'rolling_accuracy': 'Rolling Accuracy Rate',
                    'id_user_hash': 'User ID'
                }
            )
            
            # Add overall trend line
            overall_trend = all_progression.groupby('attempt_number')['rolling_accuracy'].mean().reset_index()
            
            fig.add_scatter(
                x=overall_trend['attempt_number'],
                y=overall_trend['rolling_accuracy'],
                mode='lines',
                name='Average Rolling Trend',
                line=dict(color='blue', width=4, dash='dash')
            )
        
        fig.update_layout(height=600, showlegend=False if analysis_mode != "Both (Comparison)" else True)
        fig.update_yaxes(tickformat='.0%', range=[0, 1])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced visual interpretation guide
        st.markdown("""
        ### 👁️ **What You're Looking At in This Enhanced Chart:**
        """)
        
        if analysis_mode == "Both (Comparison)":
            st.markdown("""
            - **📊 Chart Type:** Dual-metric comparison (dotted = cumulative, solid = rolling)
            - **📈 X-Axis:** Attempt number (1st attempt, 2nd attempt, etc.)
            - **📊 Y-Axis:** Accuracy rate (0% to 100%)
            - **🎯 Dotted Lines:** Cumulative accuracy (lifetime performance)
            - **🎯 Solid Lines:** Rolling accuracy (recent performance window)
            - **📏 Line Separation:** When lines diverge, recent performance differs from overall
            - **🔴 Red Trend:** Average cumulative progression
            - **🔵 Blue Trend:** Average rolling progression
            
            **How to Read the Comparison:**
            - **Solid line ABOVE dotted** = Recent performance better than lifetime average
            - **Solid line BELOW dotted** = Recent performance worse than lifetime average
            - **Lines close together** = Consistent performance over time
            - **Lines far apart** = Recent change in performance pattern
            """)
        elif analysis_mode == "Cumulative Accuracy":
            st.markdown("""
            - **📊 Chart Type:** Multi-line chart (cumulative performance)
            - **📈 X-Axis:** Attempt number (chronological progression)
            - **📊 Y-Axis:** Cumulative accuracy rate (lifetime average)
            - **🎯 Each Line:** One user's overall learning trajectory
            - **📏 Line Direction:** Shows long-term learning effectiveness
            - **🔴 Red Trend:** Platform-wide average progression
            
            **How to Read Cumulative Accuracy:**
            - **Steady upward trend** = Consistent long-term learning
            - **Early plateau** = Quick mastery, then maintenance
            - **Late surge** = Breakthrough after initial struggle
            - **Declining trend** = Systematic performance deterioration
            """)
        else:  # Rolling Accuracy
            st.markdown("""
            - **📊 Chart Type:** Multi-line chart (recent performance)
            - **📈 X-Axis:** Attempt number (chronological progression)
            - **📊 Y-Axis:** Rolling accuracy rate (recent window average)
            - **🎯 Each Line:** One user's current performance level
            - **📏 Line Volatility:** Shows performance consistency
            - **🔵 Blue Trend:** Platform-wide recent performance
            
            **How to Read Rolling Accuracy:**
            - **High volatility** = Inconsistent recent performance
            - **Sudden jumps** = Recent breakthroughs or improvements
            - **Sudden drops** = Recent difficulties or fatigue
            - **Stable lines** = Consistent current performance level
            """)
        
        # Advanced trend analysis
        st.subheader("🎯 Advanced Trend Analysis")
        
        trend_df = pd.DataFrame(trend_analysis)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            surge_users = (trend_df['trend_type'] == 'Recent Surge').sum()
            st.metric(
                "Recent Surge Users",
                surge_users,
                f"{surge_users/len(trend_df):.1%}",
                help="Users performing >10pp better recently than overall"
            )
        
        with col2:
            decline_users = (trend_df['trend_type'] == 'Recent Decline').sum()
            st.metric(
                "Recent Decline Users", 
                decline_users,
                f"{decline_users/len(trend_df):.1%}",
                help="Users performing >10pp worse recently than overall"
            )
        
        with col3:
            avg_volatility = trend_df['rolling_volatility'].mean()
            st.metric(
                "Average Volatility",
                f"{avg_volatility:.3f}",
                help="Standard deviation of rolling accuracy (lower = more consistent)"
            )
        
        with col4:
            avg_performance_gap = trend_df['performance_gap'].mean()
            st.metric(
                "Avg Performance Gap",
                f"{avg_performance_gap:+.1%}",
                help="Average difference: rolling - cumulative accuracy"
            )
        
        # Detailed trend breakdown
        if analysis_mode == "Both (Comparison)":
            st.subheader("📋 Detailed User Trend Analysis")
            
            # Create detailed analysis table
            display_df = trend_df.copy()
            display_df['user_id'] = display_df['user_id'].str[:12] + '...'
            display_df['final_cumulative'] = (display_df['final_cumulative'] * 100).round(1).astype(str) + '%'
            display_df['final_rolling'] = (display_df['final_rolling'] * 100).round(1).astype(str) + '%'
            display_df['performance_gap'] = (display_df['performance_gap'] * 100).round(1).astype(str) + 'pp'
            display_df['rolling_volatility'] = display_df['rolling_volatility'].round(3)
            
            st.dataframe(
                display_df[['user_id', 'final_cumulative', 'final_rolling', 'performance_gap', 'trend_type', 'rolling_volatility', 'total_attempts']],
                column_config={
                    'user_id': 'User ID',
                    'final_cumulative': 'Cumulative Accuracy',
                    'final_rolling': 'Rolling Accuracy', 
                    'performance_gap': 'Performance Gap',
                    'trend_type': 'Trend Classification',
                    'rolling_volatility': 'Volatility Index',
                    'total_attempts': 'Total Attempts'
                },
                use_container_width=True
            )
        
        # Business insights and recommendations
        st.subheader("💼 Business Insights & Recommendations")
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown("""
            **📈 Trend-Based Actions:**
            """)
            
            if surge_users > 0:
                st.success(f"""
                **{surge_users} users showing recent breakthroughs!**
                - Celebrate their progress with recognition
                - Offer advanced content or challenges
                - Use as success stories for other users
                """)
            
            if decline_users > 0:
                st.warning(f"""
                **{decline_users} users showing recent decline**
                - Immediate check-in recommended
                - Review recent content difficulty
                - Consider tutoring or additional support
                """)
        
        with insight_col2:
            st.markdown("""
            **🎯 Methodology Recommendations:**
            """)
            
            if analysis_mode == "Both (Comparison)":
                st.info("""
                **Optimal dual-metric approach:**
                - Use cumulative for progress reports
                - Use rolling for coaching decisions
                - Monitor gaps for intervention timing
                - Track volatility for consistency
                """)
            elif analysis_mode == "Cumulative Accuracy":
                st.info("""
                **Cumulative accuracy insights:**
                - Best for long-term assessment
                - Shows overall learning effectiveness
                - Consider adding rolling window for complete picture
                """)
            else:
                st.info("""
                **Rolling accuracy insights:**
                - Best for immediate interventions
                - Shows current performance state
                - Consider adding cumulative for context
                """)


def render_user_segments(data_loader):
    """
    Render user segmentation based on performance patterns.
    """
    
    st.header("👥 User Performance Segments")
    
    # How it's built explanation
    with st.expander("🔧 User Segmentation Logic & Business Strategy"):
        st.markdown("""
        **Two-Dimensional Segmentation Approach:**
        ```python
        # Step 1: Calculate performance and engagement metrics per user
        user_stats = responses_df.groupby('id_user_hash').agg({
            'is_correct': ['mean', 'count'],      # Performance & Engagement
            'exam_created_at': ['min', 'max']     # Activity timespan
        })
        
        # Step 2: Apply segmentation logic
        def segment_user(accuracy, attempts):
            if accuracy >= 0.8 and attempts >= 20:
                return 'High Performers'
            elif accuracy >= 0.8 and attempts < 20:
                return 'Quick Learners' 
            elif accuracy < 0.5:
                return 'Struggling Users'
            else:
                return 'Average Learners'
        ```
        
        **Segmentation Matrix Explanation:**
        """)
        
        # Create segmentation matrix table
        segment_data = {
            'Segment': ['High Performers', 'Quick Learners', 'Average Learners', 'Struggling Users'],
            'Accuracy Criteria': ['≥80%', '≥80%', '50-80%', '<50%'],
            'Engagement Criteria': ['≥20 attempts', '<20 attempts', 'Any attempts', 'Any attempts'],
            'User Characteristics': [
                'Skilled AND highly engaged',
                'Skilled BUT limited engagement',
                'Moderate skill, normal engagement',
                'Low skill, needs immediate help'
            ],
            'Business Interpretation': [
                'Platform advocates and success stories',
                'Efficient learners who master quickly',
                'Typical user base with room to grow',
                'At-risk users requiring intervention'
            ]
        }
        
        segment_df = pd.DataFrame(segment_data)
        st.table(segment_df)
        
        st.markdown("""
        **Strategic Actions by Segment:**
        """)
        
        # Create action strategy table
        strategy_data = {
            'Segment': ['High Performers', 'Quick Learners', 'Average Learners', 'Struggling Users'],
            'Immediate Action': [
                'Advanced content & leadership roles',
                'Efficiency optimization & shortcuts',
                'Standard progression path',
                'Urgent intervention & support'
            ],
            'Content Strategy': [
                'Complex cases, peer teaching',
                'Condensed high-value content',
                'Balanced difficulty progression',
                'Fundamentals review, easier questions'
            ],
            'Support Level': [
                'Minimal - self-directed',
                'Low - occasional check-ins',
                'Standard - regular guidance',
                'High - intensive tutoring'
            ],
            'Business Priority': [
                'Retention & advocacy',
                'Engagement increase',
                'Skill development',
                'Prevent churn'
            ]
        }
        
        strategy_df = pd.DataFrame(strategy_data)
        st.table(strategy_df)
        
        st.markdown("""
        **Why Two Dimensions Matter:**
        """)
        
        # Create dimension explanation table
        dimension_data = {
            'Dimension': ['Accuracy (Performance)', 'Attempts (Engagement)', 'Combined Analysis'],
            'What It Measures': [
                'Learning effectiveness and skill level',
                'Platform usage and commitment level',
                'Complete user behavior profile'
            ],
            'Business Insight': [
                'How well content is working',
                'How engaged users are',
                'Optimal intervention strategy'
            ],
            'Action Trigger': [
                'Content difficulty adjustment',
                'Engagement campaign targeting',
                'Personalized learning paths'
            ]
        }
        
        dimension_df = pd.DataFrame(dimension_data)
        st.table(dimension_df)
        
        st.markdown("""
        **Statistical Validation:**
        - All users are assigned to exactly one segment (100% coverage)
        - Thresholds based on educational research standards
        - Clear boundaries prevent misclassification
        - Actionable insights tied to each segment
        """)
        
    
    # Load data
    responses_df = data_loader.load_responses()
    
    # Calculate user statistics
    user_stats = responses_df.groupby('id_user_hash').agg({
        'is_correct': ['mean', 'count'],
        'exam_created_at': ['min', 'max']
    }).reset_index()
    
    # Flatten column names
    user_stats.columns = ['user_id', 'accuracy', 'total_attempts', 'first_attempt', 'last_attempt']
    
    # Calculate engagement days
    user_stats['engagement_days'] = (user_stats['last_attempt'] - user_stats['first_attempt']).dt.days + 1
    
    # Define user segments
    def segment_user(row):
        accuracy = row['accuracy']
        attempts = row['total_attempts']
        
        if accuracy >= 0.8 and attempts >= 20:
            return 'High Performers'
        elif accuracy >= 0.8 and attempts < 20:
            return 'Quick Learners'
        elif accuracy < 0.5:
            return 'Struggling Users'
        else:
            return 'Average Learners'
    
    user_stats['segment'] = user_stats.apply(segment_user, axis=1)
    
    # Create scatter plot
    fig = px.scatter(
        user_stats,
        x='total_attempts',
        y='accuracy',
        color='segment',
        title='User Segments: Performance vs. Engagement',
        labels={
            'total_attempts': 'Total Attempts',
            'accuracy': 'Overall Accuracy',
            'segment': 'User Segment'
        },
        hover_data=['engagement_days'],
        color_discrete_map={
            'High Performers': '#2E8B57',      # Sea Green
            'Quick Learners': '#4169E1',       # Royal Blue
            'Average Learners': '#FFA500',     # Orange
            'Struggling Users': '#DC143C'      # Crimson
        }
    )
    
    # Add segment boundary lines
    fig.add_hline(y=0.8, line_dash="dash", line_color="gray", annotation_text="80% accuracy threshold")
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="50% accuracy threshold")
    fig.add_vline(x=20, line_dash="dash", line_color="gray", annotation_text="20 attempts threshold")
    
    fig.update_layout(height=500)
    fig.update_yaxes(tickformat='.0%')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Scatter plot (dots representing individual users)
    - **📈 X-Axis:** Total attempts per user (engagement level)
    - **📊 Y-Axis:** Overall accuracy per user (performance level)
    - **🎯 Each Dot:** Represents one user positioned by their performance & engagement
    - **🌈 Dot Colors:** Green = High Performers, Blue = Quick Learners, Orange = Average, Red = Struggling
    - **📏 Gray Lines:** Show the boundaries that define each segment
    
    **How to Read It:**
    - **TOP RIGHT (Green dots)** = High performers: skilled AND highly engaged
    - **TOP LEFT (Blue dots)** = Quick learners: skilled BUT less engaged  
    - **MIDDLE (Orange dots)** = Average learners: moderate skill and engagement
    - **BOTTOM (Red dots)** = Struggling users: low accuracy regardless of engagement
    - **Dots higher up** = Better performance
    - **Dots further right** = More engaged users
    """)
    
    # Show segment statistics
    st.subheader("📊 Segment Breakdown")
    
    segment_summary = user_stats.groupby('segment').agg({
        'user_id': 'count',
        'accuracy': 'mean',
        'total_attempts': 'mean',
        'engagement_days': 'mean'
    }).round(2)
    
    segment_summary.columns = ['User Count', 'Avg Accuracy', 'Avg Attempts', 'Avg Engagement Days']
    segment_summary['Percentage'] = (segment_summary['User Count'] / len(user_stats) * 100).round(1)
    
    # Format the display
    segment_summary['Avg Accuracy'] = segment_summary['Avg Accuracy'].apply(lambda x: f"{x:.1%}")
    segment_summary['Percentage'] = segment_summary['Percentage'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(segment_summary, use_container_width=True)
    
    # Actionable insights
    struggling_count = user_stats[user_stats['segment'] == 'Struggling Users'].shape[0]
    high_performer_count = user_stats[user_stats['segment'] == 'High Performers'].shape[0]
    
    if struggling_count > 0:
        st.warning(f"⚠️ **Action Needed:** {struggling_count} users are struggling (accuracy < 50%). Consider targeted interventions.")
    
    if high_performer_count > 0:
        st.success(f"🌟 **Success:** {high_performer_count} users are high performers. Consider advanced content for them.")


def render_retention_analysis(data_loader):
    """
    Render user survival/retention analysis showing percentage of users still active after N days.
    """
    
    st.header("🔄 User Survival Analysis")
    
    # How it's built explanation
    with st.expander("🔧 How Survival Analysis Works"):
        st.markdown("""
        **Data Processing:**
        ```python
        # Step 1: Find each user's last activity day
        user_last_activity = responses_df.groupby('id_user_hash')['exam_created_at'].apply(
            lambda x: (x.max() - x.min()).days
        )
        
        # Step 2: Create survival curve - % still active after each day
        for day in range(max_days):
            users_still_active = (user_last_activity >= day).sum()
            survival_rate = users_still_active / total_users
        ```
        
        **Methodology:**
        - **Survival Analysis:** Classic method from statistics/medicine
        - **Day 0:** 100% of users (everyone starts here)
        - **Day N:** % of users who had activity AFTER day N (still "alive" on platform)
        - **No Double Counting:** Each user appears exactly once at their exit point
        
        **Why This Matters:**
        - Shows true user lifecycle and platform "stickiness"
        - Identifies critical drop-off points for intervention
        - Comparable across cohorts and industry benchmarks
        - Directly answers "How long do users stick around?"
        
        **Key Patterns to Look For:**
        - **Steep initial drop:** Onboarding or first-experience issues
        - **Gradual decline:** Natural, healthy user lifecycle
        - **Plateaus:** Core engaged user base that stays long-term
        - **Industry benchmarks:** D1 (day-1), D7, D30 retention rates
        """)
    
    # Load data
    responses_df = data_loader.load_responses()
    
    # Calculate each user's first and last activity
    user_activity = responses_df.groupby('id_user_hash')['exam_created_at'].agg(['min', 'max']).reset_index()
    user_activity.columns = ['user_id', 'first_activity', 'last_activity']
    
    # Calculate days since first attempt for last activity (user's "lifespan")
    user_activity['lifespan_days'] = (user_activity['last_activity'] - user_activity['first_activity']).dt.days
    
    # Calculate survival curve
    max_days = min(90, user_activity['lifespan_days'].max())  # Limit to 90 days
    total_users = len(user_activity)
    
    survival_data = []
    
    for day in range(0, max_days + 1):
        # Count users who were still active AFTER this day (lifespan > day)
        users_still_active = (user_activity['lifespan_days'] > day).sum()
        survival_rate = users_still_active / total_users
        
        survival_data.append({
            'day': day,
            'users_still_active': users_still_active,
            'survival_rate': survival_rate
        })
    
    survival_df = pd.DataFrame(survival_data)
    
    # Create survival curve
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=survival_df['day'],
        y=survival_df['survival_rate'],
        mode='lines',
        name='Survival Rate',
        line=dict(color='#2E8B57', width=3, shape='hv'),  # Step plot
        fill='tonexty',
        fillcolor='rgba(46, 139, 87, 0.1)',
        hovertemplate='<b>After Day %{x}</b><br>Still Active: %{y:.1%}<br>Users: %{customdata}<extra></extra>',
        customdata=survival_df['users_still_active']
    ))
    
    # Add milestone lines
    milestones = [1, 7, 30]
    for milestone in milestones:
        if milestone <= max_days:
            milestone_rate = survival_df[survival_df['day'] == milestone]['survival_rate'].iloc[0]
            fig.add_vline(
                x=milestone, 
                line_dash="dash", 
                line_color="gray", 
                annotation_text=f"D{milestone}: {milestone_rate:.1%}",
                annotation_position="top"
            )
    
    fig.update_layout(
        title='User Survival Curve - Percentage Still Active After N Days',
        xaxis_title='Days Since First Attempt',
        yaxis_title='Percentage Still Active',
        height=400,
        showlegend=False
    )
    
    fig.update_yaxes(tickformat='.0%', range=[0, 1])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Survival curve (step plot with shaded area)
    - **📈 X-Axis:** Days since user's first attempt (0 = first day, 30 = after 30 days)
    - **📊 Y-Axis:** Percentage of users still active (had activity AFTER that day)
    - **🎯 Line:** Shows what % of users survived past each day
    - **📏 Line Direction:** Always decreases (users can only exit, never re-enter)
    - **📊 Shaded Area:** Visual emphasis of survival rate
    - **📏 Dashed Lines:** Key milestone markers (D1, D7, D30)
    
    **How to Read It:**
    - **Starts at 100%** = All users are "alive" on day 0
    - **Steep drops** = Many users leaving (potential problem areas)
    - **Gradual slopes** = Natural, healthy user lifecycle
    - **Flat sections** = Stable, engaged user base
    - **Never goes up** = Once a user exits, they stay exited in this analysis
    - **Higher line = better retention** = More users staying engaged longer
    """)
    
    # Show key retention metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        day1_retention = survival_df[survival_df['day'] == 1]['survival_rate'].iloc[0] if len(survival_df) > 1 else 0
        st.metric("Day 1 Retention", f"{day1_retention:.1%}")
    
    with col2:
        day7_retention = survival_df[survival_df['day'] == 7]['survival_rate'].iloc[0] if len(survival_df) > 7 else 0
        st.metric("Day 7 Retention", f"{day7_retention:.1%}")
    
    with col3:
        day30_retention = survival_df[survival_df['day'] == 30]['survival_rate'].iloc[0] if len(survival_df) > 30 else 0
        st.metric("Day 30 Retention", f"{day30_retention:.1%}")
    
    with col4:
        avg_lifespan = user_activity['lifespan_days'].mean()
        st.metric("Avg User Lifespan", f"{avg_lifespan:.1f} days")
    
    # Show detailed survival stats
    st.subheader("📊 Survival Statistics")
    
    # Create summary table
    summary_stats = {
        'Metric': [
            'Total Users',
            'Single-Session Users',
            'Multi-Session Users', 
            'Median Lifespan',
            '75th Percentile Lifespan',
            'Longest User Lifespan'
        ],
        'Value': [
            f"{total_users:,}",
            f"{(user_activity['lifespan_days'] == 0).sum():,} ({(user_activity['lifespan_days'] == 0).mean():.1%})",
            f"{(user_activity['lifespan_days'] > 0).sum():,} ({(user_activity['lifespan_days'] > 0).mean():.1%})",
            f"{user_activity['lifespan_days'].median():.1f} days",
            f"{user_activity['lifespan_days'].quantile(0.75):.1f} days",
            f"{user_activity['lifespan_days'].max():.0f} days"
        ]
    }
    
    summary_df = pd.DataFrame(summary_stats)
    st.table(summary_df)
    
    # Show insights
    single_session_rate = (user_activity['lifespan_days'] == 0).mean()
    
    if day1_retention < 0.3:
        st.warning("⚠️ Low day-1 retention suggests onboarding issues")
    elif day1_retention > 0.6:
        st.success("✅ Strong day-1 retention indicates good first experience")
    
    if single_session_rate > 0.5:
        st.warning(f"⚠️ High single-session rate ({single_session_rate:.1%}) - many users never return")
    
    if len(survival_df) > 30 and day30_retention > 0.1:
        st.success("✅ Good long-term retention - users find ongoing value") 