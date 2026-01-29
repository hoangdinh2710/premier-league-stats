---
title: "I Built a Premier League Analytics Dashboard to See Which Teams Are Actually Good"
date: 2026-01-28
tags: [python, data-engineering, sports-analytics, streamlit, postgresql, etl]
description: "How I built an end-to-end data pipeline and interactive dashboard to analyze Premier League Expected Goals (xG) data - and what the numbers revealed about who's really performing"
---

# I Built a Premier League Analytics Dashboard to See Which Teams Are Actually Good

You know that feeling when your team wins 1-0 and everyone's celebrating, but deep down you know they got absolutely battered and survived on vibes alone? That's basically why Expected Goals (xG) exists - and why I built this project.

I wanted to create something that combined my love for football with my data engineering skills. The result: a full ETL pipeline that pulls Premier League data, transforms it through multiple layers, and serves it up in an interactive dashboard where you can actually *see* which teams are lucky and which ones are genuinely clinical.

<!-- IMAGE: Dashboard home page showing season overview -->

## What Even Is xG?

Quick primer if you're not familiar: Expected Goals (xG) measures the quality of a scoring chance. A penalty? That's about 0.76 xG. A header from 18 yards? Maybe 0.03 xG. Add up all a team's chances, and you get how many goals they *should* have scored based on historical data.

The gap between actual goals and xG tells you a lot. Consistently outperforming xG? You've got a clinical finisher (or an unsustainable hot streak). Underperforming? Either bad luck or genuinely poor finishing.

## The Architecture: Four Layers of Data Goodness

I built this using a **medallion architecture** - fancy term for organizing data in progressive layers, each cleaner than the last.

<!-- IMAGE: Architecture diagram showing Extract → Bronze Stage → Bronze Prod → Silver → Dashboard -->

### Layer 1: Extract

Everything starts with the Understat API. I wrote separate extraction modules for different data types:

- **Teams** - league-wide statistics
- **Players** - individual performance metrics
- **Matches** - game results and xG breakdowns
- **Shots** - the granular stuff: every shot with X/Y coordinates and xG values
- **Rosters** - who played, how long, what they contributed

The shot data is the most interesting (and the most demanding). I'm pulling every single shot from every match, complete with pitch coordinates. Rate limiting was essential here - 1 second between requests to play nice with the API.

```python
# Each match gets its own shot extraction
for match in matches:
    shots = client.get_match_shots(match_id)
    time.sleep(1)  # Be a good API citizen
```

### Layer 2: Bronze Stage (Landing Zone)

Raw JSON hits a staging area first. I use a simple TRUNCATE + INSERT strategy here - blow away the old staging data and load fresh. This is just a temporary holding pen.

### Layer 3: Bronze Prod (The Source of Truth)

Here's where it gets interesting. I merge the staged data into production tables using UPSERT (INSERT ... ON CONFLICT DO UPDATE). This means I can:

- Run the pipeline repeatedly without duplicating data
- Preserve historical records while updating changed ones
- Handle partial failures gracefully

```sql
INSERT INTO bronze_prod.prod_shots (id, match_id, player, xg, result, ...)
VALUES (...)
ON CONFLICT (id) DO UPDATE SET ...
```

### Layer 4: Silver (Analytics-Ready)

The final transformation layer builds proper dimensional models:

- **Dimension tables**: Teams, Players (the "who")
- **Fact tables**: Matches, Shots, Player Stats (the "what happened")

This is where I cast JSONB fields to proper types, calculate derived metrics, and structure everything for fast dashboard queries.

## The Dashboard: Where the Fun Happens

I built the frontend with Streamlit because I wanted something interactive without wrestling with JavaScript. Five pages, each answering different questions:

<!-- IMAGE: League table comparison - actual vs xG standings -->

### 1. League Table (The Reality Check)

Side-by-side comparison: where teams actually sit vs. where xG says they should be. Green highlighting for overperformers, red for teams living on borrowed time.

This is the "are they actually good?" page. When a team is 5th in the real table but 12th in xG... that's a red flag for sustainability.

### 2. Team Analysis

Deep dives into individual teams. How has their xG trended over the season? Are they creating better chances lately or just grinding out results?

### 3. Shot Maps (My Personal Favorite)

<!-- IMAGE: Shot map showing pitch visualization with xG-colored dots -->

Interactive pitch visualizations showing every shot a team has taken. Filter by:
- Team
- Shot result (goal, saved, blocked, missed)
- Situation (open play, set piece, counter)

You can immediately see patterns. Some teams pepper the box with high-quality chances. Others are taking low-percentage shots from distance. The visual difference is striking.

### 4. Player Stats

Scatter plots of Goals vs. xG to find the clinical finishers. Players above the diagonal line are outperforming their chances. Below? They're leaving goals on the table.

This page answered my burning question: "Is [insert striker] actually good or just getting good service?" The data doesn't lie.

### 5. Match Analysis

Drilling into individual games. Great for settling pub arguments about whether that 2-1 win was deserved or daylight robbery.

## What I Actually Learned (The Insights)

Building the pipeline was one thing. Using it revealed some genuinely interesting patterns:

**The xG Table Never Lies (Eventually)**: Teams riding luck early in the season tend to regress. The mid-season xG table is often a better predictor of final standings than the actual table.

**Shot Location > Shot Volume**: Teams taking 20 shots from outside the box aren't creating - they're just shooting. Quality beats quantity every time in the xG world.

**Set Pieces Are Underrated**: Some teams generate a huge chunk of their xG from corners and free kicks. It's a real, repeatable skill - not luck.

## Tech Stack Rundown

For the technically curious:

- **Python 3.11** - the whole pipeline
- **PostgreSQL via Supabase** - managed database, generous free tier
- **psycopg2 with connection pooling** - direct DB access for bulk operations
- **Streamlit** - dashboard framework
- **Plotly** - interactive visualizations

I went with direct Postgres connections over Supabase's REST API for the bulk loading. Way faster when you're inserting thousands of shot records.

## What I'd Do Differently

A few lessons for next time:

1. **Add proper logging from day one** - debugging pipeline failures is painful without it
2. **Consider dbt for transformations** - my SQL files work, but dbt's testing and documentation would be nice
3. **Build in data quality checks** - automated validation between layers

## Try It Yourself

The dashboard is live and the code is on GitHub. Pull it down, point it at your own Supabase instance, and you've got your own Premier League analytics platform.

Whether you're a football fan who wants data-backed opinions, a data engineer curious about pipeline patterns, or a recruiter wondering if I can actually build things - this project should answer your questions.

<!-- IMAGE: GitHub repo card or demo link -->

---

*Built with Python, PostgreSQL, Streamlit, and an unreasonable amount of opinions about football.*
