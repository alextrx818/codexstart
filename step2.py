#!/usr/bin/env python3
"""
STEP 2 - DATA PROCESSOR (MERGER AND FILTER)
====================================

This script will extract specific fields from step1.json and merge them by match ID.
To be built incrementally in Jupyter.

ENVIRONMENT DATA CONVERSIONS:
-----------------------------
Step 2 automatically converts environment data to user-friendly formats:

1. WEATHER - Converts numeric ID to descriptive text:
   - 1 → "Partially cloudy"
   - 2 → "Cloudy"
   - 3 → "Partially cloudy/rain"
   - 4 → "Snow"
   - 5 → "Sunny"
   - 6 → "Overcast Rain/partial thunderstorm"
   - 7 → "Overcast"
   - 8 → "Mist"
   - 9 → "Cloudy with rain"
   - 10 → "Cloudy with rain"
   - 11 → "Cloudy with rain/partial Thunderstorms"
   - 12 → "Clouds/rains and thunderstorms locally"
   - 13 → "Fog"

2. TEMPERATURE - Converts Celsius to Fahrenheit:
   - Field: temperature_fahrenheit
   - Formula: (°C × 9/5) + 32
{{ ... }}
"""

# ============================================================================
# SCHEMA CONTRACT - DO NOT MODIFY FIELD NAMES
# ============================================================================
# This file reads step1.json and produces step2.json with EXACT field names:
# {
#   "summaries": [
#     {
#       "match_id": str,                    # REQUIRED: Unique match identifier
#       "home": str,                        # REQUIRED: Home team name
#       "away": str,                        # REQUIRED: Away team name
#       "home_id": str,                     # REQUIRED: Home team ID
#       "away_id": str,                     # REQUIRED: Away team ID
#       "score": str,                       # REQUIRED: Format "X-Y"
#       "status": int,                      # REQUIRED: Match status code
#       "status_id": int,                   # REQUIRED: Same as status
#       "competition": str,                 # REQUIRED: Competition name
#       "competition_id": str,              # REQUIRED: Competition ID
#       "country": str,                     # REQUIRED: Country name
#       "match_time": int,                  # REQUIRED: Unix timestamp
#       "kickoff": str,                     # Kickoff time
#       "venue": str,                       # Venue name
#       "home_position": str,               # Home team position
#       "away_position": str,               # Away team position
#       
#       # ODDS FIELDS - Both formats supported for compatibility
#       "money_line": [[timestamp, source, home, draw, away, status, ?, score]],
#       "money_line_american": [[...same structure...]],
#       "spread": [[timestamp, source, home, handicap, away, status, ?, score]],
#       "spread_american": [[...same structure...]],
#       "over_under": [[timestamp, source, over, line, under, status, ?, score]],
#       "over_under_american": [[...same structure...]],
#       
#       # Additional odds
#       "corners": [...],
#       "corners_american": [...],
#       
#       # Environment data
#       "environment": {
#         "weather": int/str,               # Weather code or description
#         "weather_description": str,       # Human-readable weather
#         "temperature": str,               # Original temp with unit
#         "temperature_fahrenheit": str,   # Converted to F
#         "wind_speed": str,                # Original with unit
#         "wind_speed_mph": str,            # Converted to mph
#         "humidity": str,                  # With %
#         "pressure": str                   # With unit
#       },
#       
#       # Other fields
#       "events": [...],                    # Match events
#       "odds": {...},                      # Raw odds data
#       "odds_company_id": str,
#       "odds_company_name": str
#     }
#   ],
#   "$schema": "https://github.com/alextrx818/codexstart/schemas/match-summary/v2025-06-11",
#   "version": "2025-06-11"
# }
#
# CRITICAL: Use models.py MatchSummary for validation. Never change field names!
# ============================================================================

import json
import logging
from datetime import datetime
import pytz
import time
from pathlib import Path

# Constants
STEP1_JSON = "/root/6-4-2025/step1.json"
STEP2_JSON = "/root/6-4-2025/step2.json"
TZ = pytz.timezone("America/New_York")

