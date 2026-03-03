#!/usr/bin/env python3
"""MTH240 Exam Processor - Raw PDF to Structured JSON"""

import json
import re
import fitz
from pathlib import Path
from datetime import datetime
import hashlib

class MTH240ExamProcessor:
    def __init__(self):
        self.course = "MTH240"
        self.course_name = "Calculus II"
        
    def process(self, pdf_path: Path) -> dict:
        """Process exam PDF to structured JSON"""
        
        # Extract raw text
        doc = fitz.open(pdf_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        
        full_text = "\n".join(pages_text)
        
        # Parse filename
        filename = pdf_path.stem
        metadata = self._parse_filename(filename)
        
        # Detect questions
        questions = self._detect_questions(full_text, pages_text)
        
        # Build output
        output = {
            "metadata": {
                "course": self.course,
                "course_name": self.course_name,
                "year": metadata["year"],
                "semester": metadata["semester"],
                "exam_type": metadata["exam_type"],
                "exam_version": metadata["version"],
                "date": "",
                "duration_minutes": self._detect_duration(full_text),
                "total_marks": self._detect_total_marks(full_text),
                "solution_provider": metadata["solution_provider"],
                "solution_quality": "unknown",
                "source_file": filename,
                "file_hash": hashlib.md5(pdf_path.read_bytes()).hexdigest(),
                "processed_at": datetime.now().isoformat()
            },
            "questions": questions,
            "raw_text": full_text[:5000] + "..." if len(full_text) > 5000 else full_text
        }
        
        return output
    
    def _parse_filename(self, filename: str) -> dict:
        """Extract metadata from filename"""
        lower = filename.lower()
        
        # Year
        year_match = re.search(r'(20\d{2})', filename)
        year = int(year_match.group(1)) if year_match else 0
        
        # Semester
        semester = ""
        if "w" in filename[:5].lower() or "winter" in lower:
            semester = "Winter"
        elif "s" in filename[:5].lower() or "spring" in lower:
            semester = "Spring"
        elif "f" in filename[:5].lower() or "fall" in lower:
            semester = "Fall"
        
        # Exam type
        exam_type = "unknown"
        if "midterm" in lower or "m1" in lower or "m2" in lower:
            exam_type = "midterm"
        elif "final" in lower:
            exam_type = "final"
        
        # Version
        version = ""
        if "M1" in filename or "m1" in filename:
            version = "M1"
        elif "M2" in filename or "m2" in filename:
            version = "M2"
        elif "V1" in filename:
            version = "V1"
        elif "V2" in filename:
            version = "V2"
        
        # Solution provider
        solution = "unknown"
        if any(x in lower for x in ["solution", "solutions", "ts", "test"]):
            solution = "professor"
        elif "student" in lower:
            solution = "student"
        elif any(x in lower for x in ["ns", "no sol"]):
            solution = "none"
        
        return {
            "year": year,
            "semester": semester,
            "exam_type": exam_type,
            "version": version,
            "solution_provider": solution
        }
    
    def _detect_questions(self, text: str, pages: list) -> list:
        """Detect question boundaries and content"""
        questions = []
        
        # Pattern: number followed by content
        pattern = r'(?:^|\n)\s*(\d+)\s*[.\)]\s*(.*?)(?=\n\s*\d+\s*[.\)]|\Z)'
        matches = list(re.finditer(pattern, text, re.DOTALL))
        
        for i, match in enumerate(matches[:20]):  # Limit to 20 questions
            num = int(match.group(1))
            content = match.group(2).strip()
            
            # Detect marks
            marks = 0
            marks_match = re.search(r'\[(\d+)\s*marks?\]|\((\d+)\s*marks?\)', content)
            if marks_match:
                marks = int(marks_match.group(1) or marks_match.group(2))
            
            # Detect subparts
            subparts = []
            subpart_pattern = r'\(([a-z])\)\s*(.*?)(?=\([a-z]\)|\Z)'
            for sp_match in re.finditer(subpart_pattern, content, re.DOTALL):
                subparts.append({
                    "label": sp_match.group(1),
                    "marks": 0,
                    "problem": sp_match.group(2).strip()[:500]
                })
            
            questions.append({
                "number": num,
                "marks": marks,
                "problem": content[:1000],
                "problem_latex": "",
                "topics": [],
                "has_subparts": len(subparts) > 0,
                "subparts": subparts[:5],
                "solution": {
                    "provider": "unknown",
                    "text": "",
                    "latex": "",
                    "verified": False
                }
            })
        
        return questions
    
    def _detect_duration(self, text: str) -> int:
        match = re.search(r'(\d+)\s*(?:hour|hr)', text, re.I)
        return int(match.group(1)) * 60 if match else 0
    
    def _detect_total_marks(self, text: str) -> int:
        for pattern in [r'total\s*(\d+)\s*marks', r'\[\s*(\d+)\s*marks?\s*\]']:
            match = re.search(pattern, text, re.I)
            if match:
                return int(match.group(1))
        return 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    processor = MTH240ExamProcessor()
    result = processor.process(Path(args.input))
    
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Processed: {args.input} -> {args.output}")
    print(f"  Questions: {len(result['questions'])}")
    print(f"  Year: {result['metadata']['year']}")
    print(f"  Type: {result['metadata']['exam_type']}")
