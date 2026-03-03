# AI Enrichment Status - MTH240

## Template
Using detailed template: `templates/ai_enrichment_template.md`

## Output Format
Per-question JSON with:
- Complete problem statement in LaTeX
- Granular solution steps (one action per step)
- Metadata (difficulty, topics, techniques)
- Coaching layer (first_move, common_mistakes, pattern_signal, trap_check, exam_tip)

## Processing Queue

Run `python courses/MTH240/scripts/enrich_with_ai.py --list` to see pending files.

## Processing Log

| File | Questions | Status | Enriched By | Date | Notes |
|------|-----------|--------|-------------|------|-------|
| | | | | | |

## Per-Question Output

Each question saved as:
`finished/{midterms,finals}/MTH240_{year}_{type}_{version}_Q{number}.json`
