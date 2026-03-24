---
name: research-synthesizer
description: Multi-source research with auto-synthesis, contradiction detection, and source quality scoring. Use when researching topics across multiple sources, comparing approaches, or needing synthesized findings from scattered information.
---

# Research Synthesizer

Synthesize information from multiple sources with quality assessment and contradiction detection.

## When to Use

- "Research X for me"
- Comparing multiple approaches
- Information scattered across sources
- Need to reconcile conflicting information
- Evaluating source credibility

## Workflow

### Phase 1: Source Collection

Gather from multiple sources:
- Web search
- Documentation
- Code repositories
- Academic papers
- Previous conversations

Tag each source:
```markdown
| Source | Type | Reliability | Date |
|--------|------|-------------|------|
| docs.openclaw.ai | Official | High | 2026-03 |
| stackoverflow.com | Community | Medium | 2026-02 |
| blog.example.com | Personal | Low | 2025-08 |
```

### Phase 2: Synthesis

Extract key points from each source:

```markdown
## Findings

### From Source A (High reliability):
- Point 1 with evidence
- Point 2 with evidence

### From Source B (Medium reliability):
- Point 3 with caveat
- Point 4 (conflicts with Source A on X)
```

### Phase 3: Contradiction Detection

Flag conflicts:

```markdown
⚠️ CONTRADICTION
**Topic:** Solana transaction finality

- Source A (docs.solana.com): "400ms finality"
- Source B (blog): "Sometimes 2-5 seconds"

**Analysis:** 
- Source A is official docs - more reliable
- Source B may refer to worst-case or specific conditions
- Likely both true under different conditions

**Resolve:** Ask clarifying question or note condition differences
```

### Phase 4: Quality Assessment

Score each finding:

| Finding | Sources | Reliability | Confidence |
|---------|---------|-------------|------------|
| Jupiter supports v6 API | 3 (docs, code, blog) | High | 95% |
| Best practice is X | 1 (opinion) | Low | 40% |

### Phase 5: Final Synthesis

Deliver structured findings:

```markdown
# Research: Solana DEX Aggregators

## High Confidence Findings
1. Jupiter is the largest aggregator by volume ✓
   - Source: Multiple + DeFiLlama data
2. V6 API has better latency than V4 ✓
   - Source: Official docs + benchmarks

## Medium Confidence Findings
3. Orca has lower fees for small trades ~
   - Source: Community comparison, needs verification

## Contradictions Noted
- Fee structure varies by source (see details above)

## Recommendations
1. Use Jupiter V6 API for new projects
2. Benchmark Orca vs Jupiter for your specific size
3. Check current fee structures as they change frequently
```

## Source Quality Tiers

| Tier | Examples | Trust Level |
|------|----------|-------------|
| Official | docs, github repo, official blog | High |
| Established | stackoverflow, reputable blogs | Medium |
| Community | reddit, small blogs, comments | Low |
| Deprecated | outdated docs, old posts | Verify date |

## Commands

| Task | Action |
|------|--------|
| Research topic | Gather 3+ sources, synthesize, deliver |
| Compare X vs Y | Structured comparison with trade-offs |
| Verify claim | Cross-check against reliable sources |
| Find consensus | Show where sources agree/disagree |

## Output Templates

### Quick Research
```markdown
# Quick Research: [Topic]

**Time spent:** X minutes  
**Sources:** N (list key ones)

## Key Finding
[One paragraph summary]

## Details
- Point 1 (source)
- Point 2 (source)
- Contradiction noted on X

## Confidence: High/Medium/Low
```

### Deep Research
```markdown
# Deep Research: [Topic]

## Executive Summary
[3 bullet points]

## Detailed Findings
[Section per finding]

## Source Analysis
[Table with reliability]

## Uncertainties & Gaps
[What's unclear or needs more research]

## Recommendations
[Actionable next steps]
```
