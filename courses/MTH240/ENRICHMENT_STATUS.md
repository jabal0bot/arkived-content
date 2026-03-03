# AI Enrichment Status - MTH240

## How It Works

1. **Raw files** are in `processing/` (extracted text, basic metadata)
2. **Agent (me)** manually processes each file through Kimi K2.5
3. **Enriched files** go to `finished/{midterms,finals,content}/`

## Current Queue

Run `python courses/MTH240/scripts/enrich_with_ai.py --list` to see pending files.

## Processing Log

| File | Status | Enriched By | Date | Notes |
|------|--------|-------------|------|-------|
| | | | | |

## Process

1. Get list of pending files from agent
2. Agent generates prompt and processes with Kimi
3. Agent returns enriched JSON
4. Save to `finished/` with `_enrichment` metadata
5. Update this log
