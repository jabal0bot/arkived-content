#!/usr/bin/env python3
"""
Main upload processing orchestrator for MTH240

Usage: python process_upload.py --zip uploads/MTH240/files.zip
"""

import zipfile
import shutil
import json
from pathlib import Path
import subprocess
import sys

def process_zip(zip_path: Path):
    """Process uploaded zip file"""
    
    course = "MTH240"
    raw_dir = Path(f"courses/{course}/raw")
    processing_dir = Path(f"courses/{course}/processing")
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processing_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing: {zip_path}")
    
    # Extract zip
    extract_dir = raw_dir / "_temp_extract"
    extract_dir.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)
    
    # Move PDFs to raw/
    pdf_count = 0
    for pdf in extract_dir.rglob("*.pdf"):
        dest = raw_dir / pdf.name
        shutil.move(pdf, dest)
        pdf_count += 1
        print(f"  Extracted: {pdf.name}")
    
    # Clean up temp
    shutil.rmtree(extract_dir, ignore_errors=True)
    
    print(f"\nExtracted {pdf_count} PDFs")
    
    # Run deduplication
    print("\nGrouping related exams...")
    subprocess.run([sys.executable, "courses/MTH240/scripts/deduplicate.py"])
    
    # Run raw extraction
    print("\nExtracting raw structure...")
    for pdf in raw_dir.glob("*.pdf"):
        output = processing_dir / f"{pdf.stem}_raw.json"
        if output.exists():
            continue
        
        subprocess.run([
            sys.executable, "courses/MTH240/scripts/extract_raw.py",
            "--input", str(pdf),
            "--output", str(output)
        ])
    
    # Generate enrichment queue
    print("\nGenerating enrichment queue...")
    subprocess.run([
        sys.executable, "courses/MTH240/scripts/enrich_with_ai.py",
        "--list"
    ])
    
    print("\n" + "="*50)
    print("Upload processing complete!")
    print(f"PDFs in: courses/{course}/raw/")
    print(f"Raw JSON in: courses/{course}/processing/")
    print("\nNext: Agent will manually enrich questions")
    print("="*50)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, help="Path to uploaded zip")
    args = parser.parse_args()
    
    process_zip(Path(args.zip))
