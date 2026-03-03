#!/usr/bin/env python3
"""Daily comprehensive audit of all content"""

import json
import random
from pathlib import Path
import fitz

def audit_exam(json_path: Path) -> dict:
    """Audit a single exam file"""
    issues = []
    
    with open(json_path) as f:
        data = json.load(f)
    
    # Check for truncation
    for q in data.get("questions", []):
        if len(q.get("problem", "")) > 900:
            issues.append(f"Q{q['number']}: Problem text may be truncated")
        
        # Check LaTeX
        latex = q.get("problem_latex", "")
        if latex and latex.count("$") % 2 != 0:
            issues.append(f"Q{q['number']}: Unbalanced $ in LaTeX")
    
    # Check metadata completeness
    meta = data.get("metadata", {})
    if meta.get("year", 0) == 0:
        issues.append("Missing year")
    if meta.get("exam_type") == "unknown":
        issues.append("Unknown exam type")
    
    return {
        "file": json_path.name,
        "issues": issues,
        "question_count": len(data.get("questions", [])),
        "valid": len(issues) == 0
    }

def sample_audit():
    """Audit random sample of files"""
    processing_dir = Path("courses/MTH240/processing")
    all_files = list(processing_dir.glob("*.json"))
    
    if not all_files:
        print("No files to audit")
        return
    
    # Audit 20% or at least 5 files
    sample_size = max(5, len(all_files) // 5)
    sample = random.sample(all_files, min(sample_size, len(all_files)))
    
    print(f"Auditing {len(sample)} of {len(all_files)} files...")
    
    all_valid = True
    for f in sample:
        result = audit_exam(f)
        if result["valid"]:
            print(f"✅ {result['file']} ({result['question_count']} questions)")
        else:
            print(f"❌ {result['file']}:")
            for issue in result["issues"]:
                print(f"   - {issue}")
            all_valid = False
    
    return all_valid

def main():
    import sys
    success = sample_audit()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
