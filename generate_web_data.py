#!/usr/bin/env python3
"""
Generate web-friendly JSON data from analysis files.
Updates data/dates.json and creates data/{date}.json for each date folder.

Usage: python generate_web_data.py
"""

import json
import os
import re
from datetime import datetime

DATA_DIR = "data"
DATES_FILE = os.path.join(DATA_DIR, "dates.json")


def find_date_folders():
    """Find all date folders (YYYY-MM-DD format)."""
    dates = []
    for item in os.listdir("."):
        if os.path.isdir(item) and re.match(r"^\d{4}-\d{2}-\d{2}$", item):
            # Check if it has required files
            if os.path.exists(os.path.join(item, "news_results.json")):
                dates.append(item)
    return sorted(dates)


def extract_clock_data(analysis_md):
    """Extract clock rating from analysis markdown."""
    # Default values
    clock = {
        "rating": 7,
        "status": "SEVERE",
        "trend": "Stable",
        "description": "Civil disobedience, enforcement conflicts"
    }

    # Try to extract from markdown
    lines = analysis_md.split("\n")
    for i, line in enumerate(lines):
        if "Overall Clock Rating:" in line:
            match = re.search(r"(\d+)/12", line)
            if match:
                clock["rating"] = int(match.group(1))

        if "Trend:" in line:
            if "Rising" in line:
                clock["trend"] = "Rising"
            elif "Falling" in line:
                clock["trend"] = "Falling"
            else:
                clock["trend"] = "Stable"

    # Set status based on rating
    if clock["rating"] <= 2:
        clock["status"] = "PEACEFUL"
        clock["description"] = "Normal political discourse"
    elif clock["rating"] <= 4:
        clock["status"] = "ELEVATED"
        clock["description"] = "Increased tensions, protests"
    elif clock["rating"] <= 6:
        clock["status"] = "HIGH"
        clock["description"] = "Significant confrontations, legal battles"
    elif clock["rating"] <= 8:
        clock["status"] = "SEVERE"
        clock["description"] = "Civil disobedience, enforcement conflicts"
    elif clock["rating"] <= 10:
        clock["status"] = "CRITICAL"
        clock["description"] = "Widespread unrest, potential violence"
    else:
        clock["status"] = "MIDNIGHT"
        clock["description"] = "Active civil conflict"

    return clock


def extract_events(analysis_md):
    """Extract key events from analysis markdown."""
    events = []
    in_events = False

    for line in analysis_md.split("\n"):
        if "Critical Incidents:" in line or "Key Events" in line:
            in_events = True
            continue
        if in_events:
            if line.startswith("---") or (line.startswith("##") and "Events" not in line):
                break
            if line.startswith("- **"):
                match = re.match(r"- \*\*(.+?)\*\*[:\s]*(.+)", line)
                if match:
                    events.append({
                        "title": match.group(1).strip(),
                        "description": match.group(2).strip()
                    })

    return events[:10]  # Limit to 10 events


def extract_news_for_web(news_results):
    """Convert news results to web-friendly format."""
    total_articles = 0
    web_news = {
        "total_articles": 0,
        "total_sources": 18,
        "minnesota_local": {
            "left_leaning": [],
            "centrist": [],
            "right_leaning": []
        },
        "us_national": {
            "left_leaning": [],
            "centrist": [],
            "right_leaning": []
        }
    }

    for region in ["minnesota_local", "us_national"]:
        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            sources = news_results.get(region, {}).get(leaning, [])
            for source in sources:
                article_count = len(source.get("articles", []))
                total_articles += article_count

                # Get top 3 articles
                top_articles = []
                for article in source.get("articles", [])[:3]:
                    top_articles.append({
                        "headline": article.get("headline", "")[:100],
                        "url": article.get("url", "")
                    })

                if top_articles:
                    web_news[region][leaning].append({
                        "name": source.get("name", "Unknown"),
                        "count": article_count,
                        "articles": top_articles
                    })

    web_news["total_articles"] = total_articles
    return web_news


