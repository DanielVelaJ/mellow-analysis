"""
Interactive Two-Sample Statistical Tests

Allows users to compare performance between different groups of medical professionals
using appropriate statistical tests (t-test, Mann-Whitney U, etc.).
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

from .utils import (
    prepare_user_level_data,
    check_normality,
    check_equal_variances, 
    calculate_effect_size,
    create_comparison_plots,
    interpret_p_value,
    get_available_grouping_variables
)


def render_two_sample_tests(data_loader):
    """
    Render the interactive two-sample testing interface.
    """
    
    st.header("🧪 Two-Sample Statistical Tests")
    st.markdown("**Compare performance between two groups of medical professionals**")
    
    # Educational explanation
    with st.expander("📚 What Are Two-Sample Tests & When to Use Them"):
        st.markdown("""
        **Two-Sample Tests answer the question:**
        *"Is there a statistically significant difference in performance between Group A and Group B?"*
        
        **When to Use:**
        - Comparing **2 distinct groups** (e.g., Residents vs Specialists)
        - Testing if **group membership predicts performance**
        - Validating **educational program effectiveness**
        - Identifying **demographic performance gaps**
        
        **What We're Testing:**
        - **Null Hypothesis (H₀):** The two groups have equal average performance
        - **Alternative Hypothesis (H₁):** The two groups have different average performance
        
        **Types of Tests:**
        - **T-Test:** When data is normally distributed with equal variances
        - **Welch's T-Test:** When data is normal but variances differ
        - **Mann-Whitney U:** When data is not normally distributed (non-parametric)
        
        **Key Outputs:**
        - **P-value:** Probability of seeing this difference by chance
        - **Effect Size:** How practically meaningful the difference is
        - **Confidence Interval:** Range of likely true difference values
        """)
    
    # Prepare user-level data
    with st.spinner("Preparing user-level data..."):
        user_df = prepare_user_level_data(data_loader)
        
    st.success(f"✅ Data prepared: {len(user_df)} users ready for analysis")
    
    # Display data overview
    with st.expander("👥 User Data Overview"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(user_df))
            st.metric("Avg Accuracy", f"{user_df['accuracy'].mean():.1%}")
            
        with col2:
            st.metric("Avg Responses/User", f"{user_df['total_responses'].mean():.1f}")
            st.metric("Countries", user_df['country'].nunique())
            
        with col3:
            st.metric("Education Levels", user_df['education_level'].nunique())
            st.metric("Specialties", user_df['specialty'].nunique())
            
        # Show sample of data
        st.subheader("Sample Data")
        display_cols = ['accuracy', 'total_responses', 'education_level', 'gender', 'country', 'specialty']
        available_cols = [col for col in display_cols if col in user_df.columns]
        st.dataframe(user_df[available_cols].head(10))
    
    st.divider()
    
    # ==========================================================================
    # USER INTERFACE FOR TEST CONFIGURATION
    # ==========================================================================
    
    st.subheader("🎯 Configure Your Test")
    
    # Get available grouping variables
    grouping_vars = get_available_grouping_variables(user_df)
    
    if not grouping_vars:
        st.error("❌ No suitable grouping variables found in the data")
        return
        
    # Step 1: Choose grouping variable
    col1, col2 = st.columns(2)
    
    with col1:
        grouping_var_display = st.selectbox(
            "**Step 1:** Choose how to group users",
            options=list(grouping_vars.keys()),
            help="Select the variable that will split users into groups"
        )
        grouping_var = grouping_vars[grouping_var_display]
    
    with col2:
        outcome_var = st.selectbox(
            "**Step 2:** Choose outcome to compare",
            options=[
                'accuracy',
                'total_responses', 
                'responses_per_day'
            ],
            format_func=lambda x: {
                'accuracy': 'User Accuracy Rate (%)',
                'total_responses': 'Total Responses Count',
                'responses_per_day': 'Responses per Day'
            }[x],
            help="Select what metric to compare between groups"
        )
    
    # Handle special grouping variables
    if grouping_var == 'resident_vs_specialist':
        # Create the binary variable
        user_df = user_df.copy()
        user_df['resident_vs_specialist'] = user_df['education_level'].apply(
            lambda x: 'Resident' if pd.notna(x) and 'Residente' in str(x) 
                     else 'Specialist' if pd.notna(x) and 'Especialista' in str(x)
                     else 'Other'
        )
        
        # Filter out 'Other' category
        user_df = user_df[user_df['resident_vs_specialist'].isin(['Resident', 'Specialist'])]
    
    # Step 2: Choose specific groups
    if grouping_var in user_df.columns:
        available_groups = user_df[grouping_var].dropna().unique()
        available_groups = sorted(available_groups)
        
        if len(available_groups) < 2:
            st.error(f"❌ Need at least 2 groups in {grouping_var_display}, found {len(available_groups)}")
            return
            
        col1, col2 = st.columns(2)
        
        with col1:
            group_a = st.selectbox(
                "**Step 3a:** Select Group A",
                options=available_groups,
                help="First group for comparison"
            )
            
        with col2:
            remaining_groups = [g for g in available_groups if g != group_a]
            group_b = st.selectbox(
                "**Step 3b:** Select Group B", 
                options=remaining_groups,
                help="Second group for comparison"
            )
    
    # Step 3: Configure test parameters
    col1, col2 = st.columns(2)
    
    with col1:
        alpha = st.slider(
            "**Step 4:** Significance level (α)",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01,
            help="Probability threshold for rejecting null hypothesis"
        )
        
    with col2:
        min_users_per_group = st.slider(
            "**Step 5:** Minimum users per group",
            min_value=5,
            max_value=50,
            value=10,
            help="Filter groups with too few users for reliable testing"
        )
    
    # ==========================================================================
    # PERFORM THE STATISTICAL TEST
    # ==========================================================================
    
    if st.button("🧪 Run Statistical Test", type="primary"):
        
        with st.spinner("Running statistical analysis..."):
            
            # Extract groups
            group_a_data = user_df[user_df[grouping_var] == group_a][outcome_var].dropna()
            group_b_data = user_df[user_df[grouping_var] == group_b][outcome_var].dropna()
            
            # Check minimum sample sizes
            if len(group_a_data) < min_users_per_group or len(group_b_data) < min_users_per_group:
                st.error(f"""
                ❌ **Insufficient Sample Sizes**
                - {group_a}: {len(group_a_data)} users (need ≥{min_users_per_group})
                - {group_b}: {len(group_b_data)} users (need ≥{min_users_per_group})
                """)
                return
            
            # =================================================================
            # ASSUMPTION CHECKING
            # =================================================================
            
            st.subheader("🔍 Statistical Assumptions Check")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Normality Tests**")
                norm_a = check_normality(group_a_data, group_a)
                norm_b = check_normality(group_b_data, group_b)
                
                if norm_a['is_normal']:
                    st.success(f"✅ {norm_a['interpretation']}")
                else:
                    st.warning(f"⚠️ {norm_a['interpretation']}")
                    
                if norm_b['is_normal']:
                    st.success(f"✅ {norm_b['interpretation']}")
                else:
                    st.warning(f"⚠️ {norm_b['interpretation']}")
                    
            with col2:
                st.write("**Equal Variances Test**")
                var_test = check_equal_variances(group_a_data, group_b_data, group_a, group_b)
                
                if var_test['equal_variances']:
                    st.success(f"✅ {var_test['interpretation']}")
                else:
                    st.warning(f"⚠️ {var_test['interpretation']}")
            
            # =================================================================
            # CHOOSE APPROPRIATE TEST
            # =================================================================
            
            both_normal = norm_a['is_normal'] and norm_b['is_normal']
            equal_vars = var_test['equal_variances']
            
            if both_normal and equal_vars:
                test_choice = "Student's t-test"
                statistic, p_value = stats.ttest_ind(group_a_data, group_b_data)
                test_description = "Parametric test assuming normal distribution and equal variances"
                
            elif both_normal and not equal_vars:
                test_choice = "Welch's t-test" 
                statistic, p_value = stats.ttest_ind(group_a_data, group_b_data, equal_var=False)
                test_description = "Parametric test for normal data with unequal variances"
                
            else:
                test_choice = "Mann-Whitney U test"
                statistic, p_value = stats.mannwhitneyu(group_a_data, group_b_data, alternative='two-sided')
                test_description = "Non-parametric test (doesn't assume normal distribution)"
            
            # =================================================================
            # DISPLAY RESULTS
            # =================================================================
            
            st.subheader("📊 Test Results")
            
            # Test selection explanation
            st.info(f"""
            **Selected Test:** {test_choice}
            
            **Why:** {test_description}
            
            **Decision Logic:**
            - Both groups normal? {both_normal}
            - Equal variances? {equal_vars if both_normal else 'N/A (not both normal)'}
            """)
            
            # Main results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Test Statistic",
                    f"{statistic:.3f}",
                    help=f"The calculated {test_choice} statistic"
                )
                
            with col2:
                st.metric(
                    "P-value", 
                    f"{p_value:.6f}",
                    help="Probability of observing this difference by chance"
                )
                
            with col3:
                is_significant = p_value < alpha
                significance = "Significant" if is_significant else "Not Significant"
                st.metric(
                    f"Result (α={alpha})",
                    significance,
                    help=f"Whether the difference is statistically significant at α={alpha}"
                )
            
            # Interpretation
            interpretation = interpret_p_value(p_value, alpha)
            
            if is_significant:
                st.success(f"✅ **{interpretation}**")
                st.success(f"We reject the null hypothesis. There appears to be a real difference between {group_a} and {group_b}.")
            else:
                st.info(f"ℹ️ **{interpretation}**")
                st.info(f"We fail to reject the null hypothesis. No strong evidence of difference between {group_a} and {group_b}.")
            
            # Effect size
            effect_size = calculate_effect_size(group_a_data, group_b_data)
            
            if effect_size['cohens_d'] is not None:
                st.write(f"**Effect Size:** {effect_size['interpretation']}")
                
                if abs(effect_size['cohens_d']) < 0.2:
                    st.info("📏 The difference, even if statistically significant, is practically negligible.")
                elif abs(effect_size['cohens_d']) >= 0.8:
                    st.warning("📏 This represents a large, practically important difference!")
            
            # =================================================================
            # DESCRIPTIVE STATISTICS
            # =================================================================
            
            st.subheader("📈 Descriptive Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{group_a}** (n={len(group_a_data)})")
                st.write(f"- Mean: {group_a_data.mean():.4f}")
                st.write(f"- Median: {group_a_data.median():.4f}")
                st.write(f"- Std Dev: {group_a_data.std():.4f}")
                st.write(f"- Range: {group_a_data.min():.4f} - {group_a_data.max():.4f}")
                
            with col2:
                st.write(f"**{group_b}** (n={len(group_b_data)})")
                st.write(f"- Mean: {group_b_data.mean():.4f}")
                st.write(f"- Median: {group_b_data.median():.4f}")
                st.write(f"- Std Dev: {group_b_data.std():.4f}")
                st.write(f"- Range: {group_b_data.min():.4f} - {group_b_data.max():.4f}")
            
            mean_diff = group_a_data.mean() - group_b_data.mean()
            st.write(f"**Mean Difference:** {group_a} - {group_b} = {mean_diff:.4f}")
            
            # =================================================================
            # VISUALIZATIONS
            # =================================================================
            
            st.subheader("📊 Visual Comparison")
            
            # Create comprehensive comparison plots
            comparison_fig = create_comparison_plots(
                group_a_data, group_b_data, group_a, group_b, outcome_var
            )
            st.plotly_chart(comparison_fig, use_container_width=True)
            
            # =================================================================
            # BUSINESS INTERPRETATION
            # =================================================================
            
            st.subheader("💼 Business Interpretation")
            
            outcome_descriptions = {
                'accuracy': 'learning effectiveness and knowledge mastery',
                'total_responses': 'platform engagement and study intensity', 
                'responses_per_day': 'learning pace and daily commitment'
            }
            
            outcome_desc = outcome_descriptions.get(outcome_var, outcome_var)
            
            with st.container():
                st.markdown(f"""
                **What This Means for Medical Education:**
                
                This test compared **{outcome_desc}** between **{group_a}** and **{group_b}** users.
                """)
                
                if is_significant:
                    direction = "higher" if mean_diff > 0 else "lower"
                    st.markdown(f"""
                    ✅ **Key Finding:** {group_a} shows significantly {direction} {outcome_desc} than {group_b}.
                    
                    **Potential Implications:**
                    - If this difference favors more experienced groups → Educational progression is working
                    - If this difference favors certain demographics → May indicate equity issues to address  
                    - If this difference is unexpected → Warrants deeper investigation
                    
                    **Recommended Actions:**
                    - Validate findings with additional data
                    - Investigate underlying causes
                    - Consider targeted interventions if needed
                    """)
                else:
                    st.markdown(f"""
                    ℹ️ **Key Finding:** No significant difference in {outcome_desc} between these groups.
                    
                    **Potential Implications:**
                    - Groups are performing similarly (good for equity)
                    - Educational interventions may be working equally well
                    - Factors other than group membership drive performance
                    
                    **Recommended Actions:**
                    - Look for other variables that might explain performance differences
                    - Consider individual-level factors rather than group-level factors
                    - Validate with larger sample sizes if groups were small
                    """)
            
            # Export results option
            st.subheader("📥 Export Results")
            
            results_summary = {
                'Test Type': test_choice,
                'Groups Compared': f"{group_a} vs {group_b}",
                'Outcome Variable': outcome_var,
                'Sample Sizes': f"{len(group_a_data)} vs {len(group_b_data)}",
                'Test Statistic': statistic,
                'P-value': p_value,
                'Significant': is_significant,
                'Effect Size (Cohen\'s d)': effect_size.get('cohens_d'),
                'Mean Difference': mean_diff,
                f'{group_a} Mean': group_a_data.mean(),
                f'{group_b} Mean': group_b_data.mean()
            }
            
            results_df = pd.DataFrame([results_summary])
            
            st.download_button(
                label="📄 Download Results as CSV",
                data=results_df.to_csv(index=False),
                file_name=f"two_sample_test_{group_a}_vs_{group_b}_{outcome_var}.csv",
                mime="text/csv"
            ) 