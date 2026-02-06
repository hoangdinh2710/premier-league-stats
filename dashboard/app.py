"""
Football xG Analytics Dashboard

A comprehensive dashboard for analyzing football performance using 
Expected Goals (xG) metrics from Understat.
Supports multiple leagues and seasons.
"""
import streamlit as st
from utils.queries import (
    get_teams_data,
    get_players_data,
    get_matches_data,
    get_available_leagues_and_seasons,
)

# Page configuration
st.set_page_config(
    page_title="Football xG Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Sidebar: League & Season selectors ----
available_leagues, available_seasons = get_available_leagues_and_seasons()

# League display names mapping
LEAGUE_DISPLAY = {
    "EPL": "Premier League",
    "La_Liga": "La Liga",
    "Bundesliga": "Bundesliga",
    "Serie_A": "Serie A",
    "Ligue_1": "Ligue 1",
    "RFPL": "Russian Premier League",
}

with st.sidebar:
    st.header("Filters")

    selected_league = st.selectbox(
        "League",
        options=available_leagues,
        format_func=lambda x: LEAGUE_DISPLAY.get(x, x),
        index=0,
    )

    selected_season = st.selectbox(
        "Season",
        options=available_seasons,
        format_func=lambda s: f"{s}/{int(s)+1}" if s.isdigit() else s,
        index=0,
    )

# Store in session state so pages can access them
st.session_state["league_name"] = selected_league
st.session_state["season"] = selected_season

league_display = LEAGUE_DISPLAY.get(selected_league, selected_league)
season_display = f"{selected_season}/{int(selected_season)+1}" if selected_season.isdigit() else selected_season

# Main header
st.markdown(f'<div class="main-header">⚽ {league_display} xG Analytics</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Expected Goals Analysis for the {season_display} Season</div>', unsafe_allow_html=True)

# Introduction
st.markdown(f"""
---

### Welcome to the Football xG Analytics Dashboard! 🎯

This dashboard provides comprehensive analysis of **{league_display}** performance using **Expected Goals (xG)** 
metrics from Understat. xG is a statistical measure that quantifies the quality of goal-scoring chances, 
helping us understand which teams and players are performing above or below expectations.

#### What you'll find here:

- 🏆 **League Table**: Compare actual standings with xG-based projections
- 📈 **Team Analysis**: Dive deep into individual team performance
- 🎯 **Shot Maps**: Visualize shot locations and quality on the pitch
- ⚡ **Player Stats**: Identify clinical finishers and wasteful shooters
- 🔮 **Match Analysis**: Review individual matches and their xG narratives

Navigate using the sidebar to explore different pages! ⬅️

---
""")

# Load data for summary metrics
try:
    teams_df = get_teams_data(league_name=selected_league, season=selected_season)
    players_df = get_players_data(league_name=selected_league, season=selected_season)
    matches_df = get_matches_data(league_name=selected_league, season=selected_season)
    
    # Display key metrics
    st.subheader("📊 Season Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_matches = len(matches_df) if not matches_df.empty else 0
        st.metric("Total Matches", total_matches)
    
    with col2:
        if not teams_df.empty and 'scored' in teams_df.columns:
            total_goals = int(teams_df['scored'].sum())
        else:
            total_goals = 0
        st.metric("Total Goals", total_goals)
    
    with col3:
        if not teams_df.empty and 'xG' in teams_df.columns:
            total_xg = round(teams_df['xG'].sum(), 1)
        else:
            total_xg = 0
        st.metric("Total xG", total_xg)
    
    with col4:
        total_players = len(players_df) if not players_df.empty else 0
        st.metric("Total Players", total_players)
    
    # Data freshness indicator
    if not teams_df.empty:
        st.success("✅ Data loaded successfully!")
    else:
        st.warning("⚠️ No data found. Please run the extraction scripts first.")
        st.info("""
        **To get started:**
        1. Run `python orchestrate.py --league EPL --season 2025`
        2. Or run individual extract scripts with `--league` and `--season` flags
        3. Refresh this page
        """)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("""
    **Troubleshooting:**
    - Make sure you've run the extraction scripts
    - Check that the `data/raw/` directory exists and contains JSON files
    - See the README for detailed instructions
    """)

# Footer
st.markdown("""
---

<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>Data source: <a href="https://understat.com" target="_blank">Understat</a> | 
    Built with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)
