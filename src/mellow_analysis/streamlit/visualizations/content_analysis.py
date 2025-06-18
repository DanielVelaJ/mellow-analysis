"""
Content analysis visualization component.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from collections import Counter


def render_question_difficulty(data_loader):
    """
    Render question difficulty analysis.
    """
    
    st.header("🎯 Question Difficulty Analysis")
    
    # How it's built explanation
    with st.expander("🔧 How This Chart Is Built & What Each Component Means"):
        st.markdown("""
        **Data Processing Step-by-Step:**
        ```python
        # Step 1: Group all responses by question CONTENT (not ID)
        # NOTE: Questions are duplicated with different IDs, so we group by actual content
        question_stats = full_df.groupby('question').agg({
            'is_correct': ['mean', 'count'],    # Calculate accuracy & sample size
            'subcategory_name': 'first',       # Get category (same for all responses)  
            'id_question': 'nunique'           # Count how many IDs this question has
        })
        
        # Step 2: Filter questions with sufficient responses for reliability
        min_responses = st.slider("Minimum responses per question", 1, 100, 20)
        filtered_stats = question_stats[question_stats['response_count'] >= min_responses]
        ```
        
        **What Each Aggregation Function Does:**
        """)
        
        # Create explanation table
        explanation_data = {
            'Function': ['mean', 'count', 'first', 'nunique'],
            'Applied To': ['is_correct', 'is_correct', 'subcategory_name', 'id_question'],
            'What It Calculates': [
                'Average of 1s and 0s = Accuracy Rate',
                'Number of responses = Sample Size', 
                'Medical category (identical for all responses)',
                'Number of different question IDs with same content'
            ],
            'Example': [
                '[1,0,1,1,0] → 3/5 = 0.60 = 60% accuracy',
                '[1,0,1,1,0] → 5 responses total across all IDs',
                'Same category for all responses to this question',
                'Usually 2 IDs per question (systematic duplication)'
            ],
            'Business Value': [
                'Identifies question difficulty',
                'Measures statistical reliability (now more robust!)',
                'Enables topic-based analysis',
                'Tracks content duplication patterns'
            ]
        }
        
        explanation_df = pd.DataFrame(explanation_data)
        st.table(explanation_df)
        
        st.markdown("""
        **Difficulty Categories & Business Logic:**
        """)
        
        # Create difficulty categories table
        difficulty_data = {
            'Category': ['Very Easy', 'Easy', 'Moderate', 'Difficult', 'Very Difficult'],
            'Accuracy Range': ['>90%', '80-90%', '70-80%', '50-70%', '<50%'],
            'Interpretation': [
                'Might be too easy - consider advanced versions',
                'Good for confidence building',
                'Optimal learning difficulty',
                'Challenging but fair',
                'May need better explanations or prerequisites'
            ],
            'Action Required': [
                'Add complexity or advanced follow-ups',
                'Use for skill reinforcement',
                'Monitor for consistency',
                'Review explanations and examples',
                'Major content revision needed'
            ]
        }
        
        difficulty_df = pd.DataFrame(difficulty_data)
        st.table(difficulty_df)
        
        st.markdown("""
        **Why the Minimum Responses Slider Matters (Now Even More Important!):**
        - **Sample Size Problem:** A question answered by only 1-2 people can show 0% or 100% by pure chance
        - **Statistical Reliability:** More responses = more confident we can be in the accuracy estimate
        - **Duplication Advantage:** Since questions appear with 2 IDs, we get ~2x the sample size per question!
        - **Quality Control:** Filters out unreliable data that could mislead decision-making
        - **Balance:** Higher threshold = more reliable, but fewer questions included
        - **New Reality:** With duplication, minimum 20 responses = ~10 per question ID (better reliability)
        """)
    
    # Load data
    full_df = data_loader.load_full_dataset()
    
    # Calculate question difficulty by CONTENT (not ID) to handle duplication
    question_stats = full_df.groupby('question').agg({
        'is_correct': ['mean', 'count'],
        'subcategory_name': 'first',
        'id_question': 'nunique'  # Track how many IDs this question has
    }).reset_index()
    
    # Flatten column names
    question_stats.columns = ['question_text', 'accuracy', 'response_count', 'subcategory', 'num_question_ids']
    
    # Filter questions with sufficient responses
    min_responses = st.slider("Minimum responses per question", 1, 100, 20)
    filtered_stats = question_stats[question_stats['response_count'] >= min_responses]
    
    # Add duplication info
    st.info(f"""
    📊 **Duplication-Aware Analysis:**
    - Total unique question texts: {len(question_stats):,}
    - Questions with multiple IDs: {(question_stats['num_question_ids'] > 1).sum():,}
    - Average responses per question (after combining duplicates): {question_stats['response_count'].mean():.1f}
    """)
    
    # Create difficulty categories
    def categorize_difficulty(accuracy):
        if accuracy < 0.5:
            return 'Very Difficult (<50%)'
        elif accuracy < 0.7:
            return 'Difficult (50-70%)'
        elif accuracy < 0.8:
            return 'Moderate (70-80%)'
        elif accuracy < 0.9:
            return 'Easy (80-90%)'
        else:
            return 'Very Easy (>90%)'
    
    # Fix pandas warning by using .loc for assignment
    filtered_stats = filtered_stats.copy()
    filtered_stats.loc[:, 'difficulty_category'] = filtered_stats['accuracy'].apply(categorize_difficulty)
    
    # Create histogram
    fig = px.histogram(
        filtered_stats,
        x='accuracy',
        nbins=20,
        title=f'Distribution of Question Difficulty ({len(filtered_stats)} questions)',
        labels={'accuracy': 'Accuracy Rate', 'count': 'Number of Questions'},
        color_discrete_sequence=['#3498db']
    )
    
    # Add vertical lines for difficulty thresholds
    fig.add_vline(x=0.5, line_dash="dash", line_color="red", annotation_text="50% threshold")
    fig.add_vline(x=0.8, line_dash="dash", line_color="orange", annotation_text="80% threshold")
    
    fig.update_layout(height=400)
    fig.update_xaxes(tickformat='.0%')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Histogram (bar chart showing distribution)
    - **📈 X-Axis:** Question accuracy rate (0% to 100%)
    - **📊 Y-Axis:** Number of questions with that accuracy rate
    - **🎯 Each Bar:** Represents questions grouped by accuracy range
    - **📏 Red Line (50%):** Questions below this need major improvement
    - **📏 Orange Line (80%):** Questions above this are performing well
    
    **How to Read It:**
    - **Tall bars on the RIGHT (high accuracy)** = Many easy questions
    - **Tall bars on the LEFT (low accuracy)** = Many difficult questions  
    - **Balanced distribution** = Good mix of question difficulties
    """)
    
    # Show difficulty breakdown
    difficulty_counts = filtered_stats['difficulty_category'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Difficulty Breakdown")
        for category, count in difficulty_counts.items():
            percentage = count / len(filtered_stats) * 100
            st.write(f"**{category}:** {count} questions ({percentage:.1f}%)")
    
    with col2:
        # Show most difficult questions
        st.subheader("🔴 Most Difficult Questions")
        difficult_questions = filtered_stats.nsmallest(3, 'accuracy')
        
        for idx, row in difficult_questions.iterrows():
            st.write(f"**{row['accuracy']:.1%}** - {row['question_text'][:100]}...")
            st.caption(f"Category: {row['subcategory']} | Responses: {row['response_count']} | Question IDs: {row['num_question_ids']}")


def render_category_performance(data_loader):
    """
    Render performance by category and subcategory.
    """
    
    st.header("📚 Performance by Topic")
    
    # How it's built explanation
    with st.expander("🔧 How This Chart Is Built"):
        st.markdown("""
        **Data Processing:**
        ```python
        # Group by category and calculate performance metrics
        # NOTE: This analysis is NOT affected by question duplication since we group by category
        category_stats = full_df.groupby(['category_name', 'subcategory_name']).agg({
            'is_correct': ['mean', 'count', 'sum']
        })
        ```
        
        **Visualization Method:**
        - **Horizontal Bar Chart:** Easy to read category names
        - **Color Gradient:** Performance-based coloring (red = poor, green = good)
        - **Sorted by Performance:** Worst performing topics at top for immediate attention
        
        **Business Intuition:**
        This helps identify:
        - Which medical topics students struggle with most
        - Areas where curriculum needs strengthening
        - Topics that might need more practice questions
        
        **Actionable Insights:**
        - Low-performing categories need content review
        - High-performing topics might need advanced questions
        - Balanced performance indicates good curriculum design
        """)
    
    # Load data
    full_df = data_loader.load_full_dataset()
    
    # Calculate category performance
    category_stats = full_df.groupby(['category_name', 'subcategory_name']).agg({
        'is_correct': ['mean', 'count', 'sum']
    }).reset_index()
    
    # Flatten column names
    category_stats.columns = ['category', 'subcategory', 'accuracy', 'total_responses', 'correct_responses']
    
    # Create combined label
    category_stats['topic'] = category_stats['category'] + ' → ' + category_stats['subcategory']
    
    # Sort by accuracy (worst first)
    category_stats = category_stats.sort_values('accuracy')
    
    # Create horizontal bar chart
    fig = px.bar(
        category_stats,
        x='accuracy',
        y='topic',
        orientation='h',
        title='Performance by Topic Area',
        labels={'accuracy': 'Accuracy Rate', 'topic': 'Topic'},
        color='accuracy',
        color_continuous_scale='RdYlGn',
        text='accuracy'
    )
    
    # Update text format
    fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
    fig.update_layout(height=max(400, len(category_stats) * 40))
    fig.update_xaxes(tickformat='.0%')
    fig.update_coloraxes(colorbar_title="Accuracy Rate")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Horizontal bar chart (bars extend from left to right)
    - **📈 X-Axis:** Accuracy rate (0% to 100%)
    - **📊 Y-Axis:** Medical topics (Category → Subcategory)
    - **🎯 Each Bar:** Represents one topic's overall performance
    - **🌈 Bar Colors:** Red = Poor performance, Green = Excellent performance
    - **📏 Bar Length:** Longer bars = Higher accuracy rates
    - **📊 Sorting:** Worst performing topics at the TOP for immediate attention
    
    **How to Read It:**
    - **RED bars at TOP** = Topics needing urgent improvement
    - **GREEN bars at BOTTOM** = Topics performing excellently
    - **Short bars** = Low accuracy, needs content review
    - **Long bars** = High accuracy, consider advanced content
    """)
    
    # Show detailed statistics
    st.subheader("📋 Detailed Topic Statistics")
    
    # Add response volume information
    display_df = category_stats[['topic', 'accuracy', 'total_responses', 'correct_responses']].copy()
    display_df['accuracy'] = display_df['accuracy'].apply(lambda x: f"{x:.1%}")
    display_df.columns = ['Topic', 'Accuracy', 'Total Responses', 'Correct Responses']
    
    st.dataframe(display_df, use_container_width=True)


def render_wrong_answers_analysis(data_loader):
    """
    Render analysis of common wrong answers.
    """
    
    st.header("❌ Common Mistakes Analysis")
    
    # How it's built explanation
    with st.expander("🔧 How This Chart Is Built"):
        st.markdown("""
        **Data Processing:**
        ```python
        # Filter incorrect responses and count frequencies
        wrong_answers = responses_df[responses_df['is_user_answer_correct'] == 'INCORRECTA']
        wrong_counts = Counter(wrong_answers['user_answer'])
        ```
        
        **Visualization Method:**
        - **Horizontal Bar Chart:** Shows most frequent wrong answers
        - **Percentage Calculation:** Shows what % of all mistakes each answer represents
        - **Text Truncation:** Long medical terms are shortened for readability
        
        **Business Intuition:**
        Understanding common mistakes helps:
        - Identify misconceptions in medical knowledge
        - Improve question design and distractors
        - Create targeted educational content
        - Develop better feedback mechanisms
        
        **Educational Value:**
        - Most common wrong answers reveal systematic knowledge gaps
        - Patterns might indicate confusing medical terminology
        - Can guide development of additional learning materials
        """)
    
    # Load data
    responses_df = data_loader.load_responses()
    
    # Get wrong answers
    wrong_answers = responses_df[responses_df['is_user_answer_correct'] == 'INCORRECTA']
    
    if len(wrong_answers) == 0:
        st.info("No incorrect answers found in the dataset.")
        return
    
    # Count wrong answers
    wrong_counts = Counter(wrong_answers['user_answer'])
    
    # Convert to DataFrame
    wrong_df = pd.DataFrame(wrong_counts.most_common(15), columns=['answer', 'count'])
    wrong_df['percentage'] = wrong_df['count'] / len(wrong_answers) * 100
    
    # Truncate long answers for display
    wrong_df['display_answer'] = wrong_df['answer'].apply(
        lambda x: x[:50] + '...' if len(x) > 50 else x
    )
    
    # Create horizontal bar chart
    fig = px.bar(
        wrong_df,
        x='count',
        y='display_answer',
        orientation='h',
        title='Most Common Wrong Answers',
        labels={'count': 'Frequency', 'display_answer': 'Wrong Answer'},
        color='count',
        color_continuous_scale='Reds',
        text='percentage'
    )
    
    # Update text format
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=600)
    fig.update_yaxes(categoryorder='total ascending')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Visual interpretation guide
    st.markdown("""
    ### 👁️ **What You're Looking At in This Chart:**
    - **📊 Chart Type:** Horizontal bar chart (bars extend from left to right)
    - **📈 X-Axis:** Frequency (number of times this wrong answer was given)
    - **📊 Y-Axis:** Wrong answer text (truncated for readability)
    - **🎯 Each Bar:** Represents one specific incorrect answer
    - **🌈 Bar Colors:** Darker red = More frequent mistake
    - **📏 Bar Length:** Longer bars = More common mistakes
    - **📊 Sorting:** Most frequent mistakes at the TOP
    - **💯 Percentages:** Show what % of all mistakes each answer represents
    
    **How to Read It:**
    - **LONGEST bars at TOP** = Most common misconceptions
    - **Shorter bars** = Less frequent mistakes
    - **High percentages** = Systematic knowledge gaps affecting many users
    - **Clustered mistakes** = Specific topic areas needing attention
    """)
    
    # Show insights
    total_wrong = len(wrong_answers)
    most_common = wrong_df.iloc[0]
    
    st.info(f"""
    **Key Insights:**
    - Total incorrect responses: {total_wrong:,}
    - Most common mistake: "{most_common['answer']}" ({most_common['count']} times, {most_common['percentage']:.1f}% of all mistakes)
    - Top 5 mistakes account for {wrong_df.head()['percentage'].sum():.1f}% of all errors
    """)
    
    # Show detailed breakdown
    st.subheader("📊 Wrong Answer Details")
    
    display_df = wrong_df[['answer', 'count', 'percentage']].copy()
    display_df['percentage'] = display_df['percentage'].apply(lambda x: f"{x:.1f}%")
    display_df.columns = ['Wrong Answer', 'Frequency', '% of All Mistakes']
    
    st.dataframe(display_df, use_container_width=True) 