#!/usr/bin/env python3
"""
Comprehensive Test Script for Data Flow Analysis with SSH Monitoring
This script starts the project, monitors data flow, and runs comprehensive analysis
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append('/root/6-4-2025')

from data_flow_analyzer import DataFlowAnalyzer

class ProjectTester:
    def __init__(self):
        self.project_dir = Path("/root/6-4-2025")
        self.analyzer = DataFlowAnalyzer(str(self.project_dir))
        self.test_results = {}
        
    def print_status(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def print_section(self, title):
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def check_project_status(self):
        """Check if project is currently running"""
        self.print_status("Checking project status...")
        
        try:
            result = subprocess.run(
                ["./start.sh", "status"], 
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            is_running = "RUNNING" in result.stdout
            self.test_results["initial_status"] = {
                "running": is_running,
                "output": result.stdout,
                "error": result.stderr
            }
            
            if is_running:
                self.print_status("✅ Project is currently running")
            else:
                self.print_status("⏸️ Project is not running")
                
            return is_running
            
        except Exception as e:
            self.print_status(f"❌ Error checking status: {e}")
            return False
    
    def stop_project(self):
        """Stop the project if running"""
        self.print_status("Stopping project...")
        
        try:
            result = subprocess.run(
                ["./start.sh", "stop"], 
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.test_results["stop_result"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
            if result.returncode == 0:
                self.print_status("✅ Project stopped successfully")
            else:
                self.print_status(f"⚠️ Stop command returned code {result.returncode}")
                
            time.sleep(2)  # Wait for cleanup
            
        except Exception as e:
            self.print_status(f"❌ Error stopping project: {e}")
    
    def start_project_with_ssh_monitoring(self):
        """Start project with SSH monitoring"""
        self.print_status("Starting project with SSH monitoring...")
        
        try:
            # Start the SSH monitoring version
            result = subprocess.run(
                ["./start_ssh_monitor.sh"], 
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self.test_results["ssh_start_result"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
            if result.returncode == 0:
                self.print_status("✅ Project started with SSH monitoring")
            else:
                self.print_status(f"⚠️ SSH monitoring start returned code {result.returncode}")
                # Try regular start as fallback
                self.print_status("Trying regular start as fallback...")
                fallback_result = subprocess.run(
                    ["./start.sh", "start"], 
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                self.test_results["fallback_start"] = {
                    "success": fallback_result.returncode == 0,
                    "output": fallback_result.stdout,
                    "error": fallback_result.stderr
                }
            
            # Wait for project to initialize
            time.sleep(5)
            
        except Exception as e:
            self.print_status(f"❌ Error starting project: {e}")
    
    def verify_project_running(self):
        """Verify the project is running correctly"""
        self.print_status("Verifying project is running...")
        
        try:
            result = subprocess.run(
                ["./start.sh", "status"], 
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            is_running = "RUNNING" in result.stdout
            self.test_results["verification"] = {
                "running": is_running,
                "output": result.stdout,
                "error": result.stderr
            }
            
            if is_running:
                self.print_status("✅ Project verified running")
                return True
            else:
                self.print_status("❌ Project not running after start attempt")
                return False
                
        except Exception as e:
            self.print_status(f"❌ Error verifying project: {e}")
            return False
    
    def run_data_flow_analysis(self):
        """Run comprehensive data flow analysis"""
        self.print_status("Starting comprehensive data flow analysis...")
        
        try:
            # Run analysis with monitoring
            analysis_results = self.analyzer.run_complete_analysis(with_monitoring=True)
            
            self.test_results["analysis_results"] = {
                "success": True,
                "summary": {
                    "files_analyzed": len(analysis_results.get("project_structure", {})),
                    "dependencies_found": len(analysis_results.get("file_dependencies", {})),
                    "api_endpoints": len(analysis_results.get("api_endpoints", {})),
                    "data_flows": len(analysis_results.get("data_flow_maps", {})),
                    "ssh_connections": analysis_results.get("ssh_monitoring", {}).get("total_recorded", 0),
                    "network_connections": analysis_results.get("network_monitoring", {}).get("total_recorded", 0)
                }
            }
            
            self.print_status("✅ Data flow analysis completed successfully")
            return True
            
        except Exception as e:
            self.print_status(f"❌ Error during analysis: {e}")
            self.test_results["analysis_results"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def check_generated_files(self):
        """Check what files were generated"""
        self.print_status("Checking generated files...")
        
        expected_files = [
            "data_flow_analysis.json",
            "data_flow_summary.txt", 
            "data_flow_diagram.txt",
            "ssh_monitor.log"
        ]
        
        file_status = {}
        for filename in expected_files:
            file_path = self.project_dir / filename
            if file_path.exists():
                size_kb = file_path.stat().st_size // 1024
                file_status[filename] = {"exists": True, "size_kb": size_kb}
                self.print_status(f"✅ {filename} ({size_kb}KB)")
            else:
                file_status[filename] = {"exists": False, "size_kb": 0}
                self.print_status(f"❌ {filename} (missing)")
        
        self.test_results["generated_files"] = file_status
    
    def test_data_flow_protocols(self):
        """Test specific data flow protocols"""
        self.print_status("Testing data flow protocols...")
        
        protocols_tested = {}
        
        # Test JSON data flow
        json_files = list(self.project_dir.glob("*.json"))
        protocols_tested["json_files"] = len(json_files)
        
        # Test log files
        log_files = list(self.project_dir.glob("*.log"))
        protocols_tested["log_files"] = len(log_files)
        
        # Test Python files
        py_files = list(self.project_dir.glob("*.py"))
        protocols_tested["python_files"] = len(py_files)
        
        # Test if data is flowing (check file timestamps)
        recent_files = []
        current_time = time.time()
        for file_path in self.project_dir.iterdir():
            if file_path.is_file():
                mod_time = file_path.stat().st_mtime
                if current_time - mod_time < 300:  # Modified in last 5 minutes
                    recent_files.append(file_path.name)
        
        protocols_tested["recently_modified"] = recent_files
        
        self.test_results["protocol_tests"] = protocols_tested
        
        self.print_status(f"✅ Found {len(json_files)} JSON files, {len(log_files)} log files")
        self.print_status(f"✅ {len(recent_files)} files modified recently")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_status("Generating test report...")
        
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration": "N/A",  # Could calculate if we track start time
            "results": self.test_results
        }
        
        # Save detailed test results
        report_file = self.project_dir / "test_results.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate human-readable summary
        summary_file = self.project_dir / "test_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PROJECT TEST RESULTS SUMMARY\n")
            f.write("="*80 + "\n\n")
            f.write(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Project Status
            f.write("PROJECT STATUS:\n")
            f.write("-" * 40 + "\n")
            if self.test_results.get("verification", {}).get("running"):
                f.write("✅ Project is running successfully\n")
            else:
                f.write("❌ Project failed to start or is not running\n")
            f.write("\n")
            
            # Analysis Results
            f.write("DATA FLOW ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            analysis = self.test_results.get("analysis_results", {})
            if analysis.get("success"):
                summary = analysis.get("summary", {})
                f.write(f"✅ Analysis completed successfully\n")
                f.write(f"   - Files analyzed: {summary.get('files_analyzed', 0)}\n")
                f.write(f"   - Dependencies found: {summary.get('dependencies_found', 0)}\n")
                f.write(f"   - API endpoints: {summary.get('api_endpoints', 0)}\n")
                f.write(f"   - Data flows: {summary.get('data_flows', 0)}\n")
                f.write(f"   - SSH connections monitored: {summary.get('ssh_connections', 0)}\n")
                f.write(f"   - Network connections monitored: {summary.get('network_connections', 0)}\n")
            else:
                f.write(f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}\n")
            f.write("\n")
            
            # Generated Files
            f.write("GENERATED FILES:\n")
            f.write("-" * 40 + "\n")
            files = self.test_results.get("generated_files", {})
            for filename, info in files.items():
                if info["exists"]:
                    f.write(f"✅ {filename} ({info['size_kb']}KB)\n")
                else:
                    f.write(f"❌ {filename} (missing)\n")
            f.write("\n")
        
        self.print_status(f"✅ Test report saved to {report_file}")
        self.print_status(f"✅ Test summary saved to {summary_file}")
    
    def run_comprehensive_test(self):
        """Run the complete test suite"""
        self.print_section("COMPREHENSIVE PROJECT TEST WITH SSH MONITORING")
        
        start_time = time.time()
        
        # Step 1: Check initial status
        self.print_section("STEP 1: CHECKING INITIAL STATUS")
        initial_running = self.check_project_status()
        
        # Step 2: Stop if running
        if initial_running:
            self.print_section("STEP 2: STOPPING EXISTING PROJECT")
            self.stop_project()
        
        # Step 3: Start with SSH monitoring
        self.print_section("STEP 3: STARTING WITH SSH MONITORING")
        self.start_project_with_ssh_monitoring()
        
        # Step 4: Verify running
        self.print_section("STEP 4: VERIFYING PROJECT STATUS")
        running = self.verify_project_running()
        
        if running:
            # Step 5: Run data flow analysis
            self.print_section("STEP 5: RUNNING DATA FLOW ANALYSIS")
            self.run_data_flow_analysis()
            
            # Step 6: Test protocols
            self.print_section("STEP 6: TESTING DATA FLOW PROTOCOLS")
            self.test_data_flow_protocols()
            
            # Step 7: Check generated files
            self.print_section("STEP 7: CHECKING GENERATED FILES")
            self.check_generated_files()
        else:
            self.print_status("❌ Cannot proceed with analysis - project not running")
        
        # Step 8: Generate report
        self.print_section("STEP 8: GENERATING TEST REPORT")
        self.generate_test_report()
        
        # Final summary
        end_time = time.time()
        duration = int(end_time - start_time)
        
        self.print_section("TEST COMPLETED")
        self.print_status(f"Total test duration: {duration} seconds")
        
        if running and self.test_results.get("analysis_results", {}).get("success"):
            self.print_status("✅ ALL TESTS PASSED - Project is running with full monitoring")
        else:
            self.print_status("❌ SOME TESTS FAILED - Check detailed results")
        
        return self.test_results

def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive Project Test...")
    
    tester = ProjectTester()
    results = tester.run_comprehensive_test()
    
    print("\n" + "="*60)
    print("📋 QUICK SUMMARY:")
    print("-" * 30)
    
    # Show key results
    if results.get("verification", {}).get("running"):
        print("✅ Project Status: RUNNING")
    else:
        print("❌ Project Status: NOT RUNNING")
    
    if results.get("analysis_results", {}).get("success"):
        summary = results["analysis_results"]["summary"]
        print(f"✅ Analysis: {summary['files_analyzed']} files, {summary['dependencies_found']} deps")
        print(f"📊 Monitoring: {summary['ssh_connections']} SSH, {summary['network_connections']} network")
    else:
        print("❌ Analysis: FAILED")
    
    print("\n📁 Check these files for detailed results:")
    print("   - test_results.json (detailed)")
    print("   - test_summary.txt (summary)")
    print("   - data_flow_analysis.json (analysis)")
    print("   - ssh_monitor.log (monitoring)")
    
    return 0 if results.get("verification", {}).get("running") else 1

if __name__ == "__main__":
    sys.exit(main())
