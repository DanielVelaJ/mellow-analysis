# 📊 Dashboard Documentation

## Overview

This dashboard provides comprehensive insights into medical education platform performance using modern visualization techniques and rigorous data validation.

## 🎯 Data Accuracy & Validation

### ✅ Validation Results
- **Zero Critical Issues** - All calculations validated mathematically
- **Zero Warnings** - Data integrity confirmed across all metrics
- **1,762 user responses** across **40 clinical questions**
- **141 unique users** with complete data coverage

### 🔍 Important Data Structure Discovery
- **Question Duplication Identified:** Each question appears with 2 different IDs but identical content
- **100% Duplication Rate:** All 20 unique question texts appear as 40 question IDs
- **Intentional Design:** Per client explanation, needed for exam structure (simultaneous exams)
- **Analysis Updated:** Question difficulty now groups by content, not ID (more reliable!)

### 🔒 Data Quality Assurance
- Time-ordered processing ensures chronological accuracy
- Binary conversion validation: `'CORRECTA'` → `1`, `'INCORRECTA'` → `0`
- Perfect question-answer matching (no orphaned records)
- No impossible accuracy values (all within 0-1 range)
- **Duplication Handling:** All question-based analysis now groups by content for accuracy

---

## 📈 Visualization Components

### 1. 📊 Overview Metrics

**What it shows:** High-level KPIs and platform performance summary

**How it's built:**
```python
stats = {
    'total_responses': len(responses_df),
    'unique_users': responses_df['id_user_hash'].nunique(),
    'overall_accuracy': responses_df['is_correct'].mean(),
    'avg_responses_per_user': total_responses / unique_users
}
```

**Business Value:**
- Executive summary for quick decision making
- Baseline metrics for performance tracking
- User engagement indicators

**Accuracy Notes:**
- Direct counts ensure no double-counting
- Percentages calculated from validated binary data
- Date ranges verified through datetime parsing

---

### 2. 📈 Performance Trends

**What it shows:** Daily accuracy and volume trends over time

**How it's built:**
```python
daily_stats = responses_df.groupby('date').agg({
    'is_correct': ['mean', 'count', 'sum'],
    'id_user_hash': 'nunique'
})
```

**Visualization Method:**
- Dual-axis chart: Accuracy (%) + Response volume
- Time-series line chart with trend analysis
- 7-day moving average for smooth trends

**Business Insights:**
- Learning curve validation (are users improving?)
- Seasonal usage patterns
- Correlation between volume and performance

**Accuracy Considerations:**
- **Time Ordering:** All data sorted by `exam_created_at` before grouping
- **Daily Aggregation:** Groups by date, not timestamp, for clean daily buckets
- **Volume Correlation:** Independent axes prevent visual distortion

---

### 3. 👥 User Engagement Patterns

**What it shows:** Activity distribution across 24-hour periods

**How it's built:**
```python
responses_df['hour'] = responses_df['exam_created_at'].dt.hour
hourly_activity = responses_df.groupby('hour').size()
```

**Visualization Method:**
- Bar chart with time-period color coding
- Peak hour identification and highlighting
- Business hours vs. off-hours analysis

**Business Value:**
- Server optimization and maintenance scheduling
- Content release timing optimization
- User behavior pattern recognition

**Accuracy Notes:**
- **Timezone Consistency:** All timestamps processed uniformly
- **Hour Extraction:** Uses pandas `.dt.hour` for reliable parsing
- **Color Coding:** Morning/Afternoon/Evening/Night based on medical professional schedules

---

### 4. 🎯 Question Difficulty Analysis

**What it shows:** Distribution of question accuracy rates to identify content difficulty

**How it's built (UPDATED for duplication):**
```python
# NOW groups by question CONTENT, not ID
question_stats = full_df.groupby('question').agg({
    'is_correct': ['mean', 'count'],
    'subcategory_name': 'first',
    'id_question': 'nunique'  # Track duplication
})
```

**Duplication-Aware Methodology:**
- **Content-Based Grouping:** Groups by actual question text, not ID
- **Enhanced Sample Size:** ~2x responses per question (from combining duplicate IDs)
- **Minimum Response Threshold:** User-configurable (now default: 20 responses)
- **Difficulty Categories:** <50% (Very Hard), 50-70% (Hard), 70-80% (Moderate), 80-90% (Easy), >90% (Very Easy)
- **Duplication Tracking:** Shows how many IDs each question has

**Educational Value:**
- **More Reliable Estimates:** Larger sample sizes from duplicate combination
- Identifies questions that need better explanations
- Reveals overly easy questions (>95% accuracy)
- Guides content difficulty balancing

**Accuracy Safeguards:**
- **Duplication Handled:** No artificial inflation of question count
- **Sample Size Filter:** Prevents unreliable estimates from low-response questions
- **Range Validation:** All accuracy values confirmed within [0,1]
- **Category Boundaries:** Based on educational research standards

---

### 5. 📚 Performance by Topic

**What it shows:** Accuracy rates across medical categories and subcategories

**How it's built:**
```python
category_stats = full_df.groupby(['category_name', 'subcategory_name']).agg({
    'is_correct': ['mean', 'count', 'sum']
})
```

**Visualization Method:**
- Horizontal bar chart sorted by performance (worst first)
- Color gradient: Red (poor) → Green (excellent)
- Response volume shown for statistical confidence

**Medical Education Insights:**
- Identifies knowledge gaps in specific medical domains
- Prioritizes curriculum improvements
- Guides resource allocation for content development

**Data Integrity:**
- **Perfect Merge:** Zero null values after joining cases and responses
- **Category Coverage:** All responses successfully categorized
- **Volume Weighting:** Shows response counts for confidence assessment

---

### 6. ❌ Common Mistakes Analysis

**What it shows:** Most frequent incorrect answers to identify misconceptions

**How it's built:**
```python
wrong_answers = responses_df[responses_df['is_user_answer_correct'] == 'INCORRECTA']
wrong_counts = Counter(wrong_answers['user_answer'])
```

**Analysis Method:**
- Frequency count of incorrect responses
- Percentage of total mistakes calculation
- Text truncation for readability (50 chars)

**Educational Applications:**
- Reveals systematic knowledge gaps
- Identifies confusing medical terminology
- Guides development of targeted feedback

**Accuracy Measures:**
- **Binary Filter:** Only analyzes confirmed incorrect responses
- **Frequency Validation:** Cross-checked against total error count
- **Percentage Verification:** Sum of top errors vs. total confirmed

## 🔧 Development

### Adding New Visualizations
1. Create new file in `src/mellow_analysis/streamlit/visualizations/`
2. Implement render function with data_loader parameter
3. Add import and function call to `dashboard.py`
4. Include documentation in function docstring

### Data Validation
- All new calculations should be validated in `data_validation.py`
- Include accuracy checks and range validations
- Document assumptions and limitations 