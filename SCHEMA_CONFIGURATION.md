# Schema Configuration

## Using DB_SCHEMA Environment Variable

The project now supports using a custom PostgreSQL schema instead of the default `public` schema.

### Your .env Configuration

Your `.env` file includes:
```
DB_SCHEMA=premier_league_stats
```

This means all tables will be created and accessed in the `premier_league_stats` schema instead of `public`.

### What This Means

**Schema.sql:**
- Creates the `premier_league_stats` schema if it doesn't exist
- Sets the search path to use this schema
- All tables, indexes, triggers, and functions are created in `premier_league_stats` schema

**Load Script:**
- Automatically uses the `DB_SCHEMA` from your `.env` file
- Sets the PostgreSQL search_path when connecting
- All INSERT/UPDATE queries will target the correct schema

### Benefits

1. **Organization**: Keeps your tables separate from other projects/data
2. **Security**: Can grant different permissions per schema
3. **Clean namespace**: Avoids conflicts with default `public` schema tables

### How It Works

When you connect to the database, the loader automatically runs:
```sql
SET search_path TO premier_league_stats, public;
```

This means:
- First, PostgreSQL looks for tables in `premier_league_stats` schema
- If not found, it falls back to `public` schema
- You can reference tables as `raw_teams` instead of `premier_league_stats.raw_teams`

### If You Want to Use Public Schema

Simply remove or comment out the `DB_SCHEMA` line from your `.env`:
```
# DB_SCHEMA=premier_league_stats
```

The script will default to the `public` schema.

### Verifying Schema Usage

After running `schema.sql`, you can verify the schema was created:

```sql
-- List all schemas
SELECT schema_name FROM information_schema.schemata;

-- List tables in premier_league_stats schema
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'premier_league_stats';

-- Should return:
-- raw_teams
-- raw_players
-- raw_player_grouped
-- raw_matches
-- raw_rosters
-- raw_shots
-- raw_team_context
```

### Querying Data

When querying from Supabase or psql, you can use either:

**With search_path set:**
```sql
SELECT * FROM raw_teams;
```

**Fully qualified (always works):**
```sql
SELECT * FROM premier_league_stats.raw_teams;
```
