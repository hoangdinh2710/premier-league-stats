"""
Extract match results from Understat.
Supports multiple leagues and seasons.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_match_data(season="2025", league="EPL"):
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
    
    # Inject league_name and season into each match record
    if isinstance(matches, list):
        for match in matches:
            if isinstance(match, dict):
                match['league_name'] = league
                match['season'] = season
    elif isinstance(matches, dict):
        for match_id, match_data in matches.items():
            if isinstance(match_data, dict):
                match_data['league_name'] = league
                match_data['season'] = season
    
    print(f"✓ Extracted data for {len(matches)} matches")
    return matches


def save_match_data(matches, league="EPL", season="2025", output_dir="data/raw"):
    """
    Save match data to JSON file.
    
    Args:
        matches: List of match data dictionaries
        league: League code for filename
        season: Season year for filename
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with league, season, and current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/matches_{league}_{season}_{date_str}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved match data to {filename}")
    return filename


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Extract match data from Understat')
    parser.add_argument('--season', type=str, default='2025', help='Season year (e.g., 2024)')
    parser.add_argument('--league', type=str, default='EPL', help='League code (e.g., EPL, La_Liga, Bundesliga)')
    args = parser.parse_args()

    try:
        # Extract data
        matches = extract_match_data(season=args.season, league=args.league)
        
        # Save to file
        filename = save_match_data(matches, league=args.league, season=args.season)
        
        print(f"\n✓ Match extraction complete!")
        print(f"  - Matches extracted: {len(matches)}")
        print(f"  - File: {filename}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
