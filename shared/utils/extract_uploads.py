#!/usr/bin/env python3
"""Extract and sort uploaded zip files"""

import zipfile
import shutil
from pathlib import Path

def extract_uploads():
    uploads_dir = Path("uploads")
    
    for course_dir in uploads_dir.iterdir():
        if not course_dir.is_dir():
            continue
        
        course = course_dir.name
        raw_dir = Path(f"courses/{course}/raw")
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract all zips
        for zip_file in course_dir.rglob("*.zip"):
            print(f"Extracting: {zip_file}")
            with zipfile.ZipFile(zip_file, 'r') as z:
                z.extractall(raw_dir)
        
        # Move PDFs to raw root
        for pdf in course_dir.rglob("*.pdf"):
            if pdf.parent != raw_dir:
                dest = raw_dir / pdf.name
                shutil.move(pdf, dest)
                print(f"Moved: {pdf.name}")
        
        # Clean up empty dirs
        for subdir in course_dir.iterdir():
            if subdir.is_dir():
                shutil.rmtree(subdir, ignore_errors=True)

if __name__ == "__main__":
    extract_uploads()
