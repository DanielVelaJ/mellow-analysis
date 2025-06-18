"""
Utility functions for statistical testing.
"""

import pandas as pd
import numpy as np
import streamlit as st
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def prepare_user_level_data(data_loader):
    """
    Prepare user-level aggregated data for statistical testing.
    
    Returns:
        DataFrame with one row per user containing their demographics and performance metrics
    """
    responses_df = data_loader.load_responses()
    
    # Aggregate to user level
    user_stats = responses_df.groupby('id_user_hash').agg({
        'is_correct': ['mean', 'count', 'sum'],
        'user_hospital': 'first',
        'user_specialty': 'first', 
        'user_subspecialty': 'first',
        'user_education_level': 'first',
        'user_gender': 'first',
        'user_age_range': 'first',
        'country_user_made_the_exam': 'first',
        'exam_created_at': ['min', 'max']
    }).reset_index()
    
    # Flatten column names
    user_stats.columns = [
        'user_id', 'accuracy', 'total_responses', 'correct_responses',
        'hospital', 'specialty', 'subspecialty', 'education_level', 
        'gender', 'age_range', 'country', 'first_exam', 'last_exam'
    ]
    
    # Calculate additional metrics
    user_stats['days_active'] = (user_stats['last_exam'] - user_stats['first_exam']).dt.days + 1
    user_stats['responses_per_day'] = user_stats['total_responses'] / user_stats['days_active']
    
    return user_stats


def check_normality(data, group_name=""):
    """
    Check normality assumption using Shapiro-Wilk test.
    
    Args:
        data: Array of values to test
        group_name: Name for display purposes
        
    Returns:
        dict with test results and interpretation
    """
    if len(data) < 3:
        return {
            'test': 'insufficient_data',
            'statistic': None,
            'p_value': None,
            'is_normal': False,
            'interpretation': f"{group_name}: Insufficient data for normality test (n={len(data)})"
        }
    
    # Use appropriate test based on sample size
    if len(data) <= 50:
        statistic, p_value = stats.shapiro(data)
        test_name = "Shapiro-Wilk"
    else:
        # For larger samples, use Anderson-Darling or fall back to Shapiro-Wilk
        statistic, p_value = stats.shapiro(data)
        test_name = "Shapiro-Wilk"
    
    is_normal = p_value > 0.05
    
    interpretation = f"{group_name} ({test_name}): "
    if is_normal:
        interpretation += f"Data appears normally distributed (p={p_value:.3f})"
    else:
        interpretation += f"Data may not be normally distributed (p={p_value:.3f})"
    
    return {
        'test': test_name.lower(),
        'statistic': statistic,
        'p_value': p_value,
        'is_normal': is_normal,
        'interpretation': interpretation
    }


def check_equal_variances(group1, group2, group1_name="Group 1", group2_name="Group 2"):
    """
    Check equal variances assumption using Levene's test.
    
    Returns:
        dict with test results and interpretation
    """
    if len(group1) < 2 or len(group2) < 2:
        return {
            'statistic': None,
            'p_value': None,
            'equal_variances': False,
            'interpretation': "Insufficient data for variance test"
        }
    
    statistic, p_value = stats.levene(group1, group2)
    equal_variances = p_value > 0.05
    
    interpretation = f"Levene's test: "
    if equal_variances:
        interpretation += f"Equal variances assumption met (p={p_value:.3f})"
    else:
        interpretation += f"Unequal variances detected (p={p_value:.3f})"
    
    return {
        'statistic': statistic,
        'p_value': p_value,
        'equal_variances': equal_variances,
        'interpretation': interpretation
    }


