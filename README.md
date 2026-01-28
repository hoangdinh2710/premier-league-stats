# ⚽ Premier League xG Analytics Dashboard

A comprehensive data engineering portfolio project that extracts football (soccer) Expected Goals (xG) data from Understat, stores it in a database, and displays it in an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📊 Project Overview

This project demonstrates end-to-end data engineering skills by:
- **Extracting** Premier League data from Understat API
- **Loading** data to Supabase (PostgreSQL) database
- **Visualizing** insights through an interactive Streamlit dashboard
- **Analyzing** team and player performance using xG metrics

### What is xG?

Expected Goals (xG) is a statistical measure that quantifies the quality of goal-scoring chances. It helps identify:
- Teams/players performing above expectations (clinical finishing)
- Teams/players underperforming (wasteful shooting)
- Whether match results reflect the actual performance

---

## 🎯 Features

### Dashboard Pages

1. **🏆 League Table**
   - Compare actual standings vs xG-based projections
   - Identify over/underperforming teams
   - Color-coded performance indicators

2. **📈 Team Analysis**
   - Deep dive into individual team performance
   - Goals vs xG comparison charts
   - Match history and form analysis

3. **🎯 Shot Maps**
   - Visual shot location mapping on pitch
   - Color-coded by xG value
   - Filter by team, result, and situation

4. **⚡ Player Stats**
   - Top scorers and assisters
   - Clinical finishers vs wasteful shooters
   - Goals vs xG scatter plot analysis

5. **🔮 Match Analysis**
   - Individual match breakdowns
   - Did the right team win?
   - Shot maps for specific matches

---

## 🛠️ Tech Stack

- **Python 3.11+** - Core programming language
- **understatapi** - Data extraction from Understat
- **Supabase (PostgreSQL)** - Data storage
- **Streamlit** - Interactive dashboard
- **Plotly** - Data visualizations
- **Pandas** - Data manipulation
- **python-dotenv** - Environment variable management

---

## 📁 Project Structure

```
premier-league-stats/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── extract/
│   ├── __init__.py
│   ├── extract_league.py      # Extract team stats
│   ├── extract_players.py     # Extract player stats
│   ├── extract_matches.py     # Extract match results
│   └── extract_shots.py       # Extract shot-level data
│
├── load/
│   ├── __init__.py
│   └── load_to_supabase.py    # Load data to Supabase
│
├── dashboard/
│   ├── app.py                 # Main Streamlit app
│   ├── pages/
│   │   ├── 1_🏆_League_Table.py
│   │   ├── 2_📈_Team_Analysis.py
│   │   ├── 3_🎯_Shot_Maps.py
│   │   ├── 4_⚡_Player_Stats.py
│   │   └── 5_🔮_Match_Analysis.py
│   └── utils/
│       ├── __init__.py
│       ├── queries.py         # Data fetching utilities
│       └── charts.py          # Reusable chart components
│
└── data/
    └── raw/                   # Local JSON cache (gitignored)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- (Optional) Supabase account for database storage

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/premier-league-stats.git
   cd premier-league-stats
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (Optional - only for Supabase)
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

---

## 📥 Data Extraction

Extract data from Understat API:

```bash
# 1. Extract team data (fast - ~5 seconds)
python -m extract.extract_league

# 2. Extract player data (fast - ~5 seconds)
python -m extract.extract_players

# 3. Extract match data (fast - ~5 seconds)
python -m extract.extract_matches

# 4. Extract shot data (slow - 5-10 minutes due to rate limiting)
python -m extract.extract_shots
```

Data will be saved to `data/raw/` as JSON files with timestamps.

**Note:** Shot extraction takes longer because it makes one API call per match with 1-second delays to respect rate limits.

---

## 🗄️ Loading to Supabase (Optional)

If you want to use Supabase for data storage:

1. Create a Supabase project at https://supabase.com
2. Create the following tables in your Supabase database:
   - `raw_teams`
   - `raw_players`
   - `raw_matches`
   - `raw_shots`
3. Get your database connection string:
   - Go to **Project Settings > Database**
   - Find **Connection String** section
   - Copy the **Direct connection** string (URI format)
4. Add your credentials to `.env`:
   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```
   Or use individual parameters:
   ```
   DB_HOST=db.xxxxx.supabase.co
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your_database_password
   ```
5. Run the load script:
   ```bash
   python -m load.load_to_supabase
   ```

**Note:** The loader now uses direct Postgres connections for better ETL performance. The dashboard currently works with local JSON files, so Supabase is optional.

---

## 🎨 Running the Dashboard

Start the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Navigation

- Use the sidebar to navigate between pages
- Each page offers different analytical views
- Filters and selectors allow you to customize your analysis

---

## 📊 Data Details

### Season Format

Understat uses the starting year for seasons:
- 2024/25 season = "2024"
- 2023/24 season = "2023"

### Shot Coordinates

Shot locations use normalized coordinates (0 to 1):
- **X-axis**: 0 = own goal line, 1 = opponent goal line
- **Y-axis**: 0 = left touchline, 1 = right touchline
- Shot maps display the attacking half (X: 0.5 to 1)

### League Codes

- Premier League = "EPL"
- La Liga = "La_Liga"
- Bundesliga = "Bundesliga"
- Serie A = "Serie_A"
- Ligue 1 = "Ligue_1"

---

## 📈 Key Metrics Explained

### xG (Expected Goals)
Statistical measure of shot quality. A shot with 0.5 xG should be scored 50% of the time.

### xGA (Expected Goals Against)
Expected goals conceded based on the quality of chances allowed.

### G-xG (Goals minus xG)
- **Positive**: Clinical finishing (scoring more than expected)
- **Negative**: Wasteful finishing (scoring less than expected)

### Conversion Rate
Percentage of shots that result in goals.

---

## 🎯 Use Cases

### For Data Analysts
- Demonstrates ETL pipeline skills
- Shows data visualization capabilities
- Real-world sports analytics application

### For Football Fans
- Discover which teams are lucky/unlucky
- Identify clinical vs wasteful players
- Predict future performance trends

### For Recruiters
- End-to-end project showcasing multiple skills
- Clean, documented, production-ready code
- Modern data stack implementation

---

## 🔄 Updating Data

To refresh your data:

1. Run extraction scripts again (they append date to filenames)
2. The dashboard automatically uses the most recent files
3. Old data files remain in `data/raw/` for historical reference

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add dbt transformations for data modeling
- [ ] Implement GitHub Actions for scheduled updates
- [ ] Add more leagues (La Liga, Bundesliga, etc.)
- [ ] Create historical trend analysis
- [ ] Add team/player comparison features
- [ ] Implement ML predictions based on xG

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Data provided by [Understat](https://understat.com)
- Built with [Streamlit](https://streamlit.io)
- Visualizations powered by [Plotly](https://plotly.com)

---

## 📧 Contact

For questions or feedback, please open an issue or reach out via [your contact method].

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Built with ❤️ for football and data analytics**
