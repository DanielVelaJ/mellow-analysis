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
import socket
import webbrowser
from pathlib import Path

def find_available_port(start_port=8501, max_attempts=50):
    """Find the next available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts}")


def get_network_ip():
    """Get the local network IP address."""
    try:
        # Connect to a remote address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return "localhost"


def main():
    """Launch the Streamlit dashboard."""
    
    dashboard_path = Path("src/mellow_analysis/streamlit/dashboard.py")
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    print("🚀 Starting Mellow Analysis Dashboard...")
    print(f"📍 Dashboard location: {dashboard_path}")
    
    # Find an available port
    try:
        port = find_available_port()
        print(f"🔌 Found available port: {port}")
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Get network information
    network_ip = get_network_ip()
    localhost_url = f"http://localhost:{port}"
    network_url = f"http://{network_ip}:{port}"
    
    print("\n" + "="*60)
    print("🌐 Dashboard URLs:")
    print(f"   Local access:    {localhost_url}")
    if network_ip != "localhost":
        print(f"   Network access:  {network_url}")
        print(f"   📱 Share this URL with others on your network!")
    print("="*60)
    print("🔗 Press Ctrl+C to stop the server")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.address", "0.0.0.0",  # Listen on all interfaces
            "--server.port", str(port),
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching dashboard: {e}")
        print("\nTry installing streamlit manually:")
        print("    poetry add streamlit")
        print("or")
        print("    pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main() 