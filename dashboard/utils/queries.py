"""
SQL queries and data fetching utilities for the dashboard.
"""
import json
from pathlib import Path
import pandas as pd


def load_json_data(filename):
    """
    Load data from JSON file.
    
    Args:
        filename: Path to JSON file
    
    Returns:
        Data as list/dict
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_latest_file(pattern, data_dir="data/raw"):
    """
    Get the most recent file matching a pattern.
    
    Args:
        pattern: File pattern (e.g., "teams_*.json")
        data_dir: Directory to search
    
    Returns:
        Path to the latest file or None
    """
    data_path = Path(data_dir)
    files = sorted(data_path.glob(pattern), reverse=True)
    return files[0] if files else None


def normalize_team_columns(df):
    """
    Normalize column names to handle API variations.
    Maps common alternative column names to expected names.
    
    Args:
        df: DataFrame with team data
    
    Returns:
        DataFrame with normalized column names
    """
    if df.empty:
        return df
    
    # Column name mappings (alternative_name: expected_name)
    column_mappings = {
        'goals': 'scored',  # Understat might use 'goals' instead of 'scored'
        'goals_against': 'missed',  # Alternative name for 'missed'
        'ga': 'missed',  # Goals against abbreviation
        'gf': 'scored',  # Goals for abbreviation
    }
    
    # Apply mappings
    for alt_name, expected_name in column_mappings.items():
        if alt_name in df.columns and expected_name not in df.columns:
            df[expected_name] = df[alt_name]
    
    return df


def get_teams_data():
    """Get team data as DataFrame."""
    file = get_latest_file("teams_*.json")
    if not file:
        return pd.DataFrame()
    
    data = load_json_data(file)
    
    # Handle nested structure from Understat API
    # Data comes as: {"team_id": {"id": "...", "title": "...", "history": [...]}}
    teams_list = []
    
    if isinstance(data, dict):
        # Process each team
        for team_id, team_data in data.items():
            if isinstance(team_data, dict) and 'history' in team_data:
                # Aggregate stats from history array
                history = team_data.get('history', [])
                
                # Initialize aggregated stats
                aggregated = {
                    'id': team_data.get('id', team_id),
                    'title': team_data.get('title', 'Unknown'),
                    'scored': 0,
                    'missed': 0,
                    'xG': 0.0,
                    'xGA': 0.0,
                    'pts': 0,
                    'wins': 0,
                    'draws': 0,
                    'loses': 0,
                    'matches': len(history)
                }
                
                # Sum up stats from all matches
                for match in history:
                    if isinstance(match, dict):
                        aggregated['scored'] += match.get('scored', 0)
                        aggregated['missed'] += match.get('missed', 0)
                        aggregated['xG'] += match.get('xG', 0.0)
                        aggregated['xGA'] += match.get('xGA', 0.0)
                        aggregated['pts'] += match.get('pts', 0)
                        aggregated['wins'] += match.get('wins', 0)
                        aggregated['draws'] += match.get('draws', 0)
                        aggregated['loses'] += match.get('loses', 0)
                
                teams_list.append(aggregated)
            elif isinstance(team_data, dict):
                # If it's already a flat structure, use it as-is
                teams_list.append(team_data)
    
    elif isinstance(data, list):
        # If data is already a list, use it directly
        teams_list = data
    
    # Create DataFrame
    df = pd.DataFrame(teams_list)
    
    if df.empty:
        return df
    
    # Normalize column names
    df = normalize_team_columns(df)
    
    # Convert numeric columns
    numeric_cols = ['scored', 'missed', 'xG', 'xGA', 'pts', 'wins', 'draws', 'loses', 'matches']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def get_players_data():
    """Get player data as DataFrame."""
    file = get_latest_file("players_*.json")
    if not file:
        return pd.DataFrame()
    
    data = load_json_data(file)
    df = pd.DataFrame(data)
    
    # Convert numeric columns
    numeric_cols = ['goals', 'xG', 'assists', 'xA', 'shots', 'key_passes', 
                    'games', 'time', 'npg', 'npxG']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def get_matches_data():
    """Get match data as DataFrame."""
    file = get_latest_file("matches_*.json")
    if not file:
        return pd.DataFrame()
    
    data = load_json_data(file)
    df = pd.DataFrame(data)
    
    # Filter for completed matches only (exclude future matches)
    if 'isResult' in df.columns:
        df = df[df['isResult'] == True].copy()
    
    # Parse nested data
    if 'h' in df.columns:
        df['home_team'] = df['h'].apply(lambda x: x.get('title') if isinstance(x, dict) else None)
    
    if 'a' in df.columns:
        df['away_team'] = df['a'].apply(lambda x: x.get('title') if isinstance(x, dict) else None)
    
    # Goals are in a separate 'goals' object with 'h' and 'a' keys
    if 'goals' in df.columns:
        df['home_goals'] = df['goals'].apply(
            lambda x: x.get('h') if isinstance(x, dict) and 'h' in x else None
        )
        df['away_goals'] = df['goals'].apply(
            lambda x: x.get('a') if isinstance(x, dict) and 'a' in x else None
        )
    else:
        # Initialize columns if 'goals' column doesn't exist
        df['home_goals'] = None
        df['away_goals'] = None
    
    # xG is in a separate 'xG' object with 'h' and 'a' keys
    if 'xG' in df.columns:
        df['home_xG'] = df['xG'].apply(
            lambda x: x.get('h') if isinstance(x, dict) and 'h' in x else None
        )
        df['away_xG'] = df['xG'].apply(
            lambda x: x.get('a') if isinstance(x, dict) and 'a' in x else None
        )
    else:
        # Initialize columns if 'xG' column doesn't exist
        df['home_xG'] = None
        df['away_xG'] = None
    
    # Convert numeric columns - handle string values from JSON
    numeric_cols = ['home_goals', 'away_goals', 'home_xG', 'away_xG']
    for col in numeric_cols:
        if col in df.columns:
            # First convert to numeric (handles strings like "4" or "2.33")
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill NaN with 0 for goals (but keep NaN for xG if needed, though we'll use 0)
            if 'goals' in col:
                df[col] = df[col].fillna(0).astype(int)
            else:
                df[col] = df[col].fillna(0.0).astype(float)
    
    return df


def get_shots_data():
    """Get shot data as DataFrame."""
    file = get_latest_file("shots_*.json")
    if not file:
        return pd.DataFrame()
    
    data = load_json_data(file)
    df = pd.DataFrame(data)
    
    # Convert numeric columns
    numeric_cols = ['X', 'Y', 'xG', 'minute']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def calculate_league_table(teams_df):
    """
    Calculate league table sorted by points.
    
    Args:
        teams_df: DataFrame with team data
    
    Returns:
        Sorted DataFrame
    """
    if teams_df.empty:
        return teams_df
    
    # Check for required columns
    if 'scored' not in teams_df.columns or 'missed' not in teams_df.columns:
        # If columns are missing, try to calculate from available data or return unsorted
        if 'pts' in teams_df.columns:
            return teams_df.sort_values('pts', ascending=False).reset_index(drop=True)
        return teams_df
    
    # Sort by points (descending), then goal difference
    teams_df['goal_diff'] = teams_df['scored'] - teams_df['missed']
    
    # Build sort columns list, checking each exists
    sort_cols = []
    if 'pts' in teams_df.columns:
        sort_cols.append('pts')
    if 'goal_diff' in teams_df.columns:
        sort_cols.append('goal_diff')
    if 'scored' in teams_df.columns:
        sort_cols.append('scored')
    
    if sort_cols:
        table = teams_df.sort_values(sort_cols, ascending=[False] * len(sort_cols)).reset_index(drop=True)
    else:
        table = teams_df.reset_index(drop=True)
    
    return table


def calculate_xg_table(teams_df):
    """
    Calculate league table sorted by xG difference.
    
    Args:
        teams_df: DataFrame with team data
    
    Returns:
        Sorted DataFrame
    """
    if teams_df.empty:
        return teams_df
    
    # Sort by xG difference (xG - xGA)
    teams_df['xG_diff'] = teams_df['xG'] - teams_df['xGA']
    table = teams_df.sort_values('xG_diff', ascending=False).reset_index(drop=True)
    
    return table
