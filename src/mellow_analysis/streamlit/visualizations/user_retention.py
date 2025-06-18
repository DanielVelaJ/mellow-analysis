"""
User retention analysis visualization component.

Provides a survival curve showing the percentage of users who remain active
for N+ days after their first appearance on the platform.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd


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
        # Step 1: Find each user's first and last activity
        user_activity = responses_df.groupby('id_user_hash')['exam_created_at'].agg(['min', 'max'])
        
        # Step 2: Calculate each user's lifespan (days from first to last activity)
        user_activity['lifespan_days'] = (user_activity['last_activity'] - user_activity['first_activity']).dt.days
        
        # Step 3: Create survival curve - % who stayed active for N+ days
        for day in range(max_days):
            users_surviving = (user_activity['lifespan_days'] >= day).sum()
            survival_rate = users_surviving / total_users
        ```
        
        **Methodology:**
        - **User-Centric Survival:** Each user's journey starts from their personal Day 0
        - **Day 0:** 100% of users (everyone's first day)
        - **Day N:** % of users who were active for at least N days after their first appearance
        - **Reference Point:** Each user's individual first activity date
        - **"Surviving":** User remained active for at least N days from their start
        
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
    
    # Calculate survival curve - % of users who were active for N+ days after their first day
    max_days = min(90, user_activity['lifespan_days'].max())  # Limit to 90 days
    total_users = len(user_activity)
    
    survival_data = []
    
    for day in range(0, max_days + 1):
        # Count users who were active for at least this many days (lifespan >= day)
        users_still_active = (user_activity['lifespan_days'] >= day).sum()
        survival_rate = users_still_active / total_users
        
        survival_data.append({
            'day': day,
            'users_still_active': users_still_active,
            'survival_rate': survival_rate
        })
    
    survival_df = pd.DataFrame(survival_data)
    
    # Create survival curve - THE VISUALIZATION YOU REMEMBER!
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=survival_df['day'],
        y=survival_df['survival_rate'],
        mode='lines',
        name='Survival Rate',
        line=dict(color='#2E8B57', width=3, shape='hv'),  # Step plot
        fill='tonexty',
        fillcolor='rgba(46, 139, 87, 0.1)',
        hovertemplate='<b>Day %{x}</b><br>Still Active: %{y:.1%}<br>Users: %{customdata}<extra></extra>',
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
        title='User Survival Curve - Percentage Active for N+ Days After First Appearance',
        xaxis_title='Days Since User\'s First Activity',
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
    - **📈 X-Axis:** Days since each user's first activity (0 = user's first day, 30 = 30 days after user started)
    - **📊 Y-Axis:** Percentage of users who remained active for at least that many days
    - **🎯 Line:** Shows what % of users stayed engaged for N+ days from their start
    - **📏 Line Direction:** Always decreases (users can only have shorter lifespans, not longer)
    - **📊 Shaded Area:** Visual emphasis of survival rate
    - **📏 Dashed Lines:** Key milestone markers (D1, D7, D30)
    
    **How to Read It:**
    - **Starts at 100%** = All users were active on their personal Day 0 (first appearance)
    - **Steep drops** = Many users leaving early (onboarding issues)
    - **Gradual slopes** = Natural user lifecycle progression
    - **Flat sections** = Stable, long-term engaged user base
    - **Never goes up** = Once a user's lifespan is determined, it's fixed
    - **Higher line = better retention** = More users staying engaged for longer periods
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
            'Users Active 1+ Days',
            'Users Active 7+ Days', 
            'Users Active 30+ Days',
            'Median User Lifespan'
        ],
        'Value': [
            f"{total_users:,}",
            f"{(user_activity['lifespan_days'] == 0).sum():,} ({(user_activity['lifespan_days'] == 0).mean():.1%})",
            f"{(user_activity['lifespan_days'] > 0).sum():,} ({(user_activity['lifespan_days'] > 0).mean():.1%})",
            f"{(user_activity['lifespan_days'] >= 1).sum():,} ({(user_activity['lifespan_days'] >= 1).mean():.1%})",
            f"{(user_activity['lifespan_days'] >= 7).sum():,} ({(user_activity['lifespan_days'] >= 7).mean():.1%})" if max_days >= 7 else "N/A",
            f"{(user_activity['lifespan_days'] >= 30).sum():,} ({(user_activity['lifespan_days'] >= 30).mean():.1%})" if max_days >= 30 else "N/A",
            f"{user_activity['lifespan_days'].median():.1f} days"
        ]
    }
    
    summary_df = pd.DataFrame(summary_stats)
    st.table(summary_df)
    
    # Show insights
    single_session_rate = (user_activity['lifespan_days'] == 0).mean()
    
    if day1_retention < 0.7:
        st.warning("⚠️ Low day-1 retention suggests early user churn issues")
    elif day1_retention > 0.9:
        st.success("✅ Excellent day-1 retention indicates strong platform stickiness")
    
    if single_session_rate > 0.5:
        st.warning(f"⚠️ High single-session rate ({single_session_rate:.1%}) - many users never return")
    
    if max_days >= 30 and day30_retention > 0.3:
        st.success("✅ Strong long-term retention - users find ongoing value") 