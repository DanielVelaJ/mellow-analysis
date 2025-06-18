#!/usr/bin/env python3
"""
Quick test script to verify the statistical testing module works correctly.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from mellow_analysis.data.loader import data_loader
from mellow_analysis.streamlit.statistical_tests.utils import prepare_user_level_data, get_available_grouping_variables

def test_statistical_module():
    """Test the statistical module functionality."""
    
    print("🧪 Testing Statistical Module...")
    print("=" * 50)
    
    try:
        # Test data loading
        print("\n1. Testing data preparation...")
        user_df = prepare_user_level_data(data_loader)
        print(f"✅ User-level data prepared: {len(user_df)} users")
        print(f"   Columns: {list(user_df.columns)}")
        
        # Test grouping variables
        print("\n2. Testing grouping variables...")
        grouping_vars = get_available_grouping_variables(user_df)
        print(f"✅ Available grouping variables: {list(grouping_vars.keys())}")
        
        # Show sample data
        print("\n3. Sample user data:")
        display_cols = ['accuracy', 'total_responses', 'education_level', 'gender', 'country']
        available_cols = [col for col in display_cols if col in user_df.columns]
        print(user_df[available_cols].head())
        
        # Test basic statistics
        print("\n4. Basic statistics:")
        print(f"   Mean accuracy: {user_df['accuracy'].mean():.3f}")
        print(f"   Std accuracy: {user_df['accuracy'].std():.3f}")
        print(f"   Users per education level:")
        if 'education_level' in user_df.columns:
            education_counts = user_df['education_level'].value_counts()
            for level, count in education_counts.items():
                print(f"     {level}: {count}")
        
        print("\n✅ All tests passed! Statistical module is ready to use.")
        print("\n🚀 Run the dashboard with: python run_dashboard.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_statistical_module() 