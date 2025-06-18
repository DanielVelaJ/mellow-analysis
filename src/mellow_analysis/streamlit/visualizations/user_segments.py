"""
User performance segments visualization component.

Provides a scatter plot showing user performance vs engagement with clear boundary lines
to categorize users into High Performers, Quick Learners, Average Learners, and Struggling Users.
"""

import streamlit as st
import plotly.express as px
import pandas as pd


def render_user_segments(data_loader):
    """
    Render user segmentation based on performance patterns with scatter plot and boundary lines.
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
    
    # Define user segments with clear boundaries
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
    
    # Create scatter plot with boundary lines - THE VISUALIZATION YOU REMEMBER!
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
    
    # Add segment boundary lines - THE KEY FEATURE YOU REMEMBER!
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