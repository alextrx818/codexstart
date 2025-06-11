# Sports Pipeline Schema Contract

## Overview

This document defines the **single source of truth** for data structures in the sports pipeline. All code MUST use these exact field names and types to ensure consistency and prevent pipeline breakage.

## Why This Matters

- **No More Field Name Drift**: AI agents and developers use the same field names
- **Early Failure Detection**: Invalid data is caught immediately, not after deployment
- **Clear Documentation**: Everyone knows exactly what fields exist and their types
- **Automated Testing**: Contract tests verify data consistency automatically

## Core Data Models

### MatchSummary

The primary data structure for a single match:

```python
from models import MatchSummary

# Required fields (must always be present)
match = MatchSummary(
    match_id="12345",           # str: Unique match identifier
    home="Manchester United",    # str: Home team name
    away="Liverpool",           # str: Away team name
    home_id="678",              # str: Home team ID
    away_id="910",              # str: Away team ID
    score="2-1",                # str: Current score "X-Y"
    status=2,                   # int: Match status code
    status_id=2,                # int: Same as status
    competition="Premier League", # str: Competition name
    competition_id="123",       # str: Competition ID
    match_time=1704067200       # int: Unix timestamp
)
```

### Status Codes

```python
from models import MatchStatus

# Use the enum for clarity
MatchStatus.NOT_STARTED     # 1
MatchStatus.FIRST_HALF      # 2
MatchStatus.HALF_TIME       # 3
MatchStatus.SECOND_HALF     # 4
MatchStatus.OVERTIME        # 5
MatchStatus.OVERTIME_HALF_TIME # 6
MatchStatus.PENALTIES       # 7
MatchStatus.FINISHED        # 9
MatchStatus.CANCELLED       # 10
MatchStatus.POSTPONED       # 11
MatchStatus.INTERRUPTED     # 12
MatchStatus.ABANDONED       # 13
```

### Odds Fields

**IMPORTANT**: The pipeline supports two naming conventions for compatibility:

```python
# American odds format (preferred)
money_line_american = [
    [timestamp, source, home_odds, draw_odds, away_odds, status, ?, score]
]
spread_american = [
    [timestamp, source, home_odds, handicap, away_odds, status, ?, score]
]
over_under_american = [
    [timestamp, source, over_odds, line, under_odds, status, ?, score]
]

# Alternative format (legacy support)
money_line = [...]  # Same structure
spread = [...]      # Same structure
over_under = [...]  # Same structure
```

### Environment Data

```python
environment = {
    "weather": 7,                    # int or str: Weather code or description
    "weather_description": "Cloudy", # str: Human-readable weather
    "temperature": "21°C",           # str: Temperature with unit
    "wind_speed": "5.1m/s"          # str: Wind speed with unit
}
```

## Usage Examples

### Reading and Validating Data

```python
from models import validate_step2_json

# Load and validate step2.json
data = validate_step2_json("step2.json")

# Get in-play matches
in_play = data.get_in_play_matches()

# Get matches with odds
with_odds = data.get_matches_with_odds()
```

### Creating New Match Data

```python
from models import MatchSummary, Step2Output

# Create a match
match = MatchSummary(
    match_id="999",
    home="Team A",
    away="Team B",
    # ... required fields
)

# Create output structure
output = Step2Output(summaries=[match])

# Save with validation
with open("step2.json", "w") as f:
    f.write(output.model_dump_json(indent=2))
```

### Checking Field Compatibility

```python
# Step 7 checks both field names for odds
ml = match.get("money_line_american", []) or match.get("money_line", [])
```

## Contract Testing

Run contract tests to verify data consistency:

```bash
./venv/bin/python test_contracts.py
```

This will:
- Validate step2.json against the schema
- Check field consistency
- Test step7 compatibility
- Report any issues

## Migration Guide

1. **Update imports** in all pipeline files:
   ```python
   from models import MatchSummary, Step2Output
   ```

2. **Use model validation** when processing data:
   ```python
   validated_match = MatchSummary.model_validate(match_dict)
   ```

3. **Standardize field names**:
   - Use `status_id` for filtering (not `status`)
   - Prefer `money_line_american` over `money_line`
   - Always use exact field names from models.py

## For AI Agents

When generating code for this pipeline:

1. **ALWAYS import models**: `from models import MatchSummary, Step2Output`
2. **NEVER create new field names** - use only fields defined in models.py
3. **Validate data** before saving to JSON files
4. **Check both odds field variants** for compatibility

## Enforcement Tools

- `models.py` - Single source of truth for data structures
- `test_contracts.py` - Automated contract testing
- `schema_enforcer.py` - Development tool for migration
- `schemas/match-summary.schema.json` - JSON Schema definition

## Version History

- **2025-06-11**: Initial schema contract established
- Field names frozen to prevent drift
- Backward compatibility for odds fields maintained
