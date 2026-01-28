"""
Extract player grouped statistics (by season, situation, position, game state) from Understat.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from understatapi import UnderstatClient


def extract_player_grouped_data(season="2024", league="EPL", min_minutes=90):
    """
    Extract grouped statistics for all players in a given season.

    The grouped data includes stats broken down by:
    - Season
    - Situation (open play, set piece, penalty, etc.)
    - Position
    - Game state (winning, drawing, losing)

    Args:
        season: Season year (e.g., "2024" for 2024/25 season)
        league: League code (default: "EPL" for Premier League)
        min_minutes: Minimum minutes played to include player (default: 90)

    Returns:
        List of player grouped data dictionaries
    """
    print(f"Extracting player grouped data for {league} {season} season...")

    all_player_grouped = []

    with UnderstatClient() as understat:
        # First, get all players for the season
        print("  - Getting player list...")
        players = understat.league(league=league).get_player_data(season=season)
        print(f"  - Found {len(players)} players")

        # Filter players by minimum minutes
        filtered_players = [p for p in players if int(p.get('time', 0)) >= min_minutes]
        skipped = len(players) - len(filtered_players)
        if skipped > 0:
            print(f"  - Skipping {skipped} players with less than {min_minutes} minutes")
        print(f"  - Processing {len(filtered_players)} players")

        # Extract grouped data for each player
        for i, player in enumerate(filtered_players, 1):
            player_id = player.get('id')
            player_name = player.get('player_name', 'Unknown')
            team = player.get('team_title', 'Unknown')

            print(f"  - [{i}/{len(filtered_players)}] Getting grouped data for {player_name} ({team})...")

            try:
                grouped_data = understat.player(player=player_id).get_season_data()

                # Structure the data with player context
                player_entry = {
                    'player_id': player_id,
                    'player_name': player_name,
                    'team': team,
                    'position': player.get('position', ''),
                    'games': player.get('games', 0),
                    'time': player.get('time', 0),
                    'grouped_stats': grouped_data
                }

                all_player_grouped.append(player_entry)

                # Count available groupings
                groupings = list(grouped_data.keys()) if isinstance(grouped_data, dict) else []
                print(f"    Got groupings: {', '.join(groupings) if groupings else 'none'}")

                # Rate limiting: sleep between requests
                time.sleep(0.5)

            except Exception as e:
                print(f"    Error getting grouped data for {player_name}: {e}")
                continue

    print(f"Extracted grouped data for {len(all_player_grouped)} players")
    return all_player_grouped


def save_player_grouped_data(player_data, output_dir="data/raw"):
    """
    Save player grouped data to JSON file.

    Args:
        player_data: List of player grouped data dictionaries
        output_dir: Directory to save the file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename with current date
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{output_dir}/player_grouped_{date_str}.json"

    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(player_data, f, indent=2, ensure_ascii=False)

    print(f"Saved player grouped data to {filename}")
    return filename


def main():
    """Main execution function."""
    try:
        # Extract data (players with at least 90 minutes)
        player_grouped = extract_player_grouped_data(season="2025", league="EPL", min_minutes=90)

        # Save to file
        filename = save_player_grouped_data(player_grouped)

        print(f"\nPlayer grouped extraction complete!")
        print(f"  - Players processed: {len(player_grouped)}")
        print(f"  - File: {filename}")

    except Exception as e:
        print(f"Error during extraction: {e}")
        raise


if __name__ == "__main__":
    main()
