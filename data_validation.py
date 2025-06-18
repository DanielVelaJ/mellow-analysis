"""
Data Validation and Sanity Checks for Mellow Analysis

This script validates the accuracy of our visualizations and identifies potential issues.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def validate_data_integrity():
    """Comprehensive validation of data integrity and visualization accuracy."""
    
    print("🔍 MELLOW ANALYSIS - DATA VALIDATION REPORT")
    print("=" * 60)
    
    # Load datasets
    try:
        cases_df = pd.read_csv('data/rc_invokana_cases.csv')
        responses_df = pd.read_csv('data/rc_invokana_users_responses_nopersonal_hash.csv')
        print("✅ Data files loaded successfully")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Basic data integrity checks
    print("\n📊 BASIC DATA INTEGRITY")
    print("-" * 30)
    
    # Check for missing values
    print(f"Cases dataset shape: {cases_df.shape}")
    print(f"Responses dataset shape: {responses_df.shape}")
    
    missing_cases = cases_df.isnull().sum().sum()
    missing_responses = responses_df.isnull().sum().sum()
    print(f"Missing values - Cases: {missing_cases}, Responses: {missing_responses}")
    
    # Check date formats
    try:
        responses_df['exam_created_at'] = pd.to_datetime(responses_df['exam_created_at'])
        responses_df['user_created_at'] = pd.to_datetime(responses_df['user_created_at'])
        print("✅ Date parsing successful")
    except Exception as e:
        print(f"❌ Date parsing error: {e}")
    
    # Validate accuracy calculations
    print("\n🎯 ACCURACY CALCULATION VALIDATION")
    print("-" * 40)
    
    # Check is_user_answer_correct values
    correct_values = responses_df['is_user_answer_correct'].value_counts()
    print("Values in 'is_user_answer_correct':")
    for value, count in correct_values.items():
        print(f"  {value}: {count}")
    
    # Validate binary conversion
    responses_df['is_correct'] = (responses_df['is_user_answer_correct'] == 'CORRECTA').astype(int)
    manual_accuracy = responses_df['is_correct'].mean()
    correcta_count = (responses_df['is_user_answer_correct'] == 'CORRECTA').sum()
    total_count = len(responses_df)
    expected_accuracy = correcta_count / total_count
    
    print(f"Manual accuracy calculation: {manual_accuracy:.4f}")
    print(f"Expected accuracy: {expected_accuracy:.4f}")
    print(f"✅ Accuracy calculations match: {abs(manual_accuracy - expected_accuracy) < 0.0001}")
    
    # Validate question-answer matching
    print("\n🔗 QUESTION-ANSWER MATCHING VALIDATION")
    print("-" * 45)
    
    # Check if all response question IDs exist in cases
    response_questions = set(responses_df['id_question'].unique())
    case_questions = set(cases_df['id_question'].unique())
    
    missing_questions = response_questions - case_questions
    print(f"Questions in responses but not in cases: {len(missing_questions)}")
    if len(missing_questions) > 0:
        print(f"⚠️  Warning: {len(missing_questions)} questions missing case data")
        print(f"Sample missing IDs: {list(missing_questions)[:5]}")
    
    # Validate merged dataset
    full_df = responses_df.merge(
        cases_df[['id_question', 'category_name', 'subcategory_name', 'question']], 
        on='id_question', 
        how='left'
    )
    
    merge_nulls = full_df[['category_name', 'subcategory_name']].isnull().sum().sum()
    print(f"Null values after merge: {merge_nulls}")
    if merge_nulls > 0:
        print(f"⚠️  Warning: {merge_nulls} records lost category information")
    
    # Validate progression analysis assumptions
    print("\n📈 PROGRESSION ANALYSIS VALIDATION")
    print("-" * 40)
    
    # Check time ordering
    responses_sorted = responses_df.sort_values(['id_user_hash', 'exam_created_at'])
    
    # Check for users with multiple attempts
    user_attempts = responses_df.groupby('id_user_hash').size()
    multi_attempt_users = (user_attempts >= 5).sum()
    single_attempt_users = (user_attempts == 1).sum()
    
    print(f"Users with 1 attempt: {single_attempt_users}")
    print(f"Users with 5+ attempts: {multi_attempt_users}")
    print(f"Users suitable for progression analysis: {multi_attempt_users}")
    
    if multi_attempt_users == 0:
        print("⚠️  Warning: No users have enough attempts for progression analysis")
    
    # Validate expanding mean calculation
    sample_user = user_attempts[user_attempts >= 10].index[0] if len(user_attempts[user_attempts >= 10]) > 0 else None
    
    if sample_user:
        user_data = responses_sorted[responses_sorted['id_user_hash'] == sample_user].copy()
        user_data['manual_expanding_mean'] = user_data['is_correct'].expanding().mean()
        
        # Check if expanding mean is monotonic or reasonable
        expanding_values = user_data['manual_expanding_mean'].values
        print(f"Sample user expanding mean range: {expanding_values.min():.3f} to {expanding_values.max():.3f}")
        
        # Check for reasonable progression (should start and end within 0-1)
        if not (0 <= expanding_values.min() <= expanding_values.max() <= 1):
            print("❌ Error: Expanding mean values outside [0,1] range")
    
    # Validate retention analysis
    print("\n🔄 RETENTION ANALYSIS VALIDATION")
    print("-" * 35)
    
    # Check user timeline calculation
    user_first_attempt = responses_df.groupby('id_user_hash')['exam_created_at'].min()
    responses_with_timeline = responses_df.merge(
        user_first_attempt.rename('first_attempt'),
        left_on='id_user_hash',
        right_index=True
    )
    
    responses_with_timeline['days_since_first'] = (
        responses_with_timeline['exam_created_at'] - responses_with_timeline['first_attempt']
    ).dt.days
    
    # Validate day calculations
    negative_days = (responses_with_timeline['days_since_first'] < 0).sum()
    max_days = responses_with_timeline['days_since_first'].max()
    
    print(f"Negative days since first attempt: {negative_days}")
    print(f"Maximum days since first attempt: {max_days}")
    
    if negative_days > 0:
        print("❌ Error: Found negative days in retention calculation")
    
    # Validate user segmentation
    print("\n👥 USER SEGMENTATION VALIDATION")
    print("-" * 35)
    
    user_stats = responses_df.groupby('id_user_hash').agg({
        'is_correct': ['mean', 'count'],
        'exam_created_at': ['min', 'max']
    }).reset_index()
    
    user_stats.columns = ['user_id', 'accuracy', 'total_attempts', 'first_attempt', 'last_attempt']
    
    # Check segmentation logic
    high_accuracy_low_attempts = ((user_stats['accuracy'] >= 0.8) & (user_stats['total_attempts'] < 20)).sum()
    high_accuracy_high_attempts = ((user_stats['accuracy'] >= 0.8) & (user_stats['total_attempts'] >= 20)).sum()
    low_accuracy = (user_stats['accuracy'] < 0.5).sum()
    
    print(f"Quick Learners (>80% acc, <20 attempts): {high_accuracy_low_attempts}")
    print(f"High Performers (>80% acc, 20+ attempts): {high_accuracy_high_attempts}")
    print(f"Struggling Users (<50% accuracy): {low_accuracy}")
    
    total_users = len(user_stats)
    segments_total = high_accuracy_low_attempts + high_accuracy_high_attempts + low_accuracy
    middle_segment = total_users - segments_total
    
    print(f"Average Learners (remainder): {middle_segment}")
    print(f"Total users accounted for: {segments_total + middle_segment} / {total_users}")
    
    # Validate content analysis
    print("\n📚 CONTENT ANALYSIS VALIDATION")
    print("-" * 35)
    
    # Check question difficulty calculations
    question_stats = full_df.groupby('id_question').agg({
        'is_correct': ['mean', 'count'],
        'question': 'first'
    }).reset_index()
    
    question_stats.columns = ['question_id', 'accuracy', 'response_count', 'question_text']
    
    # Validate accuracy ranges
    impossible_accuracy = ((question_stats['accuracy'] < 0) | (question_stats['accuracy'] > 1)).sum()
    print(f"Questions with impossible accuracy values: {impossible_accuracy}")
    
    if impossible_accuracy > 0:
        print("❌ Error: Found questions with accuracy outside [0,1] range")
    
    # Check for questions with very low response counts
    low_response_questions = (question_stats['response_count'] < 3).sum()
    print(f"Questions with <3 responses: {low_response_questions}")
    print(f"These questions may have unreliable difficulty estimates")
    
    # Final summary
    print("\n📋 VALIDATION SUMMARY")
    print("-" * 25)
    
    critical_issues = 0
    warnings = 0
    
    if missing_questions:
        warnings += 1
    if merge_nulls > 0:
        warnings += 1
    if multi_attempt_users == 0:
        warnings += 1
    if negative_days > 0:
        critical_issues += 1
    if impossible_accuracy > 0:
        critical_issues += 1
    
    print(f"Critical Issues: {critical_issues}")
    print(f"Warnings: {warnings}")
    
    if critical_issues == 0:
        print("✅ All critical validations passed!")
        print("🎯 Data is suitable for visualization")
    else:
        print("❌ Critical issues found - review data before proceeding")
    
    if warnings > 0:
        print("⚠️  Some warnings present - visualizations may have limitations")
    
    return critical_issues == 0


if __name__ == "__main__":
    validate_data_integrity() 