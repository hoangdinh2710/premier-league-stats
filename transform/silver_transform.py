"""
Silver Transform - Transform data from prod_* to silver_* tables.
Uses SQL-based transformations with materialized tables (UPSERT).
All tables in premier_league_stats schema.
"""
import os
from typing import Dict, List, Tuple
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


# Silver transformation SQL queries
# Order matters: dimensions before facts

SILVER_TRANSFORMS: List[Tuple[str, str]] = [
    # ==========================================================================
    # DIMENSION TABLES
    # ==========================================================================
    (
        'silver_dim_teams',
        f"""
        INSERT INTO {SCHEMA}.silver_dim_teams (team_id, team_name)
        SELECT
            id::int AS team_id,
            title AS team_name
        FROM {SCHEMA}.prod_teams
        ON CONFLICT (team_id) DO UPDATE SET
            team_name = EXCLUDED.team_name
        """
    ),

    (
        'silver_dim_players',
        f"""
        INSERT INTO {SCHEMA}.silver_dim_players (player_id, player_name, position, team_name)
        SELECT
            id::int AS player_id,
            player_name,
            position,
            team_title AS team_name
        FROM {SCHEMA}.prod_players
        ON CONFLICT (player_id) DO UPDATE SET
            player_name = EXCLUDED.player_name,
            position = EXCLUDED.position,
            team_name = EXCLUDED.team_name
        """
    ),

    # ==========================================================================
    # FACT TABLES
    # ==========================================================================
    (
        'silver_fact_matches',
        f"""
        INSERT INTO {SCHEMA}.silver_fact_matches (
            match_id,
            home_team_id,
            away_team_id,
            home_team_name,
            away_team_name,
            match_date,
            match_datetime,
            is_completed,
            home_goals,
            away_goals,
            home_xg,
            away_xg,
            home_forecast,
            draw_forecast,
            away_forecast
        )
        SELECT
            id::int AS match_id,
            (h->>'id')::int AS home_team_id,
            (a->>'id')::int AS away_team_id,
            h->>'title' AS home_team_name,
            a->>'title' AS away_team_name,
            datetime::date AS match_date,
            datetime::timestamp AS match_datetime,
            "isResult" AS is_completed,
            (goals->>'h')::int AS home_goals,
            (goals->>'a')::int AS away_goals,
            ("xG"->>'h')::decimal(5,2) AS home_xg,
            ("xG"->>'a')::decimal(5,2) AS away_xg,
            (forecast->>'w')::decimal(5,4) AS home_forecast,
            (forecast->>'d')::decimal(5,4) AS draw_forecast,
            (forecast->>'l')::decimal(5,4) AS away_forecast
        FROM {SCHEMA}.prod_matches
        ON CONFLICT (match_id) DO UPDATE SET
            home_team_id = EXCLUDED.home_team_id,
            away_team_id = EXCLUDED.away_team_id,
            home_team_name = EXCLUDED.home_team_name,
            away_team_name = EXCLUDED.away_team_name,
            match_date = EXCLUDED.match_date,
            match_datetime = EXCLUDED.match_datetime,
            is_completed = EXCLUDED.is_completed,
            home_goals = EXCLUDED.home_goals,
            away_goals = EXCLUDED.away_goals,
            home_xg = EXCLUDED.home_xg,
            away_xg = EXCLUDED.away_xg,
            home_forecast = EXCLUDED.home_forecast,
            draw_forecast = EXCLUDED.draw_forecast,
            away_forecast = EXCLUDED.away_forecast
        """
    ),

    (
        'silver_fact_shots',
        f"""
        INSERT INTO {SCHEMA}.silver_fact_shots (
            shot_id,
            match_id,
            player_id,
            player_name,
            team_side,
            home_team,
            away_team,
            minute,
            x_coord,
            y_coord,
            xg,
            result,
            situation,
            shot_type,
            last_action,
            player_assisted,
            season,
            match_date,
            home_goals,
            away_goals
        )
        SELECT
            id::int AS shot_id,
            match_id::int AS match_id,
            player_id::int AS player_id,
            player AS player_name,
            h_a AS team_side,
            h_team AS home_team,
            a_team AS away_team,
            minute::int AS minute,
            "X"::decimal(6,4) AS x_coord,
            "Y"::decimal(6,4) AS y_coord,
            "xG"::decimal(6,5) AS xg,
            result,
            situation,
            "shotType" AS shot_type,
            "lastAction" AS last_action,
            player_assisted,
            season::int AS season,
            date::date AS match_date,
            h_goals::int AS home_goals,
            a_goals::int AS away_goals
        FROM {SCHEMA}.prod_shots
        ON CONFLICT (shot_id) DO UPDATE SET
            match_id = EXCLUDED.match_id,
            player_id = EXCLUDED.player_id,
            player_name = EXCLUDED.player_name,
            team_side = EXCLUDED.team_side,
            home_team = EXCLUDED.home_team,
            away_team = EXCLUDED.away_team,
            minute = EXCLUDED.minute,
            x_coord = EXCLUDED.x_coord,
            y_coord = EXCLUDED.y_coord,
            xg = EXCLUDED.xg,
            result = EXCLUDED.result,
            situation = EXCLUDED.situation,
            shot_type = EXCLUDED.shot_type,
            last_action = EXCLUDED.last_action,
            player_assisted = EXCLUDED.player_assisted,
            season = EXCLUDED.season,
            match_date = EXCLUDED.match_date,
            home_goals = EXCLUDED.home_goals,
            away_goals = EXCLUDED.away_goals
        """
    ),

    (
        'silver_fact_player_stats',
        f"""
        INSERT INTO {SCHEMA}.silver_fact_player_stats (
            player_id,
            player_name,
            team_name,
            position,
            games,
            minutes,
            goals,
            assists,
            shots,
            key_passes,
            yellow_cards,
            red_cards,
            xg,
            xa,
            npg,
            npxg,
            xg_chain,
            xg_buildup
        )
        SELECT
            id::int AS player_id,
            player_name,
            team_title AS team_name,
            position,
            games::int AS games,
            time::int AS minutes,
            goals::int AS goals,
            assists::int AS assists,
            shots::int AS shots,
            key_passes::int AS key_passes,
            yellow_cards::int AS yellow_cards,
            red_cards::int AS red_cards,
            "xG"::decimal(6,2) AS xg,
            "xA"::decimal(6,2) AS xa,
            npg::int AS npg,
            "npxG"::decimal(6,2) AS npxg,
            "xGChain"::decimal(6,2) AS xg_chain,
            "xGBuildup"::decimal(6,2) AS xg_buildup
        FROM {SCHEMA}.prod_players
        ON CONFLICT (player_id, team_name) DO UPDATE SET
            player_name = EXCLUDED.player_name,
            position = EXCLUDED.position,
            games = EXCLUDED.games,
            minutes = EXCLUDED.minutes,
            goals = EXCLUDED.goals,
            assists = EXCLUDED.assists,
            shots = EXCLUDED.shots,
            key_passes = EXCLUDED.key_passes,
            yellow_cards = EXCLUDED.yellow_cards,
            red_cards = EXCLUDED.red_cards,
            xg = EXCLUDED.xg,
            xa = EXCLUDED.xa,
            npg = EXCLUDED.npg,
            npxg = EXCLUDED.npxg,
            xg_chain = EXCLUDED.xg_chain,
            xg_buildup = EXCLUDED.xg_buildup
        """
    ),

    (
        'silver_fact_team_match_stats',
        f"""
        INSERT INTO {SCHEMA}.silver_fact_team_match_stats (
            team_id,
            team_name,
            match_date,
            opponent,
            is_home,
            goals_for,
            goals_against,
            xg_for,
            xg_against,
            result,
            points,
            ppda,
            ppda_allowed,
            deep,
            deep_allowed
        )
        SELECT
            t.id::int AS team_id,
            t.title AS team_name,
            (h->>'date')::date AS match_date,
            CASE
                WHEN h->>'h_a' = 'h' THEN h->>'a_team'
                ELSE h->>'h_team'
            END AS opponent,
            (h->>'h_a' = 'h') AS is_home,
            (h->>'scored')::int AS goals_for,
            (h->>'missed')::int AS goals_against,
            (h->>'xG')::decimal(5,2) AS xg_for,
            (h->>'xGA')::decimal(5,2) AS xg_against,
            h->>'result' AS result,
            (h->>'pts')::int AS points,
            CASE
                WHEN (h->'ppda'->>'def')::decimal != 0
                THEN (h->'ppda'->>'att')::decimal / (h->'ppda'->>'def')::decimal
                ELSE NULL
            END AS ppda,
            CASE
                WHEN (h->'ppda_allowed'->>'def')::decimal != 0
                THEN (h->'ppda_allowed'->>'att')::decimal / (h->'ppda_allowed'->>'def')::decimal
                ELSE NULL
            END AS ppda_allowed,
            (h->>'deep')::int AS deep,
            (h->>'deep_allowed')::int AS deep_allowed
        FROM {SCHEMA}.prod_teams t,
             LATERAL jsonb_array_elements(t.history) AS h
        ON CONFLICT (team_id, match_date) DO UPDATE SET
            team_name = EXCLUDED.team_name,
            opponent = EXCLUDED.opponent,
            is_home = EXCLUDED.is_home,
            goals_for = EXCLUDED.goals_for,
            goals_against = EXCLUDED.goals_against,
            xg_for = EXCLUDED.xg_for,
            xg_against = EXCLUDED.xg_against,
            result = EXCLUDED.result,
            points = EXCLUDED.points,
            ppda = EXCLUDED.ppda,
            ppda_allowed = EXCLUDED.ppda_allowed,
            deep = EXCLUDED.deep,
            deep_allowed = EXCLUDED.deep_allowed
        """
    ),

    (
        'silver_fact_rosters',
        f"""
        INSERT INTO {SCHEMA}.silver_fact_rosters (
            match_id,
            team_side,
            team_name,
            player_id,
            player_name,
            position,
            position_order,
            time_played,
            goals,
            assists,
            xg,
            xa,
            shots,
            key_passes
        )
        -- Home roster
        SELECT
            r.match_id::int,
            'home' AS team_side,
            r.home_team AS team_name,
            (p.value->>'id')::int AS player_id,
            p.value->>'player' AS player_name,
            p.value->>'position' AS position,
            (p.value->>'positionOrder')::int AS position_order,
            (p.value->>'time')::int AS time_played,
            (p.value->>'goals')::int AS goals,
            (p.value->>'assists')::int AS assists,
            (p.value->>'xG')::decimal(5,2) AS xg,
            (p.value->>'xA')::decimal(5,2) AS xa,
            (p.value->>'shots')::int AS shots,
            (p.value->>'key_passes')::int AS key_passes
        FROM {SCHEMA}.prod_rosters r,
             LATERAL jsonb_each(r.home_roster) AS p
        UNION ALL
        -- Away roster
        SELECT
            r.match_id::int,
            'away' AS team_side,
            r.away_team AS team_name,
            (p.value->>'id')::int AS player_id,
            p.value->>'player' AS player_name,
            p.value->>'position' AS position,
            (p.value->>'positionOrder')::int AS position_order,
            (p.value->>'time')::int AS time_played,
            (p.value->>'goals')::int AS goals,
            (p.value->>'assists')::int AS assists,
            (p.value->>'xG')::decimal(5,2) AS xg,
            (p.value->>'xA')::decimal(5,2) AS xa,
            (p.value->>'shots')::int AS shots,
            (p.value->>'key_passes')::int AS key_passes
        FROM {SCHEMA}.prod_rosters r,
             LATERAL jsonb_each(r.away_roster) AS p
        ON CONFLICT (match_id, team_side, player_id) DO UPDATE SET
            team_name = EXCLUDED.team_name,
            player_name = EXCLUDED.player_name,
            position = EXCLUDED.position,
            position_order = EXCLUDED.position_order,
            time_played = EXCLUDED.time_played,
            goals = EXCLUDED.goals,
            assists = EXCLUDED.assists,
            xg = EXCLUDED.xg,
            xa = EXCLUDED.xa,
            shots = EXCLUDED.shots,
            key_passes = EXCLUDED.key_passes
        """
    ),
]


