# Uploads

Drop course zip files here. Agent will sort and process.

## How It Works

1. Drop any course zip file directly in `uploads/`
2. Agent detects course from filename/content
3. Agent creates course folder structure if needed
4. Agent sorts files into appropriate course

## Examples

| Filename | Detected Course | Action |
|----------|----------------|--------|
| `MTH240_exams.zip` | MTH240 | Create `courses/MTH240/`, process |
| `PHY180_midterms.zip` | PHY180 | Create `courses/PHY180/`, process |
| `random_files.zip` | Unknown | Agent reviews and asks |

## Processing

Agent will:
1. Extract PDFs from zip
2. Detect course code from filenames
3. Create course structure (`courses/{CODE}/`)
4. Sort into `raw/`, `processing/`, `finished/`
5. Run course-specific extraction
6. Enrich with AI

## Notes

- One zip can contain multiple courses (agent will sort)
- Mixed/unclear files flagged for review
- Agent maintains sorting log
