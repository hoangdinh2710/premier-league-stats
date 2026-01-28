-- Premier League Stats Database Schema
-- Tables for storing raw data from Understat API

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS premier_league_stats;

-- Set search path to use the schema
SET search_path TO premier_league_stats, public;

-- Drop tables if they exist (be careful with this in production)
DROP TABLE IF EXISTS premier_league_stats.raw_shots CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_matches CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_players CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_player_grouped CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_rosters CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_team_context CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_teams CASCADE;

-- Teams table
CREATE TABLE premier_league_stats.raw_teams (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    history JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on team title for faster lookups
CREATE INDEX idx_raw_teams_title ON premier_league_stats.raw_teams(title);

-- Players table
CREATE TABLE premier_league_stats.raw_players (
    id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    games TEXT,
    time TEXT,
    goals TEXT,
    "xG" TEXT,
    assists TEXT,
    "xA" TEXT,
    shots TEXT,
    key_passes TEXT,
    yellow_cards TEXT,
    red_cards TEXT,
    position TEXT,
    team_title TEXT,
    npg TEXT,
    "npxG" TEXT,
    "xGChain" TEXT,
    "xGBuildup" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on player table
CREATE INDEX idx_raw_players_name ON premier_league_stats.raw_players(player_name);
CREATE INDEX idx_raw_players_team ON premier_league_stats.raw_players(team_title);

-- Matches table
CREATE TABLE premier_league_stats.raw_matches (
    id TEXT PRIMARY KEY,
    "isResult" BOOLEAN,
    h JSONB NOT NULL,
    a JSONB NOT NULL,
    goals JSONB NOT NULL,
    "xG" JSONB NOT NULL,
    datetime TEXT NOT NULL,
    forecast JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on datetime for faster date-based queries
CREATE INDEX idx_raw_matches_datetime ON premier_league_stats.raw_matches(datetime);

-- Shots table
CREATE TABLE premier_league_stats.raw_shots (
    id TEXT PRIMARY KEY,
    minute TEXT,
    result TEXT,
    "X" TEXT,
    "Y" TEXT,
    "xG" TEXT,
    player TEXT,
    h_a TEXT,
    player_id TEXT,
    situation TEXT,
    season TEXT,
    "shotType" TEXT,
    match_id TEXT,
    h_team TEXT,
    a_team TEXT,
    h_goals TEXT,
    a_goals TEXT,
    date TEXT,
    player_assisted TEXT,
    "lastAction" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on shots table for common queries
CREATE INDEX idx_raw_shots_match_id ON premier_league_stats.raw_shots(match_id);
CREATE INDEX idx_raw_shots_player_id ON premier_league_stats.raw_shots(player_id);
CREATE INDEX idx_raw_shots_season ON premier_league_stats.raw_shots(season);
CREATE INDEX idx_raw_shots_date ON premier_league_stats.raw_shots(date);

-- Add comments to tables
COMMENT ON TABLE premier_league_stats.raw_teams IS 'Raw team data from Understat API';
COMMENT ON TABLE premier_league_stats.raw_players IS 'Raw player statistics from Understat API';
COMMENT ON TABLE premier_league_stats.raw_matches IS 'Raw match results from Understat API';
COMMENT ON TABLE premier_league_stats.raw_shots IS 'Raw shot-level data from Understat API';

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION premier_league_stats.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_raw_teams_updated_at BEFORE UPDATE ON premier_league_stats.raw_teams
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

CREATE TRIGGER update_raw_players_updated_at BEFORE UPDATE ON premier_league_stats.raw_players
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

CREATE TRIGGER update_raw_matches_updated_at BEFORE UPDATE ON premier_league_stats.raw_matches
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

CREATE TRIGGER update_raw_shots_updated_at BEFORE UPDATE ON premier_league_stats.raw_shots
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

-- Player Grouped Stats table (for grouped player statistics by season/position/etc)
CREATE TABLE premier_league_stats.raw_player_grouped (
    player_id TEXT NOT NULL,
    player_name TEXT NOT NULL,
    team TEXT,
    position TEXT,
    games TEXT,
    time TEXT,
    grouped_stats JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (player_id, team)
);

-- Create indexes on player_grouped table
CREATE INDEX idx_raw_player_grouped_player_name ON premier_league_stats.raw_player_grouped(player_name);
CREATE INDEX idx_raw_player_grouped_team ON premier_league_stats.raw_player_grouped(team);

CREATE TRIGGER update_raw_player_grouped_updated_at BEFORE UPDATE ON premier_league_stats.raw_player_grouped
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

COMMENT ON TABLE premier_league_stats.raw_player_grouped IS 'Grouped player statistics by season and other dimensions from Understat API';

-- Rosters table (for match rosters/lineups)
CREATE TABLE premier_league_stats.raw_rosters (
    match_id TEXT PRIMARY KEY,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    datetime TEXT NOT NULL,
    home_roster JSONB NOT NULL,
    away_roster JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on rosters table
CREATE INDEX idx_raw_rosters_home_team ON premier_league_stats.raw_rosters(home_team);
CREATE INDEX idx_raw_rosters_away_team ON premier_league_stats.raw_rosters(away_team);
CREATE INDEX idx_raw_rosters_datetime ON premier_league_stats.raw_rosters(datetime);

CREATE TRIGGER update_raw_rosters_updated_at BEFORE UPDATE ON premier_league_stats.raw_rosters
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

COMMENT ON TABLE premier_league_stats.raw_rosters IS 'Match rosters and player lineups from Understat API';

-- Team Context Stats table (for team statistics by situation/shotType/etc)
CREATE TABLE premier_league_stats.raw_team_context (
    team_name TEXT NOT NULL,
    season TEXT NOT NULL,
    context_stats JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (team_name, season)
);

-- Create index on team_context table
CREATE INDEX idx_raw_team_context_season ON premier_league_stats.raw_team_context(season);

CREATE TRIGGER update_raw_team_context_updated_at BEFORE UPDATE ON premier_league_stats.raw_team_context
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

COMMENT ON TABLE premier_league_stats.raw_team_context IS 'Team statistics grouped by context (situation, shot type, etc) from Understat API';

-- Grant permissions (adjust as needed for your Supabase setup)
-- ALTER TABLE premier_league_stats.raw_teams ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_players ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_player_grouped ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_matches ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_rosters ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_shots ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_team_context ENABLE ROW LEVEL SECURITY;