def calculate_effect_size(group1, group2):
    """
    Calculate Cohen's d effect size.
    
    Returns:
        dict with effect size and interpretation
    """
    if len(group1) < 2 or len(group2) < 2:
        return {
            'cohens_d': None,
            'interpretation': "Insufficient data for effect size calculation"
        }
    
    # Calculate pooled standard deviation
    n1, n2 = len(group1), len(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    
    # Calculate Cohen's d
    cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std
    
    # Interpret effect size
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        magnitude = "negligible"
    elif abs_d < 0.5:
        magnitude = "small"
    elif abs_d < 0.8:
        magnitude = "medium"
    else:
        magnitude = "large"
    
    interpretation = f"Cohen's d = {cohens_d:.3f} ({magnitude} effect size)"
    
    return {
        'cohens_d': cohens_d,
        'magnitude': magnitude,
        'interpretation': interpretation
    }


def create_comparison_plots(group1, group2, group1_name, group2_name, outcome_name):
    """
    Create visualization plots for group comparison.
    
    Returns:
        plotly figure with multiple subplots
    """
    # Prepare data for plotting
    plot_data = pd.DataFrame({
        'value': list(group1) + list(group2),
        'group': [group1_name] * len(group1) + [group2_name] * len(group2)
    })
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Box Plot Comparison',
            'Distribution Histograms', 
            'Violin Plot',
            'Summary Statistics'
        ],
        specs=[[{"type": "box"}, {"type": "histogram"}],
               [{"type": "violin"}, {"type": "table"}]]
    )
    
    # Box plot
    for i, (group_data, group_name) in enumerate([(group1, group1_name), (group2, group2_name)]):
        fig.add_trace(
            go.Box(y=group_data, name=group_name, showlegend=False),
            row=1, col=1
        )
    
    # Histograms
    fig.add_trace(
        go.Histogram(x=group1, name=group1_name, opacity=0.7, showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Histogram(x=group2, name=group2_name, opacity=0.7, showlegend=False),
        row=1, col=2
    )
    
    # Violin plot
    for i, (group_data, group_name) in enumerate([(group1, group1_name), (group2, group2_name)]):
        fig.add_trace(
            go.Violin(y=group_data, name=group_name, showlegend=False),
            row=2, col=1
        )
    
    # Summary statistics table
    summary_stats = pd.DataFrame({
        'Statistic': ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max'],
        group1_name: [
            len(group1),
            f"{np.mean(group1):.3f}",
            f"{np.median(group1):.3f}",
            f"{np.std(group1, ddof=1):.3f}",
            f"{np.min(group1):.3f}",
            f"{np.max(group1):.3f}"
        ],
        group2_name: [
            len(group2),
            f"{np.mean(group2):.3f}",
            f"{np.median(group2):.3f}",
            f"{np.std(group2, ddof=1):.3f}",
            f"{np.min(group2):.3f}",
            f"{np.max(group2):.3f}"
        ]
    })
    
    fig.add_trace(
        go.Table(
            header=dict(values=list(summary_stats.columns)),
            cells=dict(values=[summary_stats[col] for col in summary_stats.columns])
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        title_text=f"Comparison of {outcome_name} between {group1_name} and {group2_name}",
        showlegend=False
    )
    
    return fig


def interpret_p_value(p_value, alpha=0.05):
    """
    Provide interpretation of p-value in plain language.
    """
    if p_value is None:
        return "Unable to calculate p-value"
    
    if p_value < 0.001:
        return f"Very strong evidence of difference (p < 0.001)"
    elif p_value < 0.01:
        return f"Strong evidence of difference (p = {p_value:.3f})"
    elif p_value < alpha:
        return f"Moderate evidence of difference (p = {p_value:.3f})"
    elif p_value < 0.1:
        return f"Weak evidence of difference (p = {p_value:.3f})"
    else:
        return f"No evidence of difference (p = {p_value:.3f})"


def get_available_grouping_variables(user_df):
    """
    Get list of variables that can be used for grouping users.
    
    Returns:
        dict mapping display names to column names
    """
    grouping_vars = {}
    
    # Check each potential grouping variable
    if 'education_level' in user_df.columns and user_df['education_level'].notna().sum() > 0:
        grouping_vars['Education Level'] = 'education_level'
        
    if 'gender' in user_df.columns and user_df['gender'].notna().sum() > 0:
        grouping_vars['Gender'] = 'gender'
        
    if 'country' in user_df.columns and user_df['country'].nunique() > 1:
        grouping_vars['Country'] = 'country'
        
    if 'specialty' in user_df.columns and user_df['specialty'].notna().sum() > 0:
        grouping_vars['Medical Specialty'] = 'specialty'
        
    if 'age_range' in user_df.columns and user_df['age_range'].notna().sum() > 0:
        grouping_vars['Age Range'] = 'age_range'
    
    # Create binary variables for common comparisons
    if 'education_level' in user_df.columns:
        # Resident vs Specialist
        resident_count = user_df['education_level'].str.contains('Residente', na=False).sum()
        specialist_count = user_df['education_level'].str.contains('Especialista', na=False).sum()
        if resident_count > 0 and specialist_count > 0:
            grouping_vars['Resident vs Specialist'] = 'resident_vs_specialist'
    
    return grouping_vars 