# Betting Company ID to Name mapping
BETTING_COMPANIES = {
    "2": "BET365",
    "3": "Crown",
    "4": "10BET",
    "5": "Ladbrokes",
    "6": "Mansion88",
    "7": "Macauslot",
    "8": "SNAI",
    "9": "William Hill",
    "10": "Easybets",
    "11": "Vcbet",
    "12": "EuroBet",
    "13": "Interwetten",
    "14": "12bet",
    "15": "Sbobet",
    "16": "Wewbet",
    "17": "18Bet",
    "18": "Fun88",
    "21": "188bet",
    "22": "Pinnacle"
}

# Weather ID to description mapping
WEATHER_DESCRIPTIONS = {
    1: "Partially cloudy",
    2: "Cloudy",
    3: "Partially cloudy/rain",
    4: "Snow",
    5: "Sunny",
    6: "Overcast Rain/partial thunderstorm",
    7: "Overcast",
    8: "Mist",
    9: "Cloudy with rain",
    10: "Cloudy with rain",
    11: "Cloudy with rain/partial Thunderstorms",
    12: "Clouds/rains and thunderstorms locally",
    13: "Fog"
}

# Preferred order for betting company selection (BET365 first)
PREFERRED_COMPANIES = ["2", "3", "4", "5", "6", "9", "10", "11", "13", "14", "15", "16", "17", "21", "22"]

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_summary_fields(match: dict) -> dict:
    """Extract key fields from a merged match for summary."""
    return {
        "match_id": match.get("id", ""),
        "home": match.get("home", {}).get("name", "Unknown"),
        "away": match.get("away", {}).get("name", "Unknown"),
        "home_id": match.get("home", {}).get("id", ""),
        "away_id": match.get("away", {}).get("id", ""),
        "score": f"{match.get('home_scores', [0])[-1] if match.get('home_scores') else 0}-{match.get('away_scores', [0])[-1] if match.get('away_scores') else 0}",
        "status_id": match.get("status_id", 0),
        "competition": match.get("league", {}).get("name", "Unknown"),
        "competition_id": match.get("league", {}).get("id", ""),
        "country": match.get("league", {}).get("country_name", "Unknown"),
        "match_time": match.get("match_time", ""),
        "kickoff": match.get("kickoff", ""),
        "venue": match.get("venue", {}).get("name", "") if match.get("venue") else "",
        "home_position": match.get("home_position", ""),
        "away_position": match.get("away_position", ""),
    }

def extract_odds(match: dict) -> dict:
    """Extract odds data from match, mapping API field names to descriptive names."""
    odds_data = {}
    if "odds" in match and isinstance(match["odds"], dict):
        # Odds are organized by company ID
        for company_id, company_odds in match["odds"].items():
            if isinstance(company_odds, dict):
                # Map old field names to new descriptive names
                odds_data[company_id] = {
                    "money_line": company_odds.get("eu", []),      # European/Money Line odds
                    "spread": company_odds.get("asia", []),        # Asian Handicap/Spread
                    "over_under": company_odds.get("bs", []),      # Ball Size/Over-Under
                    "corners": company_odds.get("cr", [])          # Corner totals
                }
    return odds_data

