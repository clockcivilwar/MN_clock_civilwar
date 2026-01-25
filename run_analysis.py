#!/usr/bin/env python3
"""
Run Civil War Clock analysis from multiple perspectives.
Uses the news data and prompts to generate analysis.

Usage: python run_analysis.py [DATE]
"""

import json
import os
import sys
from datetime import datetime

TARGET_DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = TARGET_DATE
NEWS_FILE = os.path.join(OUTPUT_DIR, "news_results.json")
PROMPTS_FILE = os.path.join(OUTPUT_DIR, "analysis_prompts.json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "civil_war_clock_analysis.md")


def load_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def extract_headlines(news_data, max_per_source=5):
    """Extract top headlines from news results."""
    headlines = {
        "minnesota_local": {"left_leaning": [], "centrist": [], "right_leaning": []},
        "us_national": {"left_leaning": [], "centrist": [], "right_leaning": []}
    }

    for region in ["minnesota_local", "us_national"]:
        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            for source in news_data.get(region, {}).get(leaning, []):
                source_name = source.get("name", "Unknown")
                for article in source.get("articles", [])[:max_per_source]:
                    headlines[region][leaning].append({
                        "source": source_name,
                        "headline": article.get("headline", ""),
                        "url": article.get("url", ""),
                        "relevance": article.get("relevance", "medium")
                    })

    return headlines


def format_headlines_for_prompt(headlines):
    """Format headlines as text for inclusion in prompts."""
    lines = []

    for region in ["minnesota_local", "us_national"]:
        region_title = "MINNESOTA LOCAL" if region == "minnesota_local" else "US NATIONAL"
        lines.append(f"\n=== {region_title} NEWS ===\n")

        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            leaning_title = leaning.replace("_", " ").title()
            lines.append(f"\n--- {leaning_title} Sources ---")

            for item in headlines[region][leaning]:
                relevance_marker = "🔴" if item["relevance"] == "high" else "○"
                lines.append(f"{relevance_marker} [{item['source']}] {item['headline']}")

    return "\n".join(lines)


def generate_analysis_template(prompts, headlines_text):
    """Generate markdown template for manual or AI analysis."""
    lines = []

    lines.append("# Minnesota Civil War Clock Analysis")
    lines.append(f"\n**Date:** {TARGET_DATE}")
    lines.append(f"**Analysis Framework:** Multi-perspective assessment")
    lines.append("\n---\n")

    # Clock scale reference
    lines.append("## Clock Scale Reference\n")
    for level, desc in prompts["output_format"]["clock_interpretation"].items():
        lines.append(f"- **{level}**: {desc}")

    lines.append("\n---\n")

    # News summary
    lines.append("## News Headlines Analyzed\n")
    lines.append(headlines_text)

    lines.append("\n---\n")

    # Analysis sections
    for role_key, role_data in prompts["perspectives"].items():
        role_title = role_key.replace("_", " ").title()
        lines.append(f"\n## {role_title} Perspectives\n")

        for leaning, perspective in role_data.items():
            leaning_title = leaning.replace("_", " ").title()
            lines.append(f"\n### {leaning_title}: {perspective['role']}\n")
            lines.append(f"**Prompt:** {perspective['prompt']}\n")
            lines.append("\n**Analysis:**\n")
            lines.append("```")
            lines.append("Clock Rating: __/12")
            lines.append("Confidence: __%")
            lines.append("")
            lines.append("Key Factors:")
            lines.append("1. ")
            lines.append("2. ")
            lines.append("3. ")
            lines.append("")
            lines.append("Reasoning:")
            lines.append("[Your analysis here]")
            lines.append("")
            lines.append("Recommendations:")
            lines.append("1. ")
            lines.append("2. ")
            lines.append("```")
            lines.append("")

    # Summary table
    lines.append("\n---\n")
    lines.append("## Summary Matrix\n")
    lines.append("| Perspective | Left Wing | Centrist | Right Wing | Average |")
    lines.append("|-------------|-----------|----------|------------|---------|")
    lines.append("| Politician  |    /12    |    /12   |    /12     |   /12   |")
    lines.append("| News Analyst|    /12    |    /12   |    /12     |   /12   |")
    lines.append("| Legal Expert|    /12    |    /12   |    /12     |   /12   |")
    lines.append("| Finance     |    /12    |    /12   |    /12     |   /12   |")
    lines.append("| **Average** |  **/12**  | **/12**  |  **/12**   |**/12**  |")

    lines.append("\n---\n")
    lines.append("## Consensus Assessment\n")
    lines.append("**Overall Clock Rating:** __/12\n")
    lines.append("**Trend:** ⬆️ Rising / ➡️ Stable / ⬇️ Falling\n")
    lines.append("**Key Drivers:**\n")
    lines.append("1. \n2. \n3. \n")
    lines.append("\n**Critical Watch Items:**\n")
    lines.append("- \n- \n- \n")

    return "\n".join(lines)


def main():
    print(f"Generating Civil War Clock Analysis for {TARGET_DATE}")

    # Check files exist
    if not os.path.exists(NEWS_FILE):
        print(f"Error: {NEWS_FILE} not found. Run news_extractor.py first.")
        return

    if not os.path.exists(PROMPTS_FILE):
        print(f"Error: {PROMPTS_FILE} not found.")
        return

    # Load data
    news_data = load_json(NEWS_FILE)
    prompts = load_json(PROMPTS_FILE)

    # Extract and format headlines
    headlines = extract_headlines(news_data)
    headlines_text = format_headlines_for_prompt(headlines)

    # Generate analysis template
    analysis = generate_analysis_template(prompts, headlines_text)

    # Save
    with open(OUTPUT_FILE, "w") as f:
        f.write(analysis)

    print(f"Analysis template saved to: {OUTPUT_FILE}")
    print("\nYou can now:")
    print("1. Fill in the analysis manually")
    print("2. Use the prompts with an AI to generate each perspective's analysis")
    print("3. Import into a collaborative document for team analysis")


if __name__ == "__main__":
    main()
