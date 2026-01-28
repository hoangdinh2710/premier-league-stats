# 🚀 Quick Start Guide

Get up and running with the Premier League xG Analytics Dashboard in minutes!

## ⚡ Fast Track (5 minutes)

### Step 1: Setup Environment
```bash
# Activate virtual environment (if not already active)
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Extract Data
```bash
# Extract all data (takes about 1 minute total, excluding shots)
python -m extract.extract_league
python -m extract.extract_players
python -m extract.extract_matches

# Optional: Extract shots (takes 5-10 minutes due to rate limiting)
# python -m extract.extract_shots
```

### Step 3: Run Dashboard
```bash
streamlit run dashboard/app.py
```

Your browser will open at `http://localhost:8501` with the dashboard! 🎉

---

## 📊 What You'll See

Without shot data, you'll have access to:
- ✅ League Table with actual vs xG standings
- ✅ Team Analysis with performance metrics
- ✅ Player Statistics and efficiency analysis
- ✅ Match Analysis (without shot maps)

With shot data extraction:
- ✅ Full Shot Maps visualization
- ✅ Complete Match Analysis with shot locations

---

## 🎯 First Time Using?

### Recommended Exploration Path:

1. **Start at Home** - See the season overview
2. **Check League Table** - Spot over/underperforming teams
3. **Pick Your Team** - Analyze detailed team performance
4. **Explore Players** - Find clinical finishers vs wasteful shooters
5. **Review Matches** - See if results matched expectations

---

## 🔧 Troubleshooting

### "No data available" error?
- Make sure you've run the extraction scripts
- Check that `data/raw/` contains JSON files
- Look for files like `teams_20240126.json`

### Dashboard won't start?
```bash
# Check if port 8501 is in use
netstat -ano | findstr :8501  # Windows
# lsof -i :8501  # macOS/Linux

# Use different port
streamlit run dashboard/app.py --server.port 8502
```

### Import errors?
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 💡 Pro Tips

1. **Extract shots last**: They take longest but aren't required for most features
2. **Update regularly**: Premier League is live - extract new data weekly
3. **Compare over time**: Keep old JSON files to track trends
4. **Filter intelligently**: Use minimum games filter in Player Stats for meaningful data

---

## 🎓 Learn More

- Check `README.md` for full documentation
- See `claude_code_spec.md` for project specification
- Explore the code - it's well commented!

---

**Ready to dive into Premier League analytics? Let's go! ⚽**
