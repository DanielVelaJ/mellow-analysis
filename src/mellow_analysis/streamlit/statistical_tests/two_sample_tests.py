"""
Enhanced Two-Sample Statistical Tests with Flexible Group Building.

Allows users to create complex group comparisons using multiple categorical 
variables and continuous ranges, with automated statistical test selection.
"""

import streamlit as st
import pandas as pd
from typing import Optional
from scipy import stats

from .data_analyzer import DataTypeAnalyzer, VariableInfo
from .data_preparation import prepare_user_level_data, validate_data_quality
from .group_builder import GroupBuilder, GroupDefinition
from .statistical_engine import StatisticalTestEngine, TestResult


def render_two_sample_tests(data_loader):
    """Render the enhanced two-sample statistical tests interface."""
    
    st.header("🧪 Two-Sample Statistical Tests")
    st.caption("Compare any two groups using automatically selected statistical tests")
    
    # Step 1: Data Preparation
    with st.spinner("Preparing data for analysis..."):
        try:
            user_df = prepare_user_level_data(data_loader)
            data_validation = validate_data_quality(user_df)
        except Exception as e:
            st.error(f"Error preparing data: {str(e)}")
            return
    
    # Quick data quality check
    if data_validation['issues']:
        for issue in data_validation['issues']:
            st.error(f"❌ {issue}")
        st.stop()
    
    # Show warnings compactly if any exist
    warning_count = len(data_validation['warnings'])
    if warning_count > 0:
        with st.expander(f"⚠️ {warning_count} data warnings"):
            for warning in data_validation['warnings']:
                st.caption(warning)
    else:
        # Consolidate success message and how-it-works into single row
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"✅ {data_validation['total_users']:,} users ready for analysis")
        with col2:
            with st.expander("ℹ️ How it works"):
                st.markdown("""
                **Compare two groups** to find statistically significant differences.
                
                **Test selection is automatic:**
                - Student's t-test (normal data, equal variances)
                - Welch's t-test (normal data, unequal variances)  
                - Mann-Whitney U (non-normal data)
                
                **Results include:** p-value, effect size, and test rationale.
                """)
    
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
    
    # Simplified configuration with better defaults
    col1, col2 = st.columns([3, 1])
    
    with col1:
        outcome_var = st.selectbox(
            "📊 Outcome Variable:",
            options=list(outcome_variables.keys()),
            format_func=lambda x: outcome_variables[x].display_name,
            help="The metric to compare between your two groups"
        )
    
    with col2:
        # Simplified significance options
        significance_options = {
            "Standard (5%)": 0.05,
            "Strict (1%)": 0.01,
            "Lenient (10%)": 0.10
        }
        alpha_label = st.selectbox(
            "📈 Significance Level:",
            options=list(significance_options.keys()),
            index=0,
            help="Lower = more strict requirements for finding differences"
        )
        alpha = significance_options[alpha_label]
    
    if not outcome_var:
        st.warning("Please select an outcome variable to continue.")
        return
    
    # Group building
    st.subheader("Define Groups")
    st.caption("Build two groups for comparison with live diagnostics")
    
    group_builder = GroupBuilder(variables)
    
    # Create columns for side-by-side group building
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 👥 Group A")
        with st.expander("🔧 Define Filters", expanded=True):
            group_a = group_builder.render_group_builder("Group A", "group_a")
        group_builder.render_group_preview(group_a, user_df, outcome_var)
    
    with col_b:
        st.markdown("### 👥 Group B") 
        with st.expander("🔧 Define Filters", expanded=True):
            group_b = group_builder.render_group_builder("Group B", "group_b")
        group_builder.render_group_preview(group_b, user_df, outcome_var)
    
    # Step 5: Group Validation and Test Prediction
    if (group_a.categorical_filters or group_a.continuous_filters) and \
       (group_b.categorical_filters or group_b.continuous_filters):
        
        validation = group_builder.validate_groups(group_a, group_b, user_df)
        
        # Simplified validation messages
        if validation['has_overlap']:
            st.error(f"❌ Groups overlap with {validation['overlap_count']} shared users. Please adjust your filters.")
            return
        
        if not validation['is_valid']:
            st.error("❌ Each group needs at least 10 users. Please adjust your filters.")
            return
        
        # Show predicted test and balance in a cleaner way
        _show_test_prediction_compact(group_a, group_b, user_df, outcome_var, validation)
    
    else:
        st.info("👆 Please define both groups to proceed with the analysis.")
        return
    
    # Run Analysis
    if st.button("🔬 Run Analysis", type="primary"):
        
        with st.spinner("Running statistical analysis..."):
            # Initialize statistical engine
            engine = StatisticalTestEngine(alpha=alpha)
            
            # Run the comparison
            try:
                result = engine.compare_groups(
                    group_a, group_b, user_df, outcome_var
                )
                
                # Display results
                _display_test_results_simplified(result, group_a, group_b, alpha)
                
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


