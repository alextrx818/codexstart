#!/usr/bin/env python3
"""
Contract tests to ensure data consistency across pipeline steps
Run this to verify all steps produce/consume valid data
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import Step2Output, MatchSummary, validate_step2_json
from pydantic import ValidationError

class ContractTester:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def test_step2_output(self) -> bool:
        """Test that step2.json conforms to schema"""
        print("\n🔍 Testing step2.json contract...")
        
        step2_path = Path("step2.json")
        if not step2_path.exists():
            self.errors.append("step2.json not found")
            return False
        
        try:
            # Validate using Pydantic model
            data = validate_step2_json("step2.json")
            print(f"  ✅ Valid Step2Output with {len(data.summaries)} matches")
            
            # Check for in-play matches
            in_play = data.get_in_play_matches()
            print(f"  ✅ Found {len(in_play)} in-play matches")
            
            # Check for matches with odds
            with_odds = data.get_matches_with_odds()
            print(f"  ✅ Found {len(with_odds)} matches with odds")
            
            return True
            
        except ValidationError as e:
            print(f"  ❌ Validation failed!")
            for error in e.errors():
                field = " -> ".join(str(x) for x in error['loc'])
                self.errors.append(f"Field '{field}': {error['msg']}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error: {str(e)}")
            return False
    
    def test_field_consistency(self) -> bool:
        """Test that expected fields are present and consistent"""
        print("\n🔍 Testing field consistency...")
        
        try:
            with open("step2.json", 'r') as f:
                raw_data = json.load(f)
            
            summaries = raw_data.get('summaries', [])
            if not summaries:
                self.warnings.append("No summaries found in step2.json")
                return True
            
            # Check first few matches for field consistency
            required_fields = ['match_id', 'home', 'away', 'status', 'score']
            optional_fields = ['money_line', 'money_line_american', 'spread', 'over_under']
            
            for i, match in enumerate(summaries[:5]):
                # Check required fields
                for field in required_fields:
                    if field not in match:
                        self.errors.append(f"Match {i}: Missing required field '{field}'")
                
                # Check optional fields exist (even if empty)
                for field in optional_fields:
                    if field not in match:
                        self.warnings.append(f"Match {i}: Missing optional field '{field}'")
            
            print(f"  ✅ Field consistency check complete")
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Field consistency test failed: {str(e)}")
            return False
    
    def test_step7_compatibility(self) -> bool:
        """Test that step7 can read the data correctly"""
        print("\n🔍 Testing step7 compatibility...")
        
        try:
            # Load and validate data
            data = validate_step2_json("step2.json")
            
            # Simulate what step7 does
            in_play_matches = [
                m for m in data.summaries 
                if m.status in [2, 3, 4, 5, 6, 7]
            ]
            
            print(f"  ✅ Step7 would process {len(in_play_matches)} matches")
            
            # Check if step7 can access all needed fields
            for match in in_play_matches[:3]:  # Test first 3
                # Fields step7 uses
                _ = match.home
                _ = match.away
                _ = match.score
                _ = match.get_status_name()
                _ = match.competition
                
                # Check odds access
                if match.money_line_american:
                    _ = match.money_line_american[0]
                
            print(f"  ✅ Step7 can access all required fields")
            return True
            
        except Exception as e:
            self.errors.append(f"Step7 compatibility test failed: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate a contract test report"""
        print("\n" + "=" * 60)
        print("📋 CONTRACT TEST REPORT")
        print("=" * 60)
        
        if not self.errors and not self.warnings:
            print("✅ All contract tests passed!")
            print("\nYour data pipeline is using consistent field names.")
            print("Any AI agent using models.py will generate compatible code.")
        else:
            if self.errors:
                print(f"\n❌ Errors ({len(self.errors)}):")
                for error in self.errors:
                    print(f"  - {error}")
            
            if self.warnings:
                print(f"\n⚠️  Warnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  - {warning}")
            
            print("\n💡 Fix suggestions:")
            print("  1. Update step2.py to use models.MatchSummary")
            print("  2. Run: datamodel-codegen --input schemas/step2-sample.json --output models_generated.py")
            print("  3. Compare models.py with models_generated.py")
    
    def run_all_tests(self):
        """Run all contract tests"""
        print("🏃 Running contract tests...")
        
        # Run tests
        self.test_step2_output()
        self.test_field_consistency()
        self.test_step7_compatibility()
        
        # Generate report
        self.generate_report()

if __name__ == "__main__":
    tester = ContractTester()
    tester.run_all_tests()
