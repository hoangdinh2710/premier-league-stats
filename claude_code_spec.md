# Premier League xG Analytics Dashboard - Project Spec

## Overview

Build an end-to-end data engineering portfolio project that extracts football (soccer) xG data from Understat, stores it in a database, transforms it with dbt, and displays it in a Streamlit dashboard.

---

## Tech Stack

- **Python 3.11+**
- **understatapi** - for extracting data from Understat
- **Supabase** (PostgreSQL) - for data storage
- **dbt** - for data transformations
- **Streamlit** - for the dashboard
- **Plotly** - for visualizations
- **GitHub Actions** - for scheduling (set up later)

---

## Project Structure

Create this folder structure:

```
premier-league-xg-tracker/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── extract/
│   ├── __init__.py
│   ├── extract_league.py      # League-level team stats
│   ├── extract_players.py     # Player stats with xG
│   ├── extract_matches.py     # Match results with xG
│   └── extract_shots.py       # Individual shot data with coordinates
│
├── load/
│   ├── __init__.py
│   └── load_to_supabase.py    # Push data to Supabase
│
├── transform/
│   └── (dbt project - set up later)
│
├── dashboard/
│   ├── app.py                 # Main Streamlit app
│   ├── pages/
│   │   ├── 1_🏆_League_Table.py
│   │   ├── 2_📈_Team_Analysis.py
│   │   ├── 3_🎯_Shot_Maps.py
│   │   ├── 4_⚡_Player_Stats.py
│   │   └── 5_🔮_Match_Analysis.py
│   └── utils/
│       ├── __init__.py
│       ├── queries.py         # SQL queries for dashboard
│       └── charts.py          # Reusable chart components
│
└── data/
    └── raw/                   # Local JSON cache (gitignored)
```

---

## Step 1: Create requirements.txt

```
understatapi>=0.6.0
pandas>=2.0.0
streamlit>=1.28.0
plotly>=5.18.0
supabase>=2.0.0
python-dotenv>=1.0.0
```

---

## Step 2: Extraction Scripts

### extract/extract_league.py

Use `understatapi` to get team-level stats for the Premier League (EPL) for the current season (2024).

```python
from understatapi import UnderstatClient

# Get team data for EPL 2024 season
# understat.league(league="EPL").get_team_data(season="2024")
```

Data should include: team name, matches played, wins, draws, losses, goals, xG, xGA, points, etc.

Save output as JSON to `data/raw/teams_{date}.json`


### extract/extract_players.py

Get player stats for all EPL players in the current season.

```python
# understat.league(league="EPL").get_player_data(season="2024")
```

Data should include: player_id, player_name, team, games, goals, xG, assists, xA, shots, key_passes, npg (non-penalty goals), npxG

Save output as JSON to `data/raw/players_{date}.json`


### extract/extract_matches.py

Get all match results for the EPL current season.

```python
# understat.league(league="EPL").get_match_data(season="2024")
```

Data should include: match_id, home_team, away_team, home_goals, away_goals, home_xG, away_xG, datetime, result

Save output as JSON to `data/raw/matches_{date}.json`


### extract/extract_shots.py

Get shot-level data for the season. This requires getting shots for each match.

```python
# For each match_id:
# understat.match(match=match_id).get_shot_data()
```

Data should include: shot_id, match_id, minute, player, player_id, team, x, y, xG, result (Goal, SavedShot, MissedShots, BlockedShot), situation (OpenPlay, FromCorner, SetPiece, DirectFreekick, Penalty), shotType (RightFoot, LeftFoot, Head)

Save output as JSON to `data/raw/shots_{date}.json`

**Important:** Add delays between requests to avoid rate limiting. Use `time.sleep(1)` between match requests.

---

## Step 3: Load Script

### load/load_to_supabase.py

Read the JSON files and insert/upsert into Supabase tables.

Tables needed:
- `raw_teams`
- `raw_players`
- `raw_matches`
- `raw_shots`

Use environment variables for Supabase credentials:
- `SUPABASE_URL`
- `SUPABASE_KEY`

---

## Step 4: Streamlit Dashboard

### dashboard/app.py

Main landing page with:
- Project title: "Premier League xG Analytics"
- Brief description
- Key metrics summary (total matches, total goals, total xG)
- Navigation hint to other pages

### dashboard/pages/1_🏆_League_Table.py

Two tables side by side:
1. **Actual Table** - sorted by points (standard league table)
2. **xG Table** - sorted by xG difference (xG - xGA)

