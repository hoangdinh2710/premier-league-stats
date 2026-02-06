-- Football Stats Database Schema
-- Tables for storing raw data from Understat API
-- Supports multiple leagues and seasons

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS premier_league_stats;

-- Set search path to use the schema
SET search_path TO premier_league_stats, public;

-- Drop tables if they exist (be careful with this in production)
DROP TABLE IF EXISTS premier_league_stats.raw_shots CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_matches CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_players CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_rosters CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_team_context CASCADE;
DROP TABLE IF EXISTS premier_league_stats.raw_teams CASCADE;

-- Teams table
CREATE TABLE premier_league_stats.raw_teams (
    id TEXT NOT NULL,
    title TEXT NOT NULL,
    history JSONB NOT NULL,
    league_name TEXT NOT NULL,
    season TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id, league_name, season)
);

-- Create indexes on team table
CREATE INDEX idx_raw_teams_title ON premier_league_stats.raw_teams(title);
CREATE INDEX idx_raw_teams_league_season ON premier_league_stats.raw_teams(league_name, season);

-- Players table
CREATE TABLE premier_league_stats.raw_players (
    id TEXT NOT NULL,
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
    league_name TEXT NOT NULL,
    season TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id, league_name, season)
);

-- Create indexes on player table
CREATE INDEX idx_raw_players_name ON premier_league_stats.raw_players(player_name);
CREATE INDEX idx_raw_players_team ON premier_league_stats.raw_players(team_title);
CREATE INDEX idx_raw_players_league_season ON premier_league_stats.raw_players(league_name, season);

-- Matches table
CREATE TABLE premier_league_stats.raw_matches (
    id TEXT NOT NULL,
    "isResult" BOOLEAN,
    h JSONB NOT NULL,
    a JSONB NOT NULL,
    goals JSONB NOT NULL,
    "xG" JSONB NOT NULL,
    datetime TEXT NOT NULL,
    forecast JSONB,
    league_name TEXT NOT NULL,
    season TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id, league_name, season)
);

-- Create indexes on matches table
CREATE INDEX idx_raw_matches_datetime ON premier_league_stats.raw_matches(datetime);
CREATE INDEX idx_raw_matches_league_season ON premier_league_stats.raw_matches(league_name, season);

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
    league_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes on shots table for common queries
CREATE INDEX idx_raw_shots_match_id ON premier_league_stats.raw_shots(match_id);
CREATE INDEX idx_raw_shots_player_id ON premier_league_stats.raw_shots(player_id);
CREATE INDEX idx_raw_shots_season ON premier_league_stats.raw_shots(season);
CREATE INDEX idx_raw_shots_date ON premier_league_stats.raw_shots(date);
CREATE INDEX idx_raw_shots_league_name ON premier_league_stats.raw_shots(league_name);
CREATE INDEX idx_raw_shots_league_season ON premier_league_stats.raw_shots(league_name, season);

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

-- Rosters table (for match rosters/lineups)
CREATE TABLE premier_league_stats.raw_rosters (
    match_id TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    datetime TEXT NOT NULL,
    home_roster JSONB NOT NULL,
    away_roster JSONB NOT NULL,
    league_name TEXT NOT NULL,
    season TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (match_id, league_name, season)
);

-- Create indexes on rosters table
CREATE INDEX idx_raw_rosters_home_team ON premier_league_stats.raw_rosters(home_team);
CREATE INDEX idx_raw_rosters_away_team ON premier_league_stats.raw_rosters(away_team);
CREATE INDEX idx_raw_rosters_datetime ON premier_league_stats.raw_rosters(datetime);
CREATE INDEX idx_raw_rosters_league_season ON premier_league_stats.raw_rosters(league_name, season);

CREATE TRIGGER update_raw_rosters_updated_at BEFORE UPDATE ON premier_league_stats.raw_rosters
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

COMMENT ON TABLE premier_league_stats.raw_rosters IS 'Match rosters and player lineups from Understat API';

-- Team Context Stats table (for team statistics by situation/shotType/etc)
CREATE TABLE premier_league_stats.raw_team_context (
    team_name TEXT NOT NULL,
    season TEXT NOT NULL,
    league_name TEXT NOT NULL,
    context_stats JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (team_name, season, league_name)
);

-- Create indexes on team_context table
CREATE INDEX idx_raw_team_context_season ON premier_league_stats.raw_team_context(season);
CREATE INDEX idx_raw_team_context_league_name ON premier_league_stats.raw_team_context(league_name);

CREATE TRIGGER update_raw_team_context_updated_at BEFORE UPDATE ON premier_league_stats.raw_team_context
    FOR EACH ROW EXECUTE FUNCTION premier_league_stats.update_updated_at_column();

COMMENT ON TABLE premier_league_stats.raw_team_context IS 'Team statistics grouped by context (situation, shot type, etc) from Understat API';

-- Grant permissions (adjust as needed for your Supabase setup)
-- ALTER TABLE premier_league_stats.raw_teams ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_players ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_matches ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_rosters ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_shots ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE premier_league_stats.raw_team_context ENABLE ROW LEVEL SECURITY;
