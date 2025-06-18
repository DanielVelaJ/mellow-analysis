"""
Command Line Interface for Mellow Analysis

Provides convenient entry points for running the analysis dashboard and other tools.
"""

import sys
import subprocess
from pathlib import Path
import click


@click.group()
@click.version_option()
def cli():
    """Mellow Analysis - Medical Education Data Analytics Tools"""
    pass


@cli.command()
@click.option('--port', default=None, help='Port to run the dashboard on (auto-selects if not specified)', type=int)
@click.option('--host', default='localhost', help='Host to bind the dashboard to')
@click.option('--browser/--no-browser', default=True, help='Auto-open browser')
def dashboard(port, host, browser):
    """Launch the interactive Streamlit dashboard"""
    
    # Get the path to the dashboard file
    dashboard_path = Path(__file__).parent / "streamlit" / "dashboard.py"
    
    if not dashboard_path.exists():
        click.echo(f"❌ Dashboard file not found at {dashboard_path}", err=True)
        sys.exit(1)
    
    # Build streamlit command - let Streamlit handle port selection and URL display
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.address", host,
    ]
    
    # Only specify port if user provided one, otherwise let Streamlit auto-select
    if port:
        cmd.extend(["--server.port", str(port)])
    
    if not browser:
        cmd.extend(["--server.headless", "true"])
    
    click.echo(f"🚀 Starting Mellow Analytics Dashboard...")
    if port:
        click.echo(f"📊 Using specified port: {port}")
    else:
        click.echo(f"📊 Auto-selecting available port...")
    click.echo(f"🔗 Press Ctrl+C to stop the server")
    click.echo("")  # Empty line for better formatting
    
    try:
        # Launch streamlit - this will show native Streamlit URLs and port selection
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        click.echo("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error launching dashboard: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ Streamlit not found. Please install with: pip install streamlit", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information"""
    from mellow_analysis import __version__
    click.echo(f"Mellow Analysis v{__version__}")


@cli.command("generate-report")
@click.option('--output', '-o', default=None, help='Output path for the PDF report')
@click.option('--format', default='pdf', type=click.Choice(['pdf']), help='Output format')
def generate_report(output, format):
    """Generate the analytics PDF report"""
    
    try:
        from mellow_analysis.reports.generate_report import MellowReportGenerator
        
        click.echo("🚀 Starting Mellow Analytics Report Generation...")
        
        generator = MellowReportGenerator()
        
        if output:
            from pathlib import Path
            output_path = Path(output)
            generator.generate_report(output_path)
            click.echo(f"📄 Report generated successfully: {output_path}")
        else:
            generator.generate_report()
            click.echo("📄 Report generated successfully: data/reports/mellow_analytics_report.pdf")
            
    except ImportError as e:
        click.echo(f"❌ Import error: {e}", err=True)
        click.echo("💡 Make sure all dependencies are installed", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 