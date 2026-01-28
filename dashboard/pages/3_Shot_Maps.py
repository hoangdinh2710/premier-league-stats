"""
Shot Maps - Visualize shot locations on the pitch.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.queries import get_shots_data
from utils.charts import draw_half_pitch

st.set_page_config(page_title="Shot Maps", page_icon="🎯", layout="wide")

st.title("🎯 Shot Maps")
st.markdown("Visualize shot locations and quality on the pitch with xG values.")

# Load shot data
try:
    shots_df = get_shots_data()
    
    if shots_df.empty:
        st.warning("No shot data available. Please run `python -m extract.extract_shots` first.")
        st.info("⚠️ Note: Shot extraction can take 5-10 minutes due to rate limiting.")
        st.stop()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Team filter - get unique teams from both home and away
        teams = []
        if 'h_team' in shots_df.columns and 'a_team' in shots_df.columns:
            # Get all unique teams from both h_team and a_team
            home_teams = set(shots_df['h_team'].unique())
            away_teams = set(shots_df['a_team'].unique())
            teams = sorted(home_teams | away_teams)
        elif 'h_team' in shots_df.columns:
            teams = sorted(shots_df['h_team'].unique())
        elif 'team' in shots_df.columns:
            teams = sorted(shots_df['team'].unique())
        
        teams_with_all = ['All Teams'] + teams
        selected_team = st.selectbox("Select Team:", teams_with_all)
    
    with col2:
        # Result filter
        result_options = ['All Shots', 'Goals Only', 'On Target', 'Off Target', 'Blocked']
        selected_result = st.selectbox("Shot Result:", result_options)
    
    with col3:
        # Situation filter
        situation_options = ['All Situations']
        if 'situation' in shots_df.columns:
            situation_options += sorted(shots_df['situation'].unique())
        selected_situation = st.selectbox("Situation:", situation_options)
    
    # Apply filters
    filtered_shots = shots_df.copy()
    
    if selected_team != 'All Teams':
        if 'h_team' in filtered_shots.columns and 'a_team' in filtered_shots.columns:
            # Get shots where the selected team is either home or away
            filtered_shots = filtered_shots[
                (filtered_shots['h_team'] == selected_team) | 
                (filtered_shots['a_team'] == selected_team)
            ]
        elif 'h_team' in filtered_shots.columns:
            filtered_shots = filtered_shots[filtered_shots['h_team'] == selected_team]
        elif 'team' in filtered_shots.columns:
            filtered_shots = filtered_shots[filtered_shots['team'] == selected_team]
    
    if selected_result != 'All Shots':
        if 'result' in filtered_shots.columns:
            if selected_result == 'Goals Only':
                filtered_shots = filtered_shots[filtered_shots['result'] == 'Goal']
            elif selected_result == 'On Target':
                filtered_shots = filtered_shots[filtered_shots['result'].isin(['Goal', 'SavedShot'])]
            elif selected_result == 'Off Target':
                filtered_shots = filtered_shots[filtered_shots['result'] == 'MissedShots']
            elif selected_result == 'Blocked':
                filtered_shots = filtered_shots[filtered_shots['result'] == 'BlockedShot']
    
    if selected_situation != 'All Situations':
        if 'situation' in filtered_shots.columns:
            filtered_shots = filtered_shots[filtered_shots['situation'] == selected_situation]
    
    st.markdown(f"**Showing {len(filtered_shots)} shots**")
    
    # Create shot map
    if not filtered_shots.empty:
        fig = draw_half_pitch()
        
        # Reset index to avoid index mismatch issues
        filtered_shots = filtered_shots.reset_index(drop=True)
        
        # Prepare shot data
        x_coords = filtered_shots['X'].values
        y_coords = filtered_shots['Y'].values
        xg_values = filtered_shots['xG'].values
        
        # Get additional info for hover
        hover_text = []
        for idx, shot in filtered_shots.iterrows():
            player = shot.get('player', 'Unknown')
            xg = shot.get('xG', 0)
            result = shot.get('result', 'Unknown')
            minute = shot.get('minute', '?')
            situation = shot.get('situation', 'Unknown')
            shot_type = shot.get('shotType', 'Unknown')
            
            hover_text.append(
                f"Player: {player}<br>"
                f"xG: {xg:.3f}<br>"
                f"Result: {result}<br>"
                f"Minute: {minute}<br>"
                f"Situation: {situation}<br>"
                f"Shot Type: {shot_type}"
            )
        
        # Map results to symbols
        symbol_map = {
            'Goal': 'star',
            'SavedShot': 'circle',
            'MissedShots': 'x',
            'BlockedShot': 'square'
        }
        
        # Add shots by result type
        if 'result' in filtered_shots.columns:
            for result_type, symbol in symbol_map.items():
                mask = filtered_shots['result'] == result_type
                if mask.any():
                    subset = filtered_shots[mask]
                    
                    fig.add_trace(go.Scatter(
                        x=subset['X'],
                        y=subset['Y'],
                        mode='markers',
                        name=result_type,
                        marker=dict(
                            size=subset['xG'] * 30 + 5,  # Size based on xG
                            symbol=symbol,
                            color=subset['xG'],  # Color based on xG
                            colorscale='RdYlGn',  # Red (low) to Green (high)
                            cmin=0,
                            cmax=0.5,
                            showscale=True if result_type == 'Goal' else False,
                            colorbar=dict(title="xG Value", x=1.15),
                            line=dict(color='white', width=1)
                        ),
                        text=[hover_text[i] for i in subset.index],
                        hovertemplate='%{text}<extra></extra>'
                    ))
        else:
            # Fallback if no result column
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers',
                name='Shots',
                marker=dict(
                    size=xg_values * 30 + 5,
                    color=xg_values,
                    colorscale='RdYlGn',
                    cmin=0,
                    cmax=0.5,
                    showscale=True,
                    colorbar=dict(title="xG Value"),
                    line=dict(color='white', width=1)
                ),
                text=hover_text,
                hovertemplate='%{text}<extra></extra>'
            ))
        
        fig.update_layout(
            title=f"Shot Map: {selected_team}",
            height=700,
            showlegend=True,
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Shot statistics
        st.markdown("---")
        st.subheader("📊 Shot Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_shots = len(filtered_shots)
            st.metric("Total Shots", total_shots)
        
        with col2:
            goals = len(filtered_shots[filtered_shots['result'] == 'Goal']) if 'result' in filtered_shots.columns else 0
            st.metric("Goals", goals)
        
        with col3:
            total_xg = filtered_shots['xG'].sum()
            st.metric("Total xG", f"{total_xg:.2f}")
        
        with col4:
            if total_xg > 0:
                conversion = (goals / total_shots * 100) if total_shots > 0 else 0
                st.metric("Conversion Rate", f"{conversion:.1f}%")
        
        # Breakdown by result
        if 'result' in filtered_shots.columns:
            st.markdown("#### Shot Breakdown")
            result_counts = filtered_shots['result'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                for result, count in result_counts.items():
                    pct = (count / total_shots * 100)
                    st.write(f"**{result}**: {count} ({pct:.1f}%)")
            
            with col2:
                # Average xG by result
                st.markdown("**Average xG by Result:**")
                avg_xg = filtered_shots.groupby('result')['xG'].mean().sort_values(ascending=False)
                for result, xg in avg_xg.items():
                    st.write(f"**{result}**: {xg:.3f}")
        
        # Legend explanation
        st.markdown("---")
        st.info("""
        **Shot Map Legend:**
        - ⭐ **Star** = Goal
        - ⚪ **Circle** = Saved Shot
        - ❌ **X** = Missed Shot
        - ⬜ **Square** = Blocked Shot
        - **Size** = xG value (bigger = higher quality chance)
        - **Color** = xG value (red = low, yellow = medium, green = high)
        """)
    
    else:
        st.warning("No shots match the selected filters.")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure you've run `python -m extract.extract_shots` first.")
