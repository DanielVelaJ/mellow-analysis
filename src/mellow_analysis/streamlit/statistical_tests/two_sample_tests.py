"""
Enhanced Two-Sample Statistical Tests with Flexible Group Building.

Allows users to create complex group comparisons using multiple categorical 
variables and continuous ranges, with automated statistical test selection.
"""

import streamlit as st
import pandas as pd
from typing import Optional

from .data_analyzer import DataTypeAnalyzer, VariableInfo
from .data_preparation import prepare_user_level_data, validate_data_quality
from .group_builder import GroupBuilder, GroupDefinition
from .statistical_engine import StatisticalTestEngine, TestResult


def render_two_sample_tests(data_loader):
    """Render the enhanced two-sample statistical tests interface."""
    
    st.header("🧪 Enhanced Two-Sample Statistical Tests")
    st.markdown("""
    Create flexible group comparisons using **multiple variables** and **ranges**. 
    Compare performance between any two custom-defined groups of users.
    """)
    
    # Educational content
    with st.expander("ℹ️ How does this work?"):
        st.markdown("""
        **Goal:** Compare two groups you define using any combination of variables.
        
        **Examples of comparisons you can make:**
        - Urban hospitals (A, B, C) vs Rural hospitals (D, E, F)
        - High performers (accuracy 80-100%) vs Average performers (60-80%)
        - Experienced residents (>100 responses) vs New residents (<50 responses)
        - Male specialists vs Female specialists
        
        **The system automatically chooses the best statistical test:**
        - **Student's t-test**: Normal data, equal variances
        - **Welch's t-test**: Normal data, unequal variances  
        - **Mann-Whitney U**: Non-parametric alternative
        """)
    
    # Step 1: Data Preparation
    with st.spinner("Preparing data for analysis..."):
        try:
            user_df = prepare_user_level_data(data_loader)
            data_validation = validate_data_quality(user_df)
        except Exception as e:
            st.error(f"Error preparing data: {str(e)}")
            return
    
    # Display data quality information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", f"{data_validation['total_users']:,}")
    with col2:
        st.metric("Data Issues", len(data_validation['issues']))
    with col3:
        st.metric("Warnings", len(data_validation['warnings']))
    
    # Show warnings if any
    for warning in data_validation['warnings']:
        st.warning(f"⚠️ {warning}")
    
    for issue in data_validation['issues']:
        st.error(f"❌ {issue}")
    
    if data_validation['issues']:
        st.stop()
    
    # Step 2: Analyze Variables
    with st.spinner("Analyzing variables..."):
        analyzer = DataTypeAnalyzer()
        variables = analyzer.analyze_dataset(user_df)
        grouping_variables = analyzer.get_grouping_variables(variables)
        outcome_variables = analyzer.get_outcome_variables(variables)
    
    if not grouping_variables:
        st.error("No suitable grouping variables found in the dataset.")
        return
    
    if not outcome_variables:
        st.error("No suitable outcome variables found in the dataset.")
        return
    
    # Step 3: Group Building Interface
    st.subheader("Step 1: Define Your Groups")
    st.markdown("Create two groups for comparison using any combination of variables.")
    
    group_builder = GroupBuilder(variables)
    
    # Create tabs for group building
    tab_a, tab_b = st.tabs(["👥 Group A", "👥 Group B"])
    
    with tab_a:
        group_a = group_builder.render_group_builder("Group A", "group_a")
        if group_a.categorical_filters or group_a.continuous_filters:
            group_builder.render_group_preview(group_a, user_df)
    
    with tab_b:
        group_b = group_builder.render_group_builder("Group B", "group_b")
        if group_b.categorical_filters or group_b.continuous_filters:
            group_builder.render_group_preview(group_b, user_df)
    
    # Step 4: Validate Groups
    if (group_a.categorical_filters or group_a.continuous_filters) and \
       (group_b.categorical_filters or group_b.continuous_filters):
        
        validation = group_builder.validate_groups(group_a, group_b, user_df)
        
        st.subheader("Step 2: Group Validation")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Group A Size", f"{validation['group_a_size']:,}")
        with col2:
            st.metric("Group B Size", f"{validation['group_b_size']:,}")
        with col3:
            balance_color = "normal" if validation['is_balanced'] else "off"
            st.metric("Balance Ratio", f"{validation['size_ratio']:.2f}", 
                     delta_color=balance_color)
        
        if validation['has_overlap']:
            st.error(f"❌ Groups have {validation['overlap_count']} overlapping users. "
                    "Please adjust your group definitions to avoid overlap.")
        
        if not validation['is_valid']:
            st.error("❌ Groups are not valid for comparison. "
                    "Ensure each group has at least 10 users and no overlap.")
            return
        
        if not validation['is_balanced']:
            st.warning("⚠️ Groups are unbalanced (>3:1 ratio). "
                      "Results should be interpreted cautiously.")
    
    else:
        st.info("👆 Please define both groups to proceed with the analysis.")
        return
    
    # Step 5: Outcome Selection and Test Configuration
    st.subheader("Step 3: Configure Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        outcome_var = st.selectbox(
            "Select outcome variable to compare:",
            options=list(outcome_variables.keys()),
            format_func=lambda x: outcome_variables[x].display_name,
            help="Choose the metric you want to compare between groups"
        )
    
    with col2:
        alpha = st.slider(
            "Significance level (α):",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01,
            help="Threshold for statistical significance"
        )
    
    # Step 6: Run Analysis
    if st.button("🔬 Run Statistical Test", type="primary"):
        if not outcome_var:
            st.error("Please select an outcome variable.")
            return
        
        with st.spinner("Running statistical analysis..."):
            # Initialize statistical engine
            engine = StatisticalTestEngine(alpha=alpha)
            
            # Run the comparison
            try:
                result = engine.compare_groups(
                    group_a, group_b, user_df, outcome_var
                )
                
                # Display results
                _display_test_results(result, group_a, group_b)
                
                # Create and display visualizations
                outcome_info = outcome_variables[outcome_var]
                fig = engine.create_comparison_visualizations(
                    group_a, group_b, user_df, outcome_var, outcome_info.display_name
                )
                
                st.subheader("📊 Visual Analysis")
                st.plotly_chart(fig, use_container_width=True)
                
                # Display detailed assumptions
                _display_statistical_assumptions(result.assumptions)
                
            except Exception as e:
                st.error(f"Error running statistical test: {str(e)}")


