"""
Interactive Two-Sample Statistical Tests

Allows users to compare performance between different groups of medical professionals
using appropriate statistical tests (t-test, Welch, Mann–Whitney U).
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

from .utils import (
    prepare_user_level_data,
    check_normality,
    check_equal_variances,
    calculate_effect_size,
    create_comparison_plots,
    interpret_p_value,
    get_available_grouping_variables,
)


# =============================================================================
# Main render function
# =============================================================================

def render_two_sample_tests(data_loader):
    """Render the interactive two-sample-test section in Streamlit."""

    st.header("🧪 Two-Sample Statistical Tests")
    st.markdown("Compare performance between **two groups** of users.")

    # ---------------------------------------------------------------------
    # 0. Education / Help
    # ---------------------------------------------------------------------
    with st.expander("ℹ️  What is a two-sample test?"):
        st.markdown(
            """
            **Goal:** Determine whether **Group A** and **Group B** differ in a
            chosen performance metric (e.g. accuracy).

            *Null hypothesis (H₀)*  : both groups have the same mean.

            Depending on data distribution & variance equality the app will
            automatically choose:

            • **Student's t-test** – normal data, equal variances  
            • **Welch's t-test**  – normal data, unequal variances  
            • **Mann–Whitney U** – non-parametric alternative (no normality)
            """
        )

    # ---------------------------------------------------------------------
    # 1. Prepare user-level dataframe
    # ---------------------------------------------------------------------
    with st.spinner("Preparing user-level data …"):
        user_df = prepare_user_level_data(data_loader)
    st.success(f"Loaded **{len(user_df):,}** users for analysis.")

    # ---------------------------------------------------------------------
    # 2. Test configuration UI
    # ---------------------------------------------------------------------

    st.subheader("1 · Select grouping variable")
    grouping_dict = get_available_grouping_variables(user_df)
    if not grouping_dict:
        st.error("No grouping variables available in the dataset.")
        return
    grouping_display = st.selectbox("Group users by …", list(grouping_dict))
    grouping_col = grouping_dict[grouping_display]

    # Create binary variable for resident vs specialist if chosen
    if grouping_col == "resident_vs_specialist":
        user_df = user_df.copy()
        user_df[grouping_col] = user_df["education_level"].apply(
            lambda x: "Resident" if pd.notna(x) and "Residente" in str(x)
            else "Specialist" if pd.notna(x) and "Especialista" in str(x)
            else np.nan
        )
        user_df = user_df.dropna(subset=[grouping_col])

    unique_groups = sorted(user_df[grouping_col].dropna().unique())
    if len(unique_groups) < 2:
        st.error("Need at least two groups to compare.")
        return

    colA, colB = st.columns(2)
    with colA:
        group_a = st.selectbox("Group A", unique_groups)
    with colB:
        group_b = st.selectbox("Group B", [g for g in unique_groups if g != group_a])

    st.subheader("2 · Select outcome variable")
    outcome_options = {
        "accuracy": "User accuracy rate",
        "total_responses": "Total responses",
        "responses_per_day": "Responses per day",
    }
    outcome_col = st.selectbox("Outcome", list(outcome_options), format_func=outcome_options.get)

    st.subheader("3 · Test parameters")
    alpha = st.slider("Significance level α", 0.01, 0.10, 0.05, 0.01)
    min_n = st.slider("Minimum users per group", 5, 50, 10)

    if not st.button("Run test", type="primary"):
        return

    # ---------------------------------------------------------------------
    # 3. Run analysis
    # ---------------------------------------------------------------------
    data_a = user_df[user_df[grouping_col] == group_a][outcome_col].dropna()
    data_b = user_df[user_df[grouping_col] == group_b][outcome_col].dropna()

    if len(data_a) < min_n or len(data_b) < min_n:
        st.error(f"Not enough data – {group_a}: {len(data_a)}, {group_b}: {len(data_b)} (need ≥ {min_n}).")
        return

    # Assumption checks
    norm_a, norm_b = check_normality(data_a, group_a), check_normality(data_b, group_b)
    var_test = check_equal_variances(data_a, data_b, group_a, group_b)

    both_normal = norm_a["is_normal"] and norm_b["is_normal"]
    equal_var = var_test["equal_variances"]

    # Choose test
    if both_normal and equal_var:
        test_name = "Student's t-test"
        stat, p = stats.ttest_ind(data_a, data_b, equal_var=True)
    elif both_normal and not equal_var:
        test_name = "Welch's t-test"
        stat, p = stats.ttest_ind(data_a, data_b, equal_var=False)
    else:
        test_name = "Mann–Whitney U"
        stat, p = stats.mannwhitneyu(data_a, data_b, alternative="two-sided")

    # ---------------------------------------------------------------------
    # 4. Results
    # ---------------------------------------------------------------------
    st.subheader("Results")
    cols = st.columns(3)
    cols[0].metric("Test", test_name)
    cols[1].metric("Statistic", f"{stat:.3f}")
    cols[2].metric("p-value", f"{p:.4f}")

    st.write(interpret_p_value(p, alpha))

    eff = calculate_effect_size(data_a, data_b)
    st.write(f"Effect size: {eff['interpretation']}")

    # ---------------------------------------------------------------------
    # 5. Visualisations
    # ---------------------------------------------------------------------
    st.plotly_chart(
        create_comparison_plots(data_a, data_b, group_a, group_b, outcome_options[outcome_col]),
        use_container_width=True,
    ) 