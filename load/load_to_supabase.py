"""
Load extracted data to Supabase database using direct Postgres connection.
Uses direct connection for better ETL performance with bulk operations.
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


# Connection pool (created on first use)
_connection_pool: SimpleConnectionPool = None


def get_connection_pool() -> SimpleConnectionPool:
    """
    Create and return a connection pool for Postgres.
    
    Returns:
        Connection pool instance
    """
    global _connection_pool
    
    if _connection_pool is None:
        # Try DATABASE_URL first (direct connection string)
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # Parse connection string
            # Format: postgresql://user:password@host:port/database
            _connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=database_url,
                options=f'-c search_path={os.getenv("DB_SCHEMA", "public")}'
            )
        else:
            # Fallback to individual parameters
            db_host = os.getenv("DB_HOST") or os.getenv("SUPABASE_DB_HOST")
            db_port = os.getenv("DB_PORT") or "5432"
            db_name = os.getenv("DB_NAME") or "postgres"
            db_user = os.getenv("DB_USER") or "postgres"
            db_password = os.getenv("DB_PASSWORD") or os.getenv("SUPABASE_DB_PASSWORD")
            
            if not all([db_host, db_user, db_password]):
                raise ValueError(
                    "Either DATABASE_URL or DB_HOST/DB_USER/DB_PASSWORD must be set in .env file.\n"
                    "For Supabase, get your connection string from:\n"
                    "Project Settings > Database > Connection String (Direct connection)"
                )
            
            _connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password,
                options=f'-c search_path={os.getenv("DB_SCHEMA", "public")}'
            )
    
    return _connection_pool


def get_connection():
    """
    Get a connection from the pool.
    
    Returns:
        Database connection
    """
    pool = get_connection_pool()
    return pool.getconn()


def return_connection(conn):
    """
    Return a connection to the pool.
    
    Args:
        conn: Database connection to return
    """
    pool = get_connection_pool()
    pool.putconn(conn)


def prepare_data_for_insert(data: List[Dict[str, Any]], table_name: str) -> tuple:
    """
    Prepare data for bulk insert by extracting column names and values.
    
    Args:
        data: List of dictionaries containing row data
        table_name: Name of the table
    
    Returns:
        Tuple of (columns, values_list)
    """
    if not data:
        return [], []
    
    # Get all unique keys from all dictionaries
    columns = list(data[0].keys())
    
    # Convert each dict to tuple of values in column order
    values_list = []
    for row in data:
        values = []
        for col in columns:
            value = row.get(col)
            # Convert dict/list to JSON for JSONB columns
            if isinstance(value, (dict, list)):
                values.append(Json(value))
            else:
                values.append(value)
        values_list.append(tuple(values))
    
    return columns, values_list


def load_teams(filename: str):
    """
    Load team data to Supabase using direct Postgres connection.
    
    Args:
        filename: Path to teams JSON file
    """
    print(f"Loading team data from {filename}...")
    
    # Read JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    if not teams:
        print("Warning: No team data to load")
        return
    
    # Prepare data
    columns, values_list = prepare_data_for_insert(teams, 'raw_teams')
    
    # Build INSERT ... ON CONFLICT DO UPDATE query
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f'"{col}"' for col in columns])
    
    # Assume first column is primary key for conflict resolution
    # Adjust based on your actual table schema
    conflict_cols = columns[0] if columns else 'id'
    
    update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
    
    query = f"""
        INSERT INTO raw_teams ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}
    """
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute batch insert
        execute_batch(cursor, query, values_list, page_size=100)
        conn.commit()
        
        print(f"Success: Loaded {len(teams)} teams to raw_teams table")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error loading teams: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def load_players(filename: str):
    """
    Load player data to Supabase using direct Postgres connection.
    
    Args:
        filename: Path to players JSON file
    """
    print(f"Loading player data from {filename}...")
    
    # Read JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        players = json.load(f)
    
    if not players:
        print("Warning: No player data to load")
        return
    
    # Prepare data
    columns, values_list = prepare_data_for_insert(players, 'raw_players')
    
    # Build INSERT ... ON CONFLICT DO UPDATE query
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f'"{col}"' for col in columns])
    
    conflict_cols = columns[0] if columns else 'id'
    update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
    
    query = f"""
        INSERT INTO raw_players ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}
    """
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute batch insert
        execute_batch(cursor, query, values_list, page_size=100)
        conn.commit()
        
        print(f"Success: Loaded {len(players)} players to raw_players table")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error loading players: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def load_matches(filename: str):
    """
    Load match data to Supabase using direct Postgres connection.
    
    Args:
        filename: Path to matches JSON file
    """
    print(f"Loading match data from {filename}...")
    
    # Read JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    if not matches:
        print("Warning: No match data to load")
        return
    
    # Prepare data
    columns, values_list = prepare_data_for_insert(matches, 'raw_matches')
    
    # Build INSERT ... ON CONFLICT DO UPDATE query
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f'"{col}"' for col in columns])
    
    conflict_cols = columns[0] if columns else 'id'
    update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
    
    query = f"""
        INSERT INTO raw_matches ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}
    """
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute batch insert
        execute_batch(cursor, query, values_list, page_size=100)
        conn.commit()
        
        print(f"Success: Loaded {len(matches)} matches to raw_matches table")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error loading matches: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def load_shots(filename: str):
    """
    Load shot data to Supabase using direct Postgres connection.
    Optimized for large datasets with efficient batch processing.
    
    Args:
        filename: Path to shots JSON file
    """
    print(f"Loading shot data from {filename}...")
    
    # Read JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        shots = json.load(f)
    
    if not shots:
        print("Warning: No shot data to load")
        return
    
    # Prepare data
    columns, values_list = prepare_data_for_insert(shots, 'raw_shots')
    
    # Build INSERT ... ON CONFLICT DO UPDATE query
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f'"{col}"' for col in columns])
    
    conflict_cols = columns[0] if columns else 'id'
    update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
    
    query = f"""
        INSERT INTO raw_shots ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}
    """
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Use larger page size for shots (more efficient for large datasets)
        batch_size = 2000
        total = len(values_list)
        
        for i in range(0, total, batch_size):
            batch = values_list[i:i + batch_size]
            execute_batch(cursor, query, batch, page_size=batch_size)
            conn.commit()
            print(f"  - Loaded batch {i // batch_size + 1} ({len(batch)} shots)")
        
        print(f"Success: Loaded {total} shots to raw_shots table")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error loading shots: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def load_rosters(filename: str):
    """
    Load roster/lineup data to Supabase using direct Postgres connection.
    
    Args:
        filename: Path to rosters JSON file
    """
    print(f"Loading roster data from {filename}...")
    
    # Read JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        rosters = json.load(f)
    
    if not rosters:
        print("Warning: No roster data to load")
        return
    
    # Prepare data
    columns, values_list = prepare_data_for_insert(rosters, 'raw_rosters')
    
    # Build INSERT ... ON CONFLICT DO UPDATE query
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f'"{col}"' for col in columns])
    
    conflict_cols = columns[0] if columns else 'match_id'
    update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
    
    query = f"""
        INSERT INTO raw_rosters ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}
    """
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute batch insert
        execute_batch(cursor, query, values_list, page_size=100)
        conn.commit()
        
        print(f"Success: Loaded {len(rosters)} rosters to raw_rosters table")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error loading rosters: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def load_team_context(filename: str):
    """
    Load team context statistics to Supabase using direct Postgres connection.
    
    Args:
        filename: Path to team_context JSON file
    """
    print(f"Loading team context data from {filename}...")
    
    # Read JSON file
    with open(filename, 'r', encoding='utf-8') as f:
        team_context = json.load(f)
    
    if not team_context:
        print("Warning: No team context data to load")
        return
    
    # Prepare data
    columns, values_list = prepare_data_for_insert(team_context, 'raw_team_context')
    
    # Build INSERT ... ON CONFLICT DO UPDATE query
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f'"{col}"' for col in columns])
    
    # Composite primary key: team_name, season
    conflict_cols = 'team_name, season'
    update_set = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
    
    query = f"""
        INSERT INTO raw_team_context ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}
    """
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Execute batch insert
        execute_batch(cursor, query, values_list, page_size=100)
        conn.commit()
        
        print(f"Success: Loaded {len(team_context)} team context records to raw_team_context table")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error loading team context data: {e}")
        raise
    finally:
        if conn:
            return_connection(conn)


def load_all(data_dir="data/raw"):
    """
    Load all data files from a directory to Supabase.
    
    Args:
        data_dir: Directory containing JSON data files
    """
    data_path = Path(data_dir)
    
    # Find the most recent files
    team_files = sorted(data_path.glob("teams_*.json"), reverse=True)
    player_files = sorted(data_path.glob("players_*.json"), reverse=True)
    match_files = sorted(data_path.glob("matches_*.json"), reverse=True)
    roster_files = sorted(data_path.glob("rosters_*.json"), reverse=True)
    shot_files = sorted(data_path.glob("shots_*.json"), reverse=True)
    team_context_files = sorted(data_path.glob("team_context_*.json"), reverse=True)
    
    print("=" * 60)
    print("Loading data to Supabase (Direct Postgres Connection)")
    print("=" * 60)
    
    # Load each dataset
    if team_files:
        load_teams(team_files[0])
    else:
        print("Warning: No team data files found")
    
    if player_files:
        load_players(player_files[0])
    else:
        print("Warning: No player data files found")
    
    if match_files:
        load_matches(match_files[0])
    else:
        print("Warning: No match data files found")
    
    if roster_files:
        load_rosters(roster_files[0])
    else:
        print("Warning: No roster data files found")
    
    if shot_files:
        load_shots(shot_files[0])
    else:
        print("Warning: No shot data files found")
    
    if team_context_files:
        load_team_context(team_context_files[0])
    else:
        print("Warning: No team context data files found")
    
    print("=" * 60)
    print("Success: Data loading complete!")
    print("=" * 60)


def close_pool():
    """
    Close the connection pool. Call this when done with all operations.
    """
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None


def main():
    """Main execution function."""
    try:
        load_all()
    except Exception as e:
        print(f"Error during data loading: {e}")
        raise
    finally:
        # Clean up connection pool
        close_pool()


if __name__ == "__main__":
    main()
