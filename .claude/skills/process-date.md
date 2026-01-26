# Process Date for Civil War Clock

Process a new date for the Minnesota Civil War Clock tension tracking system.

## Overview

This skill fetches news, extracts articles, generates 12 AI opinions, and updates the unified web UI for a specific date. The clock tracks state-federal tensions on a 0-12 scale (midnight = civil conflict).

## Architecture

```
Unified Web UI (index.html + js/main.js)
    ↓ reads from
data/
├── dates.json          # Index of all available dates
├── 2026-01-23.json     # Web-ready data for each date
├── 2026-01-24.json
└── ...

Individual Date Folders (source data)
├── 2026-01-23/
│   ├── news_results.json
│   ├── opinions.json (or civil_war_clock_analysis.md)
│   ├── news_summary.md
│   └── analysis_prompts.json
└── 2026-01-24/
    └── ...
```

## Arguments

- `DATE` - Target date in YYYY-MM-DD format (e.g., 2026-01-23)

## Workflow Steps

### 1. Fetch & Extract News

```bash
source /Users/convez/claude/clockcivilwar/clockcivilwar/bin/activate
./fetch_news.sh DATE
python3 news_extractor.py DATE
```

Creates `DATE/news_results.json` and `DATE/analysis_prompts.json`.

### 2. Generate News Summary

```bash
python3 analyze_results.py DATE
```

Creates `DATE/news_summary.md`.

### 3. Generate 12 AI Opinions

**Option A: Interactive (in Claude Code chat)**
- Read `DATE/news_results.json` and `DATE/analysis_prompts.json`
- Generate 12 opinions (4 perspectives × 3 political leanings)
- Save to `DATE/opinions.json`

**Option B: API script (requires ANTHROPIC_API_KEY)**
```bash
python3 generate_opinions.py DATE
```

### 4. Clean Up Temp Files

```bash
rm -f DATE/*.html
```

### 5. Generate Web Data

```bash
python3 generate_web_data.py
```

Reads all date folders → Creates `data/DATE.json` → Updates `data/dates.json`

## Date Folder Structure

```
DATE/
├── news_results.json       # Extracted articles from 18 sources
├── analysis_prompts.json   # 12 perspective prompts
├── news_summary.md         # Formatted news summary
└── opinions.json           # AI-generated 12 opinions (preferred)
    OR
└── civil_war_clock_analysis.md  # Manual analysis (legacy)
```

## The 12 Perspectives

| Role | Left | Center | Right |
|------|------|--------|-------|
| **Politician** | Progressive Democrat | Moderate Independent | Conservative Republican |
| **News Analyst** | Progressive Journalist | Senior Editor | Conservative Commentator |
| **Legal Expert** | ACLU Attorney | Constitutional Law Professor | Former Federal Prosecutor |
| **Finance Analyst** | Progressive Economist | Fed Reserve Economist | Free-Market Economist |

## opinions.json Format

```json
{
  "date": "2026-01-23",
  "perspectives": {
    "politician": {
      "left": {
        "role": "Progressive Democratic State Legislator",
        "rating": 10,
        "confidence": 95,
        "key_factors": ["..."],
        "reasoning": "...",
        "recommendations": ["..."],
        "summary": "One-line summary"
      },
      "center": {...},
      "right": {...}
    },
    "news_analyst": {...},
    "legal_expert": {...},
    "finance_analyst": {...}
  },
  "summary": {
    "overall_rating": 7.42,
    "polarization_index": 2.67,
    "matrix": {...}
  }
}
```

## Clock Scale

| Rating | Status | Description |
|--------|--------|-------------|
| 0-2 | PEACEFUL | Normal political discourse |
| 3-4 | ELEVATED | Increased tensions, protests |
| 5-6 | HIGH | Significant confrontations, legal battles |
| 7-8 | SEVERE | Civil disobedience, enforcement conflicts |
| 9-10 | CRITICAL | Widespread unrest, potential violence |
| 11-12 | MIDNIGHT | Active civil conflict |

## News Sources (18 total)

**Minnesota Local (9):**
- Left: MinnPost, Minnesota Reformer, Sahan Journal
- Center: Star Tribune, Pioneer Press, MPR News
- Right: Alpha News, American Experiment, Minnesota Sun

**US National (9):**
- Left: MSNBC, CNN, NY Times
- Center: AP News, Reuters, PBS NewsHour
- Right: Fox News, Daily Wire, NY Post

## Notes

- HTML files are temporary - delete after extraction
- `generate_web_data.py` prefers `opinions.json` over `civil_war_clock_analysis.md`
- Virtual environment: `/Users/convez/claude/clockcivilwar/clockcivilwar/bin/activate`
- Web UI automatically shows all dates from `data/dates.json`
