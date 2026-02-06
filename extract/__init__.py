"""
Data extraction module for Premier League xG Analytics.
"""
from .extract_league import extract_team_data, save_team_data
from .extract_players import extract_player_data, save_player_data
from .extract_matches import extract_match_data, save_match_data
from .extract_shots import extract_shot_data, save_shot_data
from .extract_rosters import extract_roster_data, save_roster_data
from .extract_team_context import extract_team_context_data, save_team_context_data

__all__ = [
    # League/Team data
    'extract_team_data',
    'save_team_data',
    # Player data
    'extract_player_data',
    'save_player_data',
    # Match data
    'extract_match_data',
    'save_match_data',
    # Shot data
    'extract_shot_data',
    'save_shot_data',
    # Roster data (NEW)
    'extract_roster_data',
    'save_roster_data',
    # Team context data (NEW)
    'extract_team_context_data',
    'save_team_context_data',
]
