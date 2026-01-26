#!/usr/bin/env python3
"""
Generate 12 perspective opinions using Claude API.
Usage: python generate_opinions.py [DATE]
Example: python generate_opinions.py 2025-01-23

Requires ANTHROPIC_API_KEY environment variable.
"""

import json
import os
import sys
import re
from datetime import datetime

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed.")
    print("Run: pip install anthropic")
    sys.exit(1)

TARGET_DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = TARGET_DATE
NEWS_FILE = os.path.join(OUTPUT_DIR, "news_results.json")
PROMPTS_FILE = os.path.join(OUTPUT_DIR, "analysis_prompts.json")
ANALYSIS_FILE = os.path.join(OUTPUT_DIR, "civil_war_clock_analysis.md")
OPINIONS_FILE = os.path.join(OUTPUT_DIR, "opinions.json")


def load_news():
    """Load news results."""
    if not os.path.exists(NEWS_FILE):
        print(f"Error: {NEWS_FILE} not found.")
        return None
    with open(NEWS_FILE, "r") as f:
        return json.load(f)


def load_prompts():
    """Load analysis prompts."""
    if not os.path.exists(PROMPTS_FILE):
        print(f"Error: {PROMPTS_FILE} not found.")
        return None
    with open(PROMPTS_FILE, "r") as f:
        return json.load(f)


def format_news_context(news_data):
    """Format news headlines for the prompt context."""
    lines = [f"# News Headlines for {TARGET_DATE}\n"]

    for region in ["minnesota_local", "us_national"]:
        region_title = "MINNESOTA LOCAL" if region == "minnesota_local" else "US NATIONAL"
        lines.append(f"\n## {region_title}\n")

        region_data = news_data.get(region, {})
        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            leaning_title = leaning.replace("_", " ").title()
            lines.append(f"\n### {leaning_title}\n")

            sources = region_data.get(leaning, [])
            for source in sources:
                name = source.get("name", "Unknown")
                articles = source.get("articles", [])
                for article in articles[:5]:  # Limit per source
                    headline = article.get("headline", "")
                    if headline:
                        lines.append(f"- [{name}] {headline}")

    return "\n".join(lines)


