#!/usr/bin/env python3
"""
Analyze scraped news results and generate a summary report.
Usage: python analyze_results.py [DATE]
Example: python analyze_results.py 2026-01-25
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict

TARGET_DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = TARGET_DATE
RESULTS_FILE = os.path.join(OUTPUT_DIR, "news_results.json")
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "news_summary.md")


def load_results():
    """Load results from JSON file."""
    if not os.path.exists(RESULTS_FILE):
        print(f"Error: {RESULTS_FILE} not found.")
        print(f"Run: python news_extractor.py {TARGET_DATE}")
        return None

    with open(RESULTS_FILE, "r") as f:
        return json.load(f)


def generate_summary(results):
    """Generate a markdown summary of the results."""
    lines = []
    lines.append(f"# News Summary: Minnesota ICE/National Guard Coverage")
    lines.append(f"\n**Extraction Date:** {results.get('extraction_date', 'N/A')}")
    lines.append(f"**Target Date:** {results.get('target_date', 'N/A')}")
    lines.append(f"\n**Keywords:** {', '.join(results.get('keywords', []))}")
    lines.append(f"**State Keywords:** {', '.join(results.get('state_keywords', []))}")
    lines.append("\n---\n")

    total_articles = 0
    high_relevance = 0

    for region in ["minnesota_local", "us_national"]:
        region_title = "Minnesota Local Sources" if region == "minnesota_local" else "US National Sources"
        lines.append(f"\n## {region_title}\n")

        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            leaning_title = leaning.replace("_", " ").title()
            lines.append(f"\n### {leaning_title}\n")

            sources = results.get(region, {}).get(leaning, [])

            for source in sources:
                name = source.get("name", "Unknown")
                url = source.get("url", "")
                articles = source.get("articles", [])
                status = source.get("status", "unknown")

                lines.append(f"\n#### [{name}]({url})\n")
                lines.append(f"- **Status:** {status}")
                lines.append(f"- **Articles Found:** {len(articles)}")

                total_articles += len(articles)

                if articles:
                    lines.append("\n**Headlines:**\n")
                    for article in articles[:10]:  # Limit to 10 per source
                        headline = article.get("headline", "No headline")
                        article_url = article.get("url", "#")
                        relevance = article.get("relevance", "unknown")

                        if relevance == "high":
                            high_relevance += 1
                            lines.append(f"- 🔴 **[{headline}]({article_url})** (High relevance)")
                        else:
                            lines.append(f"- [{headline}]({article_url})")
                else:
                    lines.append("\n*No relevant articles found.*\n")

    # Summary stats
    lines.insert(7, f"\n**Total Articles Found:** {total_articles}")
    lines.insert(8, f"**High Relevance Articles:** {high_relevance}")

    return "\n".join(lines)


def print_quick_summary(results):
    """Print a quick console summary."""
    print("\n" + "=" * 60)
    print("QUICK SUMMARY")
    print("=" * 60)

    for region in ["minnesota_local", "us_national"]:
        region_title = "MINNESOTA LOCAL" if region == "minnesota_local" else "US NATIONAL"
        print(f"\n{region_title}")
        print("-" * 40)

        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            leaning_title = leaning.replace("_", " ").title()
            sources = results.get(region, {}).get(leaning, [])

            for source in sources:
                name = source.get("name", "Unknown")
                count = len(source.get("articles", []))
                status = "✓" if count > 0 else "✗"
                print(f"  {status} {name}: {count} articles")


def main():
    """Main function."""
    results = load_results()
    if not results:
        return

    # Print quick summary to console
    print_quick_summary(results)

    # Generate markdown summary
    summary = generate_summary(results)

    with open(SUMMARY_FILE, "w") as f:
        f.write(summary)

    print(f"\n{'=' * 60}")
    print(f"Full summary saved to: {SUMMARY_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
