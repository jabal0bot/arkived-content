#!/usr/bin/env python3
"""Extract essential data from MTH240 exam PDFs"""

import fitz
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime

class MTH240RawExtractor:
    def __init__(self):
        self.course = "MTH240"
    
    def extract(self, pdf_path: Path) -> dict:
        doc = fitz.open(pdf_path)
        
        # Extract text from all pages
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        
        full_text = "\n".join(pages_text)
        filename = pdf_path.name
        
        # Parse document identity from filename
        doc_id = self._parse_filename(filename)
        
        # Extract structure
        structure = self._extract_structure(full_text, pages_text)
        
        # Extract questions
        questions = self._extract_questions(full_text)
        
        # Determine solution status
        solutions = self._detect_solutions(filename, full_text)
        
        return {
            "document_id": doc_id,
            "structure": structure,
            "questions": questions,
            "solutions": solutions,
            "source_file": {
                "filename": filename,
                "hash_md5": hashlib.md5(pdf_path.read_bytes()).hexdigest(),
                "extracted_at": datetime.now().isoformat()
            },
            "raw_text": full_text[:3000] + "..." if len(full_text) > 3000 else full_text
        }
    
    def _parse_filename(self, filename: str) -> dict:
        lower = filename.lower()
        
        # Year
        year_match = re.search(r'(20\d{2})', filename)
        year = int(year_match.group(1)) if year_match else 0
        
        # Semester
        semester = ""
        if any(x in lower for x in ['winter', 'w']):
            semester = "Winter"
        elif any(x in lower for x in ['spring', 's']):
            semester = "Spring"
        elif any(x in lower for x in ['summer']):
            semester = "Summer"
        elif any(x in lower for x in ['fall', 'f']):
            semester = "Fall"
        
        # Exam type
        exam_type = "unknown"
        if "midterm" in lower or "m1" in lower or "m2" in lower:
            exam_type = "midterm"
        elif "final" in lower:
            exam_type = "final"
        
        # Version (M1/M2 for midterms, not V1/V2)
        version = ""
        if "m1" in lower:
            version = "M1"
        elif "m2" in lower:
            version = "M2"
        
        return {
            "course": self.course,
            "year": year,
            "semester": semester,
            "exam_type": exam_type,
            "version": version,
            "date": ""
        }
    
    def _extract_structure(self, text: str, pages_text: list) -> dict:
        # Total marks
        total_marks = 0
        marks_match = re.search(r'total\s*(\d+)\s*marks?', text, re.I)
        if marks_match:
            total_marks = int(marks_match.group(1))
        
        # Duration
        duration = 0
        time_match = re.search(r'(\d+)\s*(?:hour|hr)', text, re.I)
        if time_match:
            duration = int(time_match.group(1)) * 60
        
        return {
            "pages": len(pages_text),
            "total_marks": total_marks,
            "duration_minutes": duration,
            "question_count": 0  # Will be updated
        }
    
    def _extract_questions(self, text: str) -> list:
        questions = []
        
        # Pattern: number followed by content
        pattern = r'(?:^|\n)\s*(\d+)\s*[.\)]\s*(.*?)(?=\n\s*\d+\s*[.\)]|\Z)'
        matches = list(re.finditer(pattern, text, re.DOTALL))
        
        for match in matches[:25]:  # Reasonable limit
            num = int(match.group(1))
            content = match.group(2).strip()
            
            # Detect marks
            marks = 0
            marks_match = re.search(r'\[(\d+)\s*marks?\]|\((\d+)\s*marks?\)', content)
            if marks_match:
                marks = int(marks_match.group(1) or marks_match.group(2))
            
            # Detect subparts
            subparts = []
            subpart_pattern = r'\(([a-z])\)'
            for sp_match in re.finditer(subpart_pattern, content[:500]):
                subparts.append({
                    "label": sp_match.group(1),
                    "marks": 0  # Will be filled by AI
                })
            
            questions.append({
                "number": num,
                "marks": marks,
                "has_subparts": len(subparts) > 0,
                "subparts": subparts,
                "raw_text": content[:800]  # Truncated for AI processing
            })
        
        return questions
    
    def _detect_solutions(self, filename: str, text: str) -> dict:
        lower = filename.lower()
        
        provider = "unknown"
        if any(x in lower for x in ['solution', 'solutions', 'ts', 'test']):
            provider = "professor"
        elif 'student' in lower:
            provider = "student"
        elif any(x in lower for x in ['ns', 'no sol']):
            provider = "none"
        
        return {
            "present": provider != "none",
            "provider": provider,
            "source": filename
        }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    extractor = MTH240RawExtractor()
    result = extractor.extract(Path(args.input))
    
    # Update question count
    result["structure"]["question_count"] = len(result["questions"])
    
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Extracted: {args.input}")
    print(f"  Year: {result['document_id']['year']}")
    print(f"  Type: {result['document_id']['exam_type']}")
    print(f"  Version: {result['document_id']['version']}")
    print(f"  Questions: {result['structure']['question_count']}")
    print(f"  Solutions: {result['solutions']['provider']}")

if __name__ == "__main__":
    main()
