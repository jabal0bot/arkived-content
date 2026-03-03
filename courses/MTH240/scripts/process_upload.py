#!/usr/bin/env python3
"""
Universal upload processor - detects and sorts any course
"""

import zipfile
import shutil
import json
import re
from pathlib import Path
import subprocess
import sys

COURSE_PATTERNS = {
    r'MTH\d+': 'MTH',
    r'PHY\d+': 'PHY', 
    r'CHY\d+': 'CHY',
    r'CPS\d+': 'CPS',
    r'ECN\d+': 'ECN',
}

def detect_course(filename: str) -> str:
    """Detect course code from filename"""
    upper = filename.upper()
    
    for pattern, prefix in COURSE_PATTERNS.items():
        match = re.search(pattern, upper)
        if match:
            return match.group(0)
    
    return "UNKNOWN"

def create_course_structure(course: str):
    """Create folder structure for new course"""
    base = Path(f"courses/{course}")
    
    dirs = [
        base / "raw",
        base / "processing", 
        base / "finished/midterms",
        base / "finished/finals",
        base / "finished/content",
        base / "templates",
        base / "scripts"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy templates from MTH240 as starting point
    mth240_templates = Path("courses/MTH240/templates")
    if mth240_templates.exists():
        for template in mth240_templates.glob("*.json"):
            dest = base / "templates" / template.name
            if not dest.exists():
                shutil.copy(template, dest)
    
    print(f"Created structure for {course}")

def process_zip(zip_path: Path):
    """Process uploaded zip file"""
    
    print(f"Processing: {zip_path.name}")
    
    # Detect course
    course = detect_course(zip_path.name)
    
    if course == "UNKNOWN":
        print("Warning: Could not detect course from filename")
        print("Files will be extracted for manual review")
        course = "UNKNOWN"
    
    print(f"Detected course: {course}")
    
    # Create structure if needed
    create_course_structure(course)
    
    raw_dir = Path(f"courses/{course}/raw")
    processing_dir = Path(f"courses/{course}/processing")
    
    # Extract zip
    extract_dir = Path("uploads/_temp_extract")
    extract_dir.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)
    
    # Move PDFs and detect sub-courses
    pdf_count = 0
    course_files = {}
    
    for pdf in extract_dir.rglob("*.pdf"):
        file_course = detect_course(pdf.name)
        
        if file_course not in course_files:
            course_files[file_course] = []
        
        # Create structure for this course
        create_course_structure(file_course)
        file_raw_dir = Path(f"courses/{file_course}/raw")
        
        dest = file_raw_dir / pdf.name
        shutil.move(pdf, dest)
        course_files[file_course].append(pdf.name)
        pdf_count += 1
    
    # Clean up
    shutil.rmtree(extract_dir, ignore_errors=True)
    
    # Log sorting
    with open("uploads/.sorting_log", "a") as f:
        f.write(f"\n{zip_path.name}:\n")
        for c, files in course_files.items():
            f.write(f"  {c}: {len(files)} files\n")
    
    print(f"\nExtracted {pdf_count} PDFs into {len(course_files)} course(s):")
    for c, files in course_files.items():
        print(f"  {c}: {len(files)} files")
    
    # Process each course
    for c in course_files.keys():
        if c == "UNKNOWN":
            continue
            
        print(f"\nProcessing {c}...")
        
        # Run deduplication if script exists
        dedup_script = Path(f"courses/{c}/scripts/deduplicate.py")
        if dedup_script.exists():
            subprocess.run([sys.executable, str(dedup_script)])
        
        # Run raw extraction
        raw_script = Path(f"courses/{c}/scripts/extract_raw.py")
        if raw_script.exists():
            for pdf in Path(f"courses/{c}/raw").glob("*.pdf"):
                output = Path(f"courses/{c}/processing") / f"{pdf.stem}_raw.json"
                if output.exists():
                    continue
                subprocess.run([
                    sys.executable, str(raw_script),
                    "--input", str(pdf),
                    "--output", str(output)
                ])
    
    print("\n" + "="*50)
    print("Upload processing complete!")
    print("Agent will now manually enrich questions")
    print("="*50)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True)
    args = parser.parse_args()
    
    process_zip(Path(args.zip))
