# Quick Reference: Loading Data to Supabase

## One-Time Setup

### Step 1: Create Database Tables
1. Go to your Supabase project dashboard
2. Click **SQL Editor** in the left sidebar
3. Open `schema.sql` from this project
4. Copy the entire contents
5. Paste into the SQL Editor
6. Click **RUN** to create all 7 tables

### Step 2: Verify Tables Created
Go to **Table Editor** and you should see:
- raw_teams
- raw_players
- raw_player_grouped
- raw_matches
- raw_rosters
- raw_shots
- raw_team_context

## Loading Data

### Load Everything (Recommended)
```bash
python load/load_to_supabase.py
```

This automatically loads all 7 data types from the most recent files in `data/raw/`.

### Expected Output
```
============================================================
Loading data to Supabase (Direct Postgres Connection)
============================================================
Loading team data from data\raw\teams_20260127.json...
Success: Loaded 20 teams to raw_teams table
Loading player data from data\raw\players_20260127.json...
Success: Loaded 643 players to raw_players table
Loading grouped player data from data\raw\player_grouped_20260127.json...
Success: Loaded 643 grouped player records to raw_player_grouped table
Loading match data from data\raw\matches_20260127.json...
Success: Loaded 230 matches to raw_matches table
Loading roster data from data\raw\rosters_20260127.json...
Success: Loaded 230 rosters to raw_rosters table
Loading shot data from data\raw\shots_20260127.json...
  - Loaded batch 1 (2000 shots)
  - Loaded batch 2 (2000 shots)
  ...
Success: Loaded 30000 shots to raw_shots table
Loading team context data from data\raw\team_context_20260127.json...
Success: Loaded 20 team context records to raw_team_context table
============================================================
Success: Data loading complete!
============================================================
```

## Troubleshooting

### Error: "relation 'raw_teams' does not exist"
**Solution**: You haven't created the tables yet. Run `schema.sql` in Supabase SQL Editor.

### Error: "No module named 'psycopg2'"
**Solution**: Install the dependency:
```bash
pip install psycopg2-binary
```

### Error: "DATABASE_URL not set"
**Solution**: Create/edit `.env` file with your Supabase credentials:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```
Get this from: Supabase Dashboard → Project Settings → Database → Connection String (Direct)

### Error: "UnicodeDecodeError"
**Solution**: Your `.env` file has wrong encoding. Delete it and recreate with UTF-8 encoding.

### Warning: "No [type] data files found"
**Solution**: Run the extract scripts first:
```bash
python -m extract.extract_league
python -m extract.extract_players
python -m extract.extract_player_grouped
python -m extract.extract_matches
python -m extract.extract_rosters
python -m extract.extract_shots
python -m extract.extract_team_context
```

## Data Update Workflow

When you want to refresh your data:

1. **Extract new data** (run all extract scripts)
2. **Load to Supabase** (run load script)
3. **Verify in Supabase** (check Table Editor)

The loader uses UPSERT logic, so it will:
- **Update** existing records if they already exist
- **Insert** new records that don't exist yet

## Quick Commands

```bash
# Full refresh
python -m extract.extract_league && \
python -m extract.extract_players && \
python -m extract.extract_player_grouped && \
python -m extract.extract_matches && \
python -m extract.extract_rosters && \
python -m extract.extract_shots && \
python -m extract.extract_team_context && \
python load/load_to_supabase.py

# Just load (if data already extracted)
python load/load_to_supabase.py

# Test connection
python -c "from load.load_to_supabase import get_connection; conn = get_connection(); print('Connected successfully'); conn.close()"
```

## File Mapping

| Data File | Database Table |
|-----------|----------------|
| teams_*.json | raw_teams |
| players_*.json | raw_players |
| player_grouped_*.json | raw_player_grouped |
| matches_*.json | raw_matches |
| rosters_*.json | raw_rosters |
| shots_*.json | raw_shots |
| team_context_*.json | raw_team_context |

## Need Help?

See `DATABASE_SCHEMA.md` for detailed table documentation.
