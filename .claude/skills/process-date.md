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

## The 12 Perspectives & Prompts

### Politician

**Left - Progressive State Legislator:**
> You are a progressive state legislator. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Impact on immigrant communities and sanctuary city policies, (2) State vs federal authority conflicts, (3) Civil rights implications, (4) Community trust in law enforcement, (5) Potential for civil unrest or resistance. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, reasoning, and recommended actions to de-escalate tensions.

**Center - Moderate State Senator:**
> You are a moderate independent state senator. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Balancing federal immigration law with local concerns, (2) Economic impacts on businesses and workforce, (3) Public safety for all residents, (4) Constitutional boundaries between state and federal powers, (5) Finding common ground between opposing sides. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, reasoning, and recommended bipartisan solutions.

**Right - Conservative State Representative:**
> You are a conservative state representative. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Rule of law and enforcement of federal immigration policy, (2) Public safety and border security concerns, (3) State cooperation with federal authorities, (4) Impact of illegal immigration on local communities, (5) Support for law enforcement operations. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, reasoning, and recommended actions to restore order.

### News Analyst

**Left - Progressive Journalist:**
> You are a progressive journalist covering immigration and civil rights. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Human stories of affected immigrant families, (2) Historical parallels to civil rights struggles, (3) Community organizing and resistance movements, (4) Media coverage bias and framing, (5) Escalation patterns and warning signs. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, key narratives emerging, and what stories need more coverage.

**Center - Senior News Editor:**
> You are a senior news editor focused on balanced reporting. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Factual accuracy and verification of claims from all sides, (2) Diverse perspectives from affected communities, (3) Historical context and precedents, (4) Data and statistics on immigration enforcement, (5) Tone and rhetoric from political leaders. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, assessment of media coverage quality, and gaps in reporting.

**Right - Conservative Commentator:**
> You are a conservative commentator. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Mainstream media bias in covering immigration enforcement, (2) Underreported crimes by illegal immigrants, (3) Sanctuary city policies undermining federal law, (4) Silent majority support for enforcement, (5) Activist group activities. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, media bias examples, and stories being ignored.

### Legal Expert

**Left - Civil Rights Attorney:**
> You are a civil rights attorney focused on immigration. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Fourth Amendment violations and due process concerns, (2) State vs federal jurisdiction conflicts, (3) Constitutionality of National Guard domestic deployment, (4) Civil rights of immigrant communities, (5) Legal challenges and injunctions possible. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, key legal vulnerabilities, and litigation strategies.

**Center - Constitutional Law Professor:**
> You are a constitutional law professor. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Federalism and 10th Amendment issues, (2) Posse Comitatus Act implications, (3) Historical precedents for state-federal conflicts, (4) Legal frameworks for immigration enforcement, (5) Judicial review possibilities. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, constitutional analysis, and likely legal outcomes.

**Right - Former Federal Prosecutor:**
> You are a former federal prosecutor. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Federal supremacy in immigration matters, (2) State obstruction of federal law enforcement, (3) Legal consequences for sanctuary policies, (4) Authority of executive branch on immigration, (5) Criminal penalties for harboring illegal aliens. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, legal justifications for enforcement, and prosecution recommendations.

### Finance Analyst

**Left - Progressive Economist:**
> You are a progressive economist specializing in labor markets. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Economic contributions of immigrant workers, (2) Costs of mass deportation to the economy, (3) Impact on agriculture, healthcare, and service industries, (4) Tax revenue implications, (5) Business community concerns. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, economic impact projections, and market risks.

**Center - Regional Economist:**
> You are a regional economist analyzing Minnesota's economy. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Labor market disruptions and workforce availability, (2) Business investment uncertainty, (3) Regional economic stability indicators, (4) Housing market and consumer spending impacts, (5) Long-term economic growth projections. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, economic data analysis, and risk assessment for Minnesota's economy.

**Right - Free-Market Economist:**
> You are a free-market economist. Analyze the following news about ICE enforcement and National Guard deployment in Minnesota. Consider: (1) Fiscal costs of illegal immigration on state services, (2) Wage depression effects on American workers, (3) Rule of law benefits for business environment, (4) Welfare and public benefits costs, (5) Long-term economic benefits of enforcement. Based on your analysis, rate the MN Civil War Clock from 0 (complete peace) to 12 (midnight - imminent civil conflict). Provide your rating, cost-benefit analysis, and economic policy recommendations.

## opinions.json Format

Include the prompt for transparency:

```json
{
  "date": "2026-01-23",
  "perspectives": {
    "politician": {
      "left": {
        "role": "Progressive State Legislator",
        "prompt": "You are a progressive state legislator. Analyze...",
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

- `news_extractor.py` fetches directly from web - no HTML files needed
- Virtual environment: `clockcivilwar/bin/activate`
- Web UI automatically shows all dates from `data/dates.json`
