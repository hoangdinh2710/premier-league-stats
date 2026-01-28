"""
Extract shot-level data for the Premier League from Understat.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_shot_data(season="2024", league="EPL"):
    """
    Extract shot data for all matches in a given season.
    
    Args:
        season: Season year (e.g., "2024" for 2024/25 season)
        league: League code (default: "EPL" for Premier League)
    
    Returns:
        List of shot data dictionaries
    """
    print(f"Extracting shot data for {league} {season} season...")
    
    all_shots = []
    completed_match_count = 0
    
    with UnderstatClient() as understat:
        # First, get all matches for the season
        print("  - Getting match list...")
        matches = understat.league(league=league).get_match_data(season=season)
        print(f"  - Found {len(matches)} matches")
        
        # Filter to only completed matches (isResult=True)
        completed_matches = [m for m in matches if m.get('isResult', False)]
        skipped = len(matches) - len(completed_matches)
        completed_match_count = len(completed_matches)
        if skipped > 0:
            print(f"  - Skipping {skipped} unplayed matches")
        print(f"  - Processing {completed_match_count} completed matches")
        
        # Extract shots for each match
        for i, match in enumerate(completed_matches, 1):
            match_id = match.get('id')
            home_team = match.get('h', {}).get('title', 'Unknown')
            away_team = match.get('a', {}).get('title', 'Unknown')
            
            print(f"  - [{i}/{len(completed_matches)}] Getting shots for {home_team} vs {away_team} (ID: {match_id})...")
            
            try:
                shots_data = understat.match(match=match_id).get_shot_data()
                
                # Handle the structure: shots_data is a dict with 'h' (home) and 'a' (away) keys
                # Each value is a list of shot dictionaries
                match_shots = []
                
                if isinstance(shots_data, dict):
                    # Iterate over home and away shots
                    for team_key, team_shots in shots_data.items():
                        if isinstance(team_shots, list):
                            for shot in team_shots:
                                if isinstance(shot, dict):
                                    # Add match_id to each shot for reference
                                    shot['match_id'] = match_id
                                    match_shots.append(shot)
                elif isinstance(shots_data, list):
                    # If it's already a list, use it directly
                    for shot in shots_data:
                        if isinstance(shot, dict):
                            shot['match_id'] = match_id
                            match_shots.append(shot)
                
                all_shots.extend(match_shots)
                print(f"    ✓ Got {len(match_shots)} shots")
                
                # Rate limiting: sleep for 1 second between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"    ✗ Error getting shots for match {match_id}: {e}")
                continue
    
    print(f"✓ Extracted {len(all_shots)} total shots from {completed_match_count} matches")
    return all_shots


def save_shot_data(shots, output_dir="data/raw"):
    """
    Save shot data to JSON file.
    
    Args:
        shots: List of shot data dictionaries
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename with current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/shots_{date_str}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(shots, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved shot data to {filename}")
    return filename


def main():
    """Main execution function."""
    try:
        # Extract data
        shots = extract_shot_data(season="2025", league="EPL")
        
        # Save to file
        filename = save_shot_data(shots)
        
        print(f"\n✓ Shot extraction complete!")
        print(f"  - Shots extracted: {len(shots)}")
        print(f"  - File: {filename}")
        
    except Exception as e:
        print(f"✗ Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
