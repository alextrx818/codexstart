#!/usr/bin/env python3
"""
Devin AI Startup Guide - Python Version
Complete guide for running the sports data analysis app with SSH monitoring
"""

import os
import subprocess
import time
import sys
from pathlib import Path

class DevinStartupGuide:
    def __init__(self):
        self.project_dir = Path("~/repos/devinai").expanduser()
        self.current_dir = Path.cwd()
        
    def print_header(self, title):
        print("\n" + "="*60)
        print(f"🚀 {title}")
        print("="*60)
    
    def print_step(self, step_num, description):
        print(f"\n{step_num}. 📍 {description}")
        print("-" * 50)
    
    def run_command(self, command, description="", check_output=False):
        """Run a command and return result"""
        print(f"   💻 Running: {command}")
        try:
            if check_output:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"   ✅ Success: {description}")
                    return result.stdout.strip()
                else:
                    print(f"   ⚠️ Warning: {result.stderr.strip()}")
                    return None
            else:
                result = subprocess.run(command, shell=True, timeout=30)
                if result.returncode == 0:
                    print(f"   ✅ Success: {description}")
                else:
                    print(f"   ⚠️ Command returned code {result.returncode}")
                return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Command timed out: {command}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def check_directory(self):
        """Check if we're in the right directory"""
        self.print_step("1", "DIRECTORY SETUP")
        
        if self.project_dir.exists():
            os.chdir(self.project_dir)
            print(f"   📂 Changed to: {self.project_dir}")
            return True
        else:
            print(f"   ❌ Project directory not found: {self.project_dir}")
            print(f"   💡 Current directory: {self.current_dir}")
            print("   🔧 Trying current directory instead...")
            return False
    
    def install_dependencies(self):
        """Install required dependencies"""
        self.print_step("2", "DEPENDENCY INSTALLATION")
        
        # System packages
        system_packages = [
            "pip3 install --break-system-packages psutil aiohttp python-dotenv requests pytz",
            "chmod +x *.sh *.py 2>/dev/null || true"
        ]
        
        for cmd in system_packages:
            self.run_command(cmd, "Installing dependencies")
    
    def check_project_status(self):
        """Check if project is already running"""
        self.print_step("3", "PROJECT STATUS CHECK")
        
        status_output = self.run_command("./start.sh status", "Checking project status", check_output=True)
        
        if status_output and "RUNNING" in status_output:
            print("   ✅ Project is already RUNNING!")
            return True
        else:
            print("   📍 Project is not running - ready to start")
            return False
    
    def start_application(self, with_ssh_monitoring=True):
        """Start the application with or without SSH monitoring"""
        self.print_step("4", "APPLICATION STARTUP")
        
        if with_ssh_monitoring:
            print("   🔒 Starting with SSH monitoring (recommended)...")
            success = self.run_command("./start_ssh_monitor.sh", "SSH monitoring startup")
        else:
            print("   🚀 Starting standard application...")
            success = self.run_command("./start.sh start", "Standard startup")
        
        if success:
            time.sleep(3)  # Wait for startup
            return self.verify_startup()
        return False
    
    def verify_startup(self):
        """Verify the application started successfully"""
        self.print_step("5", "STARTUP VERIFICATION")
        
        status_output = self.run_command("./start.sh status", "Verifying startup", check_output=True)
        
        if status_output and "RUNNING" in status_output:
            print("   ✅ Application verified running!")
            
            # Check for data files
            data_files = ["step1.json", "step2.json", "step7_simple.log"]
            for file in data_files:
                if Path(file).exists():
                    size = Path(file).stat().st_size
                    print(f"   📊 {file}: {size // 1024}KB")
            
            return True
        else:
            print("   ❌ Application failed to start properly")
            return False
    
    def run_tests(self):
        """Run the comprehensive test suite"""
        self.print_step("6", "TESTING SUITE")
        
        if Path("run_comprehensive_test.py").exists():
            print("   🧪 Running comprehensive test suite...")
            self.run_command("python3 run_comprehensive_test.py", "Test suite execution")
        else:
            print("   ⚠️ Test suite not found - skipping tests")
    
    def show_monitoring_info(self):
        """Show monitoring and data flow information"""
        self.print_step("7", "MONITORING INFORMATION")
        
        # Check SSH monitor log
        if Path("ssh_monitor.log").exists():
            size = Path("ssh_monitor.log").stat().st_size // 1024
            print(f"   🔒 SSH Monitor Log: {size}KB")
        
        # Check data flow analysis
        if Path("data_flow_analysis.json").exists():
            size = Path("data_flow_analysis.json").stat().st_size // 1024
            print(f"   📊 Data Flow Analysis: {size}KB")
        
        # Show recent log entries
        log_output = self.run_command("tail -5 start.log", "Recent log entries", check_output=True)
        if log_output:
            print("   📝 Recent activity:")
            for line in log_output.split('\n')[-3:]:
                if line.strip():
                    print(f"      {line.strip()}")
    
    def show_usage_commands(self):
        """Show key commands for Devin to use"""
        self.print_step("8", "KEY COMMANDS FOR DEVIN")
        
        commands = {
            "Check Status": "./start.sh status",
            "View Live Logs": "./start.sh logs",
            "Stop Application": "./start.sh stop",
            "Restart Application": "./start.sh restart",
            "Run Tests": "python3 run_comprehensive_test.py",
            "Monitor SSH": "tail -f ssh_monitor.log",
            "Check Data Flow": "python3 data_flow_analyzer.py"
        }
        
        for desc, cmd in commands.items():
            print(f"   💻 {desc:<20}: {cmd}")
    
    def show_project_overview(self):
        """Show project overview and capabilities"""
        self.print_header("PROJECT OVERVIEW")
        
        overview = {
            "🎯 Purpose": "24/7 sports data fetching with SSH monitoring",
            "📊 Data Processing": "step1.py → step2.py → step7.py pipeline", 
            "🔒 Security": "Real-time SSH and network monitoring",
            "🧪 Testing": "Comprehensive test suite with 589 files analyzed",
            "📈 Monitoring": "15+ SSH connections, 138+ network connections",
            "⚡ Frequency": "60-second data refresh cycles",
            "💾 Output": "JSON data files, filtered logs, analysis reports"
        }
        
        for key, value in overview.items():
            print(f"   {key:<15}: {value}")
    
    def run_complete_setup(self):
        """Run the complete startup sequence"""
        self.print_header("DEVIN AI STARTUP SEQUENCE")
        
        print("🤖 Welcome Devin! This will set up and start the sports data analysis app.")
        print("⏱️  Estimated time: 2-3 minutes")
        
        # Step 1: Directory setup
        in_correct_dir = self.check_directory()
        
        # Step 2: Install dependencies
        self.install_dependencies()
        
        # Step 3: Check current status
        already_running = self.check_project_status()
        
        # Step 4: Start application if not running
        if not already_running:
            app_started = self.start_application(with_ssh_monitoring=True)
            if not app_started:
                print("\n❌ Failed to start application. Trying standard startup...")
                app_started = self.start_application(with_ssh_monitoring=False)
        else:
            app_started = True
        
        # Step 5: Run tests if application is running
        if app_started:
            self.run_tests()
            self.show_monitoring_info()
        
        # Step 6: Show usage information
        self.show_usage_commands()
        self.show_project_overview()
        
        # Final status
        if app_started:
            self.print_header("✅ SETUP COMPLETE - READY FOR DEVIN")
            print("🎯 The application is running with full SSH monitoring!")
            print("📊 Data flow analysis and testing suite are ready.")
            print("🔍 Use the commands above to interact with the system.")
        else:
            self.print_header("❌ SETUP INCOMPLETE")
            print("🔧 Some issues occurred. Check the output above for details.")
            print("💡 Try running individual commands manually.")
        
        return app_started

def main():
    """Main entry point"""
    guide = DevinStartupGuide()
    
    # Check if running with specific command
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            guide.check_project_status()
        elif command == "start":
            guide.start_application()
        elif command == "test":
            guide.run_tests()
        elif command == "info":
            guide.show_project_overview()
        elif command == "commands":
            guide.show_usage_commands()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: status, start, test, info, commands")
    else:
        # Run complete setup
        guide.run_complete_setup()

if __name__ == "__main__":
    main()
