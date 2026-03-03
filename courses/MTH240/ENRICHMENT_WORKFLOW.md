# AI Enrichment Verification Workflow

## Overview

Raw extraction → AI enrichment → Verification → Final output

## Step 1: Raw Extraction (Automated)

**Script:** `scripts/extract_raw.py`

**Extracts:**
- Document ID (year, semester, type, version)
- Structure (pages, marks, duration, question count)
- Questions (number, marks, has_subparts, raw_text)
- Solutions (present, provider, source)

**Output:** `processing/MTH240_{year}_{type}_{version}_raw.json`

## Step 2: AI Enrichment (Manual - Agent)

**Input:** Raw JSON + original PDF

**Agent uses template:** `templates/ai_enrichment_template.md`

**For each question, agent extracts:**

### Required Fields
- `question_number`: From raw extraction
- `total_marks`: From raw extraction
- `problem_statement`: Full LaTeX formatted problem
- `metadata.difficulty`: 1-5 rating
- `metadata.tricky`: true/false
- `metadata.tricky_why`: Explanation
- `metadata.topics`: List from MTH240 syllabus
- `metadata.techniques`: Specific methods
- `metadata.section`: Chapter/section reference
- `first_move`: First step advice
- `common_mistakes`: 4-5 specific errors with context
- `pattern_signal`: Recognition heuristic
- `trap_check`: What to verify
- `exam_tip`: Strategic advice
- `solutions.part_{a,b,c}`: Granular steps

### Solution Handling

| Raw Status | Action |
|------------|--------|
| Professor solutions | Use as ground truth, verify correctness |
| Student solutions | Verify, flag errors, mark unverified |
| No solutions | Leave empty, mark for generation |
| Unclear | Flag for human review |

## Step 3: Verification Checklist

Before saving enriched question:

- [ ] LaTeX renders correctly (balanced $, proper commands)
- [ ] All math in $...$ or $$...$$
- [ ] Solution steps are granular (one action per step)
- [ ] Common mistakes include math context
- [ ] Topics match MTH240 syllabus
- [ ] Difficulty rating justified
- [ ] Solution matches problem (if provided)
- [ ] No hallucinated content

## Step 4: Save Enriched Output

**Location:** `finished/{midterms,finals}/MTH240_{year}_{type}_{version}_Q{number}.json`

**Naming:**
- Midterms: `finished/midterms/MTH240_2023_midterm_M1_Q01.json`
- Finals: `finished/finals/MTH240_2023_final_Q01.json`

## MTH240 Syllabus Reference

**Topics by Chapter:**
- Ch 3: Integration Techniques (3.1-3.4, 3.7)
- Ch 4: First-Order DEs (4.1, 4.3, 4.5)
- Ch 5: Sequences and Series (5.1-5.6)
- Ch 6: Power Series (6.1-6.4)
- Ch 4 (Vol 3): Functions of Several Variables (4.1-4.3, 4.5, 4.7)

**Common Techniques:**
- u-Substitution
- Integration by Parts
- Cyclic Integration
- Trigonometric Substitution
- Partial Fractions
- Improper Integrals
- Separation of Variables
- Integrating Factor
- Power Series Expansion
- Ratio Test
- Comparison Test

## Error Handling

### Truncated Text
- Check raw_text length
- If cut off, note in `_enrichment.notes`

### Unclear Solutions
- Mark `solution.verified = false`
- Add note about uncertainty

### Missing Information
- Leave field empty rather than guess
- Flag for human review

### LaTeX Errors
- Fix unbalanced $
- Use \, for spacing in integrals
- Verify fractions render correctly

## Batch Processing

Agent processes 3-5 questions at a time for quality control.

After each batch:
1. Review output
2. Check for systematic errors
3. Adjust prompt if needed
4. Continue with next batch
