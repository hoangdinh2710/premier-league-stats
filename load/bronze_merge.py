"""
Bronze Merge - Merge data from stg_* to prod_* tables.
Uses UPSERT (INSERT ... ON CONFLICT DO UPDATE) strategy.
All tables in premier_league_stats schema.
Supports multiple leagues and seasons.
"""
import os
from typing import Dict, List
from dotenv import load_dotenv
import psycopg2
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


# Table configurations: columns and primary keys
TABLE_CONFIGS = {
    'teams': {
        'columns': ['id', 'title', 'history', 'league_name', 'season'],
        'pk': ['id', 'league_name', 'season'],
    },
    'players': {
        'columns': [
            'id', 'player_name', 'games', 'time', 'goals', 'xG', 'assists', 'xA',
            'shots', 'key_passes', 'yellow_cards', 'red_cards', 'position',
            'team_title', 'npg', 'npxG', 'xGChain', 'xGBuildup',
            'league_name', 'season'
        ],
        'pk': ['id', 'league_name', 'season'],
    },
    'matches': {
        'columns': ['id', 'isResult', 'h', 'a', 'goals', 'xG', 'datetime', 'forecast',
                     'league_name', 'season'],
        'pk': ['id', 'league_name', 'season'],
    },
    'shots': {
        'columns': [
            'id', 'minute', 'result', 'X', 'Y', 'xG', 'player', 'h_a', 'player_id',
            'situation', 'season', 'shotType', 'match_id', 'h_team', 'a_team',
            'h_goals', 'a_goals', 'date', 'player_assisted', 'lastAction',
            'league_name'
        ],
        'pk': ['id'],
    },
    'rosters': {
        'columns': ['match_id', 'home_team', 'away_team', 'datetime', 'home_roster', 'away_roster',
                     'league_name', 'season'],
        'pk': ['match_id', 'league_name', 'season'],
    },
    'team_context': {
        'columns': ['team_name', 'season', 'league_name', 'context_stats'],
        'pk': ['team_name', 'season', 'league_name'],
    },
}


def merge_table(table_name: str, columns: List[str], pk_columns: List[str]) -> Dict[str, int]:
    """
    Merge data from stg_* to prod_* using UPSERT.

    Args:
        table_name: Name of the table (without prefix)
        columns: List of column names
        pk_columns: List of primary key column names

    Returns:
        Dictionary with 'inserted' and 'updated' counts
    """
    stg_table = f"{SCHEMA}.stg_{table_name}"
    prod_table = f"{SCHEMA}.prod_{table_name}"

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get count before merge
        cursor.execute(f"SELECT COUNT(*) FROM {prod_table}")
        count_before = cursor.fetchone()[0]

        # Get stage count
        cursor.execute(f"SELECT COUNT(*) FROM {stg_table}")
        stage_count = cursor.fetchone()[0]

        if stage_count == 0:
            print(f"  {table_name}: No data in stage to merge")
            return {'inserted': 0, 'updated': 0}

        # Build column strings
        columns_str = ', '.join([f'"{col}"' for col in columns])
        pk_str = ', '.join([f'"{col}"' for col in pk_columns])

        # Build update set (exclude PK columns and timestamps)
        update_columns = [c for c in columns if c not in pk_columns]
        update_set = ', '.join([
            f'"{col}" = EXCLUDED."{col}"' for col in update_columns
        ])

        # Add updated_at to update set
        update_set += ', updated_at = NOW()'

        # Build merge query
        merge_sql = f"""
            INSERT INTO {prod_table} ({columns_str}, created_at, updated_at)
            SELECT {columns_str}, NOW(), NOW()
            FROM {stg_table}
            ON CONFLICT ({pk_str}) DO UPDATE SET {update_set}
        """

        cursor.execute(merge_sql)
        rows_affected = cursor.rowcount
        conn.commit()

        # Get count after merge
        cursor.execute(f"SELECT COUNT(*) FROM {prod_table}")
        count_after = cursor.fetchone()[0]

        inserted = count_after - count_before
        updated = rows_affected - inserted

        return {'inserted': inserted, 'updated': updated}

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def merge_all_to_prod() -> Dict[str, Dict[str, int]]:
    """
    Merge all stg_* tables to prod_*.

    Returns:
        Dictionary with table names and their insert/update counts
    """
    results = {}

    print("=" * 60)
    print("Merging Bronze Stage (stg_*) -> Bronze Prod (prod_*)")
    print("=" * 60)

    for table_name, config in TABLE_CONFIGS.items():
        print(f"Merging {table_name}...")
        result = merge_table(table_name, config['columns'], config['pk'])
        results[table_name] = result
        print(f"  Inserted: {result['inserted']}, Updated: {result['updated']}")

    print("=" * 60)
    print("Bronze Merge complete!")
    total_inserted = sum(r['inserted'] for r in results.values())
    total_updated = sum(r['updated'] for r in results.values())
    print(f"Total inserted: {total_inserted}, Total updated: {total_updated}")
    print("=" * 60)

    return results


def get_prod_counts() -> Dict[str, int]:
    """Get row counts for all prod_* tables."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        counts = {}
        for table_name in TABLE_CONFIGS.keys():
            cursor.execute(f"SELECT COUNT(*) FROM {SCHEMA}.prod_{table_name}")
            counts[table_name] = cursor.fetchone()[0]

        return counts
    finally:
        if conn:
            return_connection(conn)


def close_pool():
    """Close the connection pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None


def main():
    """Main execution function."""
    try:
        merge_all_to_prod()

        print("\nBronze Prod (prod_*) table counts:")
        counts = get_prod_counts()
        for table, count in counts.items():
            print(f"  prod_{table}: {count}")

    except Exception as e:
        print(f"Error during merge: {e}")
        raise
    finally:
        close_pool()


if __name__ == "__main__":
    main()