def extract_environment(match: dict) -> dict:
    """Extract environment/weather data from match with temperature and wind conversions."""
    env = match.get("environment", {})
    if isinstance(env, dict):
        # Extract raw values
        temperature_str = env.get("temperature", "")
        wind_str = env.get("wind", "")  # Field is "wind" not "wind_speed" in the data
        
        # Initialize converted values
        temperature_fahrenheit = ""
        wind_mph = ""
        
        # Convert temperature from Celsius to Fahrenheit
        if temperature_str and "°C" in temperature_str:
            try:
                # Extract numeric value (e.g., "30°C" -> 30)
                temp_celsius = float(temperature_str.replace("°C", "").strip())
                temp_fahrenheit = (temp_celsius * 9/5) + 32
                temperature_fahrenheit = f"{temp_fahrenheit:.1f}°F"
            except (ValueError, AttributeError):
                temperature_fahrenheit = ""
        
        # Convert wind speed from m/s to mph
        if wind_str and "m/s" in wind_str:
            try:
                # Extract numeric value (e.g., "7.0m/s" -> 7.0)
                wind_ms = float(wind_str.replace("m/s", "").strip())
                wind_mph_value = wind_ms * 2.237
                wind_mph = f"{wind_mph_value:.1f}mph"
            except (ValueError, AttributeError):
                wind_mph = ""
        
        # Convert weather ID to description
        weather_id = env.get("weather", "")
        weather_description = ""
        if weather_id:
            try:
                weather_description = WEATHER_DESCRIPTIONS.get(int(weather_id), f"Unknown weather ID: {weather_id}")
            except (ValueError, TypeError):
                weather_description = f"Invalid weather ID: {weather_id}"
        
        return {
            "weather": weather_id,
            "weather_description": weather_description,
            "temperature": temperature_str,
            "temperature_fahrenheit": temperature_fahrenheit,
            "humidity": env.get("humidity", ""),
            "wind_speed": wind_str,
            "wind_speed_mph": wind_mph,
            "pressure": env.get("pressure", "")
        }
    return {}

def extract_events(match: dict) -> list:
    """Extract match events if available."""
    return match.get("events", [])

def convert_decimal_to_american(decimal_odd):
    """Convert decimal odds to American odds format."""
    try:
        d = float(decimal_odd)
        if d >= 2.00:
            # Positive American odds
            return int(round((d - 1) * 100))
        elif d >= 1.00:
            # Negative American odds
            return int(round(-100 / (d - 1)))
        else:
            # Invalid decimal odd (should be >= 1.00)
            return None
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def convert_hong_kong_to_american(hk_odd):
    """Convert Hong Kong odds to American odds format."""
    try:
        h = float(hk_odd)
        if h >= 1.00:
            # Positive American odds
            return int(round(h * 100))
        elif h > 0:
            # Negative American odds
            return int(round(-100 / h))
        else:
            # Invalid HK odd (should be > 0)
            return None
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def convert_odds_array(odds_array, odds_type):
    """
    Convert an odds array to include American odds format.
    Returns the original array plus a converted array.
    
    Args:
        odds_array: List of odds arrays
        odds_type: 'money_line', 'spread', 'over_under', or 'corners'
    
    Returns:
        Tuple of (original_array, american_array)
    """
    american_arrays = []
    
    for odds_entry in odds_array:
        if len(odds_entry) >= 8:
            # Extract the original values
            timestamp = odds_entry[0]
            minute = odds_entry[1]
            val1 = odds_entry[2]
            val2 = odds_entry[3]
            val3 = odds_entry[4]
            status = odds_entry[5]
            sealed = odds_entry[6]
            score = odds_entry[7]
            
            # Convert based on odds type
            if odds_type == "money_line":
                # Money Line uses decimal odds
                american1 = convert_decimal_to_american(val1)
                american2 = convert_decimal_to_american(val2)
                american3 = convert_decimal_to_american(val3)
            else:
                # Spread, Over/Under, Corners use Hong Kong odds
                american1 = convert_hong_kong_to_american(val1)
                american3 = convert_hong_kong_to_american(val3)
                # val2 is the handicap/total line, not an odd
                american2 = val2
            
            # Format American odds with proper sign
            def format_american(value, is_middle_value=False):
                if value is None:
                    return value
                # For spread/over-under/corners, the middle value is the line, not odds
                if is_middle_value and odds_type != "money_line":
                    return value  # Keep handicap/line as numeric
                if isinstance(value, (int, float)):
                    return f"+{int(value)}" if value > 0 else str(int(value))
                return value
            
            # Create American odds array
            american_entry = [
                timestamp,
                minute,
                format_american(american1),
                format_american(american2, is_middle_value=True),
                format_american(american3),
                status,
                sealed,
                score
            ]
            american_arrays.append(american_entry)
    
    return odds_array, american_arrays

