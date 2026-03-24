#!/bin/bash
# Quick reconnaissance script
# Usage: ./recon.sh target.com

if [ -z "$1" ]; then
    echo "Usage: ./recon.sh <target.com>"
    exit 1
fi

TARGET=$1
OUTPUT_DIR="targets/$TARGET-$(date +%Y%m%d)"
mkdir -p $OUTPUT_DIR

echo "=========================================="
echo "🐛 Starting recon for: $TARGET"
echo "=========================================="
echo "Output: $OUTPUT_DIR"
echo ""

# Check if tools exist
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "⚠️  Warning: $1 not found. Install with instructions in INSTALL.md"
        return 1
    fi
    return 0
}

# Subdomain enumeration
echo "[*] Finding subdomains..."
if check_tool subfinder; then
    subfinder -d $TARGET -o $OUTPUT_DIR/subdomains_subfinder.txt 2>/dev/null
fi

if check_tool assetfinder; then
    assetfinder --subs-only $TARGET > $OUTPUT_DIR/subdomains_assetfinder.txt 2>/dev/null
fi

# Combine results
if [ -f "$OUTPUT_DIR/subdomains_subfinder.txt" ] || [ -f "$OUTPUT_DIR/subdomains_assetfinder.txt" ]; then
    cat $OUTPUT_DIR/subdomains_*.txt 2>/dev/null | sort -u > $OUTPUT_DIR/subdomains.txt
    echo "    Found: $(wc -l < $OUTPUT_DIR/subdomains.txt) subdomains"
else
    echo "    No subdomain tools available. Add manually to $OUTPUT_DIR/subdomains.txt"
    touch $OUTPUT_DIR/subdomains.txt
fi

# Probe for live hosts
echo "[*] Probing for live hosts..."
if check_tool httpx; then
    cat $OUTPUT_DIR/subdomains.txt | httpx -o $OUTPUT_DIR/live_hosts.txt -silent 2>/dev/null
    echo "    Live: $(wc -l < $OUTPUT_DIR/live_hosts.txt) hosts"
else
    echo "    httpx not available. Using manual list."
    cp $OUTPUT_DIR/subdomains.txt $OUTPUT_DIR/live_hosts.txt
fi

# Wayback URLs
echo "[*] Fetching URLs from Wayback Machine..."
if check_tool waybackurls; then
    cat $OUTPUT_DIR/live_hosts.txt | waybackurls > $OUTPUT_DIR/wayback_urls.txt 2>/dev/null
    echo "    Wayback: $(wc -l < $OUTPUT_DIR/wayback_urls.txt) URLs"
else
    echo "    waybackurls not available. Skipping."
    touch $OUTPUT_DIR/wayback_urls.txt
fi

# Katana crawl
echo "[*] Crawling discovered hosts..."
if check_tool katana; then
    cat $OUTPUT_DIR/live_hosts.txt | katana -o $OUTPUT_DIR/katana_urls.txt -silent 2>/dev/null
    echo "    Crawled: $(wc -l < $OUTPUT_DIR/katana_urls.txt) URLs"
else
    echo "    katana not available. Skipping."
    touch $OUTPUT_DIR/katana_urls.txt
fi

# Combine and dedupe URLs
echo "[*] Combining URL sources..."
cat $OUTPUT_DIR/wayback_urls.txt $OUTPUT_DIR/katana_urls.txt 2>/dev/null | sort -u > $OUTPUT_DIR/all_urls.txt
echo "    Total unique: $(wc -l < $OUTPUT_DIR/all_urls.txt) URLs"

# Extract interesting URLs
echo "[*] Extracting interesting endpoints..."
grep -E "\.(php|asp|aspx|jsp|json|xml|yaml|yml|config|env|git|svn|bak|old|backup|swp|sql|db|sqlite)" $OUTPUT_DIR/all_urls.txt > $OUTPUT_DIR/interesting_urls.txt 2>/dev/null || true
grep -E "(api|admin|login|register|upload|download|config|setup|install|test|dev|staging)" $OUTPUT_DIR/all_urls.txt >> $OUTPUT_DIR/interesting_urls.txt 2>/dev/null || true
sort -u $OUTPUT_DIR/interesting_urls.txt -o $OUTPUT_DIR/interesting_urls.txt 2>/dev/null || touch $OUTPUT_DIR/interesting_urls.txt
echo "    Interesting: $(wc -l < $OUTPUT_DIR/interesting_urls.txt) URLs"

# Extract parameters
echo "[*] Extracting URLs with parameters..."
grep "?" $OUTPUT_DIR/all_urls.txt > $OUTPUT_DIR/urls_with_params.txt 2>/dev/null || touch $OUTPUT_DIR/urls_with_params.txt
echo "    With params: $(wc -l < $OUTPUT_DIR/urls_with_params.txt) URLs"

echo ""
echo "=========================================="
echo "✅ Recon complete!"
echo "=========================================="
echo ""
echo "Results in: $OUTPUT_DIR"
echo "  - Subdomains: $(wc -l < $OUTPUT_DIR/subdomains.txt)"
echo "  - Live hosts: $(wc -l >/dev/null < $OUTPUT_DIR/live_hosts.txt 2>/dev/null || echo 0)"
echo "  - All URLs: $(wc -l >/dev/null < $OUTPUT_DIR/all_urls.txt 2>/dev/null || echo 0)"
echo "  - Interesting: $(wc -l >/dev/null < $OUTPUT_DIR/interesting_urls.txt 2>/dev/null || echo 0)"
echo ""
echo "Next steps:"
echo "  1. Review interesting URLs: cat $OUTPUT_DIR/interesting_urls.txt"
echo "  2. Check for XSS: ./scripts/check_xss.sh $OUTPUT_DIR/urls_with_params.txt"
echo "  3. Manual testing with Burp Suite"
echo ""
