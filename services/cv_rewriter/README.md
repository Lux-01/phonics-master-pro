# CV Rewriting Service

A complete CV/Résumé rewriting and optimization service built with OpenClaw skills.

## Features

1. **CV Analysis** (`cv_analyzer.py`)
   - Extract structured data from CV text
   - Identify skills, experience, education, achievements
   - Parse contact information

2. **Company Research** (`company_researcher.py`)
   - Research target company data
   - Match CV to company needs
   - Extract job requirements

3. **ATS Optimization** (`ats_optimizer.py`)
   - Analyze job postings for keywords
   - Match CV to job requirements
   - Generate optimization recommendations
   - Check ATS compatibility

4. **Output Generation** (`output_generator.py`)
   - Generate polished CVs in multiple formats:
     - Markdown
     - Plain text (ATS-optimized)
     - HTML

## Quick Start

### 1. Analyze Your CV

```bash
cd /home/skux/.openclaw/workspace/services/cv_rewriter

python3 cv_analyzer.py --input your_cv.txt --output cv_data.json
```

### 2. Research Target Company

```bash
python3 company_researcher.py --company "Tech Corp" --job "Senior Developer" \
    --output company_data.json
```

### 3. Optimize for Job Posting

```bash
python3 ats_optimizer.py --cv cv_data.json --job job_posting.txt \
    --output ats_report.json
```

### 4. Generate Optimized CV

```bash
python3 output_generator.py --input cv_data.json --output-dir ./output \
    --name optimized_cv
```

## Complete Workflow

```bash
# Step 1: Extract CV data
python3 cv_analyzer.py -i my_cv.txt -o cv_analysis.json

# Step 2: Research the company
python3 company_researcher.py -c "Target Company" -j "Job Title" -o company.json

# Step 3: Analyze job match
python3 ats_optimizer.py -cv cv_analysis.json -job job_description.txt \
    -o ats_analysis.json

# Step 4: Generate all formats
python3 output_generator.py -i cv_analysis.json -o ./output -n final_cv
```

## Output Files

After running the complete workflow, you'll have:

| File | Description |
|------|-------------|
| `output/final_cv.md` | Markdown format (GitHub, Markdown editors) |
| `output/final_cv.txt` | Plain text (ATS-optimized) |
| `output/final_cv.html` | HTML format (web display, conversion to PDF) |
| `ats_analysis.json` | Job match report with recommendations |

## ATS Optimization Tips

Based on the `ats_optimizer.py` analysis:

1. **Use Standard Headers**
   - "Experience" not "Work History"
   - "Education" not "Academic Background"
   - "Skills" not "Core Competencies"

2. **Include Keywords**
   - Review job posting for required skills
   - Add matching keywords naturally
   - Use both acronyms and full names ("AI" and "Artificial Intelligence")

3. **Format for ATS**
   - Use .docx or .pdf with selectable text
   - Avoid tables, images, and graphics
   - Use standard fonts (Arial, Calibri, Times New Roman)
   - No headers/footers

4. **Quantify Achievements**
   - "Increased revenue by 25%"
   - "Managed team of 10 developers"
   - "Reduced costs by $50,000"

## Revenue Model

This service can generate income through:

| Option | Price | Notes |
|--------|-------|-------|
| Basic CV Review | $50-75 | Analysis + recommendations |
| Full Rewrite | $150-250 | Complete rewrite + optimization |
| Package (CV + LinkedIn) | $300-400 | Includes LinkedIn optimization |
| Executive Service | $500-750 | Multiple rounds + interview prep |

## Integration with Skills

This service leverages:
- **AWB** (Autonomous Workflow Builder) - automates the pipeline
- **SIL** (Sensory Input Layer) - company research
- **Stealth Browser** - web scraping for company data
- **ATS Skill** - keyword optimization

## Future Enhancements

- [ ] LinkedIn profile optimization
- [ ] Cover letter generation
- [ ] Interview preparation based on CV
- [ ] Portfolio website generation
- [ ] Multi-language support

## Files

| File | Purpose |
|------|---------|
| `cv_analyzer.py` | Extract CV data to structured JSON |
| `company_researcher.py` | Research companies and match CV |
| `ats_optimizer.py` | Optimize for ATS and job matching |
| `output_generator.py` | Generate final CV outputs |
| `README.md` | This file |

---

Built with OpenClaw ALOE ecosystem 🦞
