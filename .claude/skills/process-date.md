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
└── ...

Individual Date Folders (source data)
├── 2026-01-23/
│   ├── news_results.json
│   ├── opinions.json
│   ├── news_summary.md
│   └── analysis_prompts.json
└── ...
```

## Arguments

- `DATE` - Target date in YYYY-MM-DD format (e.g., 2026-01-23)

## Workflow Steps

### 1. Extract News

```bash
source /Users/convez/claude/clockcivilwar/clockcivilwar/bin/activate
python3 news_extractor.py DATE
```

Fetches from 18 news sources and creates `DATE/news_results.json` and `DATE/analysis_prompts.json`.

### 2. Generate News Summary

```bash
python3 analyze_results.py DATE
```

Creates `DATE/news_summary.md`.

### 3. Generate 12 AI Opinions

**Interactive (in Claude Code chat):**
- Read `DATE/news_results.json`
- Generate 12 opinions (4 perspectives × 3 political leanings)
- Save to `DATE/opinions.json`

### 4. Generate Web Data

```bash
python3 generate_web_data.py
```

Reads all date folders → Creates `data/DATE.json` → Updates `data/dates.json`

### 5. Git Commit & Push

```bash
git add DATE/ data/
git commit -m "Add DATE data with AI-generated opinions"
git push
```

## One-Liner

```bash
source clockcivilwar/bin/activate && python3 news_extractor.py DATE && python3 analyze_results.py DATE
```

Then generate opinions interactively, then:
```bash
python3 generate_web_data.py && git add DATE/ data/ && git commit -m "Add DATE data" && git push
```

## Date Folder Structure

```
DATE/
├── news_results.json       # Extracted articles from 18 sources
├── analysis_prompts.json   # 12 perspective prompts
├── news_summary.md         # Formatted news summary
└── opinions.json           # AI-generated 12 opinions
```

## The 12 Perspectives

| Role | Left | Center | Right |
|------|------|--------|-------|
| **Politician** | Progressive State Legislator | Moderate State Senator | Conservative State Representative |
| **News Analyst** | Progressive Journalist | Senior News Editor | Conservative Commentator |
| **Legal Expert** | Civil Rights Attorney | Constitutional Law Professor | Former Federal Prosecutor |
| **Finance Analyst** | Progressive Economist | Regional Economist | Free-Market Economist |

See `analysis_prompts_template.json` for the full prompts.

## opinions.json Format

Include the prompt for transparency:

```json
{
  "date": "2026-01-23",
  "generated_at": "2026-01-23T12:00:00.000000",
  "perspectives": {
    "politician": {
      "left": {
        "role": "Progressive State Legislator",
        "prompt": "You are a progressive state legislator. Analyze...",
        "rating": 10,
        "confidence": 95,
        "key_factors": ["Factor 1", "Factor 2", "Factor 3"],
        "reasoning": "Detailed reasoning...",
        "recommendations": ["Action 1", "Action 2"],
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
    "matrix": {
      "politician": {"left": 10, "center": 8, "right": 5, "avg": 7.7},
      "news_analyst": {"left": 9, "center": 7, "right": 5, "avg": 7.0},
      "legal_expert": {"left": 9, "center": 7, "right": 4, "avg": 6.7},
      "finance_analyst": {"left": 8, "center": 6, "right": 4, "avg": 6.0},
      "averages": {"left": 9.0, "center": 7.0, "right": 4.5, "overall": 6.83}
    },
    "key_events": [
      "Major event 1",
      "Major event 2",
      "Major event 3"
    ]
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

- `news_extractor.py` fetches directly from web - no HTML files needed
- Virtual environment: `clockcivilwar/bin/activate`
- Web UI automatically shows all dates from `data/dates.json`

## Fixing/Updating Existing Dates

To fix an existing date's opinions.json (e.g., wrong format, missing fields):

1. Read the existing `DATE/opinions.json` or a neighboring date's file as reference
2. Read `DATE/news_results.json` for news context
3. Regenerate opinions with correct format and save to `DATE/opinions.json`
4. Run steps 4-5 (generate_web_data.py, git commit & push)
