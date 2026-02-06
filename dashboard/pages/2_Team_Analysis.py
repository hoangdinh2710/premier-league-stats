"""
Team Analysis - Deep dive into individual team performance.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.queries import get_teams_data, get_matches_data

st.set_page_config(page_title="Team Analysis", page_icon="📈", layout="wide")

st.title("📈 Team Analysis")
st.markdown("Analyze individual team performance, comparing actual goals with expected goals (xG).")

# Get league/season from session state (set in app.py sidebar)
league_name = st.session_state.get("league_name")
season = st.session_state.get("season")

# Load data
try:
    teams_df = get_teams_data(league_name=league_name, season=season)
    matches_df = get_matches_data(league_name=league_name, season=season)
    
    if teams_df.empty:
        st.warning("No team data available. Please run the extraction scripts first.")
        st.stop()
    
    # Team selector
    teams = sorted(teams_df['title'].unique())
    selected_team = st.selectbox("Select a team:", teams)
    
    # Get team data
    team_data = teams_df[teams_df['title'] == selected_team].iloc[0]
    
    # Display key metrics
    st.subheader(f"{selected_team} - Season Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Matches", int(team_data['matches']))
    
    with col2:
        st.metric("Points", int(team_data['pts']))
    
    with col3:
        if 'scored' in team_data.index:
            goals = int(team_data['scored'])
        else:
            goals = 0
        if 'xG' in team_data.index:
            xg = float(team_data['xG'])
        else:
            xg = 0.0
        delta_text = f"{goals - xg:.1f} vs xG" if xg > 0 else None
        st.metric("Goals", goals, delta=delta_text)
    
    with col4:
        xg_val = float(team_data['xG']) if 'xG' in team_data.index else 0.0
        st.metric("xG", f"{xg_val:.1f}")
    
    with col5:
        xga_val = float(team_data['xGA']) if 'xGA' in team_data.index else 0.0
        st.metric("xGA", f"{xga_val:.1f}")
    
    # Form: W-D-L
    st.markdown(f"**Form:** {int(team_data['wins'])}W - {int(team_data['draws'])}D - {int(team_data['loses'])}L")
    
    st.markdown("---")
    
    # Goals vs xG comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚽ Goals vs xG")
        
        # Create comparison bar chart
        scored_val = float(team_data['scored']) if 'scored' in team_data.index else 0.0
        xg_val = float(team_data['xG']) if 'xG' in team_data.index else 0.0
        missed_val = float(team_data['missed']) if 'missed' in team_data.index else 0.0
        xga_val = float(team_data['xGA']) if 'xGA' in team_data.index else 0.0
        
        comparison_data = pd.DataFrame({
            'Metric': ['Goals For', 'xG For', 'Goals Against', 'xG Against'],
            'Value': [scored_val, xg_val, missed_val, xga_val],
            'Type': ['Attacking', 'Attacking', 'Defensive', 'Defensive']
        })
        
        fig = px.bar(comparison_data, x='Metric', y='Value', color='Type',
                     color_discrete_map={'Attacking': '#00cc00', 'Defensive': '#cc0000'},
                     title=f"{selected_team} - Goals vs xG")
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Performance Indicators")
        
        # Calculate performance metrics
        scored_val = float(team_data['scored']) if 'scored' in team_data.index else 0.0
        xg_val = float(team_data['xG']) if 'xG' in team_data.index else 0.0
        missed_val = float(team_data['missed']) if 'missed' in team_data.index else 0.0
        xga_val = float(team_data['xGA']) if 'xGA' in team_data.index else 0.0
        
        goals_diff = scored_val - xg_val
        goals_against_diff = missed_val - xga_val
        
        # Display as metrics
        st.metric("Goal Difference vs xG", 
                  f"{goals_diff:+.1f}",
                  help="Positive = scoring more than expected")
        
        st.metric("Goals Conceded vs xGA", 
                  f"{goals_against_diff:+.1f}",
                  help="Negative = conceding less than expected")
        
        # Calculate efficiency
        if xg_val > 0:
            finishing_efficiency = (scored_val / xg_val) * 100
            st.metric("Finishing Efficiency", f"{finishing_efficiency:.1f}%",
                     help="Goals as % of xG (100% = as expected)")
        
        if xga_val > 0:
            defensive_efficiency = (missed_val / xga_val) * 100
            st.metric("Defensive Efficiency", f"{defensive_efficiency:.1f}%",
                     help="Goals conceded as % of xGA (lower is better)")
    
    # Match history (if available)
    if not matches_df.empty:
        st.markdown("---")
        st.subheader("📅 Recent Matches")
        
        # Filter matches for selected team
        team_matches = matches_df[
            (matches_df['home_team'] == selected_team) | 
            (matches_df['away_team'] == selected_team)
        ].copy()
        
        if not team_matches.empty:
            # Add slider to control number of matches shown
            max_matches = len(team_matches)
            num_matches = st.slider(
                "Number of matches to display:",
                min_value=5,
                max_value=min(max_matches, 38),  # Max 38 (full season)
                value=10,
                step=5
            )
            
            # Sort by date (most recent first)
            if 'datetime' in team_matches.columns:
                team_matches['datetime'] = pd.to_datetime(team_matches['datetime'], errors='coerce')
                team_matches = team_matches.sort_values('datetime', ascending=False, na_position='last')
            
            # Display selected number of matches
            recent_matches = team_matches.head(num_matches)
            
            match_display = []
            for idx, match in recent_matches.iterrows():
                home = match['home_team']
                away = match['away_team']
                
                # Extract goals and xG values directly (already converted to correct types)
                h_goals = int(match['home_goals']) if pd.notna(match['home_goals']) else 0
                a_goals = int(match['away_goals']) if pd.notna(match['away_goals']) else 0
                h_xg = float(match['home_xG']) if pd.notna(match['home_xG']) else 0.0
                a_xg = float(match['away_xG']) if pd.notna(match['away_xG']) else 0.0
                
                # Determine result for selected team
                if home == selected_team:
                    result = "W" if h_goals > a_goals else "D" if h_goals == a_goals else "L"
                else:
                    result = "W" if a_goals > h_goals else "D" if a_goals == h_goals else "L"
                
                match_display.append({
                    'Result': result,
                    'Match': f"{home} vs {away}",
                    'Score': f"{h_goals}-{a_goals}",
                    'xG': f"{h_xg:.1f}-{a_xg:.1f}"
                })
            
            if match_display:
                match_df = pd.DataFrame(match_display)
                
                # Color code results
                def color_result(val):
                    if val == 'W':
                        return 'background-color: rgba(0, 200, 0, 0.3)'
                    elif val == 'L':
                        return 'background-color: rgba(200, 0, 0, 0.3)'
                    return 'background-color: rgba(200, 200, 0, 0.3)'
                
                styled_matches = match_df.style.applymap(color_result, subset=['Result'])
                st.dataframe(styled_matches, use_container_width=True, hide_index=True)
            else:
                st.info("No match data to display.")
        else:
            st.info(f"No matches found for {selected_team}.")
    else:
        st.warning("No matches data available.")
    
    # Insights
    st.markdown("---")
    st.subheader("💡 Insights")
    
    # Generate insights based on data
    insights = []
    
    if goals_diff > 3:
        insights.append(f"🔥 **Clinical finishing**: {selected_team} is scoring {goals_diff:.1f} more goals than expected!")
    elif goals_diff < -3:
        insights.append(f"⚠️ **Wasteful in front of goal**: {selected_team} is scoring {abs(goals_diff):.1f} fewer goals than expected.")
    
    if goals_against_diff < -3:
        insights.append(f"🛡️ **Solid defense**: Conceding {abs(goals_against_diff):.1f} fewer goals than expected!")
    elif goals_against_diff > 3:
        insights.append(f"🚨 **Defensive issues**: Conceding {goals_against_diff:.1f} more goals than expected.")
    
    xg_val = float(team_data['xG']) if 'xG' in team_data.index else 0.0
    xga_val = float(team_data['xGA']) if 'xGA' in team_data.index else 0.0
    xg_diff = xg_val - xga_val
    if xg_diff > 10:
        insights.append(f"✨ **Dominant performance**: Creating far better chances than opponents (+{xg_diff:.1f} xG difference).")
    elif xg_diff < -10:
        insights.append(f"😰 **Struggling**: Opponents creating much better chances ({xg_diff:.1f} xG difference).")
    
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info(f"{selected_team} is performing close to expectations based on xG metrics.")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure you've run the extraction scripts first.")