def get_opinion(client, prompt, role, news_context):
    """Get a single opinion from Claude."""
    full_prompt = f"""Based on the following news about Minnesota ICE enforcement and state-federal tensions:

{news_context}

---

{prompt}

Please provide your analysis in the following JSON format:
{{
    "clock_rating": <number 0-12>,
    "confidence": <number 0-100>,
    "key_factors": ["factor1", "factor2", "factor3"],
    "reasoning": "<your detailed reasoning>",
    "recommendations": ["recommendation1", "recommendation2"],
    "one_line_summary": "<one sentence summary of your view>"
}}

Respond ONLY with the JSON, no other text."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )

        response_text = message.content[0].text.strip()

        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"  Warning: Could not parse JSON response")
            return None

    except Exception as e:
        print(f"  Error: {e}")
        return None


def generate_all_opinions(news_data, prompts_data):
    """Generate opinions for all 12 perspectives."""
    client = anthropic.Anthropic()

    news_context = format_news_context(news_data)
    perspectives = prompts_data.get("perspectives", {})

    results = {
        "date": TARGET_DATE,
        "generated_at": datetime.now().isoformat(),
        "perspectives": {}
    }

    leaning_map = {
        "left_wing": "left",
        "centrist": "center",
        "right_wing": "right"
    }

    total = sum(len(leanings) for leanings in perspectives.values())
    current = 0

    for perspective_name, leanings in perspectives.items():
        print(f"\n=== {perspective_name.upper()} ===")
        results["perspectives"][perspective_name] = {}

        for leaning_key, data in leanings.items():
            current += 1
            role = data.get("role", "Unknown")
            prompt = data.get("prompt", "")

            print(f"  [{current}/{total}] {leaning_key}: {role}")

            opinion = get_opinion(client, prompt, role, news_context)

            if opinion:
                leaning_short = leaning_map.get(leaning_key, leaning_key)
                results["perspectives"][perspective_name][leaning_short] = {
                    "role": role,
                    "rating": opinion.get("clock_rating", 0),
                    "confidence": opinion.get("confidence", 50),
                    "key_factors": opinion.get("key_factors", []),
                    "reasoning": opinion.get("reasoning", ""),
                    "recommendations": opinion.get("recommendations", []),
                    "summary": opinion.get("one_line_summary", "")
                }
                print(f"    Rating: {opinion.get('clock_rating', '?')}/12")
            else:
                print(f"    Failed to get opinion")

    return results


def calculate_summary(results):
    """Calculate summary statistics from opinions."""
    perspectives = results.get("perspectives", {})

    all_ratings = []
    matrix = {}

    for persp_name, leanings in perspectives.items():
        matrix[persp_name] = {}
        for leaning, data in leanings.items():
            rating = data.get("rating", 0)
            matrix[persp_name][leaning] = rating
            all_ratings.append(rating)

        ratings = [d.get("rating", 0) for d in leanings.values()]
        matrix[persp_name]["avg"] = round(sum(ratings) / len(ratings), 1) if ratings else 0

    # Calculate averages by leaning
    left_ratings = [p.get("left", {}).get("rating", 0) if isinstance(p.get("left"), dict) else p.get("left", 0)
                    for p in perspectives.values()]
    center_ratings = [p.get("center", {}).get("rating", 0) if isinstance(p.get("center"), dict) else p.get("center", 0)
                      for p in perspectives.values()]
    right_ratings = [p.get("right", {}).get("rating", 0) if isinstance(p.get("right"), dict) else p.get("right", 0)
                     for p in perspectives.values()]

    # Fix: extract ratings properly
    left_ratings = []
    center_ratings = []
    right_ratings = []

    for persp_name, leanings in perspectives.items():
        if "left" in leanings:
            left_ratings.append(leanings["left"].get("rating", 0))
        if "center" in leanings:
            center_ratings.append(leanings["center"].get("rating", 0))
        if "right" in leanings:
            right_ratings.append(leanings["right"].get("rating", 0))

    matrix["averages"] = {
        "left": round(sum(left_ratings) / len(left_ratings), 1) if left_ratings else 0,
        "center": round(sum(center_ratings) / len(center_ratings), 1) if center_ratings else 0,
        "right": round(sum(right_ratings) / len(right_ratings), 1) if right_ratings else 0,
        "overall": round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else 0
    }

    # Polarization index (std dev of ratings)
    if all_ratings:
        mean = sum(all_ratings) / len(all_ratings)
        variance = sum((r - mean) ** 2 for r in all_ratings) / len(all_ratings)
        polarization = round(variance ** 0.5, 2)
    else:
        polarization = 0

    return {
        "matrix": matrix,
        "polarization_index": polarization,
        "overall_rating": matrix["averages"]["overall"],
        "all_ratings": all_ratings
    }


def save_results(results, summary):
    """Save opinions to JSON file."""
    results["summary"] = summary

    with open(OPINIONS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nOpinions saved to: {OPINIONS_FILE}")


def main():
    """Main function."""
    print("=" * 60)
    print(f"Generating Opinions for {TARGET_DATE}")
    print("=" * 60)

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    news_data = load_news()
    if not news_data:
        sys.exit(1)

    prompts_data = load_prompts()
    if not prompts_data:
        sys.exit(1)

    results = generate_all_opinions(news_data, prompts_data)
    summary = calculate_summary(results)
    save_results(results, summary)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Overall Rating: {summary['overall_rating']}/12")
    print(f"Polarization Index: {summary['polarization_index']}")
    print(f"Left Avg: {summary['matrix']['averages']['left']}/12")
    print(f"Center Avg: {summary['matrix']['averages']['center']}/12")
    print(f"Right Avg: {summary['matrix']['averages']['right']}/12")
    print("=" * 60)


if __name__ == "__main__":
    main()
