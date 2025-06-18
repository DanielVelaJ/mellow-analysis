"""
Data preparation utilities for statistical analysis.
"""

import pandas as pd
import numpy as np
from typing import Optional


def prepare_user_level_data(data_loader) -> pd.DataFrame:
    """
    Aggregate response-level data to user-level metrics for statistical analysis.
    
    Args:
        data_loader: Data loader instance with load_responses() method
        
    Returns:
        DataFrame with user-level aggregated data
    """
    # Load raw response data
    responses_df = data_loader.load_responses()
    
    # Aggregate user-level statistics
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
    
    # Calculate derived metrics
    user_stats['days_active'] = (
        user_stats['last_exam'] - user_stats['first_exam']
    ).dt.days + 1
    
    user_stats['responses_per_day'] = (
        user_stats['total_responses'] / user_stats['days_active']
    )
    
    # Clean and standardize categorical variables
    user_stats = _clean_categorical_variables(user_stats)
    
    return user_stats


def _clean_categorical_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize categorical variables."""
    df = df.copy()
    
    # Standardize education levels
    if 'education_level' in df.columns:
        df['education_level'] = df['education_level'].fillna('Unknown')
        
        # Create simplified education categories
        def simplify_education(education):
            if pd.isna(education):
                return 'Unknown'
            education_str = str(education).lower()
            if 'residente' in education_str:
                return 'Resident'
            elif 'especialista' in education_str:
                return 'Specialist'
            elif 'estudiante' in education_str:
                return 'Student'
            else:
                return 'Other'
        
        df['education_simplified'] = df['education_level'].apply(simplify_education)
    
    # Clean hospital names
    if 'hospital' in df.columns:
        df['hospital'] = df['hospital'].fillna('Unknown')
        df['hospital'] = df['hospital'].astype(str).str.strip()
    
    # Clean specialty names
    if 'specialty' in df.columns:
        df['specialty'] = df['specialty'].fillna('Unknown')
        df['specialty'] = df['specialty'].astype(str).str.strip()
    
    # Clean gender
    if 'gender' in df.columns:
        df['gender'] = df['gender'].fillna('Unknown')
        df['gender'] = df['gender'].astype(str).str.strip()
    
    # Clean country
    if 'country' in df.columns:
        df['country'] = df['country'].fillna('Unknown')
        df['country'] = df['country'].astype(str).str.strip()
    
    return df


def validate_data_quality(df: pd.DataFrame) -> dict:
    """
    Validate data quality for statistical analysis.
    
    Returns:
        Dictionary with validation results and recommendations
    """
    validation = {
        'total_users': len(df),
        'issues': [],
        'warnings': [],
        'recommendations': []
    }
    
    # Check for minimum sample size
    if len(df) < 20:
        validation['issues'].append(f"Very small sample size ({len(df)} users)")
        validation['recommendations'].append("Consider collecting more data")
    elif len(df) < 50:
        validation['warnings'].append(f"Small sample size ({len(df)} users)")
        validation['recommendations'].append("Results should be interpreted cautiously")
    
    # Check for missing outcome variables
    outcome_vars = ['accuracy', 'total_responses', 'responses_per_day']
    for var in outcome_vars:
        if var in df.columns:
            missing_pct = df[var].isna().mean() * 100
            if missing_pct > 10:
                validation['warnings'].append(f"{var} has {missing_pct:.1f}% missing values")
    
    # Check for extreme outliers in continuous variables
    continuous_vars = ['accuracy', 'total_responses', 'responses_per_day', 'days_active']
    for var in continuous_vars:
        if var in df.columns and df[var].notna().any():
            q1 = df[var].quantile(0.25)
            q3 = df[var].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 3 * iqr
            upper_bound = q3 + 3 * iqr
            
            outliers = df[(df[var] < lower_bound) | (df[var] > upper_bound)]
            if len(outliers) > 0:
                pct_outliers = len(outliers) / len(df) * 100
                validation['warnings'].append(
                    f"{var} has {len(outliers)} extreme outliers ({pct_outliers:.1f}%)"
                )
    
    # Check categorical variable distributions
    categorical_vars = ['hospital', 'specialty', 'education_level', 'gender', 'country']
    for var in categorical_vars:
        if var in df.columns:
            value_counts = df[var].value_counts()
            if len(value_counts) > 20:
                validation['warnings'].append(
                    f"{var} has many categories ({len(value_counts)}), consider grouping"
                )
            
            # Check for categories with very few observations
            small_categories = value_counts[value_counts < 5]
            if len(small_categories) > 0:
                validation['warnings'].append(
                    f"{var} has {len(small_categories)} categories with <5 observations"
                )
    
    return validation 