"""
Extract team-level statistics for the Premier League from Understat.
"""
import json
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_team_data(season="2024", league="EPL"):
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
    
    print(f"✓ Extracted data for {len(teams)} teams")
    return teams


def save_team_data(teams, output_dir="data/raw"):
    """
    Save team data to JSON file.
    
    Args:
        teams: List of team data dictionaries
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/teams_{date_str}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved team data to {filename}")
    return filename


def main():
    """Main execution function."""
    try:
        # Extract data
        teams = extract_team_data(season="2025", league="EPL")
        
        # Save to file
        filename = save_team_data(teams)
        
        print(f"\n✓ Team extraction complete!")
        print(f"  - Teams extracted: {len(teams)}")
        print(f"  - File: {filename}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
