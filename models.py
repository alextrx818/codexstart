"""
Data models for the sports pipeline - Single Source of Truth
Generated from step2.json schema - DO NOT MODIFY FIELD NAMES
Version: 2025-06-11
"""
from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import IntEnum
from datetime import datetime

class MatchStatus(IntEnum):
    """Match status constants - no magic numbers"""
    NOT_STARTED = 1
    FIRST_HALF = 2
    HALF_TIME = 3
    SECOND_HALF = 4
    OVERTIME = 5
    OVERTIME_HALF_TIME = 6
    PENALTIES = 7
    FINISHED = 9
    CANCELLED = 10
    POSTPONED = 11
    INTERRUPTED = 12
    ABANDONED = 13

# Define odds data structure
OddsEntry = List[Union[int, str, float]]  # [timestamp, source, odds1, odds2, odds3, status, ?, score]

class Environment(BaseModel):
    """Environment data for a match"""
    weather: Optional[Union[str, int]] = None  # Can be int code or string
    weather_description: Optional[str] = None
    temperature: Optional[str] = None  # String with unit like "21°C"
    wind_speed: Optional[str] = None   # String with unit like "5.1m/s"
    
    model_config = ConfigDict(extra='allow')
    
    def get_temperature_value(self) -> Optional[float]:
        """Extract numeric temperature value"""
        if self.temperature and '°' in self.temperature:
            try:
                return float(self.temperature.split('°')[0])
            except ValueError:
                return None
        return None
    
    def get_wind_speed_value(self) -> Optional[float]:
        """Extract numeric wind speed value"""
        if self.wind_speed and 'm/s' in self.wind_speed:
            try:
                return float(self.wind_speed.replace('m/s', '').strip())
            except ValueError:
                return None
        return None

class MatchSummary(BaseModel):
    """Single match data structure - enforced schema"""
    # Core identifiers
    match_id: str = Field(..., description="Unique match identifier")
    home: str = Field(..., description="Home team name")
    away: str = Field(..., description="Away team name")
    home_id: str = Field(..., description="Home team ID")
    away_id: str = Field(..., description="Away team ID")
    
    # Match status and score
    score: str = Field(..., description="Current score in format 'X-Y'")
    status: int = Field(..., description="Match status code")
    status_id: int = Field(..., description="Match status ID (same as status)")
    
    # Competition info
    competition: str = Field(..., description="Competition name")
    competition_id: str = Field(..., description="Competition ID")
    country: str = Field(default="Unknown", description="Country name")
    
    # Timing
    match_time: int = Field(..., description="Match timestamp")
    kickoff: str = Field(default="", description="Kickoff time")
    
    # Venue and positions
    venue: str = Field(default="", description="Venue name")
    home_position: str = Field(default="", description="Home team position")
    away_position: str = Field(default="", description="Away team position")
    
    # Odds data - these are lists of entries
    money_line: List[OddsEntry] = Field(default_factory=list)
    money_line_american: List[OddsEntry] = Field(default_factory=list)
    spread: List[OddsEntry] = Field(default_factory=list)
    spread_american: List[OddsEntry] = Field(default_factory=list)
    over_under: List[OddsEntry] = Field(default_factory=list)
    over_under_american: List[OddsEntry] = Field(default_factory=list)
    
    # Optional fields
    environment: Optional[Environment] = None
    
    # Allow extra fields for backward compatibility
    model_config = ConfigDict(extra='allow')
    
    def is_in_play(self) -> bool:
        """Check if match is currently in play (status 2-7)"""
        return self.status in [2, 3, 4, 5, 6, 7]
    
    def has_odds(self) -> bool:
        """Check if match has any odds data"""
        return bool(self.money_line or self.money_line_american)
    
    def get_status_name(self) -> str:
        """Get human-readable status name"""
        try:
            return MatchStatus(self.status).name.replace('_', ' ').title()
        except ValueError:
            return f"Unknown ({self.status})"

class Step2Output(BaseModel):
    """Complete step2.json output structure"""
    summaries: List[MatchSummary] = Field(..., description="List of match summaries")
    version: str = Field(default="2025-06-11", description="Schema version")
    schema_url: str = Field(
        alias="$schema",
        default="https://github.com/alextrx818/codexstart/schemas/match-summary/v2025-06-11"
    )
    
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True  # Allow both field name and alias
    )
    
    def get_in_play_matches(self) -> List[MatchSummary]:
        """Get all matches currently in play"""
        return [m for m in self.summaries if m.is_in_play()]
    
    def get_matches_with_odds(self) -> List[MatchSummary]:
        """Get all matches that have odds data"""
        return [m for m in self.summaries if m.has_odds()]

# Validation helpers
def validate_step2_json(filepath: str) -> Step2Output:
    """Load and validate step2.json file"""
    import json
    with open(filepath, 'r') as f:
        data = json.load(f)
    return Step2Output.model_validate(data)

def validate_match_data(match_dict: dict) -> MatchSummary:
    """Validate a single match dictionary"""
    return MatchSummary.model_validate(match_dict)
