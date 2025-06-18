"""
Statistical test execution and analysis engine.
"""

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .group_builder import GroupDefinition


@dataclass
class TestResult:
    """Results from a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    effect_size: float
    effect_magnitude: str
    interpretation: str
    assumptions: Dict[str, Any]
    sample_sizes: Dict[str, int]


class StatisticalTestEngine:
    """Handles statistical test execution and result interpretation."""
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
    
    def compare_groups(self, group_a: GroupDefinition, group_b: GroupDefinition, 
                      df: pd.DataFrame, outcome_variable: str) -> TestResult:
        """Compare two groups on a specified outcome variable."""
        # Extract data for each group
        data_a = self._extract_outcome_data(group_a, df, outcome_variable)
        data_b = self._extract_outcome_data(group_b, df, outcome_variable)
        
        # Check assumptions
        assumptions = self._check_assumptions(data_a, data_b, group_a.name, group_b.name)
        
        # Select and execute appropriate test
        test_result = self._execute_test(data_a, data_b, assumptions)
        
        # Calculate effect size
        effect_size, effect_magnitude = self._calculate_effect_size(data_a, data_b)
        
        # Generate interpretation
        interpretation = self._interpret_results(test_result['p_value'], effect_magnitude)
        
        return TestResult(
            test_name=test_result['test_name'],
            statistic=test_result['statistic'],
            p_value=test_result['p_value'],
            effect_size=effect_size,
            effect_magnitude=effect_magnitude,
            interpretation=interpretation,
            assumptions=assumptions,
            sample_sizes={group_a.name: len(data_a), group_b.name: len(data_b)}
        )
    
    def _extract_outcome_data(self, group_def: GroupDefinition, df: pd.DataFrame, 
                             outcome_variable: str) -> pd.Series:
        """Extract outcome data for a group."""
        filtered_df = group_def.apply_filters(df)
        return filtered_df[outcome_variable].dropna()
    
    def _check_assumptions(self, data_a: pd.Series, data_b: pd.Series, 
                          name_a: str, name_b: str) -> Dict[str, Any]:
        """Check statistical test assumptions."""
        assumptions = {}
        
        # Normality tests
        for data, name in [(data_a, name_a), (data_b, name_b)]:
            if len(data) >= 3:
                stat, p = stats.shapiro(data)
                assumptions[f'{name}_normality'] = {
                    'statistic': stat,
                    'p_value': p,
                    'is_normal': p > 0.05,
                    'interpretation': f"{name}: {'Normal' if p > 0.05 else 'Non-normal'} (p={p:.3f})"
                }
            else:
                assumptions[f'{name}_normality'] = {
                    'statistic': None,
                    'p_value': None,
                    'is_normal': False,
                    'interpretation': f"{name}: Insufficient data for normality test"
                }
        
        # Equal variances test
        if len(data_a) >= 2 and len(data_b) >= 2:
            stat_var, p_var = stats.levene(data_a, data_b)
            assumptions['equal_variances'] = {
                'statistic': stat_var,
                'p_value': p_var,
                'equal_variances': p_var > 0.05,
                'interpretation': f"{'Equal' if p_var > 0.05 else 'Unequal'} variances (p={p_var:.3f})"
            }
        else:
            assumptions['equal_variances'] = {
                'statistic': None,
                'p_value': None,
                'equal_variances': False,
                'interpretation': "Insufficient data for variance test"
            }
        
        return assumptions
    
    def _execute_test(self, data_a: pd.Series, data_b: pd.Series, 
                     assumptions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate statistical test."""
        # Get normality results
        norm_a = assumptions.get(f'{data_a.name}_normality', {}).get('is_normal', False)
        norm_b = assumptions.get(f'{data_b.name}_normality', {}).get('is_normal', False)
        equal_var = assumptions.get('equal_variances', {}).get('equal_variances', False)
        
        both_normal = norm_a and norm_b
        
        if both_normal and equal_var:
            statistic, p_value = stats.ttest_ind(data_a, data_b, equal_var=True)
            test_name = "Student's t-test"
        elif both_normal and not equal_var:
            statistic, p_value = stats.ttest_ind(data_a, data_b, equal_var=False)
            test_name = "Welch's t-test"
        else:
            statistic, p_value = stats.mannwhitneyu(data_a, data_b, alternative='two-sided')
            test_name = "Mann-Whitney U test"
        
        return {'test_name': test_name, 'statistic': statistic, 'p_value': p_value}
    
    def _calculate_effect_size(self, data_a: pd.Series, data_b: pd.Series) -> Tuple[float, str]:
        """Calculate Cohen's d effect size."""
        if len(data_a) < 2 or len(data_b) < 2:
            return 0.0, "Cannot calculate"
        
        n1, n2 = len(data_a), len(data_b)
        mean1, mean2 = data_a.mean(), data_b.mean()
        var1, var2 = data_a.var(ddof=1), data_b.var(ddof=1)
        
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0, "No variation"
        
        cohens_d = (mean1 - mean2) / pooled_std
        
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            magnitude = "Negligible"
        elif abs_d < 0.5:
            magnitude = "Small"
        elif abs_d < 0.8:
            magnitude = "Medium"
        else:
            magnitude = "Large"
        
        return cohens_d, magnitude
    
    def _interpret_results(self, p_value: float, effect_magnitude: str) -> str:
        """Generate interpretation of statistical results."""
        if p_value < 0.001:
            significance = "very strong evidence of a difference"
        elif p_value < 0.01:
            significance = "strong evidence of a difference"
        elif p_value < self.alpha:
            significance = "moderate evidence of a difference"
        elif p_value < 0.1:
            significance = "weak evidence of a difference"
        else:
            significance = "no significant evidence of a difference"
        
        if effect_magnitude.lower() in ['large', 'medium']:
            practical = "with meaningful practical significance"
        elif effect_magnitude.lower() == 'small':
            practical = "with limited practical significance"
        else:
            practical = "with negligible practical significance"
        
        return f"Results show {significance} (p={p_value:.4f}) {practical} (effect size: {effect_magnitude.lower()})."
    
    def create_comparison_visualizations(self, group_a: GroupDefinition, group_b: GroupDefinition,
                                       df: pd.DataFrame, outcome_variable: str, 
                                       outcome_display_name: str) -> go.Figure:
        """Create comprehensive comparison visualizations."""
        data_a = self._extract_outcome_data(group_a, df, outcome_variable)
        data_b = self._extract_outcome_data(group_b, df, outcome_variable)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Distribution Comparison', 'Box Plot Comparison', 
                          'Statistical Summary', 'Effect Size Visualization'],
            specs=[[{'type': 'histogram'}, {'type': 'box'}],
                   [{'type': 'table'}, {'type': 'bar'}]]
        )
        
        # Histograms
        fig.add_trace(go.Histogram(x=data_a, name=group_a.name, opacity=0.6, nbinsx=20), row=1, col=1)
        fig.add_trace(go.Histogram(x=data_b, name=group_b.name, opacity=0.6, nbinsx=20), row=1, col=1)
        
        # Box plots
        fig.add_trace(go.Box(y=data_a, name=group_a.name, showlegend=False), row=1, col=2)
        fig.add_trace(go.Box(y=data_b, name=group_b.name, showlegend=False), row=1, col=2)
        
        # Summary table
        summary_stats = pd.DataFrame({
            'Statistic': ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max'],
            group_a.name: [len(data_a), f"{data_a.mean():.3f}", f"{data_a.median():.3f}",
                          f"{data_a.std():.3f}", f"{data_a.min():.3f}", f"{data_a.max():.3f}"],
            group_b.name: [len(data_b), f"{data_b.mean():.3f}", f"{data_b.median():.3f}",
                          f"{data_b.std():.3f}", f"{data_b.min():.3f}", f"{data_b.max():.3f}"]
        })
        
        fig.add_trace(go.Table(
            header=dict(values=list(summary_stats.columns)),
            cells=dict(values=[summary_stats[col] for col in summary_stats.columns])
        ), row=2, col=1)
        
        # Effect size
        effect_size, _ = self._calculate_effect_size(data_a, data_b)
        fig.add_trace(go.Bar(
            x=['Effect Size (Cohen\'s d)'], y=[abs(effect_size)], 
            name='Effect Size', showlegend=False
        ), row=2, col=2)
        
        fig.update_layout(height=800, title=f"{outcome_display_name}: {group_a.name} vs {group_b.name}")
        return fig 