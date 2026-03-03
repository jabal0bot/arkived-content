#!/usr/bin/env python3
"""Validate all processed JSON files"""

import json
from pathlib import Path
import sys

def validate_exam(json_path: Path) -> list:
    """Validate exam JSON structure"""
    errors = []
    
    try:
        with open(json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    
    # Check required fields
    if "metadata" not in data:
        errors.append("Missing metadata")
    else:
        meta = data["metadata"]
        required = ["course", "year", "exam_type"]
        for field in required:
            if field not in meta:
                errors.append(f"Missing metadata.{field}")
    
    if "questions" not in data:
        errors.append("Missing questions")
    elif not isinstance(data["questions"], list):
        errors.append("questions must be array")
    
    return errors

def main():
    processing_dir = Path("courses/MTH240/processing")
    
    all_valid = True
    for json_file in processing_dir.glob("*.json"):
        errors = validate_exam(json_file)
        if errors:
            print(f"❌ {json_file.name}:")
            for err in errors:
                print(f"   - {err}")
            all_valid = False
        else:
            print(f"✅ {json_file.name}")
    
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
