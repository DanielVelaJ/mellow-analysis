"""
Utility functions for statistical testing.
"""

import pandas as pd
import numpy as np
import streamlit as st
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================
# Data Preparation
# =============================

def prepare_user_level_data(data_loader):
    """Aggregate response-level data to user-level metrics."""
    responses_df = data_loader.load_responses()

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

    user_stats.columns = [
        'user_id', 'accuracy', 'total_responses', 'correct_responses',
        'hospital', 'specialty', 'subspecialty', 'education_level',
        'gender', 'age_range', 'country', 'first_exam', 'last_exam'
    ]

    user_stats['days_active'] = (user_stats['last_exam'] - user_stats['first_exam']).dt.days + 1
    user_stats['responses_per_day'] = user_stats['total_responses'] / user_stats['days_active']

    return user_stats

# =============================
# Assumption Checks
# =============================

def check_normality(data, group_name=""):
    if len(data) < 3:
        return {'test': 'shapiro', 'statistic': None, 'p_value': None, 'is_normal': False,
                'interpretation': f"{group_name}: insufficient data for normality test"}
    statistic, p_value = stats.shapiro(data)
    is_normal = p_value > 0.05
    interpretation = (f"{group_name}: data appears normal (p={p_value:.3f})" if is_normal else
                      f"{group_name}: data may not be normal (p={p_value:.3f})")
    return {'test': 'shapiro', 'statistic': statistic, 'p_value': p_value,
            'is_normal': is_normal, 'interpretation': interpretation}


def check_equal_variances(group1, group2, group1_name="Group 1", group2_name="Group 2"):
    if len(group1) < 2 or len(group2) < 2:
        return {'statistic': None, 'p_value': None, 'equal_variances': False,
                'interpretation': 'insufficient data for variance test'}
    statistic, p_value = stats.levene(group1, group2)
    equal_variances = p_value > 0.05
    interpretation = (f"Equal variances (p={p_value:.3f})" if equal_variances else
                      f"Unequal variances (p={p_value:.3f})")
    return {'statistic': statistic, 'p_value': p_value, 'equal_variances': equal_variances,
            'interpretation': interpretation}

# =============================
# Effect Size
# =============================

def calculate_effect_size(group1, group2):
    if len(group1) < 2 or len(group2) < 2:
        return {'cohens_d': None, 'interpretation': 'insufficient data'}
    n1, n2 = len(group1), len(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    d = (np.mean(group1) - np.mean(group2)) / pooled_std
    magnitude = ('negligible' if abs(d) < 0.2 else 'small' if abs(d) < 0.5 else
                 'medium' if abs(d) < 0.8 else 'large')
    return {'cohens_d': d, 'magnitude': magnitude,
            'interpretation': f"Cohen's d = {d:.3f} ({magnitude})"}

# =============================
# Visualization
# =============================

def create_comparison_plots(group1, group2, name1, name2, outcome):
    fig = make_subplots(rows=2, cols=2, subplot_titles=[
        'Box Plot', 'Histograms', 'Violin Plot', 'Summary Stats'],
        specs=[[{'type':'box'}, {'type':'histogram'}], [{'type':'violin'}, {'type':'table'}]])

    # Box
    for data, name in [(group1, name1), (group2, name2)]:
        fig.add_trace(go.Box(y=data, name=name, showlegend=False), row=1, col=1)
    # Hist
    fig.add_trace(go.Histogram(x=group1, name=name1, opacity=0.6, showlegend=False), row=1, col=2)
    fig.add_trace(go.Histogram(x=group2, name=name2, opacity=0.6, showlegend=False), row=1, col=2)
    # Violin
    for data, name in [(group1, name1), (group2, name2)]:
        fig.add_trace(go.Violin(y=data, name=name, showlegend=False), row=2, col=1)

    summary = pd.DataFrame({
        'Statistic': ['Count','Mean','Median','Std','Min','Max'],
        name1: [len(group1), f"{np.mean(group1):.3f}", f"{np.median(group1):.3f}", f"{np.std(group1, ddof=1):.3f}", f"{np.min(group1):.3f}", f"{np.max(group1):.3f}"],
        name2: [len(group2), f"{np.mean(group2):.3f}", f"{np.median(group2):.3f}", f"{np.std(group2, ddof=1):.3f}", f"{np.min(group2):.3f}", f"{np.max(group2):.3f}"]
    })
    fig.add_trace(go.Table(header=dict(values=list(summary.columns)),
                           cells=dict(values=[summary[col] for col in summary.columns])),
                  row=2, col=2)
    fig.update_layout(height=800, title=f"{outcome} comparison: {name1} vs {name2}")
    return fig

# =============================
# Helper Functions
# =============================

def interpret_p_value(p, alpha=0.05):
    if p is None:
        return 'p-value unavailable'
    if p < 0.001:
        return 'Very strong evidence (p<0.001)'
    if p < 0.01:
        return f'Strong evidence (p={p:.3f})'
    if p < alpha:
        return f'Moderate evidence (p={p:.3f})'
    if p < 0.1:
        return f'Weak evidence (p={p:.3f})'
    return f'No evidence (p={p:.3f})'


def get_available_grouping_variables(df):
    vars = {}
    if 'education_level' in df.columns and df['education_level'].notna().any():
        vars['Education Level'] = 'education_level'
    if 'gender' in df.columns and df['gender'].notna().any():
        vars['Gender'] = 'gender'
    if 'country' in df.columns and df['country'].nunique() > 1:
        vars['Country'] = 'country'
    if 'specialty' in df.columns and df['specialty'].notna().any():
        vars['Medical Specialty'] = 'specialty'
    if 'age_range' in df.columns and df['age_range'].notna().any():
        vars['Age Range'] = 'age_range'

    if 'education_level' in df.columns:
        res = df['education_level'].str.contains('Residente', na=False).sum()
        spec = df['education_level'].str.contains('Especialista', na=False).sum()
        if res>0 and spec>0:
            vars['Resident vs Specialist'] = 'resident_vs_specialist'
    return vars