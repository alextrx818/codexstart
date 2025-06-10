#!/usr/bin/env python3
"""
Data Flow Protocol Analyzer for 6-4-2025 Project
Extracts all data flow protocols, file interactions, and logic mappings
"""

import os
import json
import re
import ast
import subprocess
import sys
import socket
import psutil
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta, timedelta
from typing import Dict, List, Any, Tuple
import importlib.util

class DataFlowAnalyzer:
    def __init__(self, project_dir: str = "/root/6-4-2025"):
        self.project_dir = Path(project_dir)
        self.ssh_monitor_active = False
        self.network_monitor_active = False
        self.ssh_connections = []
        self.network_traffic = []
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "project_structure": {},
            "file_dependencies": {},
            "data_flow_maps": {},
            "function_mappings": {},
            "api_endpoints": {},
            "file_io_operations": {},
            "logging_flows": {},
            "process_interactions": {},
            "ssh_configurations": {},
            "network_protocols": {}
        }
        
    def analyze_project(self):
        """Main analysis function"""
        print("🔍 Starting comprehensive data flow analysis...")
        
        # 1. Project Structure Analysis
        self.analyze_project_structure()
        
        # 2. File Dependency Mapping
        self.analyze_file_dependencies()
        
        # 3. Data Flow Protocol Extraction
        self.analyze_data_flows()
        
        # 4. Function and Logic Mapping
        self.analyze_function_mappings()
        
        # 5. API and Network Analysis
        self.analyze_api_endpoints()
        
        # 6. File I/O Operations
        self.analyze_file_operations()
        
        # 7. Logging Flow Analysis
        self.analyze_logging_flows()
        
        # 8. Process Interaction Analysis
        self.analyze_process_interactions()
        
        # 9. SSH and Network Configuration
        self.analyze_ssh_network_config()
        
        # 10. Generate Reports
        self.generate_reports()
        
        return self.analysis_results
    
    def analyze_project_structure(self):
        """Analyze the complete project structure"""
        print("📁 Analyzing project structure...")
        
        structure = {}
        for root, dirs, files in os.walk(self.project_dir):
            rel_path = os.path.relpath(root, self.project_dir)
            if rel_path == ".":
                rel_path = "root"
                
            structure[rel_path] = {
                "directories": dirs,
                "files": []
            }
            
            for file in files:
                file_path = Path(root) / file
                file_info = {
                    "name": file,
                    "size": file_path.stat().st_size if file_path.exists() else 0,
                    "extension": file_path.suffix,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() if file_path.exists() else None
                }
                structure[rel_path]["files"].append(file_info)
        
        self.analysis_results["project_structure"] = structure
    
    def analyze_file_dependencies(self):
        """Analyze file dependencies and imports"""
        print("🔗 Analyzing file dependencies...")
        
        dependencies = {}
        python_files = list(self.project_dir.glob("*.py"))
        
        for py_file in python_files:
            deps = {
                "imports": [],
                "from_imports": [],
                "local_imports": [],
                "function_calls": [],
                "file_operations": []
            }
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse imports
                import_pattern = r'^import\s+(.+)$'
                from_import_pattern = r'^from\s+(.+)\s+import\s+(.+)$'
                
                for line in content.split('\n'):
                    line = line.strip()
                    
                    # Regular imports
                    import_match = re.match(import_pattern, line)
                    if import_match:
                        deps["imports"].append(import_match.group(1))
                    
                    # From imports
                    from_match = re.match(from_import_pattern, line)
                    if from_match:
                        deps["from_imports"].append({
                            "module": from_match.group(1),
                            "items": from_match.group(2)
                        })
                
                # Find local module imports (step1, step2, etc.)
                local_imports = re.findall(r'import\s+(step\d+)', content)
                deps["local_imports"] = list(set(local_imports))
                
                # Find function calls to other modules
                function_calls = re.findall(r'(step\d+\.\w+)\(', content)
                deps["function_calls"] = list(set(function_calls))
                
                # Find file operations
                file_ops = re.findall(r'(open|read|write|save|load)\s*\([^)]*["\']([^"\']+\.(json|log|txt|csv))["\']', content)
                deps["file_operations"] = [{"operation": op[0], "file": op[1]} for op in file_ops]
                
            except Exception as e:
                deps["error"] = str(e)
            
            dependencies[py_file.name] = deps
        
        self.analysis_results["file_dependencies"] = dependencies
    
    def analyze_data_flows(self):
        """Analyze data flow patterns and protocols"""
        print("🌊 Analyzing data flow patterns...")
        
        data_flows = {}
        
        # Analyze JSON data flow
        json_files = list(self.project_dir.glob("*.json"))
        for json_file in json_files:
            try:
                if json_file.stat().st_size < 50 * 1024 * 1024:  # Skip files larger than 50MB
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        data_flows[json_file.name] = {
                            "type": "json_data",
                            "structure": self._analyze_json_structure(data),
                            "size_kb": json_file.stat().st_size // 1024
                        }
            except Exception as e:
                data_flows[json_file.name] = {"error": str(e)}
        
        # Analyze log files for data flow patterns
        log_files = list(self.project_dir.glob("*.log"))
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    data_flows[log_file.name] = {
                        "type": "log_data",
                        "patterns": self._extract_log_patterns(content),
                        "size_kb": log_file.stat().st_size // 1024
                    }
            except Exception as e:
                data_flows[log_file.name] = {"error": str(e)}
        
        self.analysis_results["data_flow_maps"] = data_flows
    
    def analyze_function_mappings(self):
        """Analyze function definitions and their relationships"""
        print("⚙️ Analyzing function mappings...")
        
        function_maps = {}
        python_files = list(self.project_dir.glob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse AST for function definitions
                tree = ast.parse(content)
                functions = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = {
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "docstring": ast.get_docstring(node),
                            "calls": []
                        }
                        
                        # Find function calls within this function
                        for child in ast.walk(node):
                            if isinstance(child, ast.Call):
                                if isinstance(child.func, ast.Name):
                                    func_info["calls"].append(child.func.id)
                                elif isinstance(child.func, ast.Attribute):
                                    func_info["calls"].append(f"{child.func.value.id if hasattr(child.func.value, 'id') else '?'}.{child.func.attr}")
                        
                        functions.append(func_info)
                
                function_maps[py_file.name] = functions
                
            except Exception as e:
                function_maps[py_file.name] = {"error": str(e)}
        
        self.analysis_results["function_mappings"] = function_maps
    
    def analyze_api_endpoints(self):
        """Analyze API endpoints and network calls"""
        print("🌐 Analyzing API endpoints...")
        
        api_analysis = {}
        python_files = list(self.project_dir.glob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find URL patterns
                url_patterns = re.findall(r'["\']https?://[^"\']+["\']', content)
                
                # Find API calls
                api_calls = re.findall(r'(requests\.\w+|aiohttp\.\w+|urllib\.\w+)\s*\([^)]*', content)
                
                # Find async patterns
                async_patterns = re.findall(r'async\s+def\s+(\w+)', content)
                await_patterns = re.findall(r'await\s+(\w+)', content)
                
                api_analysis[py_file.name] = {
                    "urls": list(set(url_patterns)),
                    "api_calls": list(set(api_calls)),
                    "async_functions": async_patterns,
                    "await_calls": list(set(await_patterns))
                }
                
            except Exception as e:
                api_analysis[py_file.name] = {"error": str(e)}
        
        self.analysis_results["api_endpoints"] = api_analysis
    
    def analyze_file_operations(self):
        """Analyze file I/O operations"""
        print("📂 Analyzing file I/O operations...")
        
        file_ops = {}
        python_files = list(self.project_dir.glob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find file operations
                read_ops = re.findall(r'(open|read|load)\s*\([^)]*["\']([^"\']+)["\']', content)
                write_ops = re.findall(r'(write|save|dump)\s*\([^)]*["\']([^"\']+)["\']', content)
                
                # Find JSON operations
                json_ops = re.findall(r'json\.(load|dump|loads|dumps)', content)
                
                file_ops[py_file.name] = {
                    "read_operations": [{"operation": op[0], "file": op[1]} for op in read_ops],
                    "write_operations": [{"operation": op[0], "file": op[1]} for op in write_ops],
                    "json_operations": list(set(json_ops))
                }
                
            except Exception as e:
                file_ops[py_file.name] = {"error": str(e)}
        
        self.analysis_results["file_io_operations"] = file_ops
    
    def analyze_logging_flows(self):
        """Analyze logging configurations and flows"""
        print("📝 Analyzing logging flows...")
        
        logging_analysis = {}
        
        # Check for logging configurations
        config_files = ["log_config.py", "logging.conf", ".env"]
        for config_file in config_files:
            config_path = self.project_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        logging_analysis[config_file] = {
                            "type": "config",
                            "content_preview": content[:500],
                            "logging_patterns": re.findall(r'log\w*|LOG\w*', content)
                        }
                except Exception as e:
                    logging_analysis[config_file] = {"error": str(e)}
        
        # Analyze Python files for logging usage
        python_files = list(self.project_dir.glob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    logging_patterns = re.findall(r'(logging\.\w+|logger\.\w+|log\.\w+)\s*\([^)]*\)', content)
                    log_files = re.findall(r'["\']([^"\']*\.log)["\']', content)
                    
                    if logging_patterns or log_files:
                        logging_analysis[py_file.name] = {
                            "type": "usage",
                            "logging_calls": list(set(logging_patterns)),
                            "log_files": list(set(log_files))
                        }
                        
            except Exception as e:
                if py_file.name not in logging_analysis:
                    logging_analysis[py_file.name] = {"error": str(e)}
        
        self.analysis_results["logging_flows"] = logging_analysis
    
    def analyze_process_interactions(self):
        """Analyze process interactions and subprocess calls"""
        print("🔄 Analyzing process interactions...")
        
        process_analysis = {}
        
        # Check shell scripts
        shell_files = list(self.project_dir.glob("*.sh"))
        for shell_file in shell_files:
            try:
                with open(shell_file, 'r') as f:
                    content = f.read()
                    
                    # Find process commands
                    commands = re.findall(r'^\s*([a-zA-Z][a-zA-Z0-9_-]*)', content, re.MULTILINE)
                    python_calls = re.findall(r'python[0-9.]*\s+([^&\n]+)', content)
                    
                    process_analysis[shell_file.name] = {
                        "type": "shell_script",
                        "commands": list(set(commands)),
                        "python_calls": python_calls
                    }
                    
            except Exception as e:
                process_analysis[shell_file.name] = {"error": str(e)}
        
        # Check Python subprocess usage
        python_files = list(self.project_dir.glob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    subprocess_calls = re.findall(r'subprocess\.\w+\([^)]+\)', content)
                    os_system_calls = re.findall(r'os\.system\([^)]+\)', content)
                    
                    if subprocess_calls or os_system_calls:
                        process_analysis[py_file.name] = {
                            "type": "python_subprocess",
                            "subprocess_calls": subprocess_calls,
                            "os_system_calls": os_system_calls
                        }
                        
            except Exception as e:
                if py_file.name not in process_analysis:
                    process_analysis[py_file.name] = {"error": str(e)}
        
        self.analysis_results["process_interactions"] = process_analysis
    
    def analyze_ssh_network_config(self):
        """Analyze SSH and network configurations"""
        print("🔒 Analyzing SSH and network configurations...")
        
        ssh_network = {}
        
        # Check for SSH configurations
        ssh_configs = [".ssh/config", "ssh_config", ".env"]
        for config in ssh_configs:
            config_path = self.project_dir / config
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        ssh_network[config] = {
                            "type": "ssh_config",
                            "hosts": re.findall(r'Host\s+([^\s]+)', content),
                            "ports": re.findall(r'Port\s+(\d+)', content),
                            "users": re.findall(r'User\s+([^\s]+)', content)
                        }
                except Exception as e:
                    ssh_network[config] = {"error": str(e)}
        
        # Check Python files for network/SSH usage
        python_files = list(self.project_dir.glob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Find network-related imports and calls
                    network_imports = re.findall(r'import\s+(paramiko|ssh|socket|requests|aiohttp|urllib)', content)
                    ssh_calls = re.findall(r'(ssh|SSH|paramiko)\.\w+', content)
                    socket_calls = re.findall(r'socket\.\w+', content)
                    
                    if network_imports or ssh_calls or socket_calls:
                        ssh_network[py_file.name] = {
                            "type": "network_usage",
                            "network_imports": network_imports,
                            "ssh_calls": ssh_calls,
                            "socket_calls": socket_calls
                        }
                        
            except Exception as e:
                if py_file.name not in ssh_network:
                    ssh_network[py_file.name] = {"error": str(e)}
        
        self.analysis_results["ssh_configurations"] = ssh_network
    
    def start_ssh_monitoring(self):
        """Start SSH connection monitoring"""
        print("🔒 Starting SSH monitoring...")
        self.ssh_monitor_active = True
        
        def monitor_ssh():
            while self.ssh_monitor_active:
                try:
                    # Monitor SSH connections
                    connections = []
                    for conn in psutil.net_connections():
                        if conn.laddr.port == 22 or (conn.raddr and conn.raddr.port == 22):
                            connections.append({
                                "timestamp": datetime.now().isoformat(),
                                "local_addr": f"{conn.laddr.ip}:{conn.laddr.port}",
                                "remote_addr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "None",
                                "status": conn.status,
                                "pid": conn.pid
                            })
                    
                    self.ssh_connections.extend(connections)
                    
                    # Keep only last 100 connections
                    if len(self.ssh_connections) > 100:
                        self.ssh_connections = self.ssh_connections[-100:]
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    print(f"SSH monitoring error: {e}")
                    time.sleep(10)
        
        # Start monitoring in background thread
        ssh_thread = threading.Thread(target=monitor_ssh, daemon=True)
        ssh_thread.start()
    
    def start_network_monitoring(self):
        """Start network traffic monitoring"""
        print("🌐 Starting network monitoring...")
        self.network_monitor_active = True
        
        def monitor_network():
            while self.network_monitor_active:
                try:
                    # Get network connections
                    connections = psutil.net_connections()
                    active_connections = []
                    
                    for conn in connections:
                        if conn.status == 'ESTABLISHED':
                            active_connections.append({
                                "timestamp": datetime.now().isoformat(),
                                "local_addr": f"{conn.laddr.ip}:{conn.laddr.port}",
                                "remote_addr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "None",
                                "status": conn.status,
                                "pid": conn.pid
                            })
                    
                    self.network_traffic.extend(active_connections)
                    
                    # Keep only last 200 connections
                    if len(self.network_traffic) > 200:
                        self.network_traffic = self.network_traffic[-200:]
                    
                    time.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    print(f"Network monitoring error: {e}")
                    time.sleep(15)
        
        # Start monitoring in background thread
        network_thread = threading.Thread(target=monitor_network, daemon=True)
        network_thread.start()
    
    def stop_monitoring(self):
        """Stop all monitoring"""
        print("⏹️ Stopping all monitoring...")
        self.ssh_monitor_active = False
        self.network_monitor_active = False
    
    def get_ssh_status(self):
        """Get current SSH connection status"""
        return {
            "active_connections": len([c for c in self.ssh_connections if datetime.fromisoformat(c["timestamp"]) > datetime.now().replace(microsecond=0) - timedelta(minutes=5)]),
            "total_recorded": len(self.ssh_connections),
            "latest_connections": self.ssh_connections[-5:] if self.ssh_connections else []
        }
    
    def get_network_status(self):
        """Get current network status"""
        return {
            "active_connections": len([c for c in self.network_traffic if datetime.fromisoformat(c["timestamp"]) > datetime.now().replace(microsecond=0) - timedelta(minutes=5)]),
            "total_recorded": len(self.network_traffic),
            "latest_connections": self.network_traffic[-5:] if self.network_traffic else []
        }

    def run_complete_analysis(self, with_monitoring=True):
        """Run complete analysis with optional monitoring"""
        print("🚀 Starting Complete Data Flow Analysis...")
        print("="*60)
        
        # Start monitoring if requested
        if with_monitoring:
            self.start_ssh_monitoring()
            self.start_network_monitoring()
            time.sleep(2)  # Let monitoring start
        
        # Run all analysis methods
        self.analyze_project_structure()
        self.analyze_file_dependencies()
        self.analyze_data_flows()
        self.analyze_function_mappings()
        self.analyze_api_endpoints()
        self.analyze_file_operations()
        self.analyze_logging_flows()
        self.analyze_process_interactions()
        self.analyze_ssh_network_config()
        
        # Add monitoring results
        if with_monitoring:
            time.sleep(5)  # Collect some monitoring data
            self.analysis_results["ssh_monitoring"] = self.get_ssh_status()
            self.analysis_results["network_monitoring"] = self.get_network_status()
            self.stop_monitoring()
        
        # Generate reports
        self.generate_reports()
        
        return self.analysis_results
    
    def _analyze_json_structure(self, data, max_depth=3, current_depth=0):
        """Analyze JSON structure recursively"""
        if current_depth >= max_depth:
            return "max_depth_reached"
        
        if isinstance(data, dict):
            structure = {}
            for key, value in list(data.items())[:10]:  # Limit to first 10 keys
                structure[key] = self._analyze_json_structure(value, max_depth, current_depth + 1)
            return {"type": "dict", "keys": structure, "total_keys": len(data)}
        elif isinstance(data, list):
            if data:
                sample = self._analyze_json_structure(data[0], max_depth, current_depth + 1)
                return {"type": "list", "length": len(data), "sample_element": sample}
            return {"type": "list", "length": 0}
        else:
            return {"type": type(data).__name__, "value": str(data)[:100]}
    
    def _extract_log_patterns(self, content):
        """Extract patterns from log content"""
        lines = content.split('\n')
        patterns = {
            "timestamps": len(re.findall(r'\d{4}-\d{2}-\d{2}', content)),
            "error_levels": len(re.findall(r'(ERROR|WARN|INFO|DEBUG)', content)),
            "api_calls": len(re.findall(r'(GET|POST|PUT|DELETE)\s+/', content)),
            "total_lines": len(lines)
        }
        return patterns
    
    def generate_reports(self):
        """Generate comprehensive reports"""
        print("📊 Generating analysis reports...")
        
        # Save detailed analysis
        output_file = self.project_dir / "data_flow_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        # Generate summary report
        self._generate_summary_report()
        
        # Generate data flow diagram
        self._generate_flow_diagram()
        
        print(f"✅ Analysis complete! Reports saved to:")
        print(f"   - Detailed: {output_file}")
        print(f"   - Summary: {self.project_dir}/data_flow_summary.txt")
        print(f"   - Diagram: {self.project_dir}/data_flow_diagram.txt")
    
    def _generate_summary_report(self):
        """Generate human-readable summary report"""
        summary_file = self.project_dir / "data_flow_summary.txt"
        
        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DATA FLOW AND ARCHITECTURE ANALYSIS SUMMARY\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Analysis Timestamp: {self.analysis_results['timestamp']}\n")
            f.write(f"Project Directory: {self.project_dir}\n\n")
            
            # Project Structure Summary
            f.write("PROJECT STRUCTURE:\n")
            f.write("-" * 40 + "\n")
            for path, info in self.analysis_results["project_structure"].items():
                f.write(f"{path}/\n")
                for file_info in info["files"]:
                    size_kb = file_info["size"] // 1024 if file_info["size"] else 0
                    f.write(f"  - {file_info['name']} ({size_kb}KB)\n")
                f.write("\n")
            
            # File Dependencies Summary
            f.write("FILE DEPENDENCIES:\n")
            f.write("-" * 40 + "\n")
            for file, deps in self.analysis_results["file_dependencies"].items():
                if "error" not in deps:
                    f.write(f"{file}:\n")
                    if deps["local_imports"]:
                        f.write(f"  Local imports: {', '.join(deps['local_imports'])}\n")
                    if deps["function_calls"]:
                        f.write(f"  Function calls: {', '.join(deps['function_calls'])}\n")
                    f.write("\n")
            
            # API Endpoints Summary
            f.write("API ENDPOINTS AND NETWORK:\n")
            f.write("-" * 40 + "\n")
            for file, api_info in self.analysis_results["api_endpoints"].items():
                if "error" not in api_info and (api_info["urls"] or api_info["async_functions"]):
                    f.write(f"{file}:\n")
                    if api_info["urls"]:
                        f.write(f"  URLs: {', '.join(api_info['urls'][:3])}\n")
                    if api_info["async_functions"]:
                        f.write(f"  Async functions: {', '.join(api_info['async_functions'])}\n")
                    f.write("\n")
            
            # Data Flow Summary
            f.write("DATA FLOW FILES:\n")
            f.write("-" * 40 + "\n")
            for file, flow_info in self.analysis_results["data_flow_maps"].items():
                if "error" not in flow_info:
                    f.write(f"{file} ({flow_info['size_kb']}KB) - {flow_info['type']}\n")
            f.write("\n")
    
    def _generate_flow_diagram(self):
        """Generate ASCII flow diagram"""
        diagram_file = self.project_dir / "data_flow_diagram.txt"
        
        with open(diagram_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DATA FLOW DIAGRAM\n")
            f.write("="*80 + "\n\n")
            
            f.write("MAIN PIPELINE FLOW:\n")
            f.write("-" * 40 + "\n")
            f.write("start.sh\n")
            f.write("    ↓\n")
            f.write("step1.py (API Collection)\n")
            f.write("    ↓ (writes)\n")
            f.write("step1.json\n")
            f.write("    ↓ (reads)\n")
            f.write("step2.py (Data Processing)\n")
            f.write("    ↓ (writes)\n")
            f.write("step2.json\n")
            f.write("    ↓ (reads)\n")
            f.write("step7.py (Filtering)\n")
            f.write("    ↓ (writes)\n")
            f.write("step7_matches.log\n\n")
            
            f.write("FILE INTERACTION MATRIX:\n")
            f.write("-" * 40 + "\n")
            
            # Create interaction matrix
            files = list(self.analysis_results["file_dependencies"].keys())
            f.write(f"{'File':<20} {'Reads From':<30} {'Writes To':<30}\n")
            f.write("-" * 80 + "\n")
            
            for file in files:
                deps = self.analysis_results["file_dependencies"][file]
                if "error" not in deps:
                    reads = ", ".join([op["file"] for op in deps.get("file_operations", []) if op["operation"] in ["read", "load", "open"]])
                    writes = ", ".join([op["file"] for op in deps.get("file_operations", []) if op["operation"] in ["write", "save", "dump"]])
                    
                    f.write(f"{file:<20} {reads[:28]:<30} {writes[:28]:<30}\n")


def main():
    """Main execution function"""
    print("🚀 Starting Data Flow Protocol Analyzer...")
    
    analyzer = DataFlowAnalyzer()
    results = analyzer.analyze_project()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    
    # Print key findings
    print(f"\nKEY FINDINGS:")
    print(f"- Python files analyzed: {len([f for f in results['file_dependencies'].keys() if f.endswith('.py')])}")
    print(f"- Data files found: {len(results['data_flow_maps'])}")
    print(f"- Network endpoints detected: {sum(len(api['urls']) for api in results['api_endpoints'].values() if 'urls' in api)}")
    
    return results

if __name__ == "__main__":
    main()
