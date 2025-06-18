# 📊 Mellow Analysis Dashboard Documentation

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

---

### 7. 📈 User Learning Progression

**What it shows:** Individual user improvement over time using expanding averages

**How it's built:**
```python
# Critical: Time-ordered processing
responses_df = responses_df.sort_values(['id_user_hash', 'exam_created_at'])

# Calculate expanding mean (cumulative accuracy)
user_data['cumulative_accuracy'] = user_data['is_correct'].expanding().mean()
```

**Mathematical Foundation:**
- **Expanding Mean:** Each point = cumulative average up to that attempt
- **Time Dependency:** Requires chronological ordering for validity
- **Multiple Attempts:** Minimum threshold (default: 15) for meaningful analysis

**Learning Science:**
- Upward trends indicate effective learning
- Flat lines suggest plateau or content difficulty
- Individual vs. aggregate trend comparison

**Statistical Rigor:**
- **Chronological Sorting:** Verified time ordering before calculation
- **Sample Size:** Only users with sufficient attempts (82 users qualify)
- **Range Validation:** All expanding means within [0,1] bounds

---

### 8. 👥 User Performance Segments

**What it shows:** User classification based on accuracy and engagement

**Segmentation Logic:**
```python
def segment_user(accuracy, attempts):
    if accuracy >= 0.8 and attempts >= 20:
        return 'High Performers'      # Skilled + Engaged
    elif accuracy >= 0.8 and attempts < 20:
        return 'Quick Learners'       # Efficient
    elif accuracy < 0.5:
        return 'Struggling Users'     # Need Help
    else:
        return 'Average Learners'     # Typical
```

**Business Applications:**
- Targeted intervention strategies
- Personalized learning path design
- Resource allocation optimization

**Segment Validation:**
- **Complete Coverage:** All 141 users assigned to segments
- **Logical Boundaries:** Thresholds based on educational standards
- **Actionable Insights:** Each segment linked to specific interventions

---

### 9. 🔄 User Retention Analysis

**What it shows:** Platform stickiness and user return patterns

**How it's built:**
```python
# Calculate days since first attempt for each user
user_first_attempt = responses_df.groupby('id_user_hash')['exam_created_at'].min()
responses_with_timeline['days_since_first'] = (
    responses_with_timeline['exam_created_at'] - responses_with_timeline['first_attempt']
).dt.days
```

**Retention Metrics:**
- **Day 0:** First attempt (100% by definition)
- **Day N:** Percentage of users active after N days
- **Cohort Analysis:** User lifecycle understanding

**Platform Health Indicators:**
- Day 1 retention (onboarding effectiveness)
- Day 30 retention (long-term value)
- Average user lifespan

**Calculation Accuracy:**
- **Zero Negative Days:** Verified no temporal inconsistencies
- **Timeline Validation:** All dates properly parsed and calculated
- **Maximum Span:** 160 days confirmed as reasonable

---

## 🔍 Key Data Accuracy Measures

### 1. **Time Ordering Verification**
- All progression analyses sort by timestamp before calculation
- Retention analysis validates chronological consistency
- No negative time intervals found

### 2. **Statistical Validation**
- Accuracy calculations cross-verified manually
- Sample size thresholds prevent unreliable estimates
- Range checks ensure all percentages within [0,1]

### 3. **Data Completeness**
- Perfect join between questions and responses (no orphaned records)
- All user segments account for 100% of users
- Missing data handled explicitly with clear documentation

### 4. **Business Logic Verification**
- Segmentation rules sum to complete user base
- Difficulty categories follow educational standards
- Retention calculations match industry definitions

---

## 🚀 Getting Started

### Running the Dashboard
```bash
# Option 1: Use the launcher
python run_dashboard.py

# Option 2: Direct streamlit command
streamlit run src/mellow_analysis/streamlit/dashboard.py
```

### Data Validation
```bash
# Run comprehensive data validation
poetry run python data_validation.py
```

### Dependencies
- **streamlit**: Interactive dashboard framework
- **plotly**: Advanced charting capabilities
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations

---

## 📋 Dashboard Features

### Interactive Elements
- **Configurable Thresholds:** Adjust minimum response counts for reliability
- **Section Selection:** Toggle analysis sections via sidebar
- **Responsive Design:** Optimized for different screen sizes
- **Export Capabilities:** Download charts and data

### Performance Optimizations
- **Caching:** `@st.cache_data` for data loading and processing
- **Lazy Loading:** Sections render only when selected
- **Efficient Processing:** Vectorized operations throughout

### Quality Assurance
- **Input Validation:** All user inputs validated before processing
- **Error Handling:** Graceful degradation for data issues
- **Documentation:** Comprehensive explanations for each visualization

---

## 📊 Best Practices Implemented

1. **Data Integrity First:** Validation before visualization
2. **Educational Context:** Each chart linked to learning science
3. **Business Relevance:** Actionable insights for decision making
4. **Statistical Rigor:** Appropriate thresholds and confidence measures
5. **User Experience:** Clear explanations and interactive controls
6. **Scalability:** Modular design for easy extension
7. **Documentation:** Comprehensive methodology explanation

## 🎓 **Enhanced Educational Features**

### **📊 Comprehensive Explanatory Tables**
Every visualization now includes detailed tables that break down:
- **Step-by-step calculations** with actual formulas and examples
- **Business interpretation guides** for decision-making
- **Statistical methodology** explanations for transparency
- **Action frameworks** linking insights to concrete next steps

### **🔍 Mathematical Transparency**
- **Expanding Mean Example:** Shows how [1,0,1,1,0] becomes cumulative accuracy progression
- **Aggregation Breakdown:** Explains why we use `mean`, `count`, `first` functions
- **Segmentation Matrix:** 2x2 grid showing accuracy vs. engagement criteria
- **Decision Framework:** If-then logic for executive actions

### **📚 Educational Value**
- **Learning Theory Integration:** Progression analysis based on educational research
- **Statistical Literacy:** Builds understanding of data analysis concepts
- **Business Acumen:** Connects data insights to strategic decisions
- **Quality Assurance:** Shows validation methods and reliability measures

This dashboard represents modern best practices in educational data analysis, combining statistical rigor with practical business insights and comprehensive educational explanations. 