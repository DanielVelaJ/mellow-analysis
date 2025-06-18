"""
Group building functionality for flexible statistical comparisons.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import streamlit as st
from .data_analyzer import VariableInfo


@dataclass
class GroupDefinition:
    """Defines a group for statistical comparison."""
    name: str
    categorical_filters: Dict[str, List[Any]] = field(default_factory=dict)
    continuous_filters: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    size: int = 0
    description: str = ""
    
    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all filters and return filtered dataframe."""
        mask = pd.Series(True, index=df.index)
        
        # Apply categorical filters
        for column, values in self.categorical_filters.items():
            if values:  # Only apply if values are selected
                mask &= df[column].isin(values)
        
        # Apply continuous filters  
        for column, (min_val, max_val) in self.continuous_filters.items():
            mask &= (df[column] >= min_val) & (df[column] <= max_val)
        
        return df[mask]
    
    def validate(self, df: pd.DataFrame, min_size: int = 10) -> Dict[str, Any]:
        """Validate the group definition."""
        filtered_df = self.apply_filters(df)
        self.size = len(filtered_df)
        
        return {
            'is_valid': self.size >= min_size,
            'size': self.size,
            'warnings': self._get_warnings(min_size)
        }
    
    def _get_warnings(self, min_size: int) -> List[str]:
        """Get validation warnings."""
        warnings = []
        
        if self.size < min_size:
            warnings.append(f"Group size ({self.size}) is below minimum ({min_size})")
        
        if not self.categorical_filters and not self.continuous_filters:
            warnings.append("No filters defined - group will include all users")
        
        return warnings
    
    def generate_description(self, variables: Dict[str, VariableInfo]) -> str:
        """Generate human-readable description of the group."""
        descriptions = []
        
        for var_name, values in self.categorical_filters.items():
            if values:
                var_info = variables.get(var_name)
                display_name = var_info.display_name if var_info else var_name
                if len(values) == 1:
                    descriptions.append(f"{display_name}: {values[0]}")
                else:
                    descriptions.append(f"{display_name}: {', '.join(map(str, values))}")
        
        for var_name, (min_val, max_val) in self.continuous_filters.items():
            var_info = variables.get(var_name)
            display_name = var_info.display_name if var_info else var_name
            descriptions.append(f"{display_name}: {min_val:.2f} - {max_val:.2f}")
        
        self.description = "; ".join(descriptions) if descriptions else "All users"
        return self.description


