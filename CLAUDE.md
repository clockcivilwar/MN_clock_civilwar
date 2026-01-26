# Minnesota Civil War Clock

Real-time tension tracking system monitoring state-federal conflicts in Minnesota on a 0-12 scale.

## Architecture

```
Unified Web UI (index.html)
    ↓ reads
data/
├── dates.json      # Index of available dates
└── {date}.json     # Web-ready data per date

Source Data (per date folder)
{date}/
├── news_results.json      # Extracted articles
├── opinions.json          # AI-generated 12 opinions
├── news_summary.md
└── analysis_prompts.json
```

## Process a New Date

See detailed docs: `.claude/skills/process-date.md`

```bash
# 1. Activate venv
source clockcivilwar/bin/activate

# 2. Extract news & generate summary
python3 news_extractor.py DATE
python3 analyze_results.py DATE

# 3. Generate 12 AI opinions (interactive in chat)
# Save to DATE/opinions.json

# 4. Generate web data
python3 generate_web_data.py
```

## Pipeline Scripts

| Script | Output |
|--------|--------|
| `news_extractor.py DATE` | `news_results.json`, `analysis_prompts.json` |
| `analyze_results.py DATE` | `news_summary.md` |
| `generate_web_data.py` | `data/*.json` |

## 12 Perspectives (4 roles × 3 leanings)

- **Politician:** Progressive Democrat, Moderate Independent, Conservative Republican
- **News Analyst:** Progressive Journalist, Senior Editor, Conservative Commentator
- **Legal Expert:** ACLU Attorney, Law Professor, Former Federal Prosecutor
- **Finance Analyst:** Progressive Economist, Fed Economist, Free-Market Economist

## Clock Scale

| Rating | Status |
|--------|--------|
| 0-2 | PEACEFUL |
| 3-4 | ELEVATED |
| 5-6 | HIGH |
| 7-8 | SEVERE |
| 9-10 | CRITICAL |
| 11-12 | MIDNIGHT |

## News Sources (18)

**MN Local:** MinnPost, MN Reformer, Sahan Journal, Star Tribune, Pioneer Press, MPR News, Alpha News, American Experiment, MN Sun

**National:** MSNBC, CNN, NY Times, AP News, Reuters, PBS, Fox News, Daily Wire, NY Post
