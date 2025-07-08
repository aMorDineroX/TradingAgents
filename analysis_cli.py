#!/usr/bin/env python3
"""
Simple CLI for project analysis without requiring all dependencies.
"""

import typer
from pathlib import Path
import sys
import os

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from project_analysis import ProjectAnalyzer

app = typer.Typer(
    name="analysis-cli",
    help="TradingAgents Project Analysis Tool",
    add_completion=False,
)

@app.command()
def analyze(
    output_file: str = typer.Option("project_analysis_report.md", help="Output file for the analysis report")
):
    """Run comprehensive project analysis."""
    typer.echo("🚀 Starting TradingAgents Project Analysis...")
    
    analyzer = ProjectAnalyzer(".")
    report = analyzer.generate_comprehensive_report()
    
    # Save report to file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    typer.echo(f"✅ Analysis complete! Report saved to: {output_path}")
    typer.echo("\n📋 Analysis Summary:")
    typer.echo("=" * 60)
    
    # Print a summary
    lines = report.split('\n')
    in_summary = False
    for line in lines:
        if "Executive Summary" in line:
            in_summary = True
            continue
        if in_summary and line.startswith("##"):
            break
        if in_summary and line.strip():
            typer.echo(line)

@app.command()
def quick(
    show_agents: bool = typer.Option(True, help="Show agent architecture details"),
    show_deps: bool = typer.Option(True, help="Show dependency analysis"),
    show_structure: bool = typer.Option(True, help="Show project structure")
):
    """Quick analysis with selected components."""
    typer.echo("⚡ Running Quick Project Analysis...")
    
    analyzer = ProjectAnalyzer(".")
    
    if show_structure:
        typer.echo("\n🏗️ Project Structure:")
        structure = analyzer.analyze_project_structure()
        typer.echo(f"Total Python Files: {structure['python_files_count']}")
        typer.echo(f"Total Lines of Code: {structure['total_lines_of_code']:,}")
        typer.echo(f"Main Directories: {list(structure['main_directories'].keys())}")
    
    if show_agents:
        typer.echo("\n🤖 Agent Architecture:")
        agents = analyzer.analyze_agents_architecture()
        typer.echo(f"Total Agents: {agents['total_agents']}")
        for category, info in agents['agent_categories'].items():
            agent_names = [agent['agent_name'] for agent in info['agents']]
            typer.echo(f"  {category}: {agent_names}")
    
    if show_deps:
        typer.echo("\n📦 Key Dependencies:")
        deps = analyzer.analyze_dependencies()
        for dep_name, dep_info in deps['key_dependencies'].items():
            req_status = "✅" if dep_info['in_requirements'] else "❌"
            pyproject_status = "✅" if dep_info['in_pyproject'] else "❌"
            typer.echo(f"  {dep_name}: Req={req_status} PyProject={pyproject_status}")

@app.command()
def structure():
    """Analyze project structure only."""
    typer.echo("🏗️ Analyzing Project Structure...")
    
    analyzer = ProjectAnalyzer(".")
    structure = analyzer.analyze_project_structure()
    
    typer.echo(f"\n📊 Structure Overview:")
    typer.echo(f"  Total Python Files: {structure['python_files_count']}")
    typer.echo(f"  Total Lines of Code: {structure['total_lines_of_code']:,}")
    typer.echo(f"  Main Directories: {len(structure['main_directories'])}")
    
    typer.echo(f"\n📁 Directory Breakdown:")
    for dir_name, dir_info in structure['main_directories'].items():
        typer.echo(f"  {dir_name}/ - {dir_info['python_files']} Python files, {dir_info['lines_of_code']:,} lines")

@app.command()
def agents():
    """Analyze agent architecture only."""
    typer.echo("🤖 Analyzing Agent Architecture...")
    
    analyzer = ProjectAnalyzer(".")
    agents = analyzer.analyze_agents_architecture()
    
    typer.echo(f"\n🎯 Agent Overview:")
    typer.echo(f"  Total Agents: {agents['total_agents']}")
    typer.echo(f"  Agent Categories: {len(agents['agent_categories'])}")
    
    typer.echo(f"\n🏷️ Agent Categories:")
    for category, info in agents['agent_categories'].items():
        typer.echo(f"\n  {category.upper()} ({len(info['agents'])} agents)")
        typer.echo(f"    Description: {info['description']}")
        for agent in info['agents']:
            create_func = "✅" if agent['has_create_function'] else "❌"
            typer.echo(f"    - {agent['agent_name']}: {agent['lines_of_code']} lines, Create Function: {create_func}")

if __name__ == "__main__":
    app()