def extract_analysis_matrix(analysis_md):
    """Extract analysis matrix from markdown."""
    matrix = {
        "politician": {"left": 9, "center": 7, "right": 6, "avg": 7.3},
        "news_analyst": {"left": 9, "center": 7, "right": 5, "avg": 7.0},
        "legal_expert": {"left": 9, "center": 7, "right": 4, "avg": 6.7},
        "finance_analyst": {"left": 8, "center": 6, "right": 4, "avg": 6.0},
        "averages": {"left": 8.75, "center": 6.75, "right": 4.75, "overall": 6.75}
    }

    # Try to extract from Summary Matrix section
    lines = analysis_md.split("\n")
    in_matrix = False

    for line in lines:
        if "| Politician" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                try:
                    matrix["politician"]["left"] = int(re.search(r"(\d+)", parts[1]).group(1))
                    matrix["politician"]["center"] = int(re.search(r"(\d+)", parts[2]).group(1))
                    matrix["politician"]["right"] = int(re.search(r"(\d+)", parts[3]).group(1))
                except:
                    pass
        elif "| News Analyst" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                try:
                    matrix["news_analyst"]["left"] = int(re.search(r"(\d+)", parts[1]).group(1))
                    matrix["news_analyst"]["center"] = int(re.search(r"(\d+)", parts[2]).group(1))
                    matrix["news_analyst"]["right"] = int(re.search(r"(\d+)", parts[3]).group(1))
                except:
                    pass
        elif "| Legal Expert" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                try:
                    matrix["legal_expert"]["left"] = int(re.search(r"(\d+)", parts[1]).group(1))
                    matrix["legal_expert"]["center"] = int(re.search(r"(\d+)", parts[2]).group(1))
                    matrix["legal_expert"]["right"] = int(re.search(r"(\d+)", parts[3]).group(1))
                except:
                    pass
        elif "| Finance" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4:
                try:
                    matrix["finance_analyst"]["left"] = int(re.search(r"(\d+)", parts[1]).group(1))
                    matrix["finance_analyst"]["center"] = int(re.search(r"(\d+)", parts[2]).group(1))
                    matrix["finance_analyst"]["right"] = int(re.search(r"(\d+)", parts[3]).group(1))
                except:
                    pass

    # Calculate averages
    for key in ["politician", "news_analyst", "legal_expert", "finance_analyst"]:
        m = matrix[key]
        m["avg"] = round((m["left"] + m["center"] + m["right"]) / 3, 1)

    matrix["averages"]["left"] = round(sum(matrix[k]["left"] for k in ["politician", "news_analyst", "legal_expert", "finance_analyst"]) / 4, 2)
    matrix["averages"]["center"] = round(sum(matrix[k]["center"] for k in ["politician", "news_analyst", "legal_expert", "finance_analyst"]) / 4, 2)
    matrix["averages"]["right"] = round(sum(matrix[k]["right"] for k in ["politician", "news_analyst", "legal_expert", "finance_analyst"]) / 4, 2)
    matrix["averages"]["overall"] = round((matrix["averages"]["left"] + matrix["averages"]["center"] + matrix["averages"]["right"]) / 3, 2)

    return matrix


