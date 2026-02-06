"""
Extract team-level statistics from Understat.
Supports multiple leagues and seasons.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_team_data(season="2025", league="EPL"):
    """
    Extract team statistics for a given season.
    
    Args:
        season: Season year (e.g., "2024" for 2024/25 season)
        league: League code (default: "EPL" for Premier League)
    
    Returns:
        List of team data dictionaries
    """
    print(f"Extracting team data for {league} {season} season...")
    
    with UnderstatClient() as understat:
        teams = understat.league(league=league).get_team_data(season=season)
    
    # Inject league_name and season into each team record
    if isinstance(teams, dict):
        for team_id, team_data in teams.items():
            if isinstance(team_data, dict):
                team_data['league_name'] = league
                team_data['season'] = season
    elif isinstance(teams, list):
        for team in teams:
            if isinstance(team, dict):
                team['league_name'] = league
                team['season'] = season
    
    print(f"✓ Extracted data for {len(teams)} teams")
    return teams


def save_team_data(teams, league="EPL", season="2025", output_dir="data/raw"):
    """
    Save team data to JSON file.
    
    Args:
        teams: List of team data dictionaries
        league: League code for filename
        season: Season year for filename
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with league, season, and current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/teams_{league}_{season}_{date_str}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved team data to {filename}")
    return filename


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Extract team data from Understat')
    parser.add_argument('--season', type=str, default='2025', help='Season year (e.g., 2024)')
    parser.add_argument('--league', type=str, default='EPL', help='League code (e.g., EPL, La_Liga, Bundesliga)')
    args = parser.parse_args()

    try:
        # Extract data
        teams = extract_team_data(season=args.season, league=args.league)
        
        # Save to file
        filename = save_team_data(teams, league=args.league, season=args.season)
        
        print(f"\n✓ Team extraction complete!")
        print(f"  - Teams extracted: {len(teams)}")
        print(f"  - File: {filename}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
