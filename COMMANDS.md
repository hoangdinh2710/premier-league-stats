# Premier League xG Analytics - Command Reference

## 📥 Data Extraction Commands

### Extract Team Statistics
```bash
python -m extract.extract_league
```
- Duration: ~5 seconds
- Output: `data/raw/teams_YYYYMMDD.json`
- Contains: Team standings, goals, xG, xGA, points

### Extract Player Statistics
```bash
python -m extract.extract_players
```
- Duration: ~5 seconds
- Output: `data/raw/players_YYYYMMDD.json`
- Contains: Player goals, xG, assists, shots, conversion rates

### Extract Match Results
```bash
python -m extract.extract_matches
```
- Duration: ~5 seconds
- Output: `data/raw/matches_YYYYMMDD.json`
- Contains: Match results, scores, xG for both teams

### Extract Shot Data
```bash
python -m extract.extract_shots
```
- Duration: 5-10 minutes (rate limited)
- Output: `data/raw/shots_YYYYMMDD.json`
- Contains: Individual shot locations, xG values, results

### Extract All Data (Recommended)
```bash
python -m extract.extract_league && python -m extract.extract_players && python -m extract.extract_matches && python -m extract.extract_shots
```

---

## 🗄️ Database Commands (Optional)

### Load All Data to Supabase
```bash
python -m load.load_to_supabase
```
- Requires: `.env` file with Supabase credentials
- Loads all recent JSON files to database tables

---

## 🎨 Dashboard Commands

### Start Dashboard
```bash
streamlit run dashboard/app.py
```
- Opens browser at: `http://localhost:8501`
- Use sidebar to navigate between pages

### Start on Different Port
```bash
streamlit run dashboard/app.py --server.port 8502
```

### Start Without Auto-Open
```bash
streamlit run dashboard/app.py --server.headless true
```

---

## 🔧 Utility Commands

### Check System Setup
```bash
python check_setup.py
```
- Verifies dependencies installed
- Checks for data files
- Tests data loading

### Install/Update Dependencies
```bash
pip install -r requirements.txt
```

### Upgrade All Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

---

## 📊 Common Workflows

### First-Time Setup
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Extract data (quick)
python -m extract.extract_league
python -m extract.extract_players
python -m extract.extract_matches

# 4. Start dashboard
streamlit run dashboard/app.py
```

### Weekly Update
```bash
# 1. Activate environment
venv\Scripts\activate

# 2. Extract fresh data
python -m extract.extract_league
python -m extract.extract_players
python -m extract.extract_matches

# 3. (Optional) Update shots
python -m extract.extract_shots

# 4. Restart dashboard
streamlit run dashboard/app.py
```

### Full Data Refresh
```bash
# Extract everything from scratch
python -m extract.extract_league
python -m extract.extract_players
python -m extract.extract_matches
python -m extract.extract_shots

# Load to Supabase (if using)
python -m load.load_to_supabase

# Start dashboard
streamlit run dashboard/app.py
```

---

## 🐛 Debugging Commands

### Check Python Version
```bash
python --version
# Should be 3.11 or higher
```

### List Installed Packages
```bash
pip list
```

### Check Port Usage (Windows)
```bash
netstat -ano | findstr :8501
```

### Check Port Usage (macOS/Linux)
```bash
lsof -i :8501
```

### Test Individual Module
```bash
python -c "from extract.extract_league import extract_team_data; print(extract_team_data())"
```

---

## 📁 File Management

### View Recent Data Files
```bash
# Windows PowerShell
Get-ChildItem data\raw\*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 10

# Windows CMD
dir /od data\raw\*.json

# macOS/Linux
ls -lt data/raw/*.json | head -10
```

### Clean Old Data Files
```bash
# Keep only most recent files (manual - review before deleting)
# Windows: Manually delete older files from data/raw/
# Linux/macOS: Consider using find command with -mtime
```

---

## 🚀 Pro Tips

1. **Chain commands** with `&&` for sequential execution
2. **Background tasks**: Use `&` (Linux/macOS) or start separate terminals (Windows)
3. **Save time**: Skip shot extraction for quick updates
4. **Automate**: Create batch/shell scripts for regular updates
5. **Version control**: Keep extraction logs to track data freshness

---

## 📚 Additional Resources

- Full documentation: `README.md`
- Quick start: `QUICKSTART.md`
- Project spec: `claude_code_spec.md`
- Check setup: `python check_setup.py`

---

**For help, run: `streamlit run dashboard/app.py --help`**