def generate_date_data(date_folder):
    """Generate web data for a specific date."""
    print(f"Processing {date_folder}...")

    # Load source files
    news_file = os.path.join(date_folder, "news_results.json")
    analysis_file = os.path.join(date_folder, "civil_war_clock_analysis.md")

    with open(news_file, "r") as f:
        news_results = json.load(f)

    analysis_md = ""
    if os.path.exists(analysis_file):
        with open(analysis_file, "r") as f:
            analysis_md = f.read()

    # Extract data
    clock = extract_clock_data(analysis_md)
    events = extract_events(analysis_md)
    news = extract_news_for_web(news_results)
    matrix = extract_analysis_matrix(analysis_md)

    # Build perspectives (simplified for web)
    perspectives = {
        "politician": {
            "left": {"rating": matrix["politician"]["left"], "role": "Progressive Democratic State Legislator from Minneapolis", "summary": "Federal occupation unprecedented. One more incident away from catastrophic violence."},
            "center": {"rating": matrix["politician"]["center"], "role": "Moderate Independent State Senator", "summary": "Extremely serious but not yet at point of no return. Cooler heads could prevail."},
            "right": {"rating": matrix["politician"]["right"], "role": "Conservative Republican Representative", "summary": "Unrest manufactured by radical left. Federal officers doing their lawful duty."}
        },
        "news_analyst": {
            "left": {"rating": matrix["news_analyst"]["left"], "role": "Progressive Journalist", "summary": "Defining story of the era. Federal government occupation of Minneapolis."},
            "center": {"rating": matrix["news_analyst"]["center"], "role": "Senior Editor", "summary": "Federal agencies stonewalling. Both sides have legitimate grievances."},
            "right": {"rating": matrix["news_analyst"]["right"], "role": "Conservative Commentator", "summary": "Mainstream media disinformation campaign against federal law enforcement."}
        },
        "legal_expert": {
            "left": {"rating": matrix["legal_expert"]["left"], "role": "ACLU Immigration Rights Attorney", "summary": "Constitutional crisis of the highest order. Lawlessness wearing a badge."},
            "center": {"rating": matrix["legal_expert"]["center"], "role": "Constitutional Law Professor", "summary": "Genuinely novel territory. Federal government likely prevails legally."},
            "right": {"rating": matrix["legal_expert"]["right"], "role": "Former Federal Prosecutor", "summary": "Immigration enforcement exclusively federal jurisdiction. Shooting justified."}
        },
        "finance_analyst": {
            "left": {"rating": matrix["finance_analyst"]["left"], "role": "Progressive Economist", "summary": "Economic damage severe. Could set Minnesota back a decade."},
            "center": {"rating": matrix["finance_analyst"]["center"], "role": "Federal Reserve Economist", "summary": "Meaningful but not severe impacts yet. Duration is key variable."},
            "right": {"rating": matrix["finance_analyst"]["right"], "role": "Free-Market Economist", "summary": "Market correction, not crisis. Enforcement creates level playing field."}
        }
    }

    # Build full data object
    data = {
        "date": date_folder,
        "clock": clock,
        "events": events if events else [
            {"title": "Data extraction", "description": "See full analysis for details"}
        ],
        "news": news,
        "analysis": {
            "polarization_index": round(matrix["averages"]["left"] - matrix["averages"]["right"], 1),
            "confidence_weighted_avg": round(matrix["averages"]["overall"], 1),
            "perspectives": perspectives,
            "matrix": matrix
        },
        "watch": {
            "escalation": [
                "Additional fatal incidents",
                "National Guard deployment",
                "Federal arrests of state officials",
                "Spread to other cities",
                "Counter-protests or militia involvement"
            ],
            "deescalation": [
                "Federal pause in operations",
                "Independent investigation",
                "Release of detained children",
                "Withdrawal of legal actions",
                "State-federal dialogue"
            ]
        }
    }

    return data


def main():
    """Main function."""
    print("Generating web data...")

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Find all date folders
    dates = find_date_folders()
    print(f"Found {len(dates)} date folders: {dates}")

    if not dates:
        print("No date folders found.")
        return

    # Generate data for each date
    for date in dates:
        data = generate_date_data(date)
        output_file = os.path.join(DATA_DIR, f"{date}.json")
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Created: {output_file}")

    # Update dates.json
    dates_data = {
        "available_dates": dates,
        "latest": dates[-1]  # Most recent
    }
    with open(DATES_FILE, "w") as f:
        json.dump(dates_data, f, indent=2)
    print(f"Updated: {DATES_FILE}")

    print("Done!")


if __name__ == "__main__":
    main()
