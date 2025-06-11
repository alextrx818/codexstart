# 🔒 LOCKED FIELD REFERENCE - DO NOT MODIFY

## Quick Reference for Pipeline Field Names

### Match Core Fields (REQUIRED)
```
match_id        → "12345"           # Unique identifier
home            → "Manchester United" # Home team name  
away            → "Liverpool"        # Away team name
home_id         → "678"             # Home team ID
away_id         → "910"             # Away team ID
score           → "2-1"             # Format: "HOME-AWAY"
status          → 2                 # Status code (1-13)
status_id       → 2                 # Same as status (FILTER ON THIS!)
competition     → "Premier League"   # Competition name
competition_id  → "123"             # Competition ID
country         → "England"         # Country name
match_time      → 1704067200        # Unix timestamp
```

### Match Optional Fields
```
kickoff         → "15:00"           # Kickoff time
venue           → "Old Trafford"    # Venue name
home_position   → "3"               # League position
away_position   → "5"               # League position
```

### Odds Arrays (8 elements each)
```
# Both field names supported for compatibility:
money_line OR money_line_american   → [[timestamp, minute, home, draw, away, status, sealed, score]]
spread OR spread_american           → [[timestamp, minute, home, handicap, away, status, sealed, score]]
over_under OR over_under_american   → [[timestamp, minute, over, line, under, status, sealed, score]]
corners OR corners_american         → [[timestamp, minute, over, line, under, status, sealed, score]]

# Example:
money_line_american: [[1704067200, "3", -150, +280, +185, 2, 0, "0-0"]]
```

### Environment Object
```
environment: {
  weather: 7,                       # Int code OR string
  weather_description: "Overcast",  # Human readable
  temperature: "21°C",              # With unit
  temperature_fahrenheit: "69.8°F", # Converted
  wind_speed: "5.1m/s",            # With unit  
  wind_speed_mph: "11.4mph",       # Converted
  humidity: "65%",                 # With %
  pressure: "1013hPa"              # With unit
}
```

### Status Codes (for filtering)
```
1  = Not Started
2  = First Half      ┐
3  = Half-time       │
4  = Second Half     ├─ IN-PLAY (step7 filters for these)
5  = Overtime        │
6  = OT Half-time    │
7  = Penalties       ┘
9  = Finished
10 = Cancelled
11 = Postponed
12 = Interrupted
13 = Abandoned
```

## 🚨 CRITICAL RULES

1. **NEVER create new field names** - Use ONLY the fields above
2. **Always use `status_id`** for filtering (not `status`)
3. **Check both odds field variants** (e.g., `money_line` OR `money_line_american`)
4. **Import models for validation**: `from models import MatchSummary, Step2Output`
5. **Run contract tests**: `./venv/bin/python test_contracts.py`

## File → Field Mapping

### step1.json produces:
- `live_matches` array with raw match data
- Uses `home_team`, `away_team`, `home_team_id`, `away_team_id`

### step2.json produces:
- `summaries` array with enriched match data
- Uses standardized field names above
- Includes odds and environment data

### step7.py reads:
- Filters `summaries` where `status_id` in [2,3,4,5,6,7]
- Checks both odds field name variants
- Outputs to `step7_simple.log`
