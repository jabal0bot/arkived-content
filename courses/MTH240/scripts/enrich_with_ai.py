#!/usr/bin/env python3
"""
AI Enrichment - Manual processing interface

This script prepares files for manual AI enrichment.
The actual AI processing is done by the agent (me) through conversation.
"""

import json
from pathlib import Path
from datetime import datetime

def prepare_for_enrichment():
    """List all files ready for AI enrichment"""
    processing_dir = Path("courses/MTH240/processing")
    finished_dir = Path("courses/MTH240/finished")
    
    ready = []
    for json_file in processing_dir.glob("*.json"):
        # Check if already enriched
        finished_path = finished_dir / json_file.name
        if finished_path.exists():
            continue
        
        with open(json_file) as f:
            data = json.load(f)
        
        meta = data.get("metadata", {})
        ready.append({
            "file": json_file.name,
            "year": meta.get("year"),
            "type": meta.get("exam_type"),
            "questions": len(data.get("questions", [])),
            "path": str(json_file)
        })
    
    return ready

def mark_enriched(processing_file: Path, enriched_data: dict):
    """Save enriched data to finished/"""
    finished_dir = Path("courses/MTH240/finished")
    
    # Determine subfolder
    exam_type = enriched_data.get("metadata", {}).get("exam_type", "unknown")
    if exam_type == "midterm":
        subfolder = "midterms"
    elif exam_type == "final":
        subfolder = "finals"
    else:
        subfolder = "content"
    
    output_dir = finished_dir / subfolder
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / processing_file.name
    
    # Add enrichment metadata
    enriched_data["_enrichment"] = {
        "enriched_by": "agent",
        "enriched_at": datetime.now().isoformat(),
        "method": "manual_kimi_k25"
    }
    
    with open(output_file, 'w') as f:
        json.dump(enriched_data, f, indent=2)
    
    print(f"Saved enriched: {output_file}")
    return output_file

def generate_enrichment_prompt(json_file: Path) -> str:
    """Generate the prompt for AI enrichment"""
    with open(json_file) as f:
        data = json.load(f)
    
    meta = data.get("metadata", {})
    questions = data.get("questions", [])
    raw_text = data.get("raw_text", "")[:3000]
    
    prompt = f"""# AI Enrichment Task: MTH240 Exam

## File: {json_file.name}
- Year: {meta.get('year')}
- Type: {meta.get('exam_type')}
- Solution Provider: {meta.get('solution_provider')}
- Questions Detected: {len(questions)}

## Raw Text Preview:
```
{raw_text}
```

## Current Question Structure:
"""
    
    for q in questions[:3]:  # Show first 3
        prompt += f"""
Q{q.get('number')}: {q.get('marks')} marks
{q.get('raw_text', '')[:200]}...
"""
    
    prompt += """

## Enrichment Tasks:

1. **Parse Questions**: Convert raw text to clean LaTeX
2. **Identify Solutions**: Professor vs Student vs None
3. **Extract Topics**: Integration techniques, series, etc.
4. **Verify Solutions**: Check if provided solutions are correct
5. **Flag Issues**: Truncated text, unclear problems

## Output Format:
Return the complete enriched JSON with:
- questions[].problem_latex (clean LaTeX)
- questions[].topics[] (list of topics)
- questions[].solution.provider (professor/student/none)
- questions[].solution.verified (true/false)
- questions[].solution.latex (solution in LaTeX)

## Important:
- Preserve ALL content exactly
- Do not hallucinate missing solutions
- Flag uncertain cases for review
"""
    
    return prompt

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List files ready for enrichment")
    parser.add_argument("--prompt", help="Generate prompt for specific file")
    args = parser.parse_args()
    
    if args.list:
        ready = prepare_for_enrichment()
        print(f"Files ready for AI enrichment: {len(ready)}")
        for item in ready:
            print(f"  - {item['file']} ({item['year']} {item['type']}, {item['questions']} questions)")
    
    elif args.prompt:
        json_file = Path(args.prompt)
        if json_file.exists():
            print(generate_enrichment_prompt(json_file))
        else:
            print(f"File not found: {json_file}")
