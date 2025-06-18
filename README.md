# 📊 Mellow Medical Education Analytics

A comprehensive data analysis dashboard for medical education platform performance, built with modern best practices and rigorous data validation.

## 🚀 Quick Start

### Running the Dashboard
```bash
# Option 1: Use the launcher script
python run_dashboard.py

# Option 2: Direct streamlit command  
poetry run streamlit run src/mellow_analysis/streamlit/dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Prerequisites
```bash
# Install dependencies
poetry install

# Or if using pip
pip install streamlit plotly pandas numpy
```

## 📈 Dashboard Features

### 🎯 **Comprehensive Analytics**
- **Overview Metrics:** KPIs, user engagement, platform performance
- **Performance Trends:** Daily accuracy and volume trends over time
- **User Engagement:** Activity patterns and peak usage analysis
- **Content Analysis:** Question difficulty and topic performance
- **User Progression:** Individual learning curves and improvement tracking
- **User Segmentation:** Performance-based user classification
- **Retention Analysis:** Platform stickiness and user lifecycle

### 🔒 **Data Quality Assurance**
- **Zero Critical Issues:** All calculations mathematically validated
- **Perfect Data Integrity:** No orphaned records or impossible values
- **Time-Ordered Processing:** Chronological accuracy for progression analysis
- **Statistical Rigor:** Minimum thresholds and confidence measures

### 🎨 **Modern UI/UX**
- **Interactive Controls:** Configurable thresholds and filters
- **Responsive Design:** Optimized for different screen sizes
- **Professional Styling:** Clean, modern interface with business-ready charts
- **Comprehensive Documentation:** Each chart includes methodology explanations

## 📁 Project Structure

```
mellow-analysis/
├── src/mellow_analysis/              # Main package
│   ├── data/                         # Data loading and processing
│   │   ├── __init__.py
│   │   └── loader.py                 # Centralized data loader with caching
│   ├── streamlit/                    # Dashboard application
│   │   ├── __init__.py
│   │   ├── dashboard.py              # Main dashboard app
│   │   └── visualizations/           # Individual visualization components
│   │       ├── __init__.py
│   │       ├── overview_metrics.py   # KPIs and summary statistics
│   │       ├── content_analysis.py   # Question difficulty and topic performance
│   │       └── user_progression.py   # Learning progression and user segments
│   └── utils/                        # Utility functions
├── data/                             # CSV data files
│   ├── rc_invokana_cases.csv         # Clinical questions and answers
│   └── rc_invokana_users_responses_nopersonal_hash.csv  # User responses
├── run_dashboard.py                  # Dashboard launcher script
├── data_validation.py               # Comprehensive data validation
├── DASHBOARD_DOCUMENTATION.md       # Detailed visualization documentation
├── pyproject.toml                   # Poetry configuration
└── README.md                        # This file
```

## 🔍 Data Validation

Run comprehensive data validation to ensure accuracy:

```bash
poetry run python data_validation.py
```

**Validation Results:**
- ✅ **1,762 user responses** across **40 clinical questions**
- ✅ **141 unique users** with complete data coverage
- ✅ **Zero critical issues** - all calculations validated
- ✅ **Perfect data integrity** - no missing or invalid records

## 📊 Key Visualizations

### 1. **Performance Trends**
- **What:** Daily accuracy and volume trends over time
- **Why:** Identifies learning patterns and platform usage
- **How:** Time-series analysis with dual-axis charting

### 2. **User Progression Analysis**
- **What:** Individual learning curves using expanding averages
- **Why:** Validates platform effectiveness for learning
- **How:** Chronologically sorted cumulative accuracy calculation

### 3. **Content Difficulty Analysis**
- **What:** Distribution of question accuracy rates
- **Why:** Identifies content that needs improvement
- **How:** Statistical grouping with minimum response thresholds

### 4. **User Segmentation**
- **What:** Performance-based user classification
- **Why:** Enables targeted interventions and personalization
- **How:** Multi-dimensional segmentation (accuracy + engagement)

### 5. **Retention Analysis**
- **What:** User return patterns and platform stickiness
- **Why:** Critical metric for platform growth and success
- **How:** Cohort analysis with days-since-first-attempt methodology

## 🎯 Business Applications

### **For Executives**
- Platform performance KPIs and ROI metrics
- User engagement trends and growth indicators
- Strategic insights for product development

### **For Educators**
- Content difficulty analysis and curriculum optimization
- Learning effectiveness validation
- Student progress tracking and intervention targeting

### **For Product Teams**
- User behavior patterns and feature usage
- Retention analysis and churn prediction
- Data-driven feature prioritization

## 🛠️ Technical Implementation

### **Architecture**
- **Modular Design:** Separate components for easy maintenance
- **Caching Strategy:** `@st.cache_data` for optimal performance
- **Error Handling:** Graceful degradation for data issues
- **Scalable Structure:** Easy to extend with new visualizations

### **Data Processing**
- **Pandas & NumPy:** Efficient data manipulation and analysis
- **Plotly:** Interactive, publication-ready charts
- **Streamlit:** Modern web app framework for rapid deployment

### **Quality Assurance**
- **Comprehensive Testing:** Data validation and accuracy checks
- **Documentation:** Detailed methodology for each visualization
- **Best Practices:** Following modern data science standards

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

## 📚 Documentation

- **[Dashboard Documentation](DASHBOARD_DOCUMENTATION.md):** Comprehensive guide to all visualizations
- **Code Documentation:** Detailed docstrings and inline comments
- **Methodology Notes:** Available in dashboard expandable sections

## 🔄 Future Enhancements

- **Real-time Data:** Connect to live databases for dynamic updates
- **Advanced Analytics:** Machine learning models for prediction
- **Export Capabilities:** PDF reports and data downloads
- **Mobile Optimization:** Enhanced mobile experience
- **Multi-language Support:** Internationalization features

---

**Built with ❤️ for Medical Education Excellence**

*This dashboard represents modern best practices in educational data analysis, combining statistical rigor with practical business insights.*
Performance analysis for consulting at Mellow
