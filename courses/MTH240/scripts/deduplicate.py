#!/usr/bin/env python3
"""
Deduplicate exams and merge solution versions

Handles cases like:
- Exam.pdf + Exam_Solutions.pdf
- Exam_NS.pdf (no solutions) + Exam_TS.pdf (test/solutions)
- Multiple years/versions of same exam
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict
import hashlib

@dataclass
class ExamGroup:
    """Group of related exam files"""
    base_name: str
    year: int
    exam_type: str
    version: str
    files: List[Path]
    
    def has_solutions(self) -> bool:
        """Check if any file in group has solutions"""
        for f in self.files:
            if 'solution' in f.name.lower() or '_ts' in f.name.lower():
                return True
        return False
    
    def get_solution_file(self) -> Optional[Path]:
        """Get the file with best solutions"""
        # Priority: professor solutions > student solutions > none
        for pattern in ['solution', '_ts', '_test']:
            for f in self.files:
                if pattern in f.name.lower():
                    return f
        return None
    
    def get_exam_file(self) -> Optional[Path]:
        """Get the main exam file (no solutions)"""
        for f in self.files:
            name = f.name.lower()
            # Skip obvious solution files
            if any(x in name for x in ['solution', '_ts', '_test', '_s.', '_sol']):
                continue
            # Skip "no solution" markers
            if '_ns' in name or 'no sol' in name:
                continue
            return f
        # If no clean exam file, return first non-solution
        for f in self.files:
            if 'solution' not in f.name.lower():
                return f
        return self.files[0] if self.files else None

def parse_exam_key(filename: str) -> Dict:
    """Extract identifying key from filename"""
    name = filename.lower()
    
    # Extract year
    year_match = re.search(r'(20\d{2})', name)
    year = int(year_match.group(1)) if year_match else 0
    
    # Extract exam type
    exam_type = "unknown"
    if "midterm" in name or "m1" in name or "m2" in name:
        exam_type = "midterm"
    elif "final" in name:
        exam_type = "final"
    
    # Extract version
    version = ""
    if "m1" in name:
        version = "M1"
    elif "m2" in name:
        version = "M2"
    elif "v1" in name:
        version = "V1"
    elif "v2" in name:
        version = "V2"
    
    # Base name (remove solution indicators)
    base = re.sub(r'_(ts|ns|sol|s|test|solutions?)(\.pdf)?$', '', name, flags=re.I)
    base = re.sub(r'\s+(ts|ns|sol|s|test|solutions?)(\.pdf)?$', '', base, flags=re.I)
    
    return {
        "year": year,
        "exam_type": exam_type,
        "version": version,
        "base": base
    }

def group_exams(raw_dir: Path) -> List[ExamGroup]:
    """Group related exam files"""
    pdf_files = list(raw_dir.glob("*.pdf"))
    
    # Parse all files
    parsed = []
    for f in pdf_files:
        key = parse_exam_key(f.name)
        parsed.append({"file": f, "key": key})
    
    # Group by year + type + version
    groups = {}
    for p in parsed:
        key = (p["key"]["year"], p["key"]["exam_type"], p["key"]["version"])
        if key not in groups:
            groups[key] = []
        groups[key].append(p["file"])
    
    # Create ExamGroup objects
    result = []
    for (year, exam_type, version), files in groups.items():
        if files:
            base = parse_exam_key(files[0].name)["base"]
            result.append(ExamGroup(
                base_name=base,
                year=year,
                exam_type=exam_type,
                version=version,
                files=files
            ))
    
    return result

def merge_exam_versions(group: ExamGroup, processing_dir: Path) -> Dict:
    """Merge exam and solution files into one enriched document"""
    
    exam_file = group.get_exam_file()
    sol_file = group.get_solution_file()
    
    # Load both JSONs if they exist
    exam_data = None
    sol_data = None
    
    if exam_file:
        exam_json = processing_dir / f"{exam_file.stem}.json"
        if exam_json.exists():
            with open(exam_json) as f:
                exam_data = json.load(f)
    
    if sol_file and sol_file != exam_file:
        sol_json = processing_dir / f"{sol_file.stem}.json"
        if sol_json.exists():
            with open(sol_json) as f:
                sol_data = json.load(f)
    
    # Start with exam data or create new
    merged = exam_data or sol_data or {"metadata": {}, "questions": []}
    
    # Update metadata
    merged["metadata"]["year"] = group.year
    merged["metadata"]["exam_type"] = group.exam_type
    merged["metadata"]["exam_version"] = group.version
    merged["metadata"]["source_files"] = [f.name for f in group.files]
    
    # Determine solution status
    if sol_file and sol_file != exam_file:
        merged["metadata"]["solution_provider"] = "professor"
        merged["metadata"]["solution_quality"] = "complete"
        merged["metadata"]["solution_source"] = sol_file.name
    elif group.has_solutions():
        merged["metadata"]["solution_provider"] = "professor"
        merged["metadata"]["solution_quality"] = "complete"
    else:
        merged["metadata"]["solution_provider"] = "none"
        merged["metadata"]["solution_quality"] = "none"
    
    # Mark for AI enrichment
    merged["_merge_info"] = {
        "grouped_files": [f.name for f in group.files],
        "exam_file": exam_file.name if exam_file else None,
        "solution_file": sol_file.name if sol_file else None,
        "needs_ai_merge": sol_file is not None and exam_file is not None and sol_file != exam_file
    }
    
    return merged

def main():
    raw_dir = Path("courses/MTH240/raw")
    processing_dir = Path("courses/MTH240/processing")
    
    print("Grouping related exams...")
    groups = group_exams(raw_dir)
    
    print(f"\nFound {len(groups)} exam groups:")
    
    for group in groups:
        print(f"\n{group.year} {group.exam_type} {group.version}:")
        for f in group.files:
            marker = ""
            if f == group.get_exam_file():
                marker = " [EXAM]"
            elif f == group.get_solution_file():
                marker = " [SOLUTIONS]"
            print(f"  - {f.name}{marker}")
        
        # Merge and save
        merged = merge_exam_versions(group, processing_dir)
        
        output_name = f"MTH240_{group.year}_{group.exam_type}_{group.version}_merged.json"
        output_path = processing_dir / output_name
        
        with open(output_path, 'w') as f:
            json.dump(merged, f, indent=2)
        
        print(f"  → Merged: {output_name}")

if __name__ == "__main__":
    main()
