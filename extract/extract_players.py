"""
Extract player statistics for the Premier League from Understat.
"""
import json
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_player_data(season="2024", league="EPL"):
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
    
    print(f"✓ Extracted data for {len(players)} players")
    return players


def save_player_data(players, output_dir="data/raw"):
    """
    Save player data to JSON file.
    
    Args:
        players: List of player data dictionaries
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/players_{date_str}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved player data to {filename}")
    return filename


def main():
    """Main execution function."""
    try:
        # Extract data
        players = extract_player_data(season="2025", league="EPL")
        
        # Save to file
        filename = save_player_data(players)
        
        print(f"\n✓ Player extraction complete!")
        print(f"  - Players extracted: {len(players)}")
        print(f"  - File: {filename}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
