"""
Extract match roster/lineup data for the Premier League from Understat.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_roster_data(season="2024", league="EPL"):
    """
    Extract roster/lineup data for all matches in a given season.

    Args:
        season: Season year (e.g., "2024" for 2024/25 season)
        league: League code (default: "EPL" for Premier League)

    Returns:
        List of roster data dictionaries with match info
    """
    print(f"Extracting roster data for {league} {season} season...")

    all_rosters = []
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

        # Extract rosters for each match
        for i, match in enumerate(completed_matches, 1):
            match_id = match.get('id')
            home_team = match.get('h', {}).get('title', 'Unknown')
            away_team = match.get('a', {}).get('title', 'Unknown')
            match_date = match.get('datetime', '')

            print(f"  - [{i}/{len(completed_matches)}] Getting roster for {home_team} vs {away_team} (ID: {match_id})...")

            try:
                roster_data = understat.match(match=match_id).get_roster_data()

                # Structure the roster data with match context
                roster_entry = {
                    'match_id': match_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'datetime': match_date,
                    'home_roster': roster_data.get('h', []) if isinstance(roster_data, dict) else [],
                    'away_roster': roster_data.get('a', []) if isinstance(roster_data, dict) else []
                }

                all_rosters.append(roster_entry)

                home_count = len(roster_entry['home_roster'])
                away_count = len(roster_entry['away_roster'])
                print(f"    Got {home_count} home players, {away_count} away players")

                # Rate limiting: sleep between requests
                time.sleep(1)

            except Exception as e:
                print(f"    Error getting roster for match {match_id}: {e}")
                continue

    print(f"Extracted rosters for {len(all_rosters)} matches")
    return all_rosters


def save_roster_data(rosters, output_dir="data/raw"):
    """
    Save roster data to JSON file.

    Args:
        rosters: List of roster data dictionaries
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename with current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/rosters_{date_str}.json"

    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(rosters, f, indent=2, ensure_ascii=False)

    print(f"Saved roster data to {filename}")
    return filename


def main():
    """Main execution function."""
    try:
        # Extract data
        rosters = extract_roster_data(season="2025", league="EPL")

        # Save to file
        filename = save_roster_data(rosters)

        print(f"\nRoster extraction complete!")
        print(f"  - Matches processed: {len(rosters)}")
        print(f"  - File: {filename}")

    except Exception as e:
        print(f"Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
