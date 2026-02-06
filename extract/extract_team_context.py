"""
Extract team context/situational data from Understat.
Supports multiple leagues and seasons.
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_team_context_data(season="2025", league="EPL"):
    """
    Extract context/situational data for all teams in a given season.

    Context data includes team performance broken down by:
    - Situation (open play, set piece, counter, etc.)
    - Game state (winning, drawing, losing)
    - Timing (first half, second half, etc.)
    - Formation used

    Args:
        season: Season year (e.g., "2024" for 2024/25 season)
        league: League code (default: "EPL" for Premier League)

    Returns:
        List of team context data dictionaries
    """
    print(f"Extracting team context data for {league} {season} season...")

    all_team_context = []

    with UnderstatClient() as understat:
        # First, get all teams for the season
        print("  - Getting team list...")
        teams = understat.league(league=league).get_team_data(season=season)

        # Extract team names from the data structure
        # teams is a dict with team IDs as keys, each value has a 'title' field
        if isinstance(teams, dict):
            team_names = []
            for team_id, team_data in teams.items():
                if isinstance(team_data, dict) and 'title' in team_data:
                    team_names.append(team_data['title'])
                elif isinstance(team_data, list) and len(team_data) > 0:
                    # Sometimes it's a list of match data with team info
                    first_entry = team_data[0]
                    if isinstance(first_entry, dict) and 'title' in first_entry:
                        team_names.append(first_entry['title'])
        else:
            team_names = [t.get('title', t.get('id')) for t in teams]

        print(f"  - Found {len(team_names)} teams: {', '.join(team_names)}")

        # Extract context data for each team
        for i, team_name in enumerate(team_names, 1):
            # Convert team name to URL format (spaces -> underscores)
            team_url_name = team_name.replace(' ', '_')
            print(f"  - [{i}/{len(team_names)}] Getting context data for {team_name}...")

            try:
                context_data = understat.team(team=team_url_name).get_context_data(season=season)

                # Structure the data with team context
                team_entry = {
                    'team_name': team_name,
                    'season': season,
                    'league_name': league,
                    'context_stats': context_data
                }

                all_team_context.append(team_entry)

                # Count available context categories
                categories = list(context_data.keys()) if isinstance(context_data, dict) else []
                print(f"    Got categories: {', '.join(categories) if categories else 'none'}")

                # Rate limiting: sleep between requests
                time.sleep(0.5)

            except Exception as e:
                print(f"    Error getting context data for {team_name}: {e}")
                continue

    print(f"Extracted context data for {len(all_team_context)} teams")
    return all_team_context


def save_team_context_data(team_data, league="EPL", season="2025", output_dir="data/raw"):
    """
    Save team context data to JSON file.

    Args:
        team_data: List of team context data dictionaries
        league: League code for filename
        season: Season year for filename
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename with league, season, and current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/team_context_{league}_{season}_{date_str}.json"

    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(team_data, f, indent=2, ensure_ascii=False)

    print(f"Saved team context data to {filename}")
    return filename


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Extract team context data from Understat')
    parser.add_argument('--season', type=str, default='2025', help='Season year (e.g., 2024)')
    parser.add_argument('--league', type=str, default='EPL', help='League code (e.g., EPL, La_Liga, Bundesliga)')
    args = parser.parse_args()

    try:
        # Extract data
        team_context = extract_team_context_data(season=args.season, league=args.league)

        # Save to file
        filename = save_team_context_data(team_context, league=args.league, season=args.season)

        print(f"\nTeam context extraction complete!")
        print(f"  - Teams processed: {len(team_context)}")
        print(f"  - File: {filename}")

    except Exception as e:
        print(f"Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
