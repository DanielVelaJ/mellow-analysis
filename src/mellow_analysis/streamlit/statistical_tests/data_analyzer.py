"""
Data type analysis and variable detection for statistical tests.
"""

from dataclasses import dataclass
from typing import Dict, List, Union, Any
import pandas as pd
import numpy as np


@dataclass
class VariableInfo:
    """Information about a variable in the dataset."""
    name: str
    display_name: str
    data_type: str  # 'categorical', 'continuous', 'ordinal'
    unique_values: List[Any]
    value_counts: Dict[Any, int]
    min_value: Union[float, None] = None
    max_value: Union[float, None] = None
    mean_value: Union[float, None] = None
    is_suitable_for_grouping: bool = True


class DataTypeAnalyzer:
    """Analyzes dataset to determine variable types and grouping possibilities."""
    
    def __init__(self, min_category_size: int = 5, max_categories: int = 20):
        self.min_category_size = min_category_size
        self.max_categories = max_categories
    
    def analyze_dataset(self, df: pd.DataFrame) -> Dict[str, VariableInfo]:
        """Analyze all variables in the dataset."""
        variables = {}
        
        # Define display names for common medical education variables
        display_names = {
            'hospital': 'Hospital',
            'specialty': 'Medical Specialty', 
            'subspecialty': 'Subspecialty',
            'education_level': 'Education Level',
            'gender': 'Gender',
            'age_range': 'Age Range',
            'country': 'Country',
            'accuracy': 'Accuracy Rate',
            'total_responses': 'Total Responses',
            'responses_per_day': 'Responses per Day',
            'days_active': 'Days Active'
        }
        
        for column in df.columns:
            if column == 'user_id':  # Skip ID columns
                continue
                
            var_info = self._analyze_variable(df, column)
            var_info.display_name = display_names.get(column, column.replace('_', ' ').title())
            variables[column] = var_info
            
        return variables
    
    def _analyze_variable(self, df: pd.DataFrame, column: str) -> VariableInfo:
        """Analyze a single variable."""
        series = df[column].dropna()
        
        if len(series) == 0:
            return VariableInfo(
                name=column,
                display_name=column,
                data_type='categorical',
                unique_values=[],
                value_counts={},
                is_suitable_for_grouping=False
            )
        
        unique_values = series.unique().tolist()
        value_counts = series.value_counts().to_dict()
        
        # Determine data type
        if self._is_continuous(series):
            return VariableInfo(
                name=column,
                display_name=column,
                data_type='continuous',
                unique_values=unique_values,
                value_counts=value_counts,
                min_value=float(series.min()),
                max_value=float(series.max()),
                mean_value=float(series.mean()),
                is_suitable_for_grouping=True
            )
        elif self._is_ordinal(column, unique_values):
            return VariableInfo(
                name=column,
                display_name=column,
                data_type='ordinal',
                unique_values=self._sort_ordinal_values(column, unique_values),
                value_counts=value_counts,
                is_suitable_for_grouping=self._is_suitable_categorical(value_counts)
            )
        else:
            return VariableInfo(
                name=column,
                display_name=column,
                data_type='categorical',
                unique_values=unique_values,
                value_counts=value_counts,
                is_suitable_for_grouping=self._is_suitable_categorical(value_counts)
            )
    
    def _is_continuous(self, series: pd.Series) -> bool:
        """Check if a variable should be treated as continuous."""
        if not pd.api.types.is_numeric_dtype(series):
            return False
        
        unique_count = series.nunique()
        total_count = len(series)
        
        # If more than 10 unique values or more than 50% of values are unique
        return unique_count > 10 or (unique_count / total_count) > 0.5
    
    def _is_ordinal(self, column: str, unique_values: List) -> bool:
        """Check if a variable should be treated as ordinal."""
        ordinal_patterns = {
            'age_range': True,
            'education_level': True,
            'experience_level': True
        }
        
        if column in ordinal_patterns:
            return True
            
        # Check for range patterns like "25-30", "31-40"
        if isinstance(unique_values[0], str):
            range_pattern = any('-' in str(val) for val in unique_values if val is not None)
            return range_pattern
            
        return False
    
    def _sort_ordinal_values(self, column: str, values: List) -> List:
        """Sort ordinal values in logical order."""
        if column == 'age_range':
            # Sort age ranges by their starting number
            def age_sort_key(val):
                if pd.isna(val):
                    return 999
                try:
                    return int(str(val).split('-')[0])
                except:
                    return 999
            return sorted(values, key=age_sort_key)
        
        elif column == 'education_level':
            # Sort by education hierarchy
            hierarchy = ['Estudiante', 'Residente', 'Especialista', 'Subespecialista']
            def edu_sort_key(val):
                if pd.isna(val):
                    return 999
                for i, level in enumerate(hierarchy):
                    if level in str(val):
                        return i
                return 999
            return sorted(values, key=edu_sort_key)
        
        return sorted(values)
    
    def _is_suitable_categorical(self, value_counts: Dict) -> bool:
        """Check if categorical variable is suitable for grouping."""
        if len(value_counts) < 2:  # Need at least 2 categories
            return False
        if len(value_counts) > self.max_categories:  # Too many categories
            return False
        
        # Check if largest categories have enough samples
        sorted_counts = sorted(value_counts.values(), reverse=True)
        return sorted_counts[0] >= self.min_category_size and sorted_counts[1] >= self.min_category_size
    
    def get_grouping_variables(self, variables: Dict[str, VariableInfo]) -> Dict[str, VariableInfo]:
        """Get variables suitable for grouping."""
        return {name: info for name, info in variables.items() if info.is_suitable_for_grouping}
    
    def get_outcome_variables(self, variables: Dict[str, VariableInfo]) -> Dict[str, VariableInfo]:
        """Get variables suitable as outcome measures."""
        outcome_candidates = {
            'accuracy', 'total_responses', 'responses_per_day', 
            'days_active', 'correct_responses'
        }
        
        return {
            name: info for name, info in variables.items() 
            if name in outcome_candidates and info.data_type == 'continuous'
        } 