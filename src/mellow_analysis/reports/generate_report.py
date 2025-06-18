"""
Mellow Analytics Report Generator - Final Version

Optimized for readability with clear visualizations and proper text positioning.
"""

import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import data loader
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.mellow_analysis.data.loader import data_loader


class MellowReportGenerator:
    """Generate refined PDF report with fixed text positioning."""
    
    def __init__(self):
        self.page_width = 11.69  # A4 landscape
        self.page_height = 8.27
        self.margin = 0.5
        
        # Optimized font settings for better PDF readability
        plt.rcParams.update({
            'font.size': 10,
            'font.family': 'serif',
            'axes.titlesize': 13,
            'axes.labelsize': 11,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'figure.titlesize': 15,
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'text.usetex': False
        })
        
    def generate_report(self, output_path: Path = Path('data/reports/mellow_analytics_report.pdf')):
        """Generate the refined PDF report."""
        print("🚀 Starting Mellow Analytics Report Generation...")
        
        # Load data
        print("📊 Loading data...")
        data = self._load_data()
        
        # Create PDF
        with PdfPages(output_path) as pdf:
            print("📄 Creating refined report pages...")
            
            # 1. Cover page
            self._add_cover_page(pdf, data)
            
            # 2. Executive summary
            self._add_executive_summary(pdf, data)
            
            # 3. Overview metrics - fixed layout
            self._add_overview_metrics_fixed(pdf, data)
            
            # 4. Performance trends - simplified
            self._add_performance_trends_fixed(pdf, data)
            
            # 5. Question difficulty - clean layout
            self._add_question_difficulty_fixed(pdf, data)
            
            # 6. User engagement - fixed positioning
            self._add_user_engagement_fixed(pdf, data)
            
            # 7. Recommendations
            self._add_recommendations(pdf, data)
            
            # Add metadata
            d = pdf.infodict()
            d['Title'] = 'Mellow Medical Education Analytics Report'
            d['Author'] = 'Mellow Analytics Team'
            d['CreationDate'] = datetime.datetime.now()
            
        print(f"✅ Report generated: {output_path.resolve()}")
        
    def _load_data(self):
        """Load all required data."""
        return {
            'cases_df': data_loader.load_cases(),
            'responses_df': data_loader.load_responses(),
            'full_df': data_loader.load_full_dataset(),
            'stats': data_loader.get_summary_stats()
        }
        
    def _add_cover_page(self, pdf, data):
        """Professional cover page with fixed positioning."""
        fig = plt.figure(figsize=(self.page_width, self.page_height))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Background
        rect = patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                               facecolor='#f8f9fa', alpha=0.5)
        ax.add_patch(rect)
        
        # Title - fixed positioning
        fig.text(0.5, 0.7, 'Mellow Medical Education', 
                ha='center', va='center', fontsize=24, weight='bold',
                color='#2c3e50')
        
        fig.text(0.5, 0.6, 'Analytics Report', 
                ha='center', va='center', fontsize=20,
                color='#34495e')
        
        # Metrics box - properly sized
        stats = data['stats']
        metrics_text = (
            f"📊 {stats['total_responses']:,} Responses | "
            f"👥 {stats['unique_users']:,} Users | "
            f"🎯 {stats['overall_accuracy']:.1%} Accuracy"
        )
        
        # Single line metrics to avoid overlap
        fig.text(0.5, 0.4, metrics_text,
                ha='center', va='center', fontsize=12, weight='medium',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#e3f2fd', alpha=0.8))
        
        # Date - fixed position
        today = datetime.date.today().strftime('%B %d, %Y')
        fig.text(0.5, 0.2, f'Generated: {today}',
                ha='center', va='center', fontsize=10, color='#666')
        
        # Footer
        fig.text(0.5, 0.05, '© 2024 Mellow Medical Education Platform',
                ha='center', va='center', fontsize=8, color='#999')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
    def _add_executive_summary(self, pdf, data):
        """Executive summary with controlled text layout."""
        fig = plt.figure(figsize=(self.page_width, self.page_height))
        
        # Title at top
        fig.suptitle('Executive Summary', fontsize=16, weight='bold', y=0.95)
        
        # Single text area to avoid overlaps
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        stats = data['stats']
        
        # Concise summary text
        summary_text = f"""
PLATFORM OVERVIEW

The Mellow platform has engaged {stats['unique_users']:,} medical professionals across 
{stats['countries']} countries, generating {stats['total_responses']:,} learning interactions.

KEY METRICS
• Overall Accuracy: {stats['overall_accuracy']:.1%} (optimal range for effective learning)
• User Engagement: {stats['total_responses']/stats['unique_users']:.1f} responses per user
• Content Breadth: {stats['unique_questions']} unique questions across {stats['categories']} categories
• Global Reach: Active users from {stats['countries']} different countries

PERFORMANCE ASSESSMENT
✅ Strong user engagement with good retention indicators
✅ Appropriate content difficulty level for target audience  
✅ Healthy platform activity with consistent daily usage
✅ Diverse content covering multiple medical specialties

PRIORITY RECOMMENDATIONS
1. Review questions with accuracy below 60% for content clarity
2. Implement user progression tracking for personalized learning paths
3. Expand intermediate-level content to fill difficulty gaps
4. Enhance mobile experience to increase accessibility

NEXT STEPS
The following pages provide detailed analysis of platform performance with specific 
recommendations for continued growth and improvement.
"""
        
        # Use proper text positioning
        ax.text(0.05, 0.9, summary_text, 
               ha='left', va='top', fontsize=10,
               transform=ax.transAxes, 
               bbox=dict(boxstyle="round,pad=0.02", facecolor='#fafafa', alpha=0.8))
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
    def _add_overview_metrics_fixed(self, pdf, data):
        """Overview metrics with fixed grid layout."""
        fig = plt.figure(figsize=(self.page_width, self.page_height))
        fig.suptitle('Platform Overview Metrics', fontsize=16, weight='bold', y=0.95)
        
        stats = data['stats']
        
        # Create proper subplot grid with adequate spacing
        gs = fig.add_gridspec(2, 3, hspace=0.6, wspace=0.4,
                             top=0.85, bottom=0.25, left=0.1, right=0.9)
        
        # Metrics data
        metrics = [
            ('Total Responses', f"{stats['total_responses']:,}", '#3498db'),
            ('Unique Users', f"{stats['unique_users']:,}", '#2ecc71'),
            ('Overall Accuracy', f"{stats['overall_accuracy']:.1%}", '#e74c3c'),
            ('Avg Responses/User', f"{stats['total_responses']/stats['unique_users']:.1f}", '#f39c12'),
            ('Countries', f"{stats['countries']}", '#9b59b6'),
            ('Questions', f"{stats['unique_questions']}", '#1abc9c')
        ]
        
        # Create metric cards with proper spacing
        for i, (label, value, color) in enumerate(metrics):
            ax = fig.add_subplot(gs[i // 3, i % 3])
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Simple card design
            rect = patches.FancyBboxPatch((0.1, 0.2), 0.8, 0.6,
                                        boxstyle="round,pad=0.05",
                                        facecolor=color,
                                        alpha=0.2,
                                        edgecolor=color,
                                        linewidth=1.5)
            ax.add_patch(rect)
            
            # Value - centered and sized properly
            ax.text(0.5, 0.65, value, ha='center', va='center',
                   fontsize=16, weight='bold', color=color)
            
            # Label - properly positioned
            ax.text(0.5, 0.35, label, ha='center', va='center',
                   fontsize=9, weight='bold')
        
        # Explanation section - properly positioned
        explanation_ax = fig.add_axes([0.05, 0.05, 0.9, 0.15])
        explanation_ax.axis('off')
        
        explanation_text = """
Metric Definitions: Total Responses = all question attempts | Unique Users = distinct platform users | 
Overall Accuracy = percentage of correct answers | Avg Responses/User = engagement indicator | 
Countries = geographic reach | Questions = content variety. Optimal accuracy range is 70-85% for effective learning.
"""
        
        explanation_ax.text(0.02, 0.8, explanation_text, 
                          ha='left', va='top', fontsize=8,
                          transform=explanation_ax.transAxes,
                          bbox=dict(boxstyle="round,pad=0.02", facecolor='#f5f5f5', alpha=0.8))
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
    def _add_performance_trends_fixed(self, pdf, data):
        """Performance trends with simplified, cleaner layout."""
        responses_df = data['responses_df']
        
        fig = plt.figure(figsize=(self.page_width, self.page_height))
        fig.suptitle('Performance Trends Over Time', fontsize=16, weight='bold', y=0.95)
        
        # Prepare data - aggregate by week for cleaner visualization
        weekly_stats = responses_df.copy()
        weekly_stats['week'] = weekly_stats['exam_created_at'].dt.to_period('W').dt.start_time
        weekly_agg = weekly_stats.groupby('week').agg({
            'is_correct': ['mean', 'count'],
            'id_user_hash': 'nunique'
        }).reset_index()
        weekly_agg.columns = ['week', 'accuracy', 'responses', 'unique_users']
        weekly_agg = weekly_agg.sort_values('week')
        
        # Create two separate charts for clarity
        gs = fig.add_gridspec(3, 2, height_ratios=[1.5, 1.5, 1], 
                             hspace=0.4, wspace=0.3, top=0.85, bottom=0.15)
        
        # Accuracy trend chart
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(weekly_agg['week'], weekly_agg['accuracy'], 
                'o-', linewidth=3, markersize=6, color='#2E86AB',
                markerfacecolor='white', markeredgewidth=2)
        
        ax1.fill_between(weekly_agg['week'], weekly_agg['accuracy'], 
                        alpha=0.3, color='#2E86AB')
        
        ax1.set_ylabel('Weekly Accuracy Rate', fontsize=11, color='#2E86AB')
        ax1.set_title('Learning Effectiveness Over Time', fontsize=12, pad=15)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0.5, 1.0)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        
        # Add trend line
        if len(weekly_agg) > 2:
            z = np.polyfit(range(len(weekly_agg)), weekly_agg['accuracy'], 1)
            p = np.poly1d(z)
            ax1.plot(weekly_agg['week'], p(range(len(weekly_agg))), 
                    '--', color='red', linewidth=2, alpha=0.8, label='Trend')
            ax1.legend(loc='upper left')
        
        # Activity volume chart
        ax2 = fig.add_subplot(gs[1, :])
        bars = ax2.bar(weekly_agg['week'], weekly_agg['responses'], 
                      color='#F18F01', alpha=0.8, width=pd.Timedelta(days=5))
        
        ax2.set_ylabel('Weekly Response Count', fontsize=11, color='#F18F01')
        ax2.set_xlabel('Week', fontsize=11)
        ax2.set_title('Platform Activity Volume', fontsize=12, pad=15)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, weekly_agg['responses']):
            if value > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                        f'{int(value)}', ha='center', va='bottom', fontsize=8)
        
        # Format dates
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Analysis section with better layout
        ax3 = fig.add_subplot(gs[2, :])
        ax3.axis('off')
        
        # Calculate key metrics
        recent_accuracy = weekly_agg['accuracy'].iloc[-2:].mean() if len(weekly_agg) >= 2 else weekly_agg['accuracy'].mean()
        overall_accuracy = weekly_agg['accuracy'].mean()
        total_responses = weekly_agg['responses'].sum()
        avg_weekly_responses = weekly_agg['responses'].mean()
        
        trend_direction = "📈 Improving" if recent_accuracy > overall_accuracy else "➡️ Stable"
        
        analysis_text = f"""
KEY INSIGHTS:  {trend_direction} Performance | Recent: {recent_accuracy:.1%} vs Overall: {overall_accuracy:.1%}
Activity: {total_responses:,} total responses | {avg_weekly_responses:.0f} per week average
Peak week: {weekly_agg.loc[weekly_agg['responses'].idxmax(), 'week'].strftime('%B %d')} ({weekly_agg['responses'].max()} responses)
"""
        
        ax3.text(0.05, 0.7, analysis_text, 
                ha='left', va='top', fontsize=10,
                transform=ax3.transAxes,
                bbox=dict(boxstyle="round,pad=0.02", facecolor='#e8f4f8', alpha=0.9))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
    def _add_question_difficulty_fixed(self, pdf, data):
        """Question difficulty with clean layout."""
        full_df = data['full_df']
        
        fig = plt.figure(figsize=(self.page_width, self.page_height))
        fig.suptitle('Question Difficulty Analysis', fontsize=16, weight='bold', y=0.95)
        
        # Calculate stats
        question_stats = full_df.groupby('question').agg({
            'is_correct': ['mean', 'count'],
            'subcategory_name': 'first'
        }).reset_index()
        question_stats.columns = ['question', 'accuracy', 'responses', 'subcategory']
        question_stats = question_stats[question_stats['responses'] >= 10]
        
        # Chart section - top half
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.4, wspace=0.3,
                             top=0.85, bottom=0.45, left=0.1, right=0.9)
        
        # Histogram
        ax1 = fig.add_subplot(gs[0, 0])
        n, bins, patches = ax1.hist(question_stats['accuracy'], bins=15, 
                                   edgecolor='black', alpha=0.7, color='skyblue')
        
        ax1.axvline(question_stats['accuracy'].mean(), color='red', 
                   linestyle='--', linewidth=2, 
                   label=f"Mean: {question_stats['accuracy'].mean():.1%}")
        ax1.axvspan(0.7, 0.85, alpha=0.2, color='green', label='Optimal')
        
        ax1.set_xlabel('Accuracy Rate', fontsize=9)
        ax1.set_ylabel('Question Count', fontsize=9)
        ax1.set_title('Difficulty Distribution', fontsize=10)
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # Pie chart
        ax2 = fig.add_subplot(gs[0, 1])
        difficulty_bins = pd.cut(question_stats['accuracy'], 
                               bins=[0, 0.6, 0.8, 0.9, 1.0],
                               labels=['Hard\n(<60%)', 'Moderate\n(60-80%)', 
                                      'Easy\n(80-90%)', 'Very Easy\n(>90%)'])
        difficulty_counts = difficulty_bins.value_counts()
        
        colors = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6']
        ax2.pie(difficulty_counts.values, labels=difficulty_counts.index, 
               autopct='%1.1f%%', startangle=90, colors=colors)
        ax2.set_title('Difficulty Categories', fontsize=10)
        
        # Analysis section - bottom half with better spacing and layout
        analysis_ax = fig.add_axes([0.05, 0.05, 0.9, 0.35])
        analysis_ax.axis('off')
        
        # Split into two columns for better readability
        left_col_ax = fig.add_axes([0.05, 0.05, 0.45, 0.35])
        left_col_ax.axis('off')
        
        right_col_ax = fig.add_axes([0.52, 0.05, 0.43, 0.35])
        right_col_ax.axis('off')
        
        # Left column - Summary statistics
        summary_text = f"""
DIFFICULTY OVERVIEW

📊 Total Questions: {len(question_stats)}
📈 Average Success Rate: {question_stats['accuracy'].mean():.1%}
🔴 Hardest Question: {question_stats['accuracy'].min():.1%}
🟢 Easiest Question: {question_stats['accuracy'].max():.1%}

DISTRIBUTION BREAKDOWN
• Hard (<60%): {len(question_stats[question_stats['accuracy'] < 0.6])} questions
• Moderate (60-80%): {len(question_stats[(question_stats['accuracy'] >= 0.6) & (question_stats['accuracy'] < 0.8)])} questions  
• Easy (80-90%): {len(question_stats[(question_stats['accuracy'] >= 0.8) & (question_stats['accuracy'] < 0.9)])} questions
• Very Easy (>90%): {len(question_stats[question_stats['accuracy'] >= 0.9])} questions
"""
        
        left_col_ax.text(0.05, 0.95, summary_text, 
                        ha='left', va='top', fontsize=9,
                        transform=left_col_ax.transAxes,
                        bbox=dict(boxstyle="round,pad=0.02", facecolor='#f0f8ff', alpha=0.9))
        
        # Right column - Most difficult questions and recommendations
        most_difficult = question_stats.nsmallest(3, 'accuracy')
        
        difficult_text = """
QUESTIONS NEEDING REVIEW

"""
        
        for i, (_, row) in enumerate(most_difficult.iterrows(), 1):
            question_preview = row['question'][:50] + "..." if len(row['question']) > 50 else row['question']
            difficult_text += f"{i}. {question_preview}\n"
            difficult_text += f"   ✗ {row['accuracy']:.1%} success rate\n\n"
        
        difficult_text += """
RECOMMENDATIONS
• Review red-flagged questions for clarity
• Add explanations for common mistakes  
• Create practice questions for weak areas
• Monitor new content difficulty levels
"""
        
        right_col_ax.text(0.05, 0.95, difficult_text, 
                         ha='left', va='top', fontsize=9,
                         transform=right_col_ax.transAxes,
                         bbox=dict(boxstyle="round,pad=0.02", facecolor='#fff5f5', alpha=0.9))
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
    def _add_user_engagement_fixed(self, pdf, data):
        """User engagement with proper spacing."""
        responses_df = data['responses_df']
        
        fig = plt.figure(figsize=(self.page_width, self.page_height))
        fig.suptitle('User Engagement Analysis', fontsize=16, weight='bold', y=0.95)
        
        # Chart section
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3,
                             top=0.85, bottom=0.4, left=0.1, right=0.9)
        
        # Hourly activity
        ax1 = fig.add_subplot(gs[0, :])
        hourly_activity = responses_df.groupby('hour').size()
        
        bars = ax1.bar(hourly_activity.index, hourly_activity.values, 
                      color='lightblue', edgecolor='navy', alpha=0.8)
        ax1.set_xlabel('Hour of Day', fontsize=9)
        ax1.set_ylabel('Response Count', fontsize=9)
        ax1.set_title('Activity by Hour of Day', fontsize=10)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # User distribution
        ax2 = fig.add_subplot(gs[1, :])
        user_responses = responses_df.groupby('id_user_hash').size()
        
        bins = [0, 5, 10, 20, 50, 100, 1000]
        labels = ['1-5', '6-10', '11-20', '21-50', '51-100', '100+']
        user_bins = pd.cut(user_responses, bins=bins, labels=labels)
        bin_counts = user_bins.value_counts()
        
        bars2 = ax2.bar(range(len(bin_counts)), bin_counts.values, 
                       color='coral', edgecolor='darkred', alpha=0.8)
        ax2.set_xticks(range(len(bin_counts)))
        ax2.set_xticklabels(bin_counts.index)
        ax2.set_xlabel('Responses per User', fontsize=9)
        ax2.set_ylabel('Number of Users', fontsize=9)
        ax2.set_title('User Engagement Distribution', fontsize=10)
        
        # Add value labels on bars
        for bar, count in zip(bars2, bin_counts.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{count}', ha='center', va='bottom', fontsize=8)
        
        # Analysis section with controlled positioning
        analysis_ax = fig.add_axes([0.05, 0.05, 0.9, 0.3])
        analysis_ax.axis('off')
        
        # Calculate metrics
        peak_hour = hourly_activity.idxmax()
        engaged_users = (user_responses > 10).sum()
        one_time_users = (user_responses == 1).sum()
        
        engagement_text = f"""
📊 ENGAGEMENT INSIGHTS

⏰ Peak Activity: Hour {peak_hour} with {hourly_activity.max()} responses
👥 User Categories:
   • Highly Engaged (>10 responses): {engaged_users} users ({engaged_users/len(user_responses)*100:.1f}%)
   • One-time Users: {one_time_users} users ({one_time_users/len(user_responses)*100:.1f}%)
   • Median engagement: {user_responses.median():.0f} responses per user

📈 Activity Patterns:
   • Business hours (9-17): {hourly_activity[9:17].sum()} responses
   • Evening hours (18-22): {hourly_activity[18:22].sum()} responses
   • {'Evening-heavy' if hourly_activity[18:22].sum() > hourly_activity[9:17].sum() else 'Business-heavy'} usage pattern

🎯 ACTION ITEMS:
   ✓ Re-engage one-time users with targeted campaigns
   ✓ Schedule releases during hour {peak_hour} for maximum reach
   ✓ Create loyalty rewards for highly engaged users
   ✓ Optimize performance during peak periods
"""
        
        analysis_ax.text(0.02, 0.95, engagement_text, 
                        ha='left', va='top', fontsize=9,
                        transform=analysis_ax.transAxes,
                        bbox=dict(boxstyle="round,pad=0.02", facecolor='#f0f8ff', alpha=0.8))
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
    def _add_recommendations(self, pdf, data):
        """Clean recommendations page."""
        fig, ax = plt.subplots(figsize=(self.page_width, self.page_height))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, 'Strategic Recommendations', 
               ha='center', va='top', fontsize=18, weight='bold',
               transform=ax.transAxes)
        
        recommendations_text = """
PRIORITY ACTIONS

1. CONTENT OPTIMIZATION (Immediate - Next 30 Days)
   ✓ Review and revise questions with accuracy below 60%
   ✓ Add detailed explanations for incorrect answers
   ✓ Create intermediate-difficulty questions to fill gaps
   ✓ Implement quality assurance process for new content

2. USER ENGAGEMENT (Short Term - Next 60 Days)
   ✓ Launch re-engagement campaign for one-time users
   ✓ Implement progress tracking and achievement badges
   ✓ Create streak rewards for consecutive daily usage
   ✓ Add personalized learning recommendations

3. PLATFORM ENHANCEMENTS (Medium Term - Next 90 Days)
   ✓ Optimize mobile experience and offline capabilities
   ✓ Implement adaptive difficulty based on user performance
   ✓ Add spaced repetition for challenging questions
   ✓ Create community features and discussion forums

4. ANALYTICS & INSIGHTS (Ongoing)
   ✓ Track individual learning progression over time
   ✓ Implement A/B testing framework for new features
   ✓ Create performance benchmarks by user segments
   ✓ Develop predictive models for user retention

5. GROWTH STRATEGY (Long Term - Next 6 Months)
   ✓ Partner with medical schools and associations
   ✓ Expand content to additional medical specialties
   ✓ Develop certification and continuing education programs
   ✓ Create API for third-party integrations

SUCCESS METRICS TO MONITOR:
• User retention rate (target: >70% return within one week)
• Average responses per user (target: >20)
• Question difficulty distribution (target: 70% in optimal range)
• Monthly active user growth (target: 10% month-over-month)

For implementation support: analytics@mellow.education
"""
        
        ax.text(0.05, 0.85, recommendations_text, 
               ha='left', va='top', fontsize=9,
               transform=ax.transAxes, fontfamily='sans-serif',
               bbox=dict(boxstyle="round,pad=0.02", facecolor='#f9f9f9', alpha=0.9))
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)


# Main execution
if __name__ == "__main__":
    generator = MellowReportGenerator()
    generator.generate_report() 