"""
Extract player statistics from Understat.
Supports multiple leagues and seasons.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_player_data(season="2025", league="EPL"):
    """
    Extract player statistics for a given season.
    
    Args:
        season: Season year (e.g., "2024" for 2024/25 season)
        league: League code (default: "EPL" for Premier League)
    
    Returns:
        List of player data dictionaries
    """
    print(f"Extracting player data for {league} {season} season...")
    
    with UnderstatClient() as understat:
        players = understat.league(league=league).get_player_data(season=season)
    
    # Inject league_name and season into each player record
    if isinstance(players, list):
        for player in players:
            if isinstance(player, dict):
                player['league_name'] = league
                player['season'] = season
    elif isinstance(players, dict):
        for player_id, player_data in players.items():
            if isinstance(player_data, dict):
                player_data['league_name'] = league
                player_data['season'] = season
    
    print(f"✓ Extracted data for {len(players)} players")
    return players


def save_player_data(players, league="EPL", season="2025", output_dir="data/raw"):
    """
    Save player data to JSON file.
    
    Args:
        players: List of player data dictionaries
        league: League code for filename
        season: Season year for filename
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with league, season, and current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/players_{league}_{season}_{date_str}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved player data to {filename}")
    return filename


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Extract player data from Understat')
    parser.add_argument('--season', type=str, default='2025', help='Season year (e.g., 2024)')
    parser.add_argument('--league', type=str, default='EPL', help='League code (e.g., EPL, La_Liga, Bundesliga)')
    args = parser.parse_args()

    try:
        # Extract data
        players = extract_player_data(season=args.season, league=args.league)
        
        # Save to file
        filename = save_player_data(players, league=args.league, season=args.season)
        
        print(f"\n✓ Player extraction complete!")
        print(f"  - Players extracted: {len(players)}")
        print(f"  - File: {filename}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