def _show_test_prediction_compact(group_a: GroupDefinition, group_b: GroupDefinition, 
                                df: pd.DataFrame, outcome_var: str, validation: dict) -> None:
    """Show test prediction and balance info in a compact format."""
    
    # Get group data for prediction
    group_a_data = group_a.apply_filters(df)[outcome_var].dropna()
    group_b_data = group_b.apply_filters(df)[outcome_var].dropna()
    
    # Predict test
    engine = StatisticalTestEngine()
    predicted_test = engine._select_test(group_a_data, group_b_data)
    
    # Compact status display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"🔬 **{predicted_test}** will be used - {engine._get_test_reason(group_a_data, group_b_data)}")
    
    with col2:
        if not validation['is_balanced']:
            st.warning(f"⚖️ Unbalanced groups ({validation['size_ratio']:.1f}:1)")
        else:
            st.success(f"⚖️ Balanced groups ({validation['size_ratio']:.1f}:1)")


def _display_test_results_simplified(result: TestResult, group_a: GroupDefinition, 
                                   group_b: GroupDefinition, alpha: float) -> None:
    """Display simplified test results with clear visual hierarchy."""
    
    # Lead with the conclusion in a prominent card
    if result.p_value < alpha:
        st.success(f"""
        ### ✅ **Significant Difference Found**
        
        {result.interpretation}
        """)
        
        # Determine evidence strength
        effect_size_abs = abs(result.effect_size)
        if effect_size_abs >= 0.5:
            st.success("**🟢 STRONG EVIDENCE**: Both statistically significant AND practically meaningful.")
        elif effect_size_abs >= 0.2:
            st.warning("**🟡 MODERATE EVIDENCE**: Statistically significant but small practical impact.")
        else:
            st.warning("**🟡 WEAK EVIDENCE**: Statistically significant but negligible practical impact.")
    else:
        st.error(f"""
        ### ❌ **No Significant Difference**
        
        {result.interpretation}
        
        **🔴 NO EVIDENCE**: Cannot conclude that groups differ on this measure.
        """)
    
    # Technical details in a compact grid
    st.markdown("#### 📊 Technical Details")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Test Used", result.test_name)
    
    with col2:
        st.metric("Test Statistic", f"{result.statistic:.3f}")
    
    with col3:
        p_display = f"{result.p_value:.4f}" if result.p_value >= 0.0001 else "< 0.0001"
        st.metric("p-value", p_display)
    
    with col4:
        st.metric("Effect Size", f"{result.effect_size:.3f}")
    
    # Simplified explanations as single line
    _show_simple_interpretations(result, alpha)


def _show_simple_interpretations(result: TestResult, alpha: float) -> None:
    """Show simple one-line interpretations."""
    
    # P-value interpretation
    if result.p_value < 0.001:
        p_interpretation = "Very strong evidence against chance"
    elif result.p_value < 0.01:
        p_interpretation = "Strong evidence against chance"
    elif result.p_value < alpha:
        p_interpretation = "Moderate evidence against chance"
    else:
        p_interpretation = "Little to no evidence against chance"
    
    st.caption(f"**p-value:** {p_interpretation} (threshold: {alpha})")
    
    # Effect size interpretation
    effect_size_abs = abs(result.effect_size)
    if effect_size_abs >= 0.8:
        effect_interpretation = "Large practical difference"
    elif effect_size_abs >= 0.5:
        effect_interpretation = "Medium practical difference"
    elif effect_size_abs >= 0.2:
        effect_interpretation = "Small practical difference"
    else:
        effect_interpretation = "Negligible practical difference"
    
    st.caption(f"**Effect size:** {effect_interpretation}")


