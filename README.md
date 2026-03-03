# Arkived Content Pipeline

Automated processing of course materials (exams, notes, study sheets) into structured, backend-ready content.

## Quick Start

1. **Upload**: Drop `MTH240.zip` in `uploads/MTH240/`
2. **Auto-process**: GitHub Actions extracts, sorts, and processes
3. **Review**: Check `courses/MTH240/processing/` for intermediate output
4. **Validate**: Daily audit runs automatically

## Repository Structure

```
.
├── .github/workflows/          # Automation
│   ├── process-upload.yml      # Triggers on upload
│   └── daily-audit.yml         # Daily validation
├── uploads/
│   └── MTH240/                 # Your zip drops here
├── courses/
│   └── MTH240/
│       ├── raw/                # Extracted PDFs (untouched)
│       ├── processing/         # Intermediate JSON
│       ├── finished/           # Final validated output
│       │   ├── midterms/
│       │   ├── finals/
│       │   └── content/        # notes, sheets, etc
│       ├── templates/          # JSON schemas
│       └── scripts/            # Course-specific processors
├── shared/
│   ├── utils/                  # Extraction utilities
│   └── validators/             # Validation scripts
└── agents/
    └── daily_audit.py          # Comprehensive audit
```

## Processing Pipeline

### Stage 1: Upload & Extract
- Drop zip file in `uploads/MTH240/`
- GitHub Action auto-extracts to `courses/MTH240/raw/`

### Stage 2: Raw Processing
- Detect exam type from filename
- Extract text (with OCR fallback)
- Detect questions, marks, subparts
- Output: `processing/{file}.json`

### Stage 3: AI Enrichment (Manual)
- Run course-specific AI prompts
- Generate LaTeX, verify solutions
- Move to `finished/{type}/`

### Stage 4: Validation
- Schema validation
- Daily audit (20% sample)
- LaTeX error detection
- Truncation checks

## Course-Specific Setup

Each course has:
- `templates/exam_schema.json` - Validation schema
- `templates/content_schema.json` - For notes/sheets
- `scripts/process_exam.py` - Raw extraction

## Validation & Audit

### Automatic (Every Push)
- JSON schema validation
- Required field checks

### Daily Audit
- 20% random sample
- LaTeX syntax check
- Truncation detection
- Missing metadata flag

### Manual Review
- Check `processing/` for issues
- Review AI-enriched `finished/` output

## Status

| Component | Status |
|-----------|--------|
| MTH240 templates | ✅ |
| Auto-extraction | ✅ |
| Raw processing | ✅ |
| Validation | ✅ |
| Daily audit | ✅ |
| AI enrichment | ⏳ Manual step |

## Adding New Courses

1. Create `courses/{CODE}/` structure
2. Copy templates from MTH240
3. Customize `process_exam.py`
4. Update schemas for course-specific fields