class GroupBuilder:
    """Interactive group builder for Streamlit interface."""
    
    def __init__(self, variables: Dict[str, VariableInfo]):
        self.variables = variables
        self.grouping_vars = {
            name: info for name, info in variables.items() 
            if info.is_suitable_for_grouping
        }
    
    def render_group_builder(self, group_name: str, key_prefix: str) -> GroupDefinition:
        """Render interactive group builder UI."""
        group_def = GroupDefinition(name=group_name)
        
        # Categorical variable selection
        categorical_vars = {
            name: info for name, info in self.grouping_vars.items() 
            if info.data_type in ['categorical', 'ordinal']
        }
        
        if categorical_vars:
            st.markdown("**Categorical Variables**")
            for var_name, var_info in categorical_vars.items():
                selected_values = st.multiselect(
                    f"{var_info.display_name}",
                    options=var_info.unique_values,
                    key=f"{key_prefix}_{var_name}",
                    help=f"Select one or more {var_info.display_name.lower()} values"
                )
                if selected_values:
                    group_def.categorical_filters[var_name] = selected_values
        
        # Continuous variable selection
        continuous_vars = {
            name: info for name, info in self.grouping_vars.items() 
            if info.data_type == 'continuous'
        }
        
        if continuous_vars:
            st.markdown("**Continuous Variables**")
            for var_name, var_info in continuous_vars.items():
                col1, col2 = st.columns(2)
                
                with col1:
                    min_val = st.number_input(
                        f"{var_info.display_name} (min)",
                        min_value=var_info.min_value,
                        max_value=var_info.max_value,
                        value=var_info.min_value,
                        key=f"{key_prefix}_{var_name}_min"
                    )
                
                with col2:
                    max_val = st.number_input(
                        f"{var_info.display_name} (max)",
                        min_value=var_info.min_value,
                        max_value=var_info.max_value,
                        value=var_info.max_value,
                        key=f"{key_prefix}_{var_name}_max"
                    )
                
                if min_val < max_val:
                    group_def.continuous_filters[var_name] = (min_val, max_val)
                else:
                    st.error(f"Invalid range for {var_info.display_name}: min must be less than max")
        
        return group_def
    
    def render_group_preview(self, group_def: GroupDefinition, df: pd.DataFrame, 
                           outcome_var: str = None) -> None:
        """Render compact group statistics."""
        validation = group_def.validate(df)
        
        # Always show basic stats if we have users and outcome variable
        if validation['size'] > 0 and outcome_var:
            self._render_compact_stats(group_def, df, outcome_var)
        elif validation['size'] == 0:
            st.info("👆 Select filters to define this group")
        
        # Show warnings compactly
        for warning in validation['warnings']:
            st.caption(f"⚠️ {warning}")
    
    def _render_compact_stats(self, group_def: GroupDefinition, df: pd.DataFrame, 
                            outcome_var: str) -> None:
        """Render essential group statistics in a natural, conversational format."""
        try:
            # Get group data
            group_data = group_def.apply_filters(df)
            if outcome_var not in group_data.columns:
                return
                
            outcome_values = group_data[outcome_var].dropna()
            if len(outcome_values) < 3:
                st.warning(f"⚠️ Only {len(outcome_values)} values (need ≥3 for analysis)")
                return
            
            # Natural language summary instead of clinical metrics
            mean_val = outcome_values.mean()
            std_val = outcome_values.std()
            count = len(outcome_values)
            
            # Create contextual description
            description = f"**{count:,} users** with average score of **{mean_val:.2f}** (spread: ±{std_val:.2f})"
            st.markdown(description)
            
            # Single normality indicator with natural language
            from scipy import stats
            try:
                _, shapiro_p = stats.shapiro(outcome_values)
                is_normal = shapiro_p > 0.05
                
                if is_normal:
                    st.caption("✅ Data follows normal distribution (good for t-tests)")
                else:
                    st.caption("⚠️ Data is non-normal (will use rank-based test)")
            except:
                st.caption("🔍 Cannot assess data distribution")
            
        except Exception as e:
            st.caption(f"Error calculating statistics: {str(e)}")
    
    def validate_groups(self, group_a: GroupDefinition, group_b: GroupDefinition, 
                       df: pd.DataFrame) -> Dict[str, Any]:
        """Validate that two groups are suitable for comparison."""
        group_a_data = group_a.apply_filters(df)
        group_b_data = group_b.apply_filters(df)
        
        # Check for overlap
        overlap_users = set(group_a_data.index) & set(group_b_data.index)
        has_overlap = len(overlap_users) > 0
        
        # Calculate balance ratio
        size_ratio = min(len(group_a_data), len(group_b_data)) / max(len(group_a_data), len(group_b_data)) if max(len(group_a_data), len(group_b_data)) > 0 else 0
        
        validation = {
            'group_a_size': len(group_a_data),
            'group_b_size': len(group_b_data),
            'has_overlap': has_overlap,
            'overlap_count': len(overlap_users),
            'size_ratio': size_ratio,
            'is_balanced': size_ratio >= 0.3,  # Groups shouldn't differ by more than 3:1
            'total_users': len(group_a_data) + len(group_b_data) - len(overlap_users)
        }
        
        validation['is_valid'] = (
            validation['group_a_size'] >= 10 and 
            validation['group_b_size'] >= 10 and
            not validation['has_overlap']
        )
        
        return validation 