"""
Match Analysis - Review individual matches and their xG narratives.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.queries import get_matches_data, get_shots_data
from utils.charts import draw_half_pitch

st.set_page_config(page_title="Match Analysis", page_icon="🔮", layout="wide")

st.title("🔮 Match Analysis")
st.markdown("Analyze individual matches and compare actual results with xG expectations.")

# Get league/season from session state (set in app.py sidebar)
league_name = st.session_state.get("league_name")
season = st.session_state.get("season")

# Load data
try:
    matches_df = get_matches_data(league_name=league_name, season=season)
    shots_df = get_shots_data(league_name=league_name, season=season)
    
    if matches_df.empty:
        st.warning("No match data available. Please run `python -m extract.extract_matches` first.")
        st.stop()
    
    # Sort matches by date (most recent first)
    if 'datetime' in matches_df.columns:
        matches_df['datetime'] = pd.to_datetime(matches_df['datetime'])
        matches_df = matches_df.sort_values('datetime', ascending=False)
    
    # Create match selector
    matches_df['match_label'] = (
        matches_df['home_team'] + " " + 
        matches_df['home_goals'].astype(str) + "-" + 
        matches_df['away_goals'].astype(str) + " " + 
        matches_df['away_team']
    )
    
    if 'datetime' in matches_df.columns:
        matches_df['match_label'] = (
            matches_df['datetime'].dt.strftime('%Y-%m-%d') + " | " + 
            matches_df['match_label']
        )
    
    match_options = matches_df['match_label'].tolist()
    selected_match_label = st.selectbox("Select a match:", match_options)
    
    # Get selected match data
    selected_match = matches_df[matches_df['match_label'] == selected_match_label].iloc[0]
    
    home_team = selected_match['home_team']
    away_team = selected_match['away_team']
    home_goals = int(selected_match['home_goals']) if pd.notna(selected_match['home_goals']) else 0
    away_goals = int(selected_match['away_goals']) if pd.notna(selected_match['away_goals']) else 0
    home_xg = float(selected_match['home_xG']) if pd.notna(selected_match['home_xG']) else 0
    away_xg = float(selected_match['away_xG']) if pd.notna(selected_match['away_xG']) else 0
    match_id = selected_match.get('id', None)
    
    # Display match header
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(f"### {home_team}")
        st.markdown(f"<h1 style='text-align: right;'>{home_goals}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: right; color: #666;'>xG: {home_xg:.2f}</p>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>vs</h2>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"### {away_team}")
        st.markdown(f"<h1 style='text-align: left;'>{away_goals}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: left; color: #666;'>xG: {away_xg:.2f}</p>", unsafe_allow_html=True)
    
    # Match verdict
    st.markdown("---")
    st.subheader("🔍 Match Verdict")
    
    # Determine actual result
    if home_goals > away_goals:
        actual_result = f"{home_team} win"
        actual_winner = home_team
    elif away_goals > home_goals:
        actual_result = f"{away_team} win"
        actual_winner = away_team
    else:
        actual_result = "Draw"
        actual_winner = None
    
    # Determine xG result
    xg_diff = abs(home_xg - away_xg)
    if home_xg > away_xg:
        xg_result = f"{home_team} deserved to win"
        xg_winner = home_team
    elif away_xg > home_xg:
        xg_result = f"{away_team} deserved to win"
        xg_winner = away_team
    else:
        xg_result = "Draw was fair"
        xg_winner = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Actual Result", actual_result)
    
    with col2:
        st.metric("Based on xG", xg_result)
    
    # Analysis
    if actual_winner == xg_winner:
        st.success(f"✅ **Fair Result**: {actual_winner} won and deserved to win based on chances created.")
    elif actual_winner and xg_winner and actual_winner != xg_winner:
        st.warning(f"⚠️ **Upset Alert**: {actual_winner} won, but {xg_winner} created better chances!")
    elif actual_result == "Draw" and xg_winner:
        st.info(f"📊 **Draw, but...**: {xg_winner} probably should have won based on xG.")
    elif actual_winner and not xg_winner:
        st.info(f"📊 **Close match**: {actual_winner} won a tight game where chances were even.")
    else:
        st.success("✅ **Even match**: A fair draw with equal chances.")
    
    # xG comparison chart
    st.markdown("---")
    st.subheader("📊 xG Comparison")
    
    comparison_data = pd.DataFrame({
        'Team': [home_team, home_team, away_team, away_team],
        'Metric': ['Goals', 'xG', 'Goals', 'xG'],
        'Value': [home_goals, home_xg, away_goals, away_xg]
    })
    
    import plotly.express as px
    fig = px.bar(comparison_data, x='Team', y='Value', color='Metric',
                 barmode='group',
                 color_discrete_map={'Goals': '#1f77b4', 'xG': '#ff7f0e'},
                 title='Goals vs xG Comparison')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Shot map for the match
    if not shots_df.empty and match_id:
        st.markdown("---")
        st.subheader("🎯 Shot Map")
        
        # Filter shots for this match
        match_shots = shots_df[shots_df['match_id'] == match_id]
        
        if not match_shots.empty:
            fig = draw_half_pitch()
            
            # Define colors for teams
            team_colors = {home_team: '#FF4444', away_team: '#4444FF'}
            
            # Add shots for each team
            for team in [home_team, away_team]:
                team_shots = match_shots[
                    (match_shots['h_team'] == team) if 'h_team' in match_shots.columns 
                    else match_shots['team'] == team
                ]
                
                if not team_shots.empty:
                    # Separate goals and non-goals
                    goals = team_shots[team_shots['result'] == 'Goal']
                    non_goals = team_shots[team_shots['result'] != 'Goal']
                    
                    # Add non-goals
                    if not non_goals.empty:
                        hover_text = []
                        for idx, shot in non_goals.iterrows():
                            player = shot.get('player', 'Unknown')
                            xg = shot.get('xG', 0)
                            result = shot.get('result', 'Unknown')
                            minute = shot.get('minute', '?')
                            
                            hover_text.append(
                                f"{team}<br>"
                                f"Player: {player}<br>"
                                f"xG: {xg:.3f}<br>"
                                f"Result: {result}<br>"
                                f"Minute: {minute}"
                            )
                        
                        fig.add_trace(go.Scatter(
                            x=non_goals['X'],
                            y=non_goals['Y'],
                            mode='markers',
                            name=f"{team} (shots)",
                            marker=dict(
                                size=non_goals['xG'] * 30 + 5,
                                color=team_colors[team],
                                symbol='circle',
                                opacity=0.6,
                                line=dict(color='white', width=1)
                            ),
                            text=hover_text,
                            hovertemplate='%{text}<extra></extra>'
                        ))
                    
                    # Add goals
                    if not goals.empty:
                        hover_text_goals = []
                        for idx, shot in goals.iterrows():
                            player = shot.get('player', 'Unknown')
                            xg = shot.get('xG', 0)
                            minute = shot.get('minute', '?')
                            
                            hover_text_goals.append(
                                f"{team}<br>"
                                f"⚽ GOAL!<br>"
                                f"Player: {player}<br>"
                                f"xG: {xg:.3f}<br>"
                                f"Minute: {minute}"
                            )
                        
                        fig.add_trace(go.Scatter(
                            x=goals['X'],
                            y=goals['Y'],
                            mode='markers',
                            name=f"{team} (goals)",
                            marker=dict(
                                size=goals['xG'] * 30 + 15,
                                color=team_colors[team],
                                symbol='star',
                                line=dict(color='gold', width=2)
                            ),
                            text=hover_text_goals,
                            hovertemplate='%{text}<extra></extra>'
                        ))
            
            fig.update_layout(
                title=f"Shot Map: {home_team} vs {away_team}",
                height=700,
                showlegend=True,
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Shot statistics
            col1, col2 = st.columns(2)
            
            with col1:
                home_shots = match_shots[
                    (match_shots['h_team'] == home_team) if 'h_team' in match_shots.columns
                    else match_shots['team'] == home_team
                ]
                st.markdown(f"**{home_team}**")
                st.write(f"Shots: {len(home_shots)}")
                st.write(f"Goals: {home_goals}")
                st.write(f"xG: {home_xg:.2f}")
            
            with col2:
                away_shots = match_shots[
                    (match_shots['h_team'] == away_team) if 'h_team' in match_shots.columns
                    else match_shots['team'] == away_team
                ]
                st.markdown(f"**{away_team}**")
                st.write(f"Shots: {len(away_shots)}")
                st.write(f"Goals: {away_goals}")
                st.write(f"xG: {away_xg:.2f}")
        
        else:
            st.info("No shot data available for this match.")
    
    elif shots_df.empty:
        st.info("💡 Shot maps are available after running `python -m extract.extract_shots`")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure you've run the extraction scripts first.")
