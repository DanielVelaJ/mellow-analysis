#!/usr/bin/env python3
"""
Mellow Analysis Dashboard Launcher

Run this script to start the Streamlit dashboard:
    python run_dashboard.py

Or use streamlit directly:
    streamlit run src/mellow_analysis/streamlit/dashboard.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit dashboard."""
    
    dashboard_path = Path("src/mellow_analysis/streamlit/dashboard.py")
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    print("🚀 Starting Mellow Analysis Dashboard...")
    print(f"📍 Dashboard location: {dashboard_path}")
    print("🌐 Opening in your default browser...")
    print("\n" + "="*50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\nTry installing streamlit manually:")
        print("    poetry add streamlit")
        print("or")
        print("    pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main() 