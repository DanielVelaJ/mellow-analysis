"""
Data loading and preprocessing utilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import streamlit as st


class DataLoader:
    """Handles loading and preprocessing of Mellow Analysis datasets."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the DataLoader.
        
        Args:
            data_dir: Path to the directory containing the CSV files
        """
        self.data_dir = Path(data_dir)
        self._cases_df = None
        self._responses_df = None
        self._full_df = None
    
    @st.cache_data
    def load_cases(_self) -> pd.DataFrame:
        """
        Load the cases dataset.
        
        Returns:
            DataFrame containing clinical cases and questions
        """
        if _self._cases_df is None:
            cases_path = _self.data_dir / "rc_invokana_cases.csv"
            _self._cases_df = pd.read_csv(cases_path)
        return _self._cases_df.copy()
    
    @st.cache_data
    def load_responses(_self) -> pd.DataFrame:
        """
        Load the user responses dataset.
        
        Returns:
            DataFrame containing user responses and demographics
        """
        if _self._responses_df is None:
            responses_path = _self.data_dir / "rc_invokana_users_responses_nopersonal_hash.csv"
            _self._responses_df = pd.read_csv(responses_path)
            
            # Add preprocessing
            _self._responses_df['exam_created_at'] = pd.to_datetime(_self._responses_df['exam_created_at'])
            _self._responses_df['user_created_at'] = pd.to_datetime(_self._responses_df['user_created_at'])
            _self._responses_df['is_correct'] = (_self._responses_df['is_user_answer_correct'] == 'CORRECTA').astype(int)
            _self._responses_df['hour'] = _self._responses_df['exam_created_at'].dt.hour
            _self._responses_df['date'] = _self._responses_df['exam_created_at'].dt.date
            
        return _self._responses_df.copy()
    
    @st.cache_data
    def load_full_dataset(_self) -> pd.DataFrame:
        """
        Load and merge both datasets.
        
        Returns:
            Combined DataFrame with cases and responses
        """
        if _self._full_df is None:
            cases_df = _self.load_cases()
            responses_df = _self.load_responses()
            
            _self._full_df = responses_df.merge(
                cases_df[['id_question', 'category_name', 'subcategory_name', 'question', 
                         'option1_correct', 'option2_incorrect', 'option3_incorrect', 'option4_incorrect']], 
                on='id_question', 
                how='left'
            )
        
        return _self._full_df.copy()
    
    def get_summary_stats(self) -> dict:
        """
        Get summary statistics for the dashboard.
        
        Returns:
            Dictionary containing key metrics
        """
        responses_df = self.load_responses()
        cases_df = self.load_cases()
        
        # Calculate question duplication metrics
        unique_question_texts = cases_df['question'].nunique()
        question_duplication = cases_df.groupby('question')['id_question'].nunique()
        duplicated_questions = (question_duplication > 1).sum()
        
        return {
            'total_responses': len(responses_df),
            'unique_users': responses_df['id_user_hash'].nunique(),
            'unique_questions': responses_df['id_question'].nunique(),
            'unique_question_texts': unique_question_texts,
            'duplicated_questions': duplicated_questions,
            'duplication_rate': duplicated_questions / unique_question_texts if unique_question_texts > 0 else 0,
            'unique_cases': cases_df['id_case'].nunique(),
            'overall_accuracy': responses_df['is_correct'].mean(),
            'date_range': {
                'start': responses_df['exam_created_at'].min(),
                'end': responses_df['exam_created_at'].max()
            },
            'countries': responses_df['country_user_made_the_exam'].nunique(),
            'categories': cases_df['category_name'].nunique(),
            'subcategories': cases_df['subcategory_name'].nunique()
        }


# Global instance for easy access
data_loader = DataLoader() 