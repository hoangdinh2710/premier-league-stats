"""
Player Stats - Analyze player performance and efficiency.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.queries import get_players_data

st.set_page_config(page_title="Player Stats", page_icon="⚡", layout="wide")

st.title("⚡ Player Statistics")
st.markdown("Analyze player performance, identify clinical finishers and wasteful shooters.")

# Get league/season from session state (set in app.py sidebar)
league_name = st.session_state.get("league_name")
season = st.session_state.get("season")

# Load player data
try:
    players_df = get_players_data(league_name=league_name, season=season)
    
    if players_df.empty:
        st.warning("No player data available. Please run `python -m extract.extract_players` first.")
        st.stop()
    
    # Clean and prepare data
    players_df['goals'] = pd.to_numeric(players_df['goals'], errors='coerce')
    players_df['xG'] = pd.to_numeric(players_df['xG'], errors='coerce')
    players_df['assists'] = pd.to_numeric(players_df['assists'], errors='coerce')
    players_df['shots'] = pd.to_numeric(players_df['shots'], errors='coerce')
    players_df['games'] = pd.to_numeric(players_df['games'], errors='coerce')
    
    # Calculate additional metrics
    players_df['goals_xG_diff'] = players_df['goals'] - players_df['xG']
    players_df['conversion_rate'] = (players_df['goals'] / players_df['shots'] * 100).fillna(0)
    
    # Filter options
    min_games = st.slider("Minimum games played:", 1, 20, 5)
    filtered_players = players_df[players_df['games'] >= min_games].copy()
    
    st.markdown(f"**Showing {len(filtered_players)} players with {min_games}+ appearances**")
    
    # Top scorers table
    st.markdown("---")
    st.subheader("🏅 Top Scorers")
    
    top_scorers = filtered_players.nlargest(20, 'goals')[
        ['player_name', 'team_title', 'games', 'goals', 'xG', 'goals_xG_diff', 
         'shots', 'conversion_rate', 'assists']
    ].copy()
    
    top_scorers.columns = ['Player', 'Team', 'Games', 'Goals', 'xG', 'G-xG', 'Shots', 'Conv %', 'Assists']
    top_scorers['xG'] = top_scorers['xG'].round(1)
    top_scorers['G-xG'] = top_scorers['G-xG'].round(1)
    top_scorers['Conv %'] = top_scorers['Conv %'].round(1)
    
    # Style the table
    def highlight_performance(row):
        if row['G-xG'] > 2:
            return ['background-color: rgba(0, 200, 0, 0.2)'] * len(row)
        elif row['G-xG'] < -2:
            return ['background-color: rgba(200, 0, 0, 0.2)'] * len(row)
        return [''] * len(row)
    
    styled_scorers = top_scorers.style.apply(highlight_performance, axis=1)
    st.dataframe(styled_scorers, use_container_width=True, hide_index=True)
    
    st.caption("🟢 Green = Overperforming xG | 🔴 Red = Underperforming xG")
    
    # Goals vs xG scatter plot
    st.markdown("---")
    st.subheader("📊 Goals vs Expected Goals (xG)")
    
    # Filter for players with meaningful data
    scatter_data = filtered_players[
        (filtered_players['goals'] > 0) | (filtered_players['xG'] > 0)
    ].copy()
    
    fig = px.scatter(
        scatter_data,
        x='xG',
        y='goals',
        hover_name='player_name',
        hover_data={'team_title': True, 'games': True, 'xG': ':.2f', 'goals': True},
        labels={'xG': 'Expected Goals (xG)', 'goals': 'Actual Goals'},
        title='Player Efficiency: Goals vs xG'
    )
    
    # Add diagonal line (y = x) for "expected" performance
    max_val = max(scatter_data['xG'].max(), scatter_data['goals'].max())
    fig.add_shape(
        type="line",
        x0=0, y0=0,
        x1=max_val, y1=max_val,
        line=dict(color="gray", width=2, dash="dash"),
        name="Expected"
    )
    
    # Add annotation
    fig.add_annotation(
        x=max_val * 0.7,
        y=max_val * 0.8,
        text="Above line = Clinical finishers<br>Below line = Wasteful",
        showarrow=False,
        bgcolor="white",
        opacity=0.8
    )
    
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='white')))
    fig.update_layout(height=600)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top performers analysis
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Most Clinical Finishers")
        st.markdown("*Players scoring significantly more than their xG*")
        
        clinical = filtered_players[filtered_players['xG'] >= 2].nlargest(5, 'goals_xG_diff')[
            ['player_name', 'team_title', 'goals', 'xG', 'goals_xG_diff']
        ]
        
        for idx, player in clinical.iterrows():
            st.write(f"**{player['player_name']}** ({player['team_title']})")
            st.write(f"   {int(player['goals'])} goals from {player['xG']:.1f} xG (+{player['goals_xG_diff']:.1f})")
    
    with col2:
        st.subheader("😰 Most Wasteful Finishers")
        st.markdown("*Players scoring significantly less than their xG*")
        
        wasteful = filtered_players[filtered_players['xG'] >= 2].nsmallest(5, 'goals_xG_diff')[
            ['player_name', 'team_title', 'goals', 'xG', 'goals_xG_diff']
        ]
        
        for idx, player in wasteful.iterrows():
            st.write(f"**{player['player_name']}** ({player['team_title']})")
            st.write(f"   {int(player['goals'])} goals from {player['xG']:.1f} xG ({player['goals_xG_diff']:.1f})")
    
    # Additional stats
    st.markdown("---")
    st.subheader("🎯 Other Notable Stats")
    
    tab1, tab2, tab3 = st.tabs(["Top Assisters", "Best Conversion Rate", "Most Shots"])
    
    with tab1:
        top_assists = filtered_players.nlargest(10, 'assists')[
            ['player_name', 'team_title', 'assists', 'xA', 'games']
        ].copy()
        top_assists.columns = ['Player', 'Team', 'Assists', 'xA', 'Games']
        if 'xA' in top_assists.columns:
            top_assists['xA'] = pd.to_numeric(top_assists['xA'], errors='coerce').round(1)
        st.dataframe(top_assists, use_container_width=True, hide_index=True)
    
    with tab2:
        # Filter players with at least 10 shots
        conversion_data = filtered_players[filtered_players['shots'] >= 10].nlargest(10, 'conversion_rate')[
            ['player_name', 'team_title', 'goals', 'shots', 'conversion_rate']
        ].copy()
        conversion_data.columns = ['Player', 'Team', 'Goals', 'Shots', 'Conv %']
        conversion_data['Conv %'] = conversion_data['Conv %'].round(1)
        st.dataframe(conversion_data, use_container_width=True, hide_index=True)
        st.caption("*Minimum 10 shots")
    
    with tab3:
        top_shots = filtered_players.nlargest(10, 'shots')[
            ['player_name', 'team_title', 'shots', 'goals', 'xG']
        ].copy()
        top_shots.columns = ['Player', 'Team', 'Shots', 'Goals', 'xG']
        top_shots['xG'] = top_shots['xG'].round(1)
        st.dataframe(top_shots, use_container_width=True, hide_index=True)
    
    # Insights
    st.markdown("---")
    st.info("""
    **💡 Understanding the Metrics:**
    - **xG (Expected Goals)**: Statistical measure of shot quality. A shot with 0.5 xG should be scored 50% of the time.
    - **G-xG**: Difference between actual goals and xG. Positive = clinical finishing, Negative = wasteful.
    - **Conversion Rate**: Percentage of shots that result in goals.
    - **Clinical finishers** consistently score more than their xG suggests (through skill, composure, or luck).
    - **Wasteful finishers** are getting good chances but not converting them.
    """)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure you've run `python -m extract.extract_players` first.")
