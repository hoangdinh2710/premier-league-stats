"""
Pipeline Orchestrator - Run the full ETL pipeline with medallion architecture.

Pipeline flow:
1. Extract: Pull data from Understat API -> data/raw/*.json
2. Bronze Stage: Load JSON files -> bronze_stage.* (TRUNCATE + INSERT)
3. Bronze Merge: Merge stage -> bronze_prod.* (UPSERT)
4. Silver Transform: Transform bronze_prod -> silver.* (UPSERT)
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_extract(season: int = None):
    """Run all extraction scripts."""
    print("\n" + "=" * 60)
    print("STEP 1: EXTRACT - Pulling data from Understat API")
    print("=" * 60)

    extract_scripts = [
        'extract/extract_league.py',
        'extract/extract_players.py',
        'extract/extract_matches.py',
        'extract/extract_shots.py',
        'extract/extract_rosters.py',
        'extract/extract_player_grouped.py',
        'extract/extract_team_context.py',
    ]

    for script in extract_scripts:
        script_path = Path(script)
        if script_path.exists():
            print(f"\nRunning {script}...")
            args = [sys.executable, str(script_path)]
            if season:
                args.extend(['--season', str(season)])
            result = subprocess.run(args, capture_output=False)
            if result.returncode != 0:
                print(f"Warning: {script} exited with code {result.returncode}")
        else:
            print(f"Warning: {script} not found, skipping")


def run_bronze_stage():
    """Load data to bronze_stage tables."""
    print("\n" + "=" * 60)
    print("STEP 2: BRONZE STAGE - Loading to staging tables")
    print("=" * 60)

    from load.bronze_stage import load_all_to_stage, close_pool

    try:
        results = load_all_to_stage()
        return results
    finally:
        close_pool()


def run_bronze_merge():
    """Merge bronze_stage to bronze_prod."""
    print("\n" + "=" * 60)
    print("STEP 3: BRONZE MERGE - Merging stage to production")
    print("=" * 60)

    from load.bronze_merge import merge_all_to_prod, close_pool

    try:
        results = merge_all_to_prod()
        return results
    finally:
        close_pool()


def run_silver_transform():
    """Transform bronze_prod to silver."""
    print("\n" + "=" * 60)
    print("STEP 4: SILVER TRANSFORM - Transforming to silver layer")
    print("=" * 60)

    from transform.silver_transform import refresh_all_silver, close_pool

    try:
        results = refresh_all_silver()
        return results
    finally:
        close_pool()


def run_pipeline(
    extract: bool = True,
    bronze_stage: bool = True,
    bronze_merge: bool = True,
    silver: bool = True,
    season: int = None
):
    """
    Run the full ETL pipeline.

    Args:
        extract: Whether to run extraction step
        bronze_stage: Whether to run bronze stage loading
        bronze_merge: Whether to run bronze merge
        silver: Whether to run silver transform
        season: Season year for extraction (e.g., 2024)
    """
    start_time = datetime.now()

    print("\n" + "#" * 60)
    print("# PREMIER LEAGUE STATS - MEDALLION PIPELINE")
    print(f"# Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("#" * 60)

    results = {}

    try:
        # Step 1: Extract
        if extract:
            run_extract(season)
            results['extract'] = 'completed'
        else:
            print("\nSkipping extraction step")
            results['extract'] = 'skipped'

        # Step 2: Bronze Stage
        if bronze_stage:
            results['bronze_stage'] = run_bronze_stage()
        else:
            print("\nSkipping bronze stage loading")
            results['bronze_stage'] = 'skipped'

        # Step 3: Bronze Merge
        if bronze_merge:
            results['bronze_merge'] = run_bronze_merge()
        else:
            print("\nSkipping bronze merge")
            results['bronze_merge'] = 'skipped'

        # Step 4: Silver Transform
        if silver:
            results['silver'] = run_silver_transform()
        else:
            print("\nSkipping silver transform")
            results['silver'] = 'skipped'

        # Summary
        end_time = datetime.now()
        duration = end_time - start_time

        print("\n" + "#" * 60)
        print("# PIPELINE COMPLETE")
        print(f"# Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# Duration: {duration}")
        print("#" * 60)

        return results

    except Exception as e:
        print(f"\nPipeline failed: {e}")
        raise


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Run the Premier League Stats ETL pipeline'
    )

    parser.add_argument(
        '--no-extract',
        action='store_true',
        help='Skip the extraction step (use existing JSON files)'
    )

    parser.add_argument(
        '--no-bronze-stage',
        action='store_true',
        help='Skip bronze stage loading'
    )

    parser.add_argument(
        '--no-bronze-merge',
        action='store_true',
        help='Skip bronze merge step'
    )

    parser.add_argument(
        '--no-silver',
        action='store_true',
        help='Skip silver transform step'
    )

    parser.add_argument(
        '--bronze-only',
        action='store_true',
        help='Only run bronze layer (stage + merge), skip extract and silver'
    )

    parser.add_argument(
        '--silver-only',
        action='store_true',
        help='Only run silver transform (assumes bronze_prod has data)'
    )

    parser.add_argument(
        '--season',
        type=int,
        help='Season year to extract (e.g., 2024 for 2024/25 season)'
    )

    args = parser.parse_args()

    # Determine which steps to run
    if args.bronze_only:
        run_pipeline(
            extract=False,
            bronze_stage=True,
            bronze_merge=True,
            silver=False,
            season=args.season
        )
    elif args.silver_only:
        run_pipeline(
            extract=False,
            bronze_stage=False,
            bronze_merge=False,
            silver=True,
            season=args.season
        )
    else:
        run_pipeline(
            extract=not args.no_extract,
            bronze_stage=not args.no_bronze_stage,
            bronze_merge=not args.no_bronze_merge,
            silver=not args.no_silver,
            season=args.season
        )


if __name__ == "__main__":
    main()