def filter_odds_by_minutes(odds_data, min_minute=2, max_minute=6):
    """
    Filter odds arrays to only keep entries where the minute field (second field) 
    is between min_minute and max_minute (inclusive).
    For multiple entries in the same minute, keep only the last one (highest timestamp).
    
    Args:
        odds_data: The odds data structure (dict with money_line, spread, over_under, corners arrays(dict with asia, bs, eu, cr arrays))
        min_minute: Minimum minute value to keep (as integer)
        max_minute: Maximum minute value to keep (as integer)
    
    Returns:
        Filtered odds data
    """
    filtered_odds = {}
    
    for odds_type in ['money_line', 'spread', 'over_under', 'corners']:
        if odds_type in odds_data:
            # First, collect all valid entries grouped by minute
            minute_entries = {}
            
            for array in odds_data[odds_type]:
                # Check if the array has at least 2 elements and the second element is the minute field
                if len(array) >= 2:
                    minute_field = array[1]  # Get the minute field
                    
                    # Convert to integer for numeric comparison
                    try:
                        minute_num = int(minute_field) if minute_field != "" else -1
                        
                        # Only keep if minute field is between min and max (inclusive)
                        if min_minute <= minute_num <= max_minute:
                            # Group by minute, keeping track of timestamp
                            if minute_num not in minute_entries:
                                minute_entries[minute_num] = []
                            minute_entries[minute_num].append(array)
                    except (ValueError, TypeError):
                        # Skip entries that can't be converted to int
                        pass
            
            # Now keep only the last entry (highest timestamp) for each minute
            filtered_arrays = []
            for minute in sorted(minute_entries.keys()):
                # Sort by timestamp (first element) and take the last one
                entries_for_minute = sorted(minute_entries[minute], key=lambda x: x[0])
                filtered_arrays.append(entries_for_minute[-1])  # Take the last (highest timestamp)
            
            filtered_odds[odds_type] = filtered_arrays
    
    return filtered_odds

