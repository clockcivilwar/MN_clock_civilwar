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

# 3. Generate 12 AI opinions using 3 independent passes
# Pass 1: Analyze news from LEFT perspective (4 roles)
# Pass 2: Analyze news from CENTER perspective (4 roles)
# Pass 3: Analyze news from RIGHT perspective (4 roles)
# Each pass is independent — leanings may diverge on the same events
# Save to DATE/opinions.json

# 4. Generate web data
python3 generate_web_data.py

# 5. Git commit & push
git add DATE/ data/
git commit -m "Add DATE data"
git push
```

## Pipeline Scripts

| Script | Output |
|--------|--------|
| `news_extractor.py DATE` | `news_results.json`, `analysis_prompts.json` |
| `analyze_results.py DATE` | `news_summary.md` |
| `generate_web_data.py` | `data/*.json` |

## 12 Perspectives (4 roles × 3 leanings)

- **Politician:** Progressive State Legislator, Moderate State Senator, Conservative State Representative
- **News Analyst:** Progressive Journalist, Senior News Editor, Conservative Commentator
- **Legal Expert:** Civil Rights Attorney, Constitutional Law Professor, Former Federal Prosecutor
- **Finance Analyst:** Progressive Economist, Regional Economist, Free-Market Economist

Note: Include the prompt in opinions.json for transparency (no institution names in roles).

### Three-Pass Methodology

Opinions are generated in **three independent analytical passes** to ensure the left/center/right trend lines can diverge:

1. **LEFT pass:** Analyze all news through progressive lens — 4 left-leaning roles rate independently
2. **CENTER pass:** Analyze all news through balanced lens — 4 centrist roles rate independently
3. **RIGHT pass:** Analyze all news through conservative lens — 4 right-leaning roles rate independently

This prevents the common bias of all leanings moving in lockstep. The same event can push different leanings in opposite directions (e.g., a Fox poll showing ICE disapproval might lower center ratings but raise right ratings due to political anxiety).

### News Sources (20)

## Clock Scale

| Rating | Status |
|--------|--------|
| 0-2 | PEACEFUL |
| 3-4 | ELEVATED |
| 5-6 | HIGH |
| 7-8 | SEVERE |
| 9-10 | CRITICAL |
| 11-12 | MIDNIGHT |

**MN Local:** MinnPost, MN Reformer, Sahan Journal, Star Tribune, Pioneer Press, MPR News, Alpha News, American Experiment, MN Sun

**National:** MSNBC, CNN, NY Times, AP News, Reuters, PBS, Fox News, Daily Wire, NY Post

**Government:** Department of Justice, Supreme Court
