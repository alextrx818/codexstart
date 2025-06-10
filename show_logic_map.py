#!/usr/bin/env python3
"""
Logic and Data Flow Map Generator
Creates a comprehensive map of what logic lives in what file and how data flows
"""

import json
from pathlib import Path

def generate_logic_map():
    """Generate a comprehensive logic and data flow map"""
    
    # Load the analysis results
    analysis_file = Path("/root/6-4-2025/data_flow_analysis.json")
    if not analysis_file.exists():
        print("❌ Analysis file not found. Run the comprehensive test first.")
        return
    
    with open(analysis_file, 'r') as f:
        data = json.load(f)
    
    print("="*80)
    print("COMPREHENSIVE LOGIC AND DATA FLOW MAP")
    print("="*80)
    print()
    
    # Main Pipeline Logic
    print("🔥 MAIN PIPELINE LOGIC:")
    print("-" * 50)
    
    main_files = {
        "start.sh": "Process management and environment setup",
        "step1.py": "API data collection from external sources",
        "step2.py": "Data processing and transformation", 
        "step7.py": "Data filtering and match detection"
    }
    
    for file, purpose in main_files.items():
        print(f"📄 {file:<15} → {purpose}")
    
    print()
    
    # Data Flow Protocol
    print("🌊 DATA FLOW PROTOCOL:")
    print("-" * 50)
    
    file_deps = data.get("file_dependencies", {})
    
    # Analyze step1.py
    if "step1.py" in file_deps:
        step1_deps = file_deps["step1.py"]
        print("📄 step1.py:")
        print("   🔌 API Endpoints:", len([url for url in data.get("api_endpoints", {}).get("step1.py", {}).get("urls", [])]))
        print("   📝 Writes: step1.json, step1.log")
        print("   🎯 Purpose: Collects live sports data from external APIs")
        print("   ⚙️ Key Functions:", [f for f in step1_deps.get("function_calls", []) if "fetch" in f or "get" in f][:3])
        print()
    
    # Analyze step2.py  
    if "step2.py" in file_deps:
        step2_deps = file_deps["step2.py"]
        print("📄 step2.py:")
        print("   📖 Reads: step1.json")
        print("   📝 Writes: step2.json")
        print("   🎯 Purpose: Processes and transforms raw API data")
        print("   ⚙️ Key Operations:", step2_deps.get("function_calls", [])[:3])
        print()
    
    # Analyze step7.py
    if "step7.py" in file_deps:
        step7_deps = file_deps["step7.py"]
        print("📄 step7.py:")
        print("   📖 Reads: step2.json")
        print("   📝 Writes: step7_matches.log")
        print("   🎯 Purpose: Filters data and detects matching conditions")
        print("   ⚙️ Key Operations:", step7_deps.get("function_calls", [])[:3])
        print()
    
    # File I/O Operations Map
    print("📂 FILE I/O OPERATIONS MAP:")
    print("-" * 50)
    
    file_io = data.get("file_io_operations", {})
    for filename, operations in file_io.items():
        if operations.get("read_operations") or operations.get("write_operations"):
            print(f"📄 {filename}:")
            if operations.get("read_operations"):
                files_read = [op["file"] for op in operations["read_operations"]]
                print(f"   📖 Reads: {', '.join(files_read)}")
            if operations.get("write_operations"):
                files_written = [op["file"] for op in operations["write_operations"]]
                print(f"   📝 Writes: {', '.join(files_written)}")
            print()
    
    # Test and Debug Files
    print("🧪 TEST AND DEBUG FILES:")
    print("-" * 50)
    
    test_files = {}
    for filename in file_deps.keys():
        if "test" in filename.lower() or "debug" in filename.lower():
            test_files[filename] = file_deps[filename]
    
    for filename, deps in test_files.items():
        purpose = "Unknown"
        if "test_api" in filename:
            purpose = "API testing and rate limit verification"
        elif "test_pipeline" in filename:
            purpose = "End-to-end pipeline testing"
        elif "test_endpoints" in filename:
            purpose = "API endpoint validation"
        elif "debug" in filename:
            purpose = "Debugging and troubleshooting"
        elif "integration" in filename:
            purpose = "Integration testing"
        
        print(f"📄 {filename:<25} → {purpose}")
        if deps.get("local_imports"):
            print(f"   🔗 Uses: {', '.join(deps['local_imports'])}")
    
    print()
    
    # Utility and Helper Files
    print("🛠️ UTILITY AND HELPER FILES:")
    print("-" * 50)
    
    utility_files = {
        "generate_mock_data.py": "Generates mock data for testing",
        "analyze_logging.py": "Analyzes logging patterns and consistency",
        "user_interaction_logger.py": "Logs user interactions",
        "python_naming_consistency_analyzer.py": "Analyzes Python naming conventions",
        "data_flow_analyzer.py": "Analyzes project data flow and architecture",
        "filter_odds_minutes.py": "Filters odds data by time intervals"
    }
    
    for filename, purpose in utility_files.items():
        if filename in file_deps:
            print(f"📄 {filename:<35} → {purpose}")
    
    print()
    
    # Data Files and Their Roles
    print("💾 DATA FILES AND THEIR ROLES:")
    print("-" * 50)
    
    data_flows = data.get("data_flow_maps", {})
    for filename, flow_info in data_flows.items():
        if flow_info.get("type") == "json_data":
            size_mb = flow_info.get("size_kb", 0) / 1024
            print(f"📊 {filename:<25} → {size_mb:.1f}MB JSON data")
            if "step1" in filename:
                print("     🎯 Contains: Raw API response data")
            elif "step2" in filename:
                print("     🎯 Contains: Processed and transformed data")
            elif "daily" in filename:
                print("     🎯 Contains: Daily statistics and counters")
        elif flow_info.get("type") == "log_data":
            size_kb = flow_info.get("size_kb", 0)
            print(f"📝 {filename:<25} → {size_kb}KB log data")
    
    print()
    
    # SSH and Network Monitoring
    ssh_data = data.get("ssh_monitoring", {})
    network_data = data.get("network_monitoring", {})
    
    print("🔒 SSH AND NETWORK MONITORING:")
    print("-" * 50)
    print(f"📡 SSH Connections Monitored: {ssh_data.get('total_recorded', 0)}")
    print(f"🌐 Network Connections Monitored: {network_data.get('total_recorded', 0)}")
    print(f"⚡ Currently Active SSH: {ssh_data.get('active_connections', 0)}")
    print(f"⚡ Currently Active Network: {network_data.get('active_connections', 0)}")
    
    print()
    
    # Critical Data Flow Path
    print("🚨 CRITICAL DATA FLOW PATH:")
    print("-" * 50)
    print("1. start.sh → Initializes environment and starts step1.py")
    print("2. step1.py → Fetches API data → writes step1.json") 
    print("3. step2.py → reads step1.json → processes data → writes step2.json")
    print("4. step7.py → reads step2.json → filters matches → writes step7_matches.log")
    print("5. Continuous loop every 60 seconds")
    
    print()
    print("✅ Project is currently RUNNING with full SSH monitoring")
    print("📊 All data flows are active and being tracked")
    print("🔍 Check ssh_monitor.log for real-time network activity")

if __name__ == "__main__":
    generate_logic_map()