def merge_and_summarize(live_matches: list, match_details: dict, match_odds: dict, 
                        team_info: dict, competition_info: dict, countries: dict) -> list:
    """Merge live match data with enriched data from other endpoints."""
    summaries = []
    
    for match in live_matches:
        match_id = str(match.get("id", ""))
        if not match_id:
            continue
            
        # Get details for this match
        details_wrapper = match_details.get(match_id, {})
        details = None
        if isinstance(details_wrapper, dict) and "results" in details_wrapper:
            results = details_wrapper.get("results", [])
            if results and isinstance(results, list) and len(results) > 0:
                details = results[0]
        
        # Initialize match structure if needed
        if not match.get("home"):
            match["home"] = {}
        if not match.get("away"):
            match["away"] = {}
        if not match.get("league"):
            match["league"] = {}
        
        # Merge details into match (including team IDs)
        if details:
            # Set team IDs
            home_team_id = details.get("home_team_id", "")
            away_team_id = details.get("away_team_id", "")
            competition_id = details.get("competition_id", "")
            
            if home_team_id:
                match["home"]["id"] = home_team_id
            if away_team_id:
                match["away"]["id"] = away_team_id
            if competition_id:
                match["league"]["id"] = competition_id
            
            # Add status_id if not present
            if "status_id" not in match and "status_id" in details:
                match["status_id"] = details["status_id"]
                
            # Merge other fields from details
            for key, value in details.items():
                if key not in ["home_team_id", "away_team_id", "competition_id"] and key not in match:
                    match[key] = value
        
        # Get odds data
        odds_wrapper = match_odds.get(match_id, {})
        if isinstance(odds_wrapper, dict) and "results" in odds_wrapper:
            odds_results = odds_wrapper.get("results", {})
            # Check if results is a dictionary (actual format) not a list
            if isinstance(odds_results, dict) and odds_results:
                match["odds"] = odds_results
            else:
                match["odds"] = {}
        
        # Get team names using team IDs
        home_team_id = str(match.get("home", {}).get("id", "") or details.get("home_team_id", ""))
        away_team_id = str(match.get("away", {}).get("id", "") or details.get("away_team_id", ""))
        
        # Lookup home team
        if home_team_id and home_team_id in team_info:
            team_wrapper = team_info[home_team_id]
            if isinstance(team_wrapper, dict) and "results" in team_wrapper:
                team_results = team_wrapper.get("results", [])
                if team_results and isinstance(team_results, list) and len(team_results) > 0:
                    team_data = team_results[0]
                    match["home"]["name"] = team_data.get("name", "Unknown")
                    match["home"]["short_name"] = team_data.get("short_name", "")
                    match["home"]["logo"] = team_data.get("logo", "")
        
        # Lookup away team
        if away_team_id and away_team_id in team_info:
            team_wrapper = team_info[away_team_id]
            if isinstance(team_wrapper, dict) and "results" in team_wrapper:
                team_results = team_wrapper.get("results", [])
                if team_results and isinstance(team_results, list) and len(team_results) > 0:
                    team_data = team_results[0]
                    match["away"]["name"] = team_data.get("name", "Unknown")
                    match["away"]["short_name"] = team_data.get("short_name", "")
                    match["away"]["logo"] = team_data.get("logo", "")
        
        # Get competition info
        comp_id = str(match.get("league", {}).get("id", "") or details.get("competition_id", ""))
        country_name = "Unknown"
        if comp_id and comp_id in competition_info:
            comp_wrapper = competition_info[comp_id]
            if isinstance(comp_wrapper, dict) and "results" in comp_wrapper:
                comp_results = comp_wrapper.get("results", [])
                if comp_results and isinstance(comp_results, list) and len(comp_results) > 0:
                    comp_data = comp_results[0]
                    match["league"]["name"] = comp_data.get("name", "Unknown")
                    match["league"]["short_name"] = comp_data.get("short_name", "")
                    match["league"]["logo"] = comp_data.get("logo", "")
                    
                    # Get country ID from competition and look up country name
                    country_id = comp_data.get("country_id", "")
                    if country_id and countries:
                        # Check if countries has the country data
                        if country_id in countries:
                            country_data = countries[country_id]
                            if isinstance(country_data, dict):
                                # Direct country object format
                                country_name = country_data.get("name", "Unknown")
                    
                    match["league"]["country_name"] = country_name
                    match["league"]["country_code"] = ""
        
        # Extract summary fields
        summary = extract_summary_fields(match)
        summary["status"] = match.get("status_id", 0)
        
        # Extract and filter odds - select only one betting company
        raw_odds = extract_odds(match)
        selected_company_id = None
        selected_odds = {}
        
        # Try to find BET365 first, then fall back to preferred order
        for company_id in PREFERRED_COMPANIES:
            if company_id in raw_odds and raw_odds[company_id]:
                # Check if this company has any odds data
                has_data = False
                for odds_type in ['money_line', 'spread', 'over_under']:
                    if raw_odds[company_id].get(odds_type):
                        has_data = True
                        break
                
                if has_data:
                    selected_company_id = company_id
                    selected_odds = filter_odds_by_minutes(raw_odds[company_id])
                    break
        
        # Set the selected odds and company info
        if selected_company_id:
            # PRIORITIZED: Descriptive field names at the top level come FIRST
            summary["money_line"], summary["money_line_american"] = convert_odds_array(selected_odds.get("money_line", []), "money_line")
            summary["spread"], summary["spread_american"] = convert_odds_array(selected_odds.get("spread", []), "spread")
            summary["over_under"], summary["over_under_american"] = convert_odds_array(selected_odds.get("over_under", []), "over_under")
            summary["corners"], summary["corners_american"] = convert_odds_array(selected_odds.get("corners", []), "corners")
            summary["odds_company_id"] = selected_company_id
            summary["odds_company_name"] = BETTING_COMPANIES.get(selected_company_id, f"Company {selected_company_id}")
            
            # Keep the original odds structure with selected company only (AFTER new fields)
            summary["odds"] = {selected_company_id: selected_odds}
        else:
            summary["money_line"] = []
            summary["money_line_american"] = []
            summary["spread"] = []
            summary["spread_american"] = []
            summary["over_under"] = []
            summary["over_under_american"] = []
            summary["corners"] = []
            summary["corners_american"] = []
            summary["odds_company_id"] = None
            summary["odds_company_name"] = None
            summary["odds"] = {}
        
        summary["environment"] = extract_environment(match)
        summary["events"] = extract_events(match)
        
        summaries.append(summary)
    
    return summaries

