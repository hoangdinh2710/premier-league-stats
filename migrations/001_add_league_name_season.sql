-- Migration: Add league_name and season to all tables
-- Purpose: Enable multi-league, multi-season support across the entire medallion architecture
-- Backfills existing rows with DEFAULT 'EPL' / '2025'

SET search_path TO premier_league_stats, public;

-- ============================================================================
-- RAW TABLES
-- ============================================================================

-- raw_teams: add league_name + season, change PK to composite
ALTER TABLE premier_league_stats.raw_teams
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.raw_teams
    DROP CONSTRAINT IF EXISTS raw_teams_pkey;
ALTER TABLE premier_league_stats.raw_teams
    ADD PRIMARY KEY (id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_raw_teams_league_season
    ON premier_league_stats.raw_teams(league_name, season);

-- raw_players: add league_name + season, change PK to composite
ALTER TABLE premier_league_stats.raw_players
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.raw_players
    DROP CONSTRAINT IF EXISTS raw_players_pkey;
ALTER TABLE premier_league_stats.raw_players
    ADD PRIMARY KEY (id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_raw_players_league_season
    ON premier_league_stats.raw_players(league_name, season);

-- raw_matches: add league_name + season, change PK to composite
ALTER TABLE premier_league_stats.raw_matches
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.raw_matches
    DROP CONSTRAINT IF EXISTS raw_matches_pkey;
ALTER TABLE premier_league_stats.raw_matches
    ADD PRIMARY KEY (id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_raw_matches_league_season
    ON premier_league_stats.raw_matches(league_name, season);

-- raw_shots: add league_name only (season already exists), PK stays id
ALTER TABLE premier_league_stats.raw_shots
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';

CREATE INDEX IF NOT EXISTS idx_raw_shots_league_name
    ON premier_league_stats.raw_shots(league_name);

CREATE INDEX IF NOT EXISTS idx_raw_shots_league_season
    ON premier_league_stats.raw_shots(league_name, season);

-- raw_rosters: add league_name + season, change PK to composite
ALTER TABLE premier_league_stats.raw_rosters
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.raw_rosters
    DROP CONSTRAINT IF EXISTS raw_rosters_pkey;
ALTER TABLE premier_league_stats.raw_rosters
    ADD PRIMARY KEY (match_id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_raw_rosters_league_season
    ON premier_league_stats.raw_rosters(league_name, season);

-- raw_team_context: add league_name, update PK to include it
ALTER TABLE premier_league_stats.raw_team_context
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';

ALTER TABLE premier_league_stats.raw_team_context
    DROP CONSTRAINT IF EXISTS raw_team_context_pkey;
ALTER TABLE premier_league_stats.raw_team_context
    ADD PRIMARY KEY (team_name, season, league_name);

CREATE INDEX IF NOT EXISTS idx_raw_team_context_league_name
    ON premier_league_stats.raw_team_context(league_name);

-- ============================================================================
-- STAGING TABLES (stg_*)
-- ============================================================================

-- stg_teams
ALTER TABLE premier_league_stats.stg_teams
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

DO $$ BEGIN
    ALTER TABLE premier_league_stats.stg_teams DROP CONSTRAINT IF EXISTS stg_teams_pkey;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;

-- stg_players
ALTER TABLE premier_league_stats.stg_players
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

DO $$ BEGIN
    ALTER TABLE premier_league_stats.stg_players DROP CONSTRAINT IF EXISTS stg_players_pkey;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;

-- stg_matches
ALTER TABLE premier_league_stats.stg_matches
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

DO $$ BEGIN
    ALTER TABLE premier_league_stats.stg_matches DROP CONSTRAINT IF EXISTS stg_matches_pkey;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;

-- stg_shots
ALTER TABLE premier_league_stats.stg_shots
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';

-- stg_rosters
ALTER TABLE premier_league_stats.stg_rosters
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

DO $$ BEGIN
    ALTER TABLE premier_league_stats.stg_rosters DROP CONSTRAINT IF EXISTS stg_rosters_pkey;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;

-- stg_team_context
ALTER TABLE premier_league_stats.stg_team_context
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';

DO $$ BEGIN
    ALTER TABLE premier_league_stats.stg_team_context DROP CONSTRAINT IF EXISTS stg_team_context_pkey;
EXCEPTION WHEN undefined_object THEN NULL;
END $$;

-- ============================================================================
-- PRODUCTION TABLES (prod_*)
-- ============================================================================

-- prod_teams
ALTER TABLE premier_league_stats.prod_teams
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.prod_teams
    DROP CONSTRAINT IF EXISTS prod_teams_pkey;
ALTER TABLE premier_league_stats.prod_teams
    ADD PRIMARY KEY (id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_prod_teams_league_season
    ON premier_league_stats.prod_teams(league_name, season);

-- prod_players
ALTER TABLE premier_league_stats.prod_players
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.prod_players
    DROP CONSTRAINT IF EXISTS prod_players_pkey;
ALTER TABLE premier_league_stats.prod_players
    ADD PRIMARY KEY (id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_prod_players_league_season
    ON premier_league_stats.prod_players(league_name, season);

-- prod_matches
ALTER TABLE premier_league_stats.prod_matches
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.prod_matches
    DROP CONSTRAINT IF EXISTS prod_matches_pkey;
ALTER TABLE premier_league_stats.prod_matches
    ADD PRIMARY KEY (id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_prod_matches_league_season
    ON premier_league_stats.prod_matches(league_name, season);

-- prod_shots
ALTER TABLE premier_league_stats.prod_shots
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';

CREATE INDEX IF NOT EXISTS idx_prod_shots_league_name
    ON premier_league_stats.prod_shots(league_name);

CREATE INDEX IF NOT EXISTS idx_prod_shots_league_season
    ON premier_league_stats.prod_shots(league_name, season);

-- prod_rosters
ALTER TABLE premier_league_stats.prod_rosters
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.prod_rosters
    DROP CONSTRAINT IF EXISTS prod_rosters_pkey;
ALTER TABLE premier_league_stats.prod_rosters
    ADD PRIMARY KEY (match_id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_prod_rosters_league_season
    ON premier_league_stats.prod_rosters(league_name, season);

-- prod_team_context
ALTER TABLE premier_league_stats.prod_team_context
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';

ALTER TABLE premier_league_stats.prod_team_context
    DROP CONSTRAINT IF EXISTS prod_team_context_pkey;
ALTER TABLE premier_league_stats.prod_team_context
    ADD PRIMARY KEY (team_name, season, league_name);

CREATE INDEX IF NOT EXISTS idx_prod_team_context_league_name
    ON premier_league_stats.prod_team_context(league_name);

-- ============================================================================
-- SILVER TABLES
-- ============================================================================

-- silver_dim_teams
ALTER TABLE premier_league_stats.silver_dim_teams
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.silver_dim_teams
    DROP CONSTRAINT IF EXISTS silver_dim_teams_pkey;
ALTER TABLE premier_league_stats.silver_dim_teams
    ADD PRIMARY KEY (team_id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_silver_dim_teams_league_season
    ON premier_league_stats.silver_dim_teams(league_name, season);

-- silver_dim_players
ALTER TABLE premier_league_stats.silver_dim_players
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.silver_dim_players
    DROP CONSTRAINT IF EXISTS silver_dim_players_pkey;
ALTER TABLE premier_league_stats.silver_dim_players
    ADD PRIMARY KEY (player_id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_silver_dim_players_league_season
    ON premier_league_stats.silver_dim_players(league_name, season);

-- silver_fact_matches
ALTER TABLE premier_league_stats.silver_fact_matches
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.silver_fact_matches
    DROP CONSTRAINT IF EXISTS silver_fact_matches_pkey;
ALTER TABLE premier_league_stats.silver_fact_matches
    ADD PRIMARY KEY (match_id, league_name, season);

CREATE INDEX IF NOT EXISTS idx_silver_fact_matches_league_season
    ON premier_league_stats.silver_fact_matches(league_name, season);

-- silver_fact_shots: add columns, PK stays shot_id (globally unique)
ALTER TABLE premier_league_stats.silver_fact_shots
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';
-- season column already exists in silver_fact_shots

CREATE INDEX IF NOT EXISTS idx_silver_fact_shots_league_name
    ON premier_league_stats.silver_fact_shots(league_name);

CREATE INDEX IF NOT EXISTS idx_silver_fact_shots_league_season
    ON premier_league_stats.silver_fact_shots(league_name, season);

-- silver_fact_player_stats
ALTER TABLE premier_league_stats.silver_fact_player_stats
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.silver_fact_player_stats
    DROP CONSTRAINT IF EXISTS silver_fact_player_stats_pkey;
ALTER TABLE premier_league_stats.silver_fact_player_stats
    ADD PRIMARY KEY (player_id, team_name, league_name, season);

CREATE INDEX IF NOT EXISTS idx_silver_fact_player_stats_league_season
    ON premier_league_stats.silver_fact_player_stats(league_name, season);

-- silver_fact_team_match_stats
ALTER TABLE premier_league_stats.silver_fact_team_match_stats
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

ALTER TABLE premier_league_stats.silver_fact_team_match_stats
    DROP CONSTRAINT IF EXISTS silver_fact_team_match_stats_pkey;
ALTER TABLE premier_league_stats.silver_fact_team_match_stats
    ADD PRIMARY KEY (team_id, match_date, league_name, season);

CREATE INDEX IF NOT EXISTS idx_silver_fact_team_match_stats_league_season
    ON premier_league_stats.silver_fact_team_match_stats(league_name, season);

-- silver_fact_rosters: add columns, PK unchanged (match_id globally unique)
ALTER TABLE premier_league_stats.silver_fact_rosters
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL',
    ADD COLUMN IF NOT EXISTS season TEXT NOT NULL DEFAULT '2025';

CREATE INDEX IF NOT EXISTS idx_silver_fact_rosters_league_season
    ON premier_league_stats.silver_fact_rosters(league_name, season);

-- silver_fact_team_context: add league_name, update PK
ALTER TABLE premier_league_stats.silver_fact_team_context
    ADD COLUMN IF NOT EXISTS league_name TEXT NOT NULL DEFAULT 'EPL';

ALTER TABLE premier_league_stats.silver_fact_team_context
    DROP CONSTRAINT IF EXISTS silver_fact_team_context_pkey;
ALTER TABLE premier_league_stats.silver_fact_team_context
    ADD PRIMARY KEY (team_name, season, league_name, context_type, context_label);

CREATE INDEX IF NOT EXISTS idx_silver_fact_team_context_league_name
    ON premier_league_stats.silver_fact_team_context(league_name);
