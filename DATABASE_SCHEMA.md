# Database Schema Updates

## New Tables Added

### 1. raw_player_grouped
**Purpose**: Stores grouped player statistics by season and other dimensions

**Columns**:
- `player_id` (TEXT) - Player identifier
- `player_name` (TEXT) - Player name
- `team` (TEXT) - Team name
- `position` (TEXT) - Player position
- `games` (TEXT) - Number of games
- `time` (TEXT) - Minutes played
- `grouped_stats` (JSONB) - Statistics grouped by season/position/etc
- `created_at`, `updated_at` (TIMESTAMP)

**Primary Key**: `(player_id, team)`

**Source File**: `player_grouped_*.json`

---

### 2. raw_rosters
**Purpose**: Stores match rosters and player lineups

**Columns**:
- `match_id` (TEXT, PRIMARY KEY) - Match identifier
- `home_team` (TEXT) - Home team name
- `away_team` (TEXT) - Away team name
- `datetime` (TEXT) - Match datetime
- `home_roster` (JSONB) - Home team player roster details
- `away_roster` (JSONB) - Away team player roster details
- `created_at`, `updated_at` (TIMESTAMP)

**Source File**: `rosters_*.json`

---

### 3. raw_team_context
**Purpose**: Stores team statistics grouped by context (situation, shot type, etc)

**Columns**:
- `team_name` (TEXT) - Team name
- `season` (TEXT) - Season year
- `context_stats` (JSONB) - Statistics by situation, shot type, etc
- `created_at`, `updated_at` (TIMESTAMP)

**Primary Key**: `(team_name, season)`

**Source File**: `team_context_*.json`

---

## Complete Table List

After running `schema.sql`, you will have these 7 tables:

1. **raw_teams** - Team data with match history
2. **raw_players** - Individual player season statistics
3. **raw_player_grouped** - ✨ NEW - Grouped player stats by dimension
4. **raw_matches** - Match results and xG data
5. **raw_rosters** - ✨ NEW - Match lineups and rosters
6. **raw_shots** - Individual shot data
7. **raw_team_context** - ✨ NEW - Team stats by context

---

## Loading the Data

The `load_to_supabase.py` script has been updated to automatically load all 7 data types:

```bash
python load/load_to_supabase.py
```

It will automatically find and load the most recent version of each file in `data/raw/`:
- `teams_*.json`
- `players_*.json`
- `player_grouped_*.json` ✨ NEW
- `matches_*.json`
- `rosters_*.json` ✨ NEW
- `shots_*.json`
- `team_context_*.json` ✨ NEW

---

## Setup Instructions

1. **Create the tables in Supabase**:
   - Go to your Supabase project
   - Open the SQL Editor
   - Copy and paste the entire contents of `schema.sql`
   - Click "Run"

2. **Load the data**:
   ```bash
   python load/load_to_supabase.py
   ```

3. **Verify the data**:
   - Check the Table Editor in Supabase to see your data
   - Each table should show row counts

---

## Changes Made

### schema.sql
- ✅ Added `raw_player_grouped` table definition
- ✅ Added `raw_rosters` table definition
- ✅ Added `raw_team_context` table definition
- ✅ Added indexes for performance
- ✅ Added triggers for automatic `updated_at` timestamps
- ✅ Added table comments for documentation

### load/load_to_supabase.py
- ✅ Added `load_player_grouped()` function
- ✅ Added `load_rosters()` function
- ✅ Added `load_team_context()` function
- ✅ Updated `load_all()` to include new data types
- ✅ Removed unicode characters that caused Windows console errors
- ✅ All functions use proper upsert logic (ON CONFLICT DO UPDATE)
