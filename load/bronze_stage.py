"""
Bronze Stage Loader - Load extracted data to stg_* tables.
Uses TRUNCATE + INSERT strategy for incremental landing zone.
All tables in premier_league_stats schema.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch, Json
from psycopg2.pool import SimpleConnectionPool


# Load environment variables
load_dotenv()

# Schema name
SCHEMA = "premier_league_stats"

# Connection pool (created on first use)
_connection_pool: SimpleConnectionPool = None


def get_connection_pool() -> SimpleConnectionPool:
    """Create and return a connection pool for Postgres."""
    global _connection_pool

    if _connection_pool is None:
        database_url = os.getenv("DATABASE_URL")

        if database_url:
            _connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=database_url,
                options=f'-c search_path={SCHEMA},public'
            )
        else:
            db_host = os.getenv("DB_HOST") or os.getenv("SUPABASE_DB_HOST")
            db_port = os.getenv("DB_PORT") or "5432"
            db_name = os.getenv("DB_NAME") or "postgres"
            db_user = os.getenv("DB_USER") or "postgres"
            db_password = os.getenv("DB_PASSWORD") or os.getenv("SUPABASE_DB_PASSWORD")

            if not all([db_host, db_user, db_password]):
                raise ValueError(
                    "Either DATABASE_URL or DB_HOST/DB_USER/DB_PASSWORD must be set"
                )

            _connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
                options=f'-c search_path={SCHEMA},public'
            )

    return _connection_pool


def get_connection():
    """Get a connection from the pool."""
    pool = get_connection_pool()
    return pool.getconn()


def return_connection(conn):
    """Return a connection to the pool."""
    pool = get_connection_pool()
    pool.putconn(conn)


def prepare_values(data: List[Dict[str, Any]], columns: List[str]) -> List[tuple]:
    """Convert dictionaries to tuples with JSON handling."""
    values_list = []
    for row in data:
        values = []
        for col in columns:
            value = row.get(col)
            if isinstance(value, (dict, list)):
                values.append(Json(value))
            else:
                values.append(value)
        values_list.append(tuple(values))
    return values_list


def load_to_stage(table_name: str, data: List[Dict[str, Any]], columns: List[str]):
    """
    Load data to stg_* table using TRUNCATE + INSERT.

    Args:
        table_name: Name of the stage table (without stg_ prefix)
        data: List of dictionaries containing row data
        columns: List of column names to insert
    """
    if not data:
        print(f"  Warning: No data to load for stg_{table_name}")
        return 0

    full_table = f"{SCHEMA}.stg_{table_name}"

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Truncate stage table
        cursor.execute(f"TRUNCATE {full_table}")

        # Prepare insert query
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([f'"{col}"' for col in columns])

        query = f"""
            INSERT INTO {full_table} ({columns_str})
            VALUES ({placeholders})
        """

        # Prepare values
        values_list = prepare_values(data, columns)

        # Batch insert
        batch_size = 1000
        for i in range(0, len(values_list), batch_size):
            batch = values_list[i:i + batch_size]
            execute_batch(cursor, query, batch, page_size=batch_size)

        conn.commit()
        return len(data)

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def load_teams_stage(filename: str) -> int:
    """Load team data to stg_teams."""
    print(f"Loading teams to stage from {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        teams_data = json.load(f)
    
    # Handle both list and dict formats (API changed from list to dict with team IDs as keys)
    if isinstance(teams_data, dict):
        teams = list(teams_data.values())
    else:
        teams = teams_data

    columns = ['id', 'title', 'history']
    count = load_to_stage('teams', teams, columns)
    print(f"  Loaded {count} teams to stg_teams")
    return count


def load_players_stage(filename: str) -> int:
    """Load player data to stg_players."""
    print(f"Loading players to stage from {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        players = json.load(f)

    columns = [
        'id', 'player_name', 'games', 'time', 'goals', 'xG', 'assists', 'xA',
        'shots', 'key_passes', 'yellow_cards', 'red_cards', 'position',
        'team_title', 'npg', 'npxG', 'xGChain', 'xGBuildup'
    ]
    count = load_to_stage('players', players, columns)
    print(f"  Loaded {count} players to stg_players")
    return count


def load_matches_stage(filename: str) -> int:
    """Load match data to stg_matches."""
    print(f"Loading matches to stage from {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        matches = json.load(f)

    columns = ['id', 'isResult', 'h', 'a', 'goals', 'xG', 'datetime', 'forecast']
    count = load_to_stage('matches', matches, columns)
    print(f"  Loaded {count} matches to stg_matches")
    return count


def load_shots_stage(filename: str) -> int:
    """Load shot data to stg_shots."""
    print(f"Loading shots to stage from {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        shots = json.load(f)

    columns = [
        'id', 'minute', 'result', 'X', 'Y', 'xG', 'player', 'h_a', 'player_id',
        'situation', 'season', 'shotType', 'match_id', 'h_team', 'a_team',
        'h_goals', 'a_goals', 'date', 'player_assisted', 'lastAction'
    ]
    count = load_to_stage('shots', shots, columns)
    print(f"  Loaded {count} shots to stg_shots")
    return count


def load_rosters_stage(filename: str) -> int:
    """Load roster data to stg_rosters."""
    print(f"Loading rosters to stage from {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        rosters = json.load(f)

    columns = ['match_id', 'home_team', 'away_team', 'datetime', 'home_roster', 'away_roster']
    count = load_to_stage('rosters', rosters, columns)
    print(f"  Loaded {count} rosters to stg_rosters")
    return count


def load_player_grouped_stage(filename: str) -> int:
    """Load grouped player data to stg_player_grouped."""
    print(f"Loading player_grouped to stage from {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        player_grouped = json.load(f)

    columns = ['player_id', 'player_name', 'team', 'position', 'games', 'time', 'grouped_stats']
    count = load_to_stage('player_grouped', player_grouped, columns)
    print(f"  Loaded {count} player_grouped records to stg_player_grouped")
    return count


def load_team_context_stage(filename: str) -> int:
    """Load team context data to stg_team_context."""
    print(f"Loading team_context to stage from {filename}...")

    with open(filename, 'r', encoding='utf-8') as f:
        team_context = json.load(f)

    columns = ['team_name', 'season', 'context_stats']
    count = load_to_stage('team_context', team_context, columns)
    print(f"  Loaded {count} team_context records to stg_team_context")
    return count


def load_all_to_stage(data_dir: str = "data/raw") -> Dict[str, int]:
    """
    Load all data files from a directory to stg_* tables.

    Args:
        data_dir: Directory containing JSON data files

    Returns:
        Dictionary with table names and row counts loaded
    """
    data_path = Path(data_dir)
    results = {}

    # Find the most recent files
    file_patterns = {
        'teams': 'teams_*.json',
        'players': 'players_*.json',
        'matches': 'matches_*.json',
        'shots': 'shots_*.json',
        'rosters': 'rosters_*.json',
        'player_grouped': 'player_grouped_*.json',
        'team_context': 'team_context_*.json',
    }

    loaders = {
        'teams': load_teams_stage,
        'players': load_players_stage,
        'matches': load_matches_stage,
        'shots': load_shots_stage,
        'rosters': load_rosters_stage,
        'player_grouped': load_player_grouped_stage,
        'team_context': load_team_context_stage,
    }

    print("=" * 60)
    print("Loading data to Bronze Stage (stg_* tables)")
    print("=" * 60)

    for table, pattern in file_patterns.items():
        files = sorted(data_path.glob(pattern), reverse=True)
        if files:
            results[table] = loaders[table](files[0])
        else:
            print(f"  Warning: No {table} data files found")
            results[table] = 0

    print("=" * 60)
    print("Bronze Stage loading complete!")
    print(f"Total records: {sum(results.values())}")
    print("=" * 60)

    return results


def close_pool():
    """Close the connection pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None


def main():
    """Main execution function."""
    try:
        load_all_to_stage()
    except Exception as e:
        print(f"Error during stage loading: {e}")
        raise
    finally:
        close_pool()


if __name__ == "__main__":
    main()
