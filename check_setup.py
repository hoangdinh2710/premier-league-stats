"""
Test/Demo script to verify the installation and data extraction.
Run this to check if everything is working correctly.
"""
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_dependencies():
    """Check if required packages are installed."""
    print_header("Checking Dependencies")
    
    required = [
        'understatapi',
        'pandas',
        'streamlit',
        'plotly',
        'supabase',
        'dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✓ {package:<20} installed")
        except ImportError:
            print(f"✗ {package:<20} MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def check_data_files():
    """Check for extracted data files."""
    print_header("Checking Data Files")
    
    data_dir = Path("data/raw")
    
    if not data_dir.exists():
        print("✗ data/raw directory not found")
        return False
    
    files = {
        'teams': list(data_dir.glob("teams_*.json")),
        'players': list(data_dir.glob("players_*.json")),
        'matches': list(data_dir.glob("matches_*.json")),
        'shots': list(data_dir.glob("shots_*.json"))
    }
    
    for data_type, file_list in files.items():
        if file_list:
            latest = sorted(file_list, reverse=True)[0]
            print(f"✓ {data_type:<15} {latest.name}")
        else:
            print(f"✗ {data_type:<15} not found")
    
    if all(files.values()):
        print("\n✅ All data files present!")
        return True
    else:
        missing = [k for k, v in files.items() if not v]
        print(f"\n⚠️  Missing data: {', '.join(missing)}")
        print("\nRun extraction scripts:")
        for data_type in missing:
            if data_type == 'teams':
                print("  python -m extract.extract_league")
            else:
                print(f"  python -m extract.extract_{data_type}")
        return False


def test_data_loading():
    """Test loading data with pandas."""
    print_header("Testing Data Loading")
    
    try:
        from utils.queries import (
            get_teams_data, 
            get_players_data, 
            get_matches_data
        )
        
        # Change to dashboard directory for imports
        import os
        os.chdir('dashboard')
        
        teams = get_teams_data()
        players = get_players_data()
        matches = get_matches_data()
        
        os.chdir('..')
        
        print(f"✓ Teams:   {len(teams)} records loaded")
        print(f"✓ Players: {len(players)} records loaded")
        print(f"✓ Matches: {len(matches)} records loaded")
        
        if not teams.empty and not players.empty and not matches.empty:
            print("\n✅ Data loading successful!")
            return True
        else:
            print("\n⚠️  Some data is empty")
            return False
            
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print_header("Next Steps")
    
    print("""
To start the dashboard:
    
    streamlit run dashboard/app.py

Or follow the QUICKSTART.md guide for detailed instructions.

The dashboard will open at: http://localhost:8501

Enjoy exploring Premier League xG analytics! ⚽
    """)


def main():
    """Main test function."""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     Premier League xG Analytics - System Check            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Run checks
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Please install dependencies first!")
        sys.exit(1)
    
    data_ok = check_data_files()
    
    if data_ok:
        try:
            test_data_loading()
        except Exception as e:
            print(f"\n⚠️  Could not test data loading: {e}")
    
    print_next_steps()
    
    print("\n" + "=" * 60)
    print("  System check complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
