# CV Rewriter Pipeline
# Quick execution script

cd "$(dirname "$0")"

echo "=== CV Rewriting Service ==="
echo ""

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <cv_file.txt> <job_description.txt> [company_name]"
    echo ""
    echo "Example:"
    echo "  $0 my_cv.txt job_posting.txt 'Tech Corp'"
    exit 1
fi

CV_FILE="$1"
JOB_FILE="$2"
COMPANY="${3:-Target Company}"
OUTPUT_DIR="./output"

mkdir -p "$OUTPUT_DIR"

echo "Step 1/4: Analyzing CV..."
python3 cv_analyzer.py --input "$CV_FILE" --output "$OUTPUT_DIR/cv_analysis.json"
echo "✓ CV analysis complete"
echo ""

echo "Step 2/4: Researching company..."
python3 company_researcher.py --company "$COMPANY" --output "$OUTPUT_DIR/company_data.json"
echo "✓ Company research complete"
echo ""

echo "Step 3/4: ATS optimization..."
python3 ats_optimizer.py --cv "$OUTPUT_DIR/cv_analysis.json" --job "$JOB_FILE" \
    --output "$OUTPUT_DIR/ats_report.json"
echo "✓ ATS optimization complete"
echo ""

echo "Step 4/4: Generating output..."
python3 output_generator.py --input "$OUTPUT_DIR/cv_analysis.json" \
    --output-dir "$OUTPUT_DIR" --name optimized_cv
echo "✓ Output generation complete"
echo ""

echo "=== Done! ==="
echo ""
echo "Output files:"
ls -la "$OUTPUT_DIR/"
echo ""
echo "View ATS report: cat $OUTPUT_DIR/ats_report.json"