def refresh_table(table_name: str, transform_sql: str, truncate: bool = False) -> int:
    """
    Refresh a silver table using the provided SQL transformation.

    Args:
        table_name: Name of the silver table
        transform_sql: SQL INSERT/UPSERT query
        truncate: Whether to truncate before insert (default: False for UPSERT)

    Returns:
        Number of rows affected
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if truncate:
            cursor.execute(f"TRUNCATE {SCHEMA}.{table_name} CASCADE")

        cursor.execute(transform_sql)
        rows_affected = cursor.rowcount
        conn.commit()

        return rows_affected

    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            return_connection(conn)


def refresh_all_silver(truncate: bool = False) -> Dict[str, int]:
    """
    Refresh all silver_* tables from prod_*.

    Args:
        truncate: Whether to truncate tables before refresh

    Returns:
        Dictionary with table names and row counts
    """
    results = {}

    print("=" * 60)
    print("Transforming Bronze Prod (prod_*) -> Silver (silver_*)")
    print("=" * 60)

    for table_name, transform_sql in SILVER_TRANSFORMS:
        print(f"Refreshing {table_name}...")
        try:
            count = refresh_table(table_name, transform_sql, truncate)
            results[table_name] = count
            print(f"  Rows affected: {count}")
        except Exception as e:
            print(f"  Error: {e}")
            results[table_name] = -1

    print("=" * 60)
    print("Silver Transform complete!")
    print("=" * 60)

    return results


def get_silver_counts() -> Dict[str, int]:
    """Get row counts for all silver_* tables."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        counts = {}
        tables = [name for name, _ in SILVER_TRANSFORMS]

        for table_name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{table_name}")
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
        refresh_all_silver()

        print("\nSilver (silver_*) table counts:")
        counts = get_silver_counts()
        for table, count in counts.items():
            print(f"  {table}: {count}")

    except Exception as e:
        print(f"Error during silver transform: {e}")
        raise
    finally:
        close_pool()


if __name__ == "__main__":
    main()
