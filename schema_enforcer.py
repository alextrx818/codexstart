#!/usr/bin/env python3
"""
Schema Enforcer - Ensures all pipeline steps use consistent field names
This is a development tool to help migrate to schema-based validation
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import Step2Output, MatchSummary

class SchemaEnforcer:
    """Tool to enforce schema compliance across the pipeline"""
    
    # Define the canonical field names from our schema
    CANONICAL_FIELDS = {
        # Core fields
        'match_id', 'home', 'away', 'home_id', 'away_id',
        'score', 'status', 'status_id',
        'competition', 'competition_id', 'country',
        'match_time', 'kickoff', 'venue',
        'home_position', 'away_position',
        
        # Odds fields - both variants for compatibility
        'money_line', 'money_line_american',
        'spread', 'spread_american', 
        'over_under', 'over_under_american',
        
        # Environment fields
        'environment'
    }
    
    def __init__(self):
        self.issues: List[str] = []
        self.suggestions: List[str] = []
    
    def check_step2_output(self) -> bool:
        """Check if step2.json conforms to schema"""
        print("\n🔍 Checking step2.json schema compliance...")
        
        try:
            # Load and validate
            data = Step2Output.model_validate_json(
                Path("step2.json").read_text()
            )
            print(f"  ✅ Valid schema with {len(data.summaries)} matches")
            
            # Check field usage
            field_usage = self._analyze_field_usage(data.summaries)
            self._report_field_usage(field_usage)
            
            return True
            
        except Exception as e:
            self.issues.append(f"step2.json validation failed: {str(e)}")
            return False
    
    def _analyze_field_usage(self, matches: List[MatchSummary]) -> Dict[str, int]:
        """Analyze which fields are actually used"""
        field_counts = {}
        
        for match in matches:
            match_dict = match.model_dump()
            for field in match_dict:
                if match_dict[field] is not None:
                    field_counts[field] = field_counts.get(field, 0) + 1
        
        return field_counts
    
    def _report_field_usage(self, field_usage: Dict[str, int]):
        """Report on field usage patterns"""
        print("\n📊 Field Usage Analysis:")
        
        # Check for non-canonical fields
        extra_fields = set(field_usage.keys()) - self.CANONICAL_FIELDS
        if extra_fields:
            print(f"  ⚠️  Non-canonical fields found: {extra_fields}")
            self.suggestions.append(
                "Consider adding these fields to models.py if they're needed"
            )
        
        # Check odds field usage
        odds_fields = {
            'money_line': field_usage.get('money_line', 0),
            'money_line_american': field_usage.get('money_line_american', 0),
            'spread': field_usage.get('spread', 0),
            'spread_american': field_usage.get('spread_american', 0),
        }
        
        print("\n  Odds field usage:")
        for field, count in odds_fields.items():
            if count > 0:
                print(f"    - {field}: {count} matches")
        
        # Suggest standardization if both variants exist
        if odds_fields['money_line'] > 0 and odds_fields['money_line_american'] > 0:
            self.suggestions.append(
                "Both 'money_line' and 'money_line_american' are used. "
                "Consider standardizing to one field name."
            )
    
    def check_code_references(self):
        """Check Python files for field references"""
        print("\n🔍 Checking code for field references...")
        
        files_to_check = ['step1.py', 'step2.py', 'step7.py']
        
        for filename in files_to_check:
            if Path(filename).exists():
                self._check_file_fields(filename)
    
    def _check_file_fields(self, filename: str):
        """Check a file for field references"""
        content = Path(filename).read_text()
        
        # Look for dictionary key access patterns
        import re
        
        # Patterns to find field access
        patterns = [
            r'\.get\(["\'](\w+)["\']',  # .get("field")
            r'\[["\'](\w+)["\']\]',      # ["field"]
            r'["\'](\w+)["\']:\s*',      # "field": value
        ]
        
        found_fields = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            found_fields.update(matches)
        
        # Check for non-canonical fields
        non_canonical = found_fields - self.CANONICAL_FIELDS - {'summaries', 'get', 'set'}
        if non_canonical:
            print(f"\n  {filename}:")
            print(f"    ⚠️  Potential non-canonical fields: {non_canonical}")
    
    def generate_migration_guide(self):
        """Generate a guide for migrating to schema-based code"""
        print("\n" + "=" * 60)
        print("📋 SCHEMA MIGRATION GUIDE")
        print("=" * 60)
        
        print("\n1. Update step2.py to use models:")
        print("   ```python")
        print("   from models import MatchSummary, Step2Output")
        print("   ")
        print("   # When creating match data:")
        print("   match = MatchSummary(")
        print("       match_id=match_id,")
        print("       home=home_team,")
        print("       away=away_team,")
        print("       # ... other fields")
        print("   )")
        print("   ```")
        
        print("\n2. Validate data before writing:")
        print("   ```python")
        print("   output = Step2Output(summaries=matches)")
        print("   with open('step2.json', 'w') as f:")
        print("       f.write(output.model_dump_json(indent=2))")
        print("   ```")
        
        print("\n3. Use consistent field names:")
        print("   - Prefer 'money_line_american' over 'money_line'")
        print("   - Use 'status_id' not 'status' for filtering")
        print("   - Always validate with models before saving")
        
        if self.suggestions:
            print("\n💡 Specific Suggestions:")
            for suggestion in self.suggestions:
                print(f"   - {suggestion}")
    
    def run(self):
        """Run all schema enforcement checks"""
        print("🏃 Running Schema Enforcer...")
        
        # Check outputs
        self.check_step2_output()
        
        # Check code
        self.check_code_references()
        
        # Generate guide
        self.generate_migration_guide()

if __name__ == "__main__":
    enforcer = SchemaEnforcer()
    enforcer.run()
