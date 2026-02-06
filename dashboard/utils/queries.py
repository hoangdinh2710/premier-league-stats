"""
SQL queries and data fetching utilities for the dashboard.
Supports both Supabase (cloud) and local JSON files (development).
Updated to work with Silver schema (normalized tables).
Supports multi-league and multi-season filtering.

Schema Configuration:
- Set DB_SCHEMA in .env file (defaults to 'premier_league_stats')
- Example: DB_SCHEMA=premier_league_stats
"""
import json
from pathlib import Path
import pandas as pd
import streamlit as st


def get_supabase_client():
    """
    Get Supabase client using Streamlit secrets or environment variables.

    Returns:
        Supabase client or None if not configured
    """
    try:
        from supabase import create_client

        # Try Streamlit secrets first (for Streamlit Cloud)
        if hasattr(st, 'secrets'):
            try:
                url = st.secrets.get("SUPABASE_URL")
                key = st.secrets.get("SUPABASE_KEY")
                if url and key:
                    return create_client(url, key)
            except Exception:
                pass

        # Fallback to environment variables (for local development)
        import os
        from dotenv import load_dotenv
        load_dotenv()

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if url and key:
            return create_client(url, key)

        return None
    except ImportError:
        return None


def get_schema():
    """
    Get the database schema name from environment or secrets.
    
    Returns:
        Schema name (defaults to 'premier_league_stats')
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Try Streamlit secrets first
    if hasattr(st, 'secrets'):
        try:
            return st.secrets.get("DB_SCHEMA", "premier_league_stats")
        except Exception:
            pass
    
    # Fallback to environment variable
    return os.getenv("DB_SCHEMA", "premier_league_stats")


@st.cache_data(ttl=300)
def fetch_from_supabase(
    table_name: str,
    select_query: str = "*",
    league_name: str = None,
    season: str = None,
) -> list:
    """
    Fetch data from Supabase table with caching.
    Queries from the schema specified in DB_SCHEMA env var.
    Optionally filters by league_name and/or season.

    Args:
        table_name: Name of the table to fetch (without schema prefix)
        select_query: Columns to select (default: "*")
        league_name: Optional league filter (e.g., "EPL")
        season: Optional season filter (e.g., "2025")

    Returns:
        List of records or empty list
    """
    client = get_supabase_client()
    if not client:
        return []

    try:
        # Get schema and chain it with the query
        schema = get_schema()
        query = client.schema(schema).table(table_name).select(select_query)

        # Apply optional filters
        if league_name:
            query = query.eq("league_name", league_name)
        if season:
            query = query.eq("season", season)

        response = query.execute()
        return response.data if response.data else []
    except Exception as e:
        st.warning(f"Supabase fetch error: {e}")
        return []


def get_available_leagues_and_seasons() -> tuple:
    """
    Fetch distinct league_name and season values from the database.

    Returns:
        Tuple of (leagues list, seasons list)
    """
    leagues = ["EPL"]
    seasons = ["2025"]

    client = get_supabase_client()
    if not client:
        return leagues, seasons

    try:
        schema = get_schema()

        # Fetch distinct leagues from silver_dim_teams
        league_resp = (
            client.schema(schema)
            .table("silver_dim_teams")
            .select("league_name")
            .execute()
        )
        if league_resp.data:
            found_leagues = sorted(set(r["league_name"] for r in league_resp.data if r.get("league_name")))
            if found_leagues:
                leagues = found_leagues

        # Fetch distinct seasons
        season_resp = (
            client.schema(schema)
            .table("silver_dim_teams")
            .select("season")
            .execute()
        )
        if season_resp.data:
            found_seasons = sorted(set(r["season"] for r in season_resp.data if r.get("season")), reverse=True)
            if found_seasons:
                seasons = found_seasons

    except Exception:
        pass

    return leagues, seasons


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
        'goals': 'scored',
        'goals_against': 'missed',
        'ga': 'missed',
        'gf': 'scored',
    }

    # Apply mappings
    for alt_name, expected_name in column_mappings.items():
        if alt_name in df.columns and expected_name not in df.columns:
            df[expected_name] = df[alt_name]

    return df


def get_teams_data(league_name: str = None, season: str = None):
    """
    Get team data as DataFrame from Silver schema.
    Aggregates data from silver_fact_team_match_stats.

    Args:
        league_name: Optional league filter (e.g., "EPL")
        season: Optional season filter (e.g., "2025")
    """
    # Try Supabase Silver schema first
    supabase_data = fetch_from_supabase(
        "silver_fact_team_match_stats",
        league_name=league_name,
        season=season,
    )

    if supabase_data:
        # Aggregate team statistics from match-level data
        df_matches = pd.DataFrame(supabase_data)
        
        if df_matches.empty:
            return pd.DataFrame()
        
        # Group by team and aggregate
        agg_dict = {
            'goals_for': 'sum',
            'goals_against': 'sum',
            'xg_for': 'sum',
            'xg_against': 'sum',
            'points': 'sum',
            'match_date': 'count'  # count matches
        }
        
        teams_df = df_matches.groupby(['team_id', 'team_name']).agg(agg_dict).reset_index()
        
        # Rename columns to match expected format
        teams_df = teams_df.rename(columns={
            'team_id': 'id',
            'team_name': 'title',
            'goals_for': 'scored',
            'goals_against': 'missed',
            'xg_for': 'xG',
            'xg_against': 'xGA',
            'points': 'pts',
            'match_date': 'matches'
        })
        
        # Calculate wins, draws, losses from result column
        result_counts = df_matches.groupby(['team_id', 'result']).size().unstack(fill_value=0)
        
        # Create dictionaries for mapping
        wins_dict = {}
        draws_dict = {}
        loses_dict = {}
        
        for team_id in teams_df['id']:
            if team_id in result_counts.index:
                wins_dict[team_id] = result_counts.loc[team_id, 'w'] if 'w' in result_counts.columns else 0
                draws_dict[team_id] = result_counts.loc[team_id, 'd'] if 'd' in result_counts.columns else 0
                loses_dict[team_id] = result_counts.loc[team_id, 'l'] if 'l' in result_counts.columns else 0
            else:
                wins_dict[team_id] = 0
                draws_dict[team_id] = 0
                loses_dict[team_id] = 0
        
        teams_df['wins'] = teams_df['id'].map(wins_dict)
        teams_df['draws'] = teams_df['id'].map(draws_dict)
        teams_df['loses'] = teams_df['id'].map(loses_dict)
        
        return teams_df

    # Fallback to local JSON files (old format)
    file = get_latest_file("teams_*.json")
    if not file:
        return pd.DataFrame()

    data = load_json_data(file)
    teams_list = []

    if isinstance(data, dict):
        for team_id, team_data in data.items():
            if isinstance(team_data, dict) and 'history' in team_data:
                history = team_data.get('history', [])

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
                teams_list.append(team_data)

    elif isinstance(data, list):
        teams_list = data

    df = pd.DataFrame(teams_list)

    if df.empty:
        return df

    df = normalize_team_columns(df)

    numeric_cols = ['scored', 'missed', 'xG', 'xGA', 'pts', 'wins', 'draws', 'loses', 'matches']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def get_players_data(league_name: str = None, season: str = None):
    """
    Get player data as DataFrame from Silver schema.
    Uses silver_fact_player_stats table.

    Args:
        league_name: Optional league filter (e.g., "EPL")
        season: Optional season filter (e.g., "2025")
    """
    # Try Supabase Silver schema first
    supabase_data = fetch_from_supabase(
        "silver_fact_player_stats",
        league_name=league_name,
        season=season,
    )

    if supabase_data:
        df = pd.DataFrame(supabase_data)
        
        # Rename columns to match expected format (camelCase for xG metrics)
        if not df.empty:
            df = df.rename(columns={
                'player_id': 'id',
                'player_name': 'player_name',
                'team_name': 'team_title',
                'position': 'position',
                'games': 'games',
                'minutes': 'time',  # 'time' is minutes in the old format
                'goals': 'goals',
                'assists': 'assists',
                'shots': 'shots',
                'key_passes': 'key_passes',
                'yellow_cards': 'yellow_cards',
                'red_cards': 'red_cards',
                'xg': 'xG',
                'xa': 'xA',
                'npg': 'npg',
                'npxg': 'npxG',
                'xg_chain': 'xGChain',
                'xg_buildup': 'xGBuildup'
            })
        
        return df

    # Fallback to local JSON files (old format)
    file = get_latest_file("players_*.json")
    if not file:
        return pd.DataFrame()

    data = load_json_data(file)
    df = pd.DataFrame(data)

    numeric_cols = ['goals', 'xG', 'assists', 'xA', 'shots', 'key_passes',
                    'games', 'time', 'npg', 'npxG']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def get_matches_data(league_name: str = None, season: str = None):
    """
    Get match data as DataFrame from Silver schema.
    Uses silver_fact_matches table.

    Args:
        league_name: Optional league filter (e.g., "EPL")
        season: Optional season filter (e.g., "2025")
    """
    # Try Supabase Silver schema first
    supabase_data = fetch_from_supabase(
        "silver_fact_matches",
        league_name=league_name,
        season=season,
    )

    if supabase_data:
        df = pd.DataFrame(supabase_data)
        
        if not df.empty:
            # Rename columns to match expected format
            df = df.rename(columns={
                'match_id': 'id',
                'is_completed': 'isResult',
                'home_xg': 'home_xG',
                'away_xg': 'away_xG',
                'match_datetime': 'datetime',
                'home_team_name': 'home_team',
                'away_team_name': 'away_team'
            })
            
            # Ensure id is string for consistency
            if 'id' in df.columns:
                df['id'] = df['id'].astype(str)
            
            # Filter for completed matches only
            if 'isResult' in df.columns:
                df = df[df['isResult'] == True].copy()
        
        return df

    # Fallback to local JSON files (old format)
    file = get_latest_file("matches_*.json")
    if not file:
        return pd.DataFrame()
        
    data = load_json_data(file)
    df = pd.DataFrame(data)

    if df.empty:
        return df

    # Filter for completed matches only
    if 'isResult' in df.columns:
        df = df[df['isResult'] == True].copy()

    # Parse nested data
    if 'h' in df.columns:
        df['home_team'] = df['h'].apply(lambda x: x.get('title') if isinstance(x, dict) else None)

    if 'a' in df.columns:
        df['away_team'] = df['a'].apply(lambda x: x.get('title') if isinstance(x, dict) else None)

    # Goals
    if 'goals' in df.columns:
        df['home_goals'] = df['goals'].apply(
            lambda x: x.get('h') if isinstance(x, dict) and 'h' in x else None
        )
        df['away_goals'] = df['goals'].apply(
            lambda x: x.get('a') if isinstance(x, dict) and 'a' in x else None
        )
    else:
        df['home_goals'] = None
        df['away_goals'] = None

    # xG
    if 'xG' in df.columns:
        df['home_xG'] = df['xG'].apply(
            lambda x: x.get('h') if isinstance(x, dict) and 'h' in x else None
        )
        df['away_xG'] = df['xG'].apply(
            lambda x: x.get('a') if isinstance(x, dict) and 'a' in x else None
        )
    else:
        df['home_xG'] = None
        df['away_xG'] = None

    # Convert numeric columns
    numeric_cols = ['home_goals', 'away_goals', 'home_xG', 'away_xG']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if 'goals' in col:
                df[col] = df[col].fillna(0).astype(int)
            else:
                df[col] = df[col].fillna(0.0).astype(float)

    return df


def get_shots_data(league_name: str = None, season: str = None):
    """
    Get shot data as DataFrame from Silver schema.
    Uses silver_fact_shots table.

    Args:
        league_name: Optional league filter (e.g., "EPL")
        season: Optional season filter (e.g., "2025")
    """
    # Try Supabase Silver schema first
    supabase_data = fetch_from_supabase(
        "silver_fact_shots",
        league_name=league_name,
        season=season,
    )

    if supabase_data:
        df = pd.DataFrame(supabase_data)
        
        if not df.empty:
            # Rename columns to match expected format
            df = df.rename(columns={
                'shot_id': 'id',
                'x_coord': 'X',
                'y_coord': 'Y',
                'xg': 'xG',
                'player_name': 'player',
                'team_side': 'h_a',
                'match_date': 'date',
                'shot_type': 'shotType',
                'last_action': 'lastAction',
                'home_team': 'h_team',
                'away_team': 'a_team',
                'home_goals': 'h_goals',
                'away_goals': 'a_goals'
            })
            
            # Ensure match_id is string for consistency
            if 'match_id' in df.columns:
                df['match_id'] = df['match_id'].astype(str)
        
        return df

    # Fallback to local JSON files (old format)
    file = get_latest_file("shots_*.json")
    if not file:
        return pd.DataFrame()
        
    data = load_json_data(file)
    df = pd.DataFrame(data)

    if df.empty:
        return df

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

    if 'scored' not in teams_df.columns or 'missed' not in teams_df.columns:
        if 'pts' in teams_df.columns:
            return teams_df.sort_values('pts', ascending=False).reset_index(drop=True)
        return teams_df

    teams_df['goal_diff'] = teams_df['scored'] - teams_df['missed']

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

    teams_df['xG_diff'] = teams_df['xG'] - teams_df['xGA']
    table = teams_df.sort_values('xG_diff', ascending=False).reset_index(drop=True)

    return table
