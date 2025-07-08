#!/usr/bin/env python3
"""
TradingAgents Project Analysis Tool
Provides comprehensive analysis of the TradingAgents multi-agent trading framework.
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import importlib.util

class ProjectAnalyzer:
    """Comprehensive analyzer for the TradingAgents project."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_data = {}
        
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze the overall project structure."""
        structure = {
            "root_files": [],
            "main_directories": {},
            "python_files_count": 0,
            "total_lines_of_code": 0
        }
        
        # Get root files
        for item in self.project_root.iterdir():
            if item.is_file():
                structure["root_files"].append(item.name)
        
        # Analyze main directories
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                dir_info = self._analyze_directory(item)
                structure["main_directories"][item.name] = dir_info
                structure["python_files_count"] += dir_info["python_files"]
                structure["total_lines_of_code"] += dir_info["lines_of_code"]
        
        return structure
    
    def _analyze_directory(self, directory: Path) -> Dict[str, Any]:
        """Analyze a specific directory."""
        info = {
            "files": [],
            "subdirectories": [],
            "python_files": 0,
            "lines_of_code": 0
        }
        
        try:
            for item in directory.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(directory)
                    info["files"].append(str(relative_path))
                    
                    if item.suffix == ".py":
                        info["python_files"] += 1
                        try:
                            with open(item, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                                info["lines_of_code"] += lines
                        except:
                            pass
                elif item.is_dir():
                    relative_path = item.relative_to(directory)
                    if str(relative_path) not in info["subdirectories"]:
                        info["subdirectories"].append(str(relative_path))
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    def analyze_agents_architecture(self) -> Dict[str, Any]:
        """Analyze the multi-agent architecture."""
        agents_dir = self.project_root / "tradingagents" / "agents"
        architecture = {
            "agent_categories": {},
            "total_agents": 0,
            "agent_relationships": []
        }
        
        if not agents_dir.exists():
            return {"error": "Agents directory not found"}
        
        # Analyze different agent categories
        for category_dir in agents_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('__'):
                category_info = {
                    "agents": [],
                    "description": self._infer_category_description(category_dir.name)
                }
                
                for agent_file in category_dir.glob("*.py"):
                    if not agent_file.name.startswith('__'):
                        agent_info = self._analyze_agent_file(agent_file)
                        category_info["agents"].append(agent_info)
                        architecture["total_agents"] += 1
                
                architecture["agent_categories"][category_dir.name] = category_info
        
        return architecture
    
    def _infer_category_description(self, category_name: str) -> str:
        """Infer description based on category name."""
        descriptions = {
            "analysts": "Specialized agents for market analysis (technical, fundamental, sentiment, news)",
            "researchers": "Bull and bear researchers for debate-based investment analysis",
            "trader": "Agent responsible for making final trading decisions",
            "risk_mgmt": "Risk management agents for portfolio risk assessment",
            "managers": "Manager agents that coordinate and oversee other agents",
            "utils": "Utility classes and helper functions for agent operations"
        }
        return descriptions.get(category_name, f"Agent category: {category_name}")
    
    def _analyze_agent_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze an individual agent file."""
        agent_info = {
            "file_name": file_path.name,
            "agent_name": file_path.stem,
            "functions": [],
            "classes": [],
            "imports": [],
            "lines_of_code": 0,
            "has_create_function": False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                agent_info["lines_of_code"] = len(content.splitlines())
            
            # Parse AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    agent_info["functions"].append(node.name)
                    if node.name.startswith("create_") and "analyst" in node.name:
                        agent_info["has_create_function"] = True
                elif isinstance(node, ast.ClassDef):
                    agent_info["classes"].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        agent_info["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            agent_info["imports"].append(f"{node.module}.{alias.name}")
        
        except Exception as e:
            agent_info["error"] = str(e)
        
        return agent_info
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies and their usage."""
        deps_info = {
            "requirements_txt": [],
            "pyproject_toml": [],
            "missing_in_requirements": [],
            "unused_dependencies": [],
            "key_dependencies": {}
        }
        
        # Read requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                deps_info["requirements_txt"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Read pyproject.toml dependencies - manual parsing for compatibility
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()
                in_deps = False
                for line in content.split('\n'):
                    line = line.strip()
                    if 'dependencies = [' in line:
                        in_deps = True
                        continue
                    if in_deps and ']' in line:
                        break
                    if in_deps and line.startswith('"') and line.endswith('",'):
                        dep = line.strip('"').strip(',')
                        deps_info["pyproject_toml"].append(dep)
                    elif in_deps and line.startswith('"') and line.endswith('"'):
                        dep = line.strip('"')
                        deps_info["pyproject_toml"].append(dep)
        
        # Analyze key dependencies
        key_deps = {
            "langchain": "Core LLM framework",
            "langgraph": "Multi-agent orchestration",
            "openai": "LLM API access",
            "typer": "CLI framework",
            "rich": "Terminal UI",
            "pandas": "Data manipulation",
            "yfinance": "Financial data",
            "finnhub": "Financial data API"
        }
        
        for dep_name, description in key_deps.items():
            found_in_req = any(dep_name in req for req in deps_info["requirements_txt"])
            found_in_pyproject = any(dep_name in req for req in deps_info["pyproject_toml"])
            deps_info["key_dependencies"][dep_name] = {
                "description": description,
                "in_requirements": found_in_req,
                "in_pyproject": found_in_pyproject
            }
        
        return deps_info
    
    def analyze_data_flows(self) -> Dict[str, Any]:
        """Analyze data flow components."""
        dataflows_dir = self.project_root / "tradingagents" / "dataflows"
        flows_info = {
            "components": [],
            "data_sources": [],
            "total_files": 0
        }
        
        if not dataflows_dir.exists():
            return {"error": "Dataflows directory not found"}
        
        for file_path in dataflows_dir.glob("*.py"):
            if not file_path.name.startswith('__'):
                component_info = {
                    "file_name": file_path.name,
                    "component_name": file_path.stem,
                    "functions": [],
                    "data_source": self._infer_data_source(file_path.stem)
                }
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            component_info["functions"].append(node.name)
                
                except Exception as e:
                    component_info["error"] = str(e)
                
                flows_info["components"].append(component_info)
                flows_info["total_files"] += 1
                
                if component_info["data_source"] not in flows_info["data_sources"]:
                    flows_info["data_sources"].append(component_info["data_source"])
        
        return flows_info
    
    def _infer_data_source(self, component_name: str) -> str:
        """Infer data source from component name."""
        sources = {
            "finnhub": "Financial data API",
            "reddit": "Social media sentiment",
            "stockstats": "Technical indicators",
            "yahoo": "Yahoo Finance data",
            "eodhd": "End-of-day historical data"
        }
        
        for source, description in sources.items():
            if source in component_name.lower():
                return f"{source}: {description}"
        
        return "Unknown data source"
    
    def analyze_cli_interface(self) -> Dict[str, Any]:
        """Analyze the CLI interface."""
        cli_dir = self.project_root / "cli"
        cli_info = {
            "files": [],
            "commands": [],
            "total_functions": 0,
            "has_typer": False
        }
        
        if not cli_dir.exists():
            return {"error": "CLI directory not found"}
        
        for file_path in cli_dir.glob("*.py"):
            if not file_path.name.startswith('__'):
                file_info = {
                    "file_name": file_path.name,
                    "functions": [],
                    "classes": [],
                    "typer_usage": False
                }
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "typer" in content:
                        file_info["typer_usage"] = True
                        cli_info["has_typer"] = True
                    
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            file_info["functions"].append(node.name)
                            cli_info["total_functions"] += 1
                            
                            # Check for CLI commands
                            if any(decorator.id == "app.command" if hasattr(decorator, 'id') 
                                  else False for decorator in node.decorator_list 
                                  if hasattr(decorator, 'id')):
                                cli_info["commands"].append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            file_info["classes"].append(node.name)
                
                except Exception as e:
                    file_info["error"] = str(e)
                
                cli_info["files"].append(file_info)
        
        return cli_info
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive analysis report."""
        print("🔍 Analyzing TradingAgents Project Structure...")
        structure = self.analyze_project_structure()
        
        print("🤖 Analyzing Multi-Agent Architecture...")
        agents = self.analyze_agents_architecture()
        
        print("📦 Analyzing Dependencies...")
        dependencies = self.analyze_dependencies()
        
        print("🔄 Analyzing Data Flows...")
        dataflows = self.analyze_data_flows()
        
        print("💻 Analyzing CLI Interface...")
        cli = self.analyze_cli_interface()
        
        # Generate report
        report = self._format_analysis_report(structure, agents, dependencies, dataflows, cli)
        
        return report
    
    def _format_analysis_report(self, structure, agents, dependencies, dataflows, cli) -> str:
        """Format the comprehensive analysis report."""
        report = f"""
# TradingAgents Project Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Executive Summary

TradingAgents is a sophisticated multi-agent LLM-powered financial trading framework that simulates real-world trading firm dynamics. The project employs specialized AI agents for market analysis, research, trading decisions, and risk management.

## 🏗️ Project Structure

### Overview
- **Total Python Files**: {structure['python_files_count']}
- **Total Lines of Code**: {structure['total_lines_of_code']:,}
- **Main Directories**: {len(structure['main_directories'])}

### Directory Breakdown
"""
        
        for dir_name, dir_info in structure['main_directories'].items():
            report += f"""
**{dir_name}/**
- Files: {len(dir_info['files'])}
- Python Files: {dir_info['python_files']}
- Lines of Code: {dir_info['lines_of_code']:,}
"""
        
        report += f"""
## 🤖 Multi-Agent Architecture

### Agent Categories
Total Agents: {agents['total_agents']}

"""
        
        for category, category_info in agents['agent_categories'].items():
            report += f"""
**{category.title()}** ({len(category_info['agents'])} agents)
- Description: {category_info['description']}
- Agents: {', '.join([agent['agent_name'] for agent in category_info['agents']])}
"""
        
        report += f"""
### Agent Implementation Details
"""
        
        for category, category_info in agents['agent_categories'].items():
            for agent in category_info['agents']:
                create_func = "✅" if agent['has_create_function'] else "❌"
                report += f"""
- **{agent['agent_name']}**: {agent['lines_of_code']} lines, {len(agent['functions'])} functions, Create Function: {create_func}
"""
        
        report += f"""
## 📦 Dependencies Analysis

### Key Dependencies Status
"""
        
        for dep_name, dep_info in dependencies['key_dependencies'].items():
            req_status = "✅" if dep_info['in_requirements'] else "❌"
            pyproject_status = "✅" if dep_info['in_pyproject'] else "❌"
            report += f"""
- **{dep_name}**: {dep_info['description']}
  - Requirements.txt: {req_status}
  - Pyproject.toml: {pyproject_status}
"""
        
        report += f"""
### Dependencies Summary
- Total requirements.txt entries: {len(dependencies['requirements_txt'])}
- Total pyproject.toml entries: {len(dependencies['pyproject_toml'])}
"""
        
        report += f"""
## 🔄 Data Flow Components

### Data Sources Integration
Total Components: {dataflows['total_files']}
Supported Data Sources: {len(dataflows['data_sources'])}

"""
        
        for component in dataflows['components']:
            report += f"""
- **{component['component_name']}**: {component['data_source']} ({len(component['functions'])} functions)
"""
        
        report += f"""
## 💻 CLI Interface

### CLI Features
- Total CLI Files: {len(cli['files'])}
- Total Functions: {cli['total_functions']}
- Available Commands: {len(cli['commands'])}
- Typer Framework: {"✅ Used" if cli['has_typer'] else "❌ Not found"}

### Available Commands
"""
        
        if cli['commands']:
            for command in cli['commands']:
                report += f"- `{command}`\n"
        else:
            report += "- No commands detected\n"
        
        report += f"""
## 🎯 Key Strengths

1. **Modular Architecture**: Clear separation of concerns with specialized agent roles
2. **Comprehensive Data Integration**: Multiple financial data sources (FinnHub, Yahoo Finance, Reddit)
3. **Advanced AI Framework**: LangGraph-based multi-agent coordination
4. **Real-world Simulation**: Mirrors actual trading firm structure with analysts, researchers, traders
5. **Interactive Interface**: Rich CLI for user interaction
6. **Debate Mechanism**: Bull vs Bear researcher debates for balanced analysis

## ⚠️ Areas for Improvement

1. **Testing Infrastructure**: No visible test framework or test files
2. **Documentation**: Limited inline documentation in some components
3. **Error Handling**: Could benefit from more robust error handling
4. **Configuration Management**: Config handling could be more centralized
5. **Performance Monitoring**: No visible performance metrics or monitoring

## 🚀 Technical Recommendations

1. **Add Testing Suite**: Implement pytest-based testing for all components
2. **Enhance Documentation**: Add comprehensive docstrings and API documentation
3. **Improve Error Handling**: Add try-catch blocks and proper error reporting
4. **Add Logging**: Implement structured logging throughout the system
5. **Performance Optimization**: Add caching and performance monitoring
6. **Security**: Add API key validation and secure credential management

## 📊 Framework Capabilities

### Supported Analysis Types
- **Technical Analysis**: Market indicators, price patterns, volume analysis
- **Fundamental Analysis**: Financial statements, company metrics, valuation
- **Sentiment Analysis**: Social media sentiment, news sentiment
- **Risk Assessment**: Portfolio risk, market volatility, risk-adjusted returns

### Supported Data Sources
- FinnHub API for financial data
- Yahoo Finance for market data
- Reddit for social sentiment
- News APIs for market news
- Technical indicators via stockstats

## 🔧 Usage Patterns

### Programmatic Usage
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2024-05-10")
```

### CLI Usage
```bash
python -m cli.main
```

## 🎯 Conclusion

TradingAgents represents a sophisticated approach to AI-powered trading analysis, leveraging multiple specialized agents to provide comprehensive market insights. The framework successfully combines technical analysis, fundamental analysis, sentiment analysis, and risk management in a cohesive system that mirrors real-world trading operations.

The project demonstrates strong architectural principles with clear separation of concerns, modular design, and extensible components. With some improvements in testing, documentation, and error handling, this framework has the potential to be a powerful tool for trading research and analysis.

---
*Analysis completed by TradingAgents Project Analyzer*
"""
        
        return report

def main():
    """Main function to run the project analysis."""
    analyzer = ProjectAnalyzer()
    report = analyzer.generate_comprehensive_report()
    
    # Save report to file
    output_file = Path("project_analysis_report.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Analysis complete! Report saved to: {output_file}")
    print("\n" + "="*80)
    print(report)
    print("="*80)

if __name__ == "__main__":
    main()