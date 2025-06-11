#!/usr/bin/env python3
"""
Diagnose why odds aren't showing in step7
"""
import json
from pathlib import Path

def diagnose_odds():
    # Load step2.json
    step2_path = Path("step2.json")
    if not step2_path.exists():
        print("❌ step2.json not found!")
        return
    
    with open(step2_path, 'r') as f:
        data = json.load(f)
    
    summaries = data.get('summaries', [])
    print(f"Total matches in step2.json: {len(summaries)}")
    
    # Check in-play matches
    in_play_statuses = [2, 3, 4, 5, 6, 7]
    in_play = [m for m in summaries if m.get('status') in in_play_statuses]
    print(f"In-play matches (status 2-7): {len(in_play)}")
    
    # Analyze odds fields
    print("\n📊 Odds Analysis:")
    
    odds_fields = {
        'money_line': 0,
        'money_line_american': 0,
        'spread': 0,
        'spread_american': 0,
        'over_under': 0,
        'over_under_american': 0
    }
    
    for match in in_play:
        for field in odds_fields:
            if match.get(field) and len(match.get(field, [])) > 0:
                odds_fields[field] += 1
    
    print("\nMatches with odds data:")
    for field, count in odds_fields.items():
        print(f"  {field}: {count}/{len(in_play)} matches")
    
    # Show sample match with odds
    print("\n📋 Sample match with odds:")
    for match in in_play:
        if match.get('money_line_american') and len(match.get('money_line_american', [])) > 0:
            print(f"\nMatch: {match.get('home', 'Unknown')} vs {match.get('away', 'Unknown')}")
            print(f"Status: {match.get('status')} ({match.get('status_id', 'N/A')})")
            print(f"Money Line American: {match.get('money_line_american', [])}")
            print(f"Money Line: {match.get('money_line', [])}")
            print(f"Spread American: {match.get('spread_american', [])}")
            print(f"Over/Under American: {match.get('over_under_american', [])}")
            break
    
    # Check what step7 is looking for
    print("\n🔍 Step7 Compatibility Check:")
    
    # Count matches that would show odds in step7
    step7_odds_count = sum(1 for m in in_play 
                          if m.get("money_line") and len(m.get("money_line", [])) > 0)
    
    print(f"Matches with 'money_line' field (step7 checks this): {step7_odds_count}")
    print(f"Matches with 'money_line_american' field: {odds_fields['money_line_american']}")
    
    if step7_odds_count < odds_fields['money_line_american']:
        print("\n⚠️  ISSUE FOUND: step7 checks 'money_line' but data has 'money_line_american'")
        print("   This is why odds aren't showing in the summary!")

if __name__ == "__main__":
    diagnose_odds()
