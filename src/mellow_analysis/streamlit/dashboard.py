"""
Main Streamlit Dashboard for Mellow Analysis

This is the entry point for the interactive dashboard that provides
comprehensive insights into medical education data.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from mellow_analysis.data.loader import data_loader
from mellow_analysis.streamlit.visualizations.overview_metrics import (
    render_overview_metrics, 
    render_performance_trends, 
    render_user_engagement
)
from mellow_analysis.streamlit.visualizations.content_analysis import (
    render_question_difficulty,
    render_category_performance,
    render_wrong_answers_analysis
)
from mellow_analysis.streamlit.visualizations.user_progression import (
    render_user_progression_analysis,
    render_user_segments,
    render_retention_analysis
)
from mellow_analysis.streamlit.statistical_tests.two_sample_tests import (
    render_two_sample_tests
)


def main():
    """Main dashboard application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Mellow Analysis Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stAlert > div {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("📊 Mellow Medical Education Analytics Dashboard")
    st.markdown("**Comprehensive insights into medical learning platform performance**")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("Select analysis sections to explore:")
    
    # Analysis sections
    sections = {
        "📊 Overview & Metrics": "overview",
        "📈 Performance Trends": "trends", 
        "👥 User Engagement": "engagement",
        "🎯 Content Analysis": "content",
        "📚 Topic Performance": "topics",
        "❌ Common Mistakes": "mistakes",
        "📈 User Progression": "progression",
        "👥 User Segments": "segments",
        "🔄 Retention Analysis": "retention",
        "🧪 Statistical Tests": "statistics"
    }
    
    selected_sections = []
    for section_name, section_key in sections.items():
        if st.sidebar.checkbox(section_name, value=True, key=section_key):
            selected_sections.append(section_key)
    
    # Data loading status
    with st.spinner("Loading data..."):
        try:
            stats = data_loader.get_summary_stats()
            st.sidebar.success(f"✅ Data loaded successfully!")
            st.sidebar.info(f"📅 Data range: {stats['date_range']['start'].strftime('%Y-%m-%d')} to {stats['date_range']['end'].strftime('%Y-%m-%d')}")
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.stop()
    
    # Render selected sections
    if "overview" in selected_sections:
        render_overview_metrics(data_loader)
        st.divider()
    
    if "trends" in selected_sections:
        render_performance_trends(data_loader)
        st.divider()
    
    if "engagement" in selected_sections:
        render_user_engagement(data_loader)
        st.divider()
    
    if "content" in selected_sections:
        render_question_difficulty(data_loader)
        st.divider()
    
    if "topics" in selected_sections:
        render_category_performance(data_loader)
        st.divider()
    
    if "mistakes" in selected_sections:
        render_wrong_answers_analysis(data_loader)
        st.divider()
    
    if "progression" in selected_sections:
        render_user_progression_analysis(data_loader)
        st.divider()
    
    if "segments" in selected_sections:
        render_user_segments(data_loader)
        st.divider()
    
    if "retention" in selected_sections:
        render_retention_analysis(data_loader)
        st.divider()
    
    if "statistics" in selected_sections:
        render_two_sample_tests(data_loader)
    
    # Footer
    st.markdown("---")
    st.markdown("**Built with ❤️ for Mellow Medical Education**")
    
    # Data quality information
    with st.expander("📋 Data Quality & Methodology Notes"):
        st.markdown("""
        **Data Sources:**
        - Cases Dataset: Clinical questions with correct answers
        - Responses Dataset: User interactions and demographics
        
        **Quality Assurance:**
        - All calculations are time-ordered to ensure chronological accuracy
        - Minimum thresholds applied where statistical significance matters
        - Missing data handling: Records with incomplete information are excluded from relevant calculations
        
        **Key Assumptions:**
        - User progression requires multiple attempts (minimum configurable)
        - Retention analysis assumes first attempt = registration date
        - Accuracy calculations exclude responses where correct answer is unknown
        
        **Statistical Methods:**
        - Expanding means for progression analysis (cumulative averages)
        - Confidence intervals shown where sample sizes are small
        - Segmentation based on percentile thresholds for robustness
        
        **Last Updated:** {stats['date_range']['end'].strftime('%Y-%m-%d')}
        """)


if __name__ == "__main__":
    main() 