Highlight teams that are:
- Overperforming (actual position > xG position) in green
- Underperforming (actual position < xG position) in red

### dashboard/pages/2_📈_Team_Analysis.py

- Dropdown to select a team
- Line chart: xG vs Actual Goals over time (cumulative)
- Bar chart: xG For vs xG Against
- Metric cards: Total xG, Total Goals, Difference

### dashboard/pages/3_🎯_Shot_Maps.py

- Dropdown to select team (or "All")
- Pitch visualization showing shot locations
- X, Y coordinates from Understat are 0-1 scaled (0,0 is bottom-left, 1,1 is top-right of attacking half)
- Color shots by xG value (low=blue, high=red)
- Different markers for: Goal (star), Saved (circle), Missed (x), Blocked (square)
- Filter options: Goals only, On target, By player

Use Plotly to draw a half-pitch and scatter the shots.

### dashboard/pages/4_⚡_Player_Stats.py

- Table of top 20 players by goals
- Columns: Player, Team, Goals, xG, Goals-xG, Shots, Conversion Rate
- Scatter plot: xG (x-axis) vs Goals (y-axis)
  - Diagonal line showing "expected" (where goals = xG)
  - Players above line = clinical finishers
  - Players below line = wasteful

### dashboard/pages/5_🔮_Match_Analysis.py

- Dropdown to select a match
- Show: Home Team vs Away Team, Score, xG for each
- Shot map for the match (both teams on one pitch, different colors)
- "Verdict" text: Did the right team win based on xG?

---

## Data Notes

### Understat Season Format
- Understat uses the starting year for seasons
- 2024/25 season = "2024"
- 2023/24 season = "2023"

### Shot Coordinates
- X: 0 to 1 (0 = own goal line, 1 = opponent goal line)
- Y: 0 to 1 (0 = left touchline, 1 = right touchline)
- For shot maps, we only care about the attacking half, so X is typically 0.5 to 1

### League Code
- Premier League = "EPL"
- Other options: "La_Liga", "Bundesliga", "Serie_A", "Ligue_1"

---

## Example Code Snippets

### Using understatapi

```python
from understatapi import UnderstatClient
import json

with UnderstatClient() as understat:
    # Get team data
    teams = understat.league(league="EPL").get_team_data(season="2024")
    
    # Get player data
    players = understat.league(league="EPL").get_player_data(season="2024")
    
    # Get match data
    matches = understat.league(league="EPL").get_match_data(season="2024")
    
    # Get shots for a specific match
    shots = understat.match(match="12345").get_shot_data()
```

### Pitch Drawing with Plotly

```python
import plotly.graph_objects as go

def draw_half_pitch():
    fig = go.Figure()
    
    # Pitch outline (half pitch)
    fig.add_shape(type="rect", x0=0.5, y0=0, x1=1, y1=1,
                  line=dict(color="white", width=2))
    
    # Penalty area
    fig.add_shape(type="rect", x0=0.83, y0=0.21, x1=1, y1=0.79,
                  line=dict(color="white", width=2))
    
    # 6-yard box
    fig.add_shape(type="rect", x0=0.94, y0=0.37, x1=1, y1=0.63,
                  line=dict(color="white", width=2))
    
    # Goal
    fig.add_shape(type="rect", x0=1, y0=0.44, x1=1.02, y1=0.56,
                  line=dict(color="white", width=2))
    
    fig.update_layout(
        plot_bgcolor="green",
        xaxis=dict(range=[0.5, 1.05], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, showticklabels=False),
        height=500,
        width=600
    )
    
    return fig
```

---

## What to Build First

1. **requirements.txt** and **.gitignore**
2. **extract/extract_league.py** - simplest extraction
3. **extract/extract_players.py** - player stats
4. **extract/extract_matches.py** - match data
5. **dashboard/app.py** - basic Streamlit app
6. **dashboard/pages/1_🏆_League_Table.py** - first visualization

Test locally with JSON files before setting up Supabase. You can use `pandas` to read JSON and display in Streamlit without a database initially.

---

## Commands to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run extraction
python -m extract.extract_league
python -m extract.extract_players
python -m extract.extract_matches

# Run dashboard
streamlit run dashboard/app.py
```

---

## Success Criteria

The project is complete when:
- [ ] Data extracts successfully from Understat
- [ ] Dashboard shows league table with actual vs xG standings
- [ ] Shot maps display correctly with pitch visualization
- [ ] Player efficiency scatter plot works
- [ ] Code is clean, documented, and on GitHub
- [ ] README explains the project clearly
