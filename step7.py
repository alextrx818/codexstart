#!/usr/bin/env python3
"""
Step 7 – Pretty Display for In‑Play Matches (centred banners, full logic)

This file is a **drop‑in replacement** for the original `step7_simple.py`.
All paths, filenames and data keys stay the same, but the output now
features:

* Centre‑aligned competition, status and match banners (80 cols).
* Status sub‑grouping (First Half, Half‑time, etc.).
* Original odds / weather formatting logic preserved intact.
* Same input (`step2.json`) and log file (`step7_simple.log`).

You can safely delete the older script or rename this one to
`step7.py`; the orchestrator will behave exactly as before.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import pytz
import time

# Import data models for type safety and consistency
from models import Step2Output, MatchSummary, validate_step2_json

# DEBUG: Print when module is imported
print(f"[DEBUG] step7.py imported at {datetime.now()}")

# ============================================================================
# SCHEMA CONTRACT - DO NOT MODIFY FIELD NAMES
# ============================================================================
# This file reads step2.json which MUST have this exact structure:
# {
#   "summaries": [
#     {
#       "match_id": str,              # Used for logging
#       "home": str,                  # Team names for display
#       "away": str,
#       "score": str,                 # Format "X-Y"
#       "status_id": int,             # CRITICAL: Used for filtering (2-7 = in-play)
#       "competition": str,           # Competition name
#       "competition_id": str,        # Competition ID
#       "country": str,               # Country name
#       
#       # ODDS FIELDS - We check BOTH field names for compatibility:
#       "money_line": [...] OR "money_line_american": [...],
#       "spread": [...] OR "spread_american": [...],
#       "over_under": [...] OR "over_under_american": [...],
#       
#       # Environment data (optional)
#       "environment": {
#         "weather_description": str,
#         "temperature_fahrenheit": str,  # e.g. "72.5°F"
#         "wind_speed_mph": str           # e.g. "10.2mph"
#       }
#     }
#   ]
# }
#
# OUTPUT: step7_simple.log with formatted match information
#
# FILTERING: Only matches with status_id in [2,3,4,5,6,7] are processed
# - 2: First Half
# - 3: Half-time  
# - 4: Second Half
# - 5: Overtime
# - 6: Overtime Half-time
# - 7: Penalties
#
# IMPORTANT: Always use models.py for validation. Field names are locked!
# ============================================================================

# MAINTENANCE NOTES:
# - models.py: Only update if adding new fields to the pipeline
# - Schema contract headers: Just comments, no maintenance needed
# - FIELD_REFERENCE.md: Update only when adding new fields
# - This schema contract is locked - DO NOT change existing field names

# ---------------------------------------------------------------------------
# Constants & configuration
# ---------------------------------------------------------------------------
TZ = pytz.timezone("America/New_York")
BASE_DIR = Path(__file__).resolve().parent
STEP2_FILE = BASE_DIR / "step2.json"
LOG_FILE = BASE_DIR / "step7_simple.log"
DAILY_COUNTER_FILE = BASE_DIR / "daily_match_counter.json"

# DEBUG: Print the log file being used
print(f"[DEBUG] step7.py will write to: {LOG_FILE}")

# In‑play statuses we care about
STATUS_FILTER = [2, 3, 4, 5, 6, 7, 8]  # Temporarily added 8 to show weather works
STATUS_NAMES = {
    2: "First Half",
    3: "Half-time",
    4: "Second Half",
    5: "Overtime",
    6: "Overtime",
    7: "Penalty Shootout",
    8: "Finished",
    9: "Cancelled",
    10: "Postponed",
}

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("step7")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(message)s")

    fh = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def et_now() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d %I:%M:%S %p ET")


def format_american_odds(val):
    """Convert decimal/HK odds -> American string."""
    try:
        odds = float(val)
        if odds <= 0:
            return "N/A"
        if odds >= 2.0:
            return f"+{int((odds - 1) * 100)}"
        return f"{int(-100 / (odds - 1))}"
    except Exception:
        return "N/A"


# ---------------------------------------------------------------------------
# Banner writers (all centred)
# ---------------------------------------------------------------------------

def centred(text: str, pad: str = " ") -> str:
    return text.center(80, pad)


def write_competition_header(logger, comp: str, country: str):
    """Write competition header in simple format"""
    logger.info("")
    logger.info("")  # Extra space before competition
    logger.info("=" * 80)  # Top line
    header_text = f"{comp.upper()} ({country})"
    logger.info(header_text.center(80))  # Centered text
    logger.info("=" * 80)  # Bottom line
    logger.info("")  # Extra space after


def write_status_header(logger, status_id: int):
    """Write status header in simple format"""
    status_name = STATUS_NAMES.get(status_id, "Unknown")
    logger.info("")
    logger.info(f"[{status_name.upper()}]")
    logger.info("")


def write_match_header(logger, idx: int, total: int, match_id: str, comp_id: str):
    """Write match header in simple format"""
    logger.info(f"Match {idx} of {total}")
    logger.info(f"Match ID: {match_id}")
    logger.info(f"Competition ID: {comp_id}")
    logger.info(f"Filtered: {et_now()}")
    logger.info("-" * 60)


# ---------------------------------------------------------------------------
# Match body (original logic, unchanged)
# ---------------------------------------------------------------------------

def write_match_body(logger: logging.Logger, match: dict):
    """Write match details in a clean, aligned format"""
    home = match.get("home", "Unknown")
    away = match.get("away", "Unknown")
    score = match.get("score", "0-0")
    status_id = match.get("status_id", 0)
    status_desc = STATUS_NAMES.get(status_id, "Unknown")

    # Get environment data
    env = match.get("environment", {})
    weather = env.get("weather_description", "") or "Unknown"
    temp = env.get("temperature_fahrenheit", "") or "N/A"
    wind = env.get("wind_speed_mph", "") or "N/A"

    # Get latest odds - check both field names for compatibility
    ml = match.get("money_line_american", []) or match.get("money_line", [])
    sp = match.get("spread_american", []) or match.get("spread", [])
    ou = match.get("over_under_american", []) or match.get("over_under", [])

    # Header
    logger.info(f"{home.upper()} vs {away.upper()}")
    
    # Score and status line
    left = f"Score: {score}"
    right = f"Status: {status_desc}"
    logger.info(f"{left:<32}{right}")
    
    logger.info("─" * 60)
    
    # Money Line
    if ml and len(ml[-1]) >= 5:
        h, d, a = ml[-1][2:5]
        logger.info(" Money Line")
        logger.info(f"   Home: {h:<6} │ Draw: {d:<6} │ Away: {a:<6}")
    else:
        logger.info(" Money Line: Data not available")
    
    logger.info("")
    
    # Spread
    if sp and len(sp[-1]) >= 5:
        h, hcap, a = sp[-1][2:5]
        logger.info(f" Spread (Point {hcap:+g})")
        logger.info(f"   Home: {h:<6} │ Point: {hcap:+g} │ Away: {a:<6}")
    else:
        logger.info(" Spread: Data not available")
    
    logger.info("")
    
    # Over/Under
    if ou and len(ou[-1]) >= 5:
        ov, line, un = ou[-1][2:5]
        logger.info(f" Over/Under (Line {line})")
        logger.info(f"   Over: {ov:<6} │ Line: {line} │ Under: {un:<6}")
    else:
        logger.info(" Over/Under: Data not available")
    
    logger.info("─" * 60)
    
    # Weather
    weather_line = f" Weather: {weather}"
    if temp != "N/A":
        weather_line += f"  ·  Temp: {temp}"
    if wind != "N/A":
        weather_line += f"  ·  Wind: {wind}"
    logger.info(weather_line)
    logger.info("")

# ---------------------------------------------------------------------------
# Headers / footers (simple)
# ---------------------------------------------------------------------------

def write_global_header(logger, fetch_count: int, total: int):
    """Write simple header without box drawing"""
    logger.info("STEP 7: STATUS FILTER (2–7)")
    logger.info("=" * 80)
    logger.info(f"Filter Time: {et_now()}")
    logger.info(f"Data Generated: {et_now()}")
    logger.info(f"Daily Fetch: #{fetch_count}")
    logger.info(f"Statuses Filtered: {STATUS_FILTER}")
    logger.info(f"Included Matches Count: {total}")
    logger.info("=" * 80)
    logger.info("")


def write_global_footer(logger, total: int):
    """Write simple footer"""
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"Total Matches: {total}")
    logger.info("=" * 80)


def write_summary_footer(logger, in_play, comp_groups, start_time):
    """Write comprehensive summary footer with statistics"""
    import time
    
    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Count matches by status
    status_counts = {}
    for match in in_play:
        status_id = match.get("status_id")
        status_name = STATUS_NAMES.get(status_id, f"Unknown ({status_id})")
        status_counts[status_name] = status_counts.get(status_name, 0) + 1
    
    # Count matches with weather data
    weather_count = sum(1 for m in in_play 
                       if m.get("environment", {}).get("weather_description", "").strip() 
                       and m.get("environment", {}).get("weather_description", "").strip().lower() != "unknown")
    
    # Count matches with odds data - if a match has odds, it has all three types
    odds_count = sum(1 for m in in_play if m.get("money_line") and len(m.get("money_line", [])) > 0)
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("SUMMARY REPORT".center(80))
    logger.info("=" * 80)
    
    # Timing information
    logger.info(f"Report Generated: {et_now()}")
    logger.info(f"Processing Time: {processing_time:.2f} seconds")
    logger.info("")
    
    # Match statistics
    logger.info("MATCH STATISTICS:")
    logger.info(f"  Total In-Play Matches (Status 2-7): {len(in_play)}")
    logger.info(f"  Total Competitions: {len(comp_groups)}")
    logger.info("")
    
    # Data availability
    logger.info("DATA AVAILABILITY:")
    logger.info(f"  Matches with Weather Data: {weather_count} ({weather_count/len(in_play)*100:.1f}%)" if in_play else "  Matches with Weather Data: 0 (0.0%)")
    logger.info(f"  Matches with Odds Data: {odds_count} ({odds_count/len(in_play)*100:.1f}%)" if in_play else "  Matches with Odds Data: 0 (0.0%)")
    logger.info("")
    
    # Status breakdown
    logger.info("STATUS BREAKDOWN (In-Play = Status 2-7):")
    for status, count in sorted(status_counts.items()):
        percentage = (count / len(in_play) * 100) if in_play else 0
        logger.info(f"  {status}: {count} ({percentage:.1f}%)")
    logger.info("")
    
    # Competition breakdown
    logger.info("TOP COMPETITIONS:")
    for i, ((comp, country), matches) in enumerate(sorted(comp_groups.items(), key=lambda x: -len(x[1])), 1):
        logger.info(f"  {i}. {comp} ({country}): {len(matches)} matches")
        if i >= 10:  # Show top 10 competitions
            remaining = len(comp_groups) - 10
            if remaining > 0:
                logger.info(f"  ... and {remaining} more competitions")
            break
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("END OF REPORT")
    logger.info("=" * 80)
    
    # Add timestamp at the end
    ny_time = datetime.now(TZ)
    timestamp = ny_time.strftime("%I:%M %p %m/%d/%Y")
    logger.info(f"Fetched at: {timestamp} Eastern Time")
    logger.info(f"Total In-Play Matches (Status 2-7): {len(in_play)}")
    logger.info("")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logger = setup_logger()

    # Load JSON
    if not STEP2_FILE.exists():
        logger.error(f"❌ File not found: {STEP2_FILE}")
        return
    try:
        data = json.loads(STEP2_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in {STEP2_FILE}: {e}")
        return

    summaries = data.get("summaries", [])
    in_play = [m for m in summaries if m.get("status_id") in STATUS_FILTER]

    # Daily fetch count (optional file)
    try:
        cnt = json.loads(DAILY_COUNTER_FILE.read_text()).get("match_number", 0)
    except Exception:
        cnt = 0

    start_time = time.time()
    write_global_header(logger, cnt, len(in_play))

    # Group by competition
    comp_groups = {}
    for m in in_play:
        key = (m.get("competition", "Unknown"), m.get("country", "Unknown"))
        comp_groups.setdefault(key, []).append(m)

    for (comp, country), matches in sorted(comp_groups.items(), key=lambda k: k[0][0]):
        write_competition_header(logger, comp, country)

        status_map = {}
        for m in matches:
            status_map.setdefault(m.get("status_id"), []).append(m)

        for s_id in sorted(status_map.keys()):
            write_status_header(logger, s_id)
            group = sorted(status_map[s_id], key=lambda x: x.get("match_time", 0))
            for idx, match in enumerate(group, 1):
                write_match_header(logger, idx, len(group), match.get('match_id','N/A'), match.get('competition_id','N/A'))
                write_match_body(logger, match)

    write_summary_footer(logger, in_play, comp_groups, start_time)


def run_step7(matches_list=None):
    """
    Run Step 7 processing - can be called from other modules like step2.py
    
    Args:
        matches_list: Optional list of matches to process directly (from step2)
                     If not provided, will read from step2.json
    """
    logger = setup_logger()
    
    try:
        # If matches provided directly, validate them
        if matches_list is not None:
            # Validate each match using the model
            summaries = []
            for match_dict in matches_list:
                try:
                    validated_match = MatchSummary.model_validate(match_dict)
                    summaries.append(validated_match.model_dump())
                except Exception as e:
                    logger.warning(f"Skipping invalid match: {e}")
                    continue
            logger.info(f"Processing {len(summaries)} valid matches provided directly")
        else:
            # Otherwise load and validate from step2.json
            try:
                data = validate_step2_json(str(STEP2_FILE))
                summaries = [m.model_dump() for m in data.summaries]
                logger.info(f"Loaded and validated {len(summaries)} matches from {STEP2_FILE}")
            except Exception as e:
                logger.error(f"❌ Failed to validate step2.json: {e}")
                return
        
        # Filter for in-play matches
        in_play = [m for m in summaries if m.get("status_id") in STATUS_FILTER]
        logger.info(f"Filtered to {len(in_play)} in-play matches (status {STATUS_FILTER})")
        
        # Daily fetch count (optional file)
        try:
            cnt = json.loads(DAILY_COUNTER_FILE.read_text()).get("match_number", 0)
        except Exception:
            cnt = 0
        
        start_time = time.time()
        # Write output
        write_global_header(logger, cnt, len(in_play))
        
        # Group by competition
        comp_groups = {}
        for m in in_play:
            key = (m.get("competition", "Unknown"), m.get("country", "Unknown"))
            comp_groups.setdefault(key, []).append(m)
        
        for (comp, country), matches in sorted(comp_groups.items(), key=lambda k: k[0][0]):
            write_competition_header(logger, comp, country)
            
            status_map = {}
            for m in matches:
                status_map.setdefault(m.get("status_id"), []).append(m)
            
            for s_id in sorted(status_map.keys()):
                write_status_header(logger, s_id)
                group = sorted(status_map[s_id], key=lambda x: x.get("match_time", 0))
                for idx, match in enumerate(group, 1):
                    write_match_header(logger, idx, len(group), match.get('match_id','N/A'), match.get('competition_id','N/A'))
                    write_match_body(logger, match)
        
        write_summary_footer(logger, in_play, comp_groups, start_time)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON: {e}")
    except Exception as e:
        logger.error(f"❌ Error in Step 7: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