def save_match_summaries(data: dict, output_file: str) -> bool:
    """Save the processed match summaries to JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save to {output_file}: {e}")
        return False

def main():
    """Main entry point"""
    logger.info("Step 2 processing started...")
    
    # Track processing time
    start_time = time.time()
    
    try:
        # Load step1.json
        logger.info(f"Loading {STEP1_JSON}...")
        with open(STEP1_JSON, 'r', encoding='utf-8') as f:
            step1_data = json.load(f)
        
        # Extract live matches and payload data
        live_matches = step1_data.get("live_matches", {})
        payload_data = {k: v for k, v in step1_data.items() if k != "live_matches"}
        
        # Build country lookup dictionary
        countries_data = payload_data.get("countries", {})
        country_lookup = {}
        for key, value in countries_data.items():
            if isinstance(value, list):
                for country in value:
                    if isinstance(country, dict) and "id" in country:
                        country_lookup[country["id"]] = country
        
        logger.info(f"Found {len(live_matches.get('results', []))} live matches")
        logger.info(f"Found {len(payload_data.get('team_info', {}))} teams")
        logger.info(f"Found {len(payload_data.get('competition_info', {}))} competitions")
        logger.info(f"Found {len(country_lookup)} countries")
        
        # Merge and summarize
        logger.info("Merging and summarizing match data...")
        merged_data = {
            "summaries": merge_and_summarize(live_matches.get("results", []), 
                                              payload_data.get("match_details", {}), 
                                              payload_data.get("match_odds", {}), 
                                              payload_data.get("team_info", {}), 
                                              payload_data.get("competition_info", {}), 
                                              country_lookup),
            "metadata": {
                "total_matches": len(live_matches.get("results", [])),
                "timestamp": datetime.now(TZ).strftime("%m/%d/%Y %I:%M:%S %p %Z"),
                "source": "step2.py"
            }
        }
        
        # Add processing time
        elapsed_time = time.time() - start_time
        processing_time = f"{elapsed_time:.2f} seconds"
        merged_data["metadata"]["processing_time"] = processing_time
        
        # Count in-play matches (status_id 2-7)
        in_play_count = sum(1 for match in merged_data["summaries"] 
                           if 2 <= match.get("status_id", 0) <= 7)
        
        # Add step2 processing summary
        merged_data["step2_processing_summary"] = {
            "processed_at": datetime.now(TZ).strftime("%m/%d/%Y %I:%M:%S %p %Z"),
            "input_file": STEP1_JSON,
            "output_file": STEP2_JSON,
            "total_matches_processed": len(merged_data["summaries"]),
            "in_play_matches": in_play_count,
            "processing_time": processing_time,
            "pipeline_timing": {
                "step2_start": datetime.now(TZ).strftime("%m/%d/%Y %I:%M:%S %p %Z"),
                "step2_duration": processing_time
            }
        }
        
        # Save to step2.json
        logger.info(f"Saving {len(merged_data['summaries'])} match summaries to {STEP2_JSON}...")
        success = save_match_summaries(merged_data, STEP2_JSON)
        
        if success:
            logger.info(f"Step 2 completed successfully in {processing_time} seconds")
            logger.info(f"Created {len(merged_data['summaries'])} match summaries")
        else:
            logger.error("Step 2 failed to save output")
            
        # Call Step 7 after Step 2 completes
        try:
            import step7
            import importlib
            importlib.reload(step7)  # Force reload to pick up any code changes
            logger.info("Starting Step 7 (filter & pretty-print)...")
            step7.run_step7(matches_list=merged_data['summaries'])
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to run Step 7: {e}")
            import traceback
            traceback.print_exc()
            
    except FileNotFoundError:
        logger.error(f"Could not find {STEP1_JSON}. Please run step1.py first.")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {STEP1_JSON}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in Step 2: {e}")
        raise

def run_step2(pipeline_start_time=None):
    """
    Run Step 2 processing - can be called from other modules.
    Returns the list of summaries for use by other steps.
    """
    logger.info("Step 2 processing started...")
    
    # Track processing time
    start_time = time.time()
    
    try:
        # Load step1.json
        logger.info(f"Loading {STEP1_JSON}...")
        with open(STEP1_JSON, 'r', encoding='utf-8') as f:
            step1_data = json.load(f)
        
        # Extract live matches and payload data
        live_matches = step1_data.get("live_matches", {})
        payload_data = {k: v for k, v in step1_data.items() if k != "live_matches"}
        
        # Build country lookup dictionary
        countries_data = payload_data.get("countries", {})
        country_lookup = {}
        for key, value in countries_data.items():
            if isinstance(value, list):
                for country in value:
                    if isinstance(country, dict) and "id" in country:
                        country_lookup[country["id"]] = country
        
        logger.info(f"Found {len(live_matches.get('results', []))} live matches")
        logger.info(f"Found {len(payload_data.get('team_info', {}))} teams")
        logger.info(f"Found {len(payload_data.get('competition_info', {}))} competitions")
        logger.info(f"Found {len(country_lookup)} countries")
        
        # Merge and summarize
        logger.info("Merging and summarizing match data...")
        summaries = merge_and_summarize(
            live_matches.get("results", []), 
            payload_data.get("match_details", {}), 
            payload_data.get("match_odds", {}), 
            payload_data.get("team_info", {}), 
            payload_data.get("competition_info", {}), 
            country_lookup
        )
        
        # Create the full data structure
        merged_data = {
            "summaries": summaries,
            "metadata": {
                "total_matches": len(live_matches.get("results", [])),
                "timestamp": datetime.now(TZ).strftime("%m/%d/%Y %I:%M:%S %p %Z"),
                "source": "step2.py"
            }
        }
        
        # Add processing time
        elapsed_time = time.time() - start_time
        processing_time = f"{elapsed_time:.2f} seconds"
        merged_data["metadata"]["processing_time"] = processing_time
        
        # Count in-play matches (status_id 2-7)
        in_play_count = sum(1 for match in summaries 
                           if 2 <= match.get("status_id", 0) <= 7)
        
        # Add step2 processing summary
        merged_data["step2_processing_summary"] = {
            "processed_at": datetime.now(TZ).strftime("%m/%d/%Y %I:%M:%S %p %Z"),
            "input_file": STEP1_JSON,
            "output_file": STEP2_JSON,
            "total_matches_processed": len(summaries),
            "in_play_matches": in_play_count,
            "processing_time": processing_time,
            "pipeline_timing": {
                "step2_start": datetime.now(TZ).strftime("%m/%d/%Y %I:%M:%S %p %Z"),
                "step2_duration": processing_time
            }
        }
        
        # If pipeline_start_time is provided, add it to timing
        if pipeline_start_time:
            merged_data["step2_processing_summary"]["pipeline_timing"]["pipeline_start"] = pipeline_start_time
        
        # Save to step2.json
        logger.info(f"Saving {len(summaries)} match summaries to {STEP2_JSON}...")
        success = save_match_summaries(merged_data, STEP2_JSON)
        
        if success:
            logger.info(f"Step 2 completed successfully in {processing_time} seconds")
            logger.info(f"Created {len(summaries)} match summaries")
            # Call Step 7 after Step 2 completes
            try:
                import step7
                import importlib
                importlib.reload(step7)  # Force reload to pick up any code changes
                logger.info("Starting Step 7 (filter & pretty-print)...")
                step7.run_step7(matches_list=summaries)
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to run Step 7 due to import or attribute error: {e}")
            return summaries
        else:
            logger.error("Step 2 failed to save output")
            return []
            
    except FileNotFoundError:
        logger.error(f"Could not find {STEP1_JSON}. Please run step1.py first.")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {STEP1_JSON}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in Step 2: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    main()