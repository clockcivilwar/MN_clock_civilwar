#!/usr/bin/env python3
"""
News Extractor Script
Extracts news about Minnesota, ICE, and National Guard from various sources.
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import os
import sys
import shutil

# Configuration
TARGET_DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
KEYWORDS = ["ICE", "Immigration and Customs Enforcement", "National Guard", "immigration", "deportation"]
STATE_KEYWORDS = ["Minnesota", "MN", "Minneapolis", "St. Paul"]
OUTPUT_DIR = TARGET_DATE
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "news_results.json")
PROMPTS_TEMPLATE = "analysis_prompts_template.json"
PROMPTS_OUTPUT = os.path.join(OUTPUT_DIR, "analysis_prompts.json")
TIMEOUT = 15

# Headers to mimic browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def load_sources(filepath="source.json"):
    """Load news sources from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def fetch_page(url):
    """Fetch a webpage and return BeautifulSoup object."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def extract_articles(soup, base_url):
    """Extract article links and headlines from a page."""
    articles = []

    if soup is None:
        return articles

    # Common article selectors
    selectors = [
        "article",
        ".article",
        ".story",
        ".post",
        ".news-item",
        ".headline",
        "h2 a",
        "h3 a",
        ".card",
        ".teaser",
    ]

    seen_urls = set()

    for selector in selectors:
        elements = soup.select(selector)
        for elem in elements:
            # Find links within the element
            links = elem.find_all("a", href=True) if elem.name != "a" else [elem]

            for link in links:
                href = link.get("href", "")
                text = link.get_text(strip=True)

                # Skip empty or navigation links
                if not text or len(text) < 10:
                    continue

                # Make absolute URL
                if href.startswith("/"):
                    href = base_url.rstrip("/") + href
                elif not href.startswith("http"):
                    continue

                if href in seen_urls:
                    continue
                seen_urls.add(href)

                articles.append({
                    "headline": text[:200],
                    "url": href
                })

    return articles


def filter_relevant_articles(articles):
    """Filter articles that mention keywords."""
    relevant = []

    for article in articles:
        headline_lower = article["headline"].lower()
        url_lower = article["url"].lower()
        combined = headline_lower + " " + url_lower

        # Check for state keywords
        has_state = any(kw.lower() in combined for kw in STATE_KEYWORDS)

        # Check for topic keywords
        has_topic = any(kw.lower() in combined for kw in KEYWORDS)

        if has_state and has_topic:
            article["relevance"] = "high"
            relevant.append(article)
        elif has_topic:
            article["relevance"] = "medium"
            relevant.append(article)

    return relevant


def build_search_url(base_url, source_name):
    """Build search URL for different news sites."""
    query = "Minnesota ICE National Guard"
    encoded_query = requests.utils.quote(query)

    # Site-specific search patterns
    search_patterns = {
        "startribune.com": f"{base_url}/search/?query={encoded_query}",
        "twincities.com": f"{base_url}/search/{encoded_query}/",
        "minnpost.com": f"{base_url}/?s={encoded_query}",
        "mprnews.org": f"{base_url}/search?query={encoded_query}",
        "minnesotareformer.com": f"{base_url}/?s={encoded_query}",
        "sahanjournal.com": f"{base_url}/?s={encoded_query}",
        "alphanews.org": f"{base_url}/?s={encoded_query}",
        "americanexperiment.org": f"{base_url}/?s={encoded_query}",
        "cnn.com": f"https://www.cnn.com/search?q={encoded_query}",
        "msnbc.com": f"https://www.msnbc.com/search/?q={encoded_query}",
        "nytimes.com": f"https://www.nytimes.com/search?query={encoded_query}",
        "apnews.com": f"https://apnews.com/search?q={encoded_query}",
        "reuters.com": f"https://www.reuters.com/search/news?blob={encoded_query}",
        "pbs.org": f"https://www.pbs.org/newshour/search-results?q={encoded_query}",
        "foxnews.com": f"https://www.foxnews.com/search-results/search?q={encoded_query}",
        "dailywire.com": f"https://www.dailywire.com/search?query={encoded_query}",
        "nypost.com": f"https://nypost.com/search/{encoded_query}/",
    }

    for domain, search_url in search_patterns.items():
        if domain in base_url:
            return search_url

    # Default: try common search patterns
    return f"{base_url}/search?q={encoded_query}"


def scrape_source(source):
    """Scrape a single news source."""
    name = source["name"]
    url = source["url"]

    print(f"\nProcessing: {name}")
    print(f"  URL: {url}")

    results = {
        "name": name,
        "url": url,
        "articles": [],
        "search_url": None,
        "status": "success",
        "error": None
    }

    # Try homepage first
    print("  Fetching homepage...")
    soup = fetch_page(url)
    if soup:
        articles = extract_articles(soup, url)
        relevant = filter_relevant_articles(articles)
        results["articles"].extend(relevant)
        print(f"  Found {len(relevant)} relevant articles on homepage")

    # Try search page
    search_url = build_search_url(url, name)
    results["search_url"] = search_url
    print(f"  Trying search: {search_url}")

    time.sleep(1)  # Rate limiting

    soup = fetch_page(search_url)
    if soup:
        articles = extract_articles(soup, url)
        relevant = filter_relevant_articles(articles)

        # Avoid duplicates
        existing_urls = {a["url"] for a in results["articles"]}
        new_articles = [a for a in relevant if a["url"] not in existing_urls]
        results["articles"].extend(new_articles)
        print(f"  Found {len(new_articles)} additional articles from search")

    if not results["articles"]:
        results["status"] = "no_results"

    return results


def main():
    """Main function to run the news extractor."""
    print("=" * 60)
    print(f"News Extractor - Minnesota ICE/National Guard Coverage")
    print(f"Target Date: {TARGET_DATE}")
    print(f"Output Directory: {OUTPUT_DIR}/")
    print("=" * 60)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Copy prompts template to date folder
    if os.path.exists(PROMPTS_TEMPLATE):
        with open(PROMPTS_TEMPLATE, "r") as f:
            prompts = json.load(f)
        prompts["meta"]["date"] = TARGET_DATE
        with open(PROMPTS_OUTPUT, "w") as f:
            json.dump(prompts, f, indent=2)
        print(f"Prompts copied to: {PROMPTS_OUTPUT}")

    # Load sources
    sources = load_sources()

    all_results = {
        "extraction_date": datetime.now().isoformat(),
        "target_date": TARGET_DATE,
        "keywords": KEYWORDS,
        "state_keywords": STATE_KEYWORDS,
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

    # Process each category
    for region in ["minnesota_local", "us_national"]:
        print(f"\n{'='*60}")
        print(f"Region: {region.upper()}")
        print("=" * 60)

        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            print(f"\n--- {leaning.replace('_', ' ').title()} ---")

            for source in sources[region][leaning]:
                result = scrape_source(source)
                all_results[region][leaning].append(result)
                time.sleep(2)  # Rate limiting between sources

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print("=" * 60)

    # Summary
    total_articles = 0
    for region in ["minnesota_local", "us_national"]:
        for leaning in ["left_leaning", "centrist", "right_leaning"]:
            for source in all_results[region][leaning]:
                total_articles += len(source["articles"])

    print(f"\nTotal relevant articles found: {total_articles}")


if __name__ == "__main__":
    main()