def _display_test_results(result: TestResult, group_a: GroupDefinition, 
                         group_b: GroupDefinition) -> None:
    """Display the statistical test results."""
    st.subheader("📈 Test Results")
    
    # Main results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Statistical Test", result.test_name)
    with col2:
        st.metric("Test Statistic", f"{result.statistic:.3f}")
    with col3:
        st.metric("p-value", f"{result.p_value:.4f}")
    with col4:
        st.metric("Effect Size", f"{result.effect_size:.3f}")
    
    # Interpretation
    st.markdown("### 🎯 Interpretation")
    st.info(result.interpretation)
    
    # Effect size interpretation
    if result.effect_magnitude.lower() == 'large':
        st.success(f"🔥 **Large effect size** ({result.effect_magnitude}) - "
                  "The difference between groups is practically significant.")
    elif result.effect_magnitude.lower() == 'medium':
        st.info(f"📊 **Medium effect size** ({result.effect_magnitude}) - "
               "The difference between groups is moderately meaningful.")
    elif result.effect_magnitude.lower() == 'small':
        st.warning(f"📉 **Small effect size** ({result.effect_magnitude}) - "
                  "The difference between groups is statistically detectable but small.")
    else:
        st.error(f"❌ **Negligible effect size** ({result.effect_magnitude}) - "
                "The difference between groups is not practically meaningful.")
    
    # Sample sizes
    st.markdown("### 👥 Sample Sizes")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{group_a.name}:** {result.sample_sizes[group_a.name]:,} users")
    with col2:
        st.write(f"**{group_b.name}:** {result.sample_sizes[group_b.name]:,} users")


def _display_statistical_assumptions(assumptions: dict) -> None:
    """Display the statistical assumptions and their test results."""
    with st.expander("🔍 Statistical Assumptions (Advanced)"):
        st.markdown("### Normality Tests")
        for key, assumption in assumptions.items():
            if 'normality' in key:
                if assumption['p_value'] is not None:
                    icon = "✅" if assumption['is_normal'] else "⚠️"
                    st.write(f"{icon} {assumption['interpretation']}")
                else:
                    st.write(f"❌ {assumption['interpretation']}")
        
        st.markdown("### Equal Variances Test")
        var_assumption = assumptions.get('equal_variances', {})
        if var_assumption.get('p_value') is not None:
            icon = "✅" if var_assumption['equal_variances'] else "⚠️"
            st.write(f"{icon} {var_assumption['interpretation']}")
        else:
            st.write(f"❌ {var_assumption['interpretation']}")
        
        st.markdown("""
        **Note:** These assumptions determine which statistical test is automatically selected:
        - If both groups are normal with equal variances → Student's t-test
        - If both groups are normal with unequal variances → Welch's t-test
        - If normality assumptions fail → Mann-Whitney U test (non-parametric)
        """) 