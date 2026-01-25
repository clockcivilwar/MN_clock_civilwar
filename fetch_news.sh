#!/bin/bash
# Quick news fetcher for Minnesota ICE/National Guard coverage
# Usage: ./fetch_news.sh [DATE]
# Example: ./fetch_news.sh 2026-01-25

DATE="${1:-$(date +%Y-%m-%d)}"
QUERY="Minnesota+ICE+National+Guard"
OUTPUT_DIR="$DATE"

mkdir -p "$OUTPUT_DIR"

echo "=================================================="
echo "Fetching news about Minnesota ICE/National Guard"
echo "Date: $DATE"
echo "=================================================="

# Function to fetch and save
fetch_source() {
    local name="$1"
    local url="$2"
    local output_file="$OUTPUT_DIR/$(echo "$name" | tr ' ' '_' | tr '[:upper:]' '[:lower:]').html"

    echo "Fetching: $name"
    curl -s -L -A "Mozilla/5.0" --max-time 15 "$url" -o "$output_file" 2>/dev/null

    if [ -f "$output_file" ]; then
        echo "  Saved to: $output_file"
    else
        echo "  Failed to fetch"
    fi
}

echo ""
echo "=== MINNESOTA LOCAL ==="

# Left-leaning
echo "--- Left Leaning ---"
fetch_source "MinnPost" "https://www.minnpost.com/?s=ICE+National+Guard"
fetch_source "Minnesota Reformer" "https://minnesotareformer.com/?s=ICE+National+Guard"
fetch_source "Sahan Journal" "https://sahanjournal.com/?s=ICE"

# Centrist
echo "--- Centrist ---"
fetch_source "Star Tribune" "https://www.startribune.com/search/?query=ICE+National+Guard"
fetch_source "Pioneer Press" "https://www.twincities.com/?s=ICE+National+Guard&orderby=date"
fetch_source "MPR News" "https://www.mprnews.org/search?query=ICE+National+Guard"

# Right-leaning
echo "--- Right Leaning ---"
fetch_source "Alpha News" "https://alphanews.org/?s=ICE+National+Guard"
fetch_source "American Experiment" "https://www.americanexperiment.org/?s=ICE"
fetch_source "Minnesota Sun" "https://theminnesotasun.com/?s=ICE"

echo ""
echo "=== US NATIONAL ==="

# Left-leaning
echo "--- Left Leaning ---"
fetch_source "MSNBC" "https://www.msnbc.com/search/?q=Minnesota+ICE+National+Guard"
fetch_source "CNN" "https://www.cnn.com/search?q=Minnesota+ICE+National+Guard"
fetch_source "NY Times" "https://www.nytimes.com/search?query=Minnesota+ICE+National+Guard"

# Centrist
echo "--- Centrist ---"
fetch_source "AP News" "https://apnews.com/search?q=Minnesota+ICE+National+Guard"
fetch_source "Reuters" "https://www.reuters.com/site-search/?query=Minnesota+ICE+National+Guard"
fetch_source "PBS NewsHour" "https://www.pbs.org/newshour/search-results?q=Minnesota+ICE+National+Guard"

# Right-leaning
echo "--- Right Leaning ---"
fetch_source "Fox News" "https://www.foxnews.com/search-results/search?q=Minnesota+ICE+National+Guard"
fetch_source "Daily Wire" "https://www.dailywire.com/search?query=Minnesota+ICE+National+Guard"
fetch_source "NY Post" "https://nypost.com/search/Minnesota+ICE+National+Guard/"

echo ""
echo "=================================================="
echo "Done! Raw HTML files saved to: $OUTPUT_DIR/"
echo "=================================================="
