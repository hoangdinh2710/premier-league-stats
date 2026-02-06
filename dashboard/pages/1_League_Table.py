"""
League Table - Compare actual standings with xG-based projections.
"""
import streamlit as st
import pandas as pd
from utils.queries import get_teams_data, calculate_league_table, calculate_xg_table

st.set_page_config(page_title="League Table", page_icon="🏆", layout="wide")

# Get league/season from session state (set in app.py sidebar)
league_name = st.session_state.get("league_name")
season = st.session_state.get("season")
league_display = league_name or "League"

st.title(f"🏆 {league_display} Table")
st.markdown("Compare the actual league standings with xG-based projections to identify over and underperforming teams.")

# Load team data
try:
    teams_df = get_teams_data(league_name=league_name, season=season)
    
    if teams_df.empty:
        st.warning("No team data available. Please run the extraction scripts first.")
        st.stop()
    
    # Calculate both tables
    actual_table = calculate_league_table(teams_df.copy())
    xg_table = calculate_xg_table(teams_df.copy())
    
    # Add positions
    actual_table.insert(0, 'Pos', range(1, len(actual_table) + 1))
    xg_table.insert(0, 'xG Pos', range(1, len(xg_table) + 1))
    
    # Create mapping for comparison
    xg_positions = dict(zip(xg_table['title'], xg_table['xG Pos']))
    actual_table['xG Pos'] = actual_table['title'].map(xg_positions)
    actual_table['Diff'] = actual_table['xG Pos'] - actual_table['Pos']
    
    # Display tables side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Actual Standings")
        st.markdown("*Based on points earned*")
        
        # Prepare display dataframe - check which columns exist
        base_cols = ['Pos', 'title', 'matches', 'wins', 'draws', 'loses']
        optional_cols = []
        if 'scored' in actual_table.columns:
            optional_cols.append('scored')
        if 'missed' in actual_table.columns:
            optional_cols.append('missed')
        end_cols = ['pts', 'xG Pos', 'Diff']
        
        display_cols = base_cols + optional_cols + end_cols
        display_cols = [col for col in display_cols if col in actual_table.columns]
        display_actual = actual_table[display_cols].copy()
        
        # Map column names for display
        col_mapping = {
            'Pos': 'Pos', 'title': 'Team', 'matches': 'P', 'wins': 'W', 
            'draws': 'D', 'loses': 'L', 'scored': 'GF', 'missed': 'GA', 
            'pts': 'Pts', 'xG Pos': 'xG Pos', 'Diff': 'Diff'
        }
        display_actual.columns = [col_mapping.get(col, col) for col in display_actual.columns]
        
        # Apply styling based on performance
        def highlight_rows(row):
            if row['Diff'] > 2:  # Overperforming (actual pos better than xG pos)
                return ['background-color: rgba(0, 200, 0, 0.2)'] * len(row)
            elif row['Diff'] < -2:  # Underperforming
                return ['background-color: rgba(200, 0, 0, 0.2)'] * len(row)
            return [''] * len(row)
        
        styled_df = display_actual.style.apply(highlight_rows, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Color coding:**
        - 🟢 Green = Overperforming vs xG (doing better than expected)
        - 🔴 Red = Underperforming vs xG (doing worse than expected)
        """)
    
    with col2:
        st.subheader("📈 xG Table")
        st.markdown("*Based on Expected Goals difference*")
        
        # Prepare display dataframe
        display_xg = xg_table[['xG Pos', 'title', 'matches', 'xG', 'xGA', 'xG_diff']].copy()
        display_xg.columns = ['Pos', 'Team', 'P', 'xGF', 'xGA', 'xGD']
        display_xg['xGF'] = display_xg['xGF'].round(1)
        display_xg['xGA'] = display_xg['xGA'].round(1)
        display_xg['xGD'] = display_xg['xGD'].round(1)
        
        st.dataframe(display_xg, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **xG Table:**
        - Shows how teams "should" rank based on chance quality
        - Higher xGD = creating better chances than opponents
        """)
    
    # Analysis section
    st.markdown("---")
    st.subheader("🔍 Performance Analysis")
    
    # Biggest overperformers
    overperformers = actual_table.nlargest(3, 'Diff')[['title', 'Pos', 'xG Pos', 'Diff', 'pts']]
    
    # Biggest underperformers
    underperformers = actual_table.nsmallest(3, 'Diff')[['title', 'Pos', 'xG Pos', 'Diff', 'pts']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Top Overperformers")
        st.markdown("*Teams performing better than their xG suggests*")
        for idx, row in overperformers.iterrows():
            if row['Diff'] > 0:
                st.write(f"**{row['title']}**: Actual {int(row['Pos'])}th, xG {int(row['xG Pos'])}th (+{int(row['Diff'])} positions)")
    
    with col2:
        st.markdown("#### 📉 Top Underperformers")
        st.markdown("*Teams performing worse than their xG suggests*")
        for idx, row in underperformers.iterrows():
            if row['Diff'] < 0:
                st.write(f"**{row['title']}**: Actual {int(row['Pos'])}th, xG {int(row['xG Pos'])}th ({int(row['Diff'])} positions)")
    
    # Insights
    st.markdown("---")
    st.info("""
    **💡 Key Insights:**
    - Teams in **green** are getting better results than their underlying performance suggests (luck, clinical finishing, or strong defense)
    - Teams in **red** are getting worse results despite creating good chances (wasteful finishing or poor defending set pieces)
    - The xG table often predicts future performance better than current standings
    """)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure you've run `python -m extract.extract_league` first.")
