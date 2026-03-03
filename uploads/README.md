# Uploads

Drop your course zip files here.

## Structure
```
uploads/
├── MTH240/          # MTH240 zip files
├── MTH141/          # Future courses
└── ...
```

## Usage

1. Drop zip file in appropriate course folder
2. Run: `python courses/MTH240/scripts/process_upload.py --zip uploads/MTH240/your_file.zip`
3. Or push to trigger GitHub Actions processing

## Supported Formats
- .zip files containing PDFs
- PDFs can be exams, notes, study sheets
