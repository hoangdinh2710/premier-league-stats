"""
Extract match results for the Premier League from Understat.
"""
import json
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_match_data(season="2024", league="EPL"):
    """
    Extract match results for a given season.
    
    Args:
        season: Season year (e.g., "2024" for 2024/25 season)
        league: League code (default: "EPL" for Premier League)
    
    Returns:
        List of match data dictionaries
    """
    print(f"Extracting match data for {league} {season} season...")
    
    with UnderstatClient() as understat:
        matches = understat.league(league=league).get_match_data(season=season)
    
    print(f"✓ Extracted data for {len(matches)} matches")
    return matches


def save_match_data(matches, output_dir="data/raw"):
    """
    Save match data to JSON file.
    
    Args:
        matches: List of match data dictionaries
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/matches_{date_str}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved match data to {filename}")
    return filename


def main():
    """Main execution function."""
    try:
        # Extract data
        matches = extract_match_data(season="2025", league="EPL")
        
        # Save to file
        filename = save_match_data(matches)
        
        print(f"\n✓ Match extraction complete!")
        print(f"  - Matches extracted: {len(matches)}")
        print(f"  - File: {filename}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
