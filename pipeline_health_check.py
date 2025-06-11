#!/usr/bin/env python3
"""
Pipeline Health Check Tool
==========================
This tool helps identify and fix common pipeline issues:
- Wrong file paths
- Missing data fields
- Import errors
- Configuration mismatches
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import importlib.util

class PipelineHealthCheck:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.issues = []
        self.warnings = []
        
    def check_file_paths(self):
        """Check if all expected files exist and are being used correctly"""
        print("\n🔍 Checking File Paths...")
        
        expected_files = {
            'step1.py': 'Main data fetcher',
            'step2.py': 'Data processor',
            'step7.py': 'Match filter and display',
            'oddsconfig.py': 'Odds configuration',
            'start.sh': 'Pipeline starter',
            '.env': 'Environment variables',
            'requirements.txt': 'Dependencies'
        }
        
        for file, desc in expected_files.items():
            path = self.base_dir / file
            if path.exists():
                print(f"  ✅ {file}: Found ({desc})")
            else:
                if file == '.env':
                    print(f"  ⚠️  {file}: Missing (copy from .env.template)")
                    self.warnings.append(f"{file} missing - copy from .env.template")
                else:
                    print(f"  ❌ {file}: MISSING! ({desc})")
                    self.issues.append(f"{file} is missing")
    
    def check_imports(self):
        """Check if all imports in main files are correct"""
        print("\n🔍 Checking Imports...")
        
        files_to_check = ['step1.py', 'step2.py', 'step7.py']
        
        for file in files_to_check:
            filepath = self.base_dir / file
            if not filepath.exists():
                continue
                
            print(f"\n  Checking {file}:")
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Check for common import issues
            lines = content.split('\n')
            for i, line in enumerate(lines[:50], 1):  # Check first 50 lines
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    # Check for relative imports that might fail
                    if 'from .' in line or 'import .' in line:
                        print(f"    ⚠️  Line {i}: Relative import - {line.strip()}")
                        self.warnings.append(f"{file}:{i} has relative import")
                    
                    # Check for importing wrong step files
                    if 'step' in line and file == 'step7.py':
                        if 'step2' not in line and 'step1' not in line:
                            print(f"    ⚠️  Line {i}: Unusual step import - {line.strip()}")
    
    def check_data_flow(self):
        """Check if data is flowing correctly between steps"""
        print("\n🔍 Checking Data Flow...")
        
        # Check step1.json
        step1_json = self.base_dir / 'step1.json'
        if step1_json.exists():
            with open(step1_json, 'r') as f:
                step1_data = json.load(f)
            print(f"  ✅ step1.json: Found ({len(step1_data.get('live_matches', {}).get('data', []))} matches)")
        else:
            print("  ❌ step1.json: MISSING!")
            self.issues.append("step1.json missing - run step1.py first")
            return
        
        # Check step2.json
        step2_json = self.base_dir / 'step2.json'
        if step2_json.exists():
            with open(step2_json, 'r') as f:
                step2_data = json.load(f)
            summaries = step2_data.get('summaries', [])
            print(f"  ✅ step2.json: Found ({len(summaries)} summaries)")
            
            # Check for odds data
            matches_with_odds = sum(1 for m in summaries if m.get('money_line') and len(m.get('money_line', [])) > 0)
            print(f"     - Matches with odds: {matches_with_odds}/{len(summaries)}")
            
            if matches_with_odds == 0 and len(summaries) > 0:
                self.warnings.append("No matches have odds data in step2.json")
        else:
            print("  ❌ step2.json: MISSING!")
            self.issues.append("step2.json missing - run step2.py first")
            return
        
        # Check step7_simple.log
        step7_log = self.base_dir / 'step7_simple.log'
        if step7_log.exists():
            with open(step7_log, 'r') as f:
                log_content = f.read()
            if 'Total In-Play Matches' in log_content:
                print("  ✅ step7_simple.log: Found and contains match data")
            else:
                print("  ⚠️  step7_simple.log: Found but may be empty")
        else:
            print("  ❌ step7_simple.log: MISSING!")
            self.issues.append("step7_simple.log missing - run step7.py")
    
    def check_configuration(self):
        """Check configuration consistency"""
        print("\n🔍 Checking Configuration...")
        
        # Check if step7.py is using the right log file
        step7_path = self.base_dir / 'step7.py'
        if step7_path.exists():
            with open(step7_path, 'r') as f:
                step7_content = f.read()
            
            if 'step7_simple.log' in step7_content:
                print("  ✅ step7.py: Using correct log file (step7_simple.log)")
            elif 'step7_matches.log' in step7_content:
                print("  ❌ step7.py: Using OLD log file (step7_matches.log)!")
                self.issues.append("step7.py is using wrong log file name")
            
            # Check if step7 reads from step2.json
            if 'step2.json' in step7_content:
                print("  ✅ step7.py: Reading from correct input (step2.json)")
            else:
                print("  ❌ step7.py: Not reading from step2.json!")
                self.issues.append("step7.py not reading from step2.json")
    
    def suggest_fixes(self):
        """Suggest fixes for common issues"""
        print("\n💡 Suggested Fixes:")
        
        fixes = {
            "step7.py is using wrong log file name": 
                "Update LOG_FILE in step7.py to use 'step7_simple.log'",
            
            "step7.py not reading from step2.json": 
                "Update STEP2_FILE in step7.py to point to 'step2.json'",
            
            "No matches have odds data in step2.json":
                "Check if step1.py is fetching odds data correctly from API",
            
            ".env missing - copy from .env.template":
                "Run: cp .env.template .env && edit .env with your API credentials"
        }
        
        for issue in self.issues + self.warnings:
            if issue in fixes:
                print(f"  🔧 {issue}:")
                print(f"     → {fixes[issue]}")
    
    def create_project_map(self):
        """Create a visual map of the project structure"""
        print("\n📊 Project Structure Map:")
        print("""
        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
        │  step1.py   │────▶│  step2.py   │────▶│  step7.py   │
        └─────────────┘     └─────────────┘     └─────────────┘
              │                   │                   │
              ▼                   ▼                   ▼
        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
        │ step1.json  │     │ step2.json  │     │step7_simple.│
        └─────────────┘     └─────────────┘     │    log      │
                                                └─────────────┘
        """)
    
    def run(self):
        """Run all health checks"""
        print("=" * 60)
        print("🏥 PIPELINE HEALTH CHECK")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Directory: {self.base_dir}")
        
        self.check_file_paths()
        self.check_imports()
        self.check_data_flow()
        self.check_configuration()
        self.create_project_map()
        
        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        
        if not self.issues and not self.warnings:
            print("✅ All checks passed! Pipeline is healthy.")
        else:
            if self.issues:
                print(f"\n❌ Critical Issues ({len(self.issues)}):")
                for issue in self.issues:
                    print(f"  - {issue}")
            
            if self.warnings:
                print(f"\n⚠️  Warnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  - {warning}")
            
            self.suggest_fixes()
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    checker = PipelineHealthCheck()
    checker.run()