def _display_statistical_assumptions(assumptions: dict) -> None:
    """Display the statistical assumptions and their test results with educational content."""
    with st.expander("🔍 Statistical Assumptions & Test Selection Details", expanded=False):
        st.markdown("""
        **Why do we check assumptions?**
        Different statistical tests make different assumptions about your data. We automatically check these assumptions to pick the best test for your specific data.
        """)
        
        st.markdown("### 📊 Normality Tests (Shapiro-Wilk)")
        st.caption("Tests whether each group follows a normal (bell-curve) distribution")
        
        col1, col2 = st.columns(2)
        
        for key, assumption in assumptions.items():
            if 'normality' in key:
                group_name = key.replace('_normality', '').replace('group_', 'Group ')
                
                if 'group_a' in key:
                    with col1:
                        _display_normality_result(group_name, assumption)
                else:
                    with col2:
                        _display_normality_result(group_name, assumption)
        
        st.markdown("### ⚖️ Equal Variances Test (Levene's Test)")
        st.caption("Tests whether both groups have similar spread/variability")
        
        var_assumption = assumptions.get('equal_variances', {})
        if var_assumption.get('p_value') is not None:
            if var_assumption['equal_variances']:
                st.success(f"""
                ✅ **Equal variances assumed** (p = {var_assumption['p_value']:.4f})
                - Both groups have similar variability
                - Student's t-test is appropriate (if normality also met)
                """)
            else:
                st.warning(f"""
                ⚠️ **Unequal variances detected** (p = {var_assumption['p_value']:.4f})
                - Groups have different levels of variability  
                - Welch's t-test is more appropriate (adjusts for unequal variances)
                """)
        else:
            st.error("❌ Could not test for equal variances")
        
        st.markdown("### 🎯 Test Selection Logic")
        st.info("""
        **How the system chooses your test:**
        
        1. **Check normality** in both groups
        2. **Check equal variances** (if both groups are normal)
        3. **Select best test:**
           - ✅ Both normal + equal variances → **Student's t-test** (most powerful)
           - ✅ Both normal + unequal variances → **Welch's t-test** (robust to variance differences)
           - ⚠️ Non-normal data → **Mann-Whitney U** (doesn't assume normal distribution)
        
        **Why this matters:** Using the wrong test can lead to incorrect conclusions!
        """)
        
        st.markdown("### 📚 Learn More")
        with st.expander("What is normality and why does it matter?"):
            st.markdown("""
            **Normal distribution** (bell curve) is a key assumption for t-tests:
            - Most values cluster around the average
            - Symmetric distribution (not skewed)
            - Predictable spread pattern
            
            **When data isn't normal:**
            - T-tests may give wrong results
            - Non-parametric tests (like Mann-Whitney U) are safer
            - These tests use ranks instead of raw values
            """)
        
        with st.expander("What are equal variances?"):
            st.markdown("""
            **Variance** measures how spread out your data is:
            - Low variance = values close to average
            - High variance = values widely scattered
            
            **Equal variances assumption:**
            - Both groups should have similar spread
            - If violated, standard t-test becomes unreliable
            - Welch's t-test fixes this by adjusting calculations
            """)


def _display_normality_result(group_name: str, assumption: dict) -> None:
    """Display normality test result for a single group."""
    if assumption['p_value'] is not None:
        if assumption['is_normal']:
            st.success(f"""
            ✅ **{group_name}: Normal distribution**
            - Shapiro-Wilk p = {assumption['p_value']:.4f}
            - Data follows bell-curve pattern
            - T-tests are appropriate
            """)
        else:
            st.warning(f"""
            ⚠️ **{group_name}: Non-normal distribution**
            - Shapiro-Wilk p = {assumption['p_value']:.4f}
            - Data doesn't follow bell-curve pattern
            - Non-parametric tests recommended
            """)
    else:
        st.error(f"❌ **{group_name}: Could not test normality**") 