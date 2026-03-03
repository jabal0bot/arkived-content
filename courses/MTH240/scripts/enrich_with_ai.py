#!/usr/bin/env python3
"""
AI Enrichment - Manual processing interface using detailed template
"""

import json
from pathlib import Path
from datetime import datetime

def load_template() -> str:
    """Load the enrichment template"""
    template_path = Path("courses/MTH240/templates/ai_enrichment_template.md")
    with open(template_path) as f:
        return f.read()

def get_pending_files() -> list:
    """Get list of files ready for enrichment"""
    processing_dir = Path("courses/MTH240/processing")
    finished_dir = Path("courses/MTH240/finished")
    
    pending = []
    for json_file in processing_dir.glob("*.json"):
        # Check if already enriched in any finished subdir
        relative = json_file.name
        already_done = False
        for subdir in ["midterms", "finals", "content"]:
            if (finished_dir / subdir / relative).exists():
                already_done = True
                break
        
        if not already_done:
            with open(json_file) as f:
                data = json.load(f)
            
            meta = data.get("metadata", {})
            pending.append({
                "file": json_file.name,
                "path": json_file,
                "year": meta.get("year"),
                "type": meta.get("exam_type"),
                "version": meta.get("exam_version"),
                "questions": len(data.get("questions", [])),
                "solution_provider": meta.get("solution_provider", "unknown")
            })
    
    return pending

def generate_enrichment_batch(pending: list, batch_size: int = 3) -> str:
    """Generate prompt for enriching a batch of questions"""
    
    template = load_template()
    
    prompt = f"""# AI Enrichment Task

{template}

---

## FILES TO PROCESS

"""
    
    for item in pending[:batch_size]:
        with open(item["path"]) as f:
            data = json.load(f)
        
        prompt += f"""
### {item['file']}
- Year: {item['year']}, Type: {item['type']}, Version: {item['version']}
- Solution Provider: {item['solution_provider']}
- Questions: {item['questions']}

Raw text preview:
```
{data.get('raw_text', '')[:1500]}...
```

Questions detected:
"""
        for q in data.get("questions", [])[:5]:
            prompt += f"\nQ{q.get('number')}: {q.get('marks')} marks\n{q.get('raw_text', '')[:200]}...\n"
    
    prompt += """

## OUTPUT INSTRUCTIONS

For each question, output a complete JSON object following the template above.
Save each question as a separate JSON file in the format:
`MTH240_{year}_{type}_{version}_Q{number}.json`

Ensure:
1. All LaTeX is properly formatted
2. Solution steps are granular
3. Common mistakes are specific with math context
4. Metadata accurately reflects difficulty and topics
"""
    
    return prompt

def save_enriched_question(question_data: dict, metadata: dict):
    """Save an enriched question to finished/"""
    
    finished_dir = Path("courses/MTH240/finished")
    
    # Determine subdirectory
    exam_type = metadata.get("exam_type", "unknown")
    if exam_type == "midterm":
        subdir = "midterms"
    elif exam_type == "final":
        subdir = "finals"
    else:
        subdir = "content"
    
    output_dir = finished_dir / subdir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build filename
    year = metadata.get("year", "unknown")
    version = metadata.get("exam_version", "")
    q_num = question_data.get("question_number", 0)
    
    filename = f"MTH240_{year}_{exam_type}_{version}_Q{q_num:02d}.json"
    output_path = output_dir / filename
    
    # Add enrichment metadata
    question_data["_enrichment"] = {
        "enriched_by": "agent_manual",
        "enriched_at": datetime.now().isoformat(),
        "source_exam": metadata.get("source_file", ""),
        "verified": False  # Pending human review
    }
    
    with open(output_path, 'w') as f:
        json.dump(question_data, f, indent=2)
    
    print(f"Saved: {output_path}")
    return output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--batch", type=int, default=3)
    args = parser.parse_args()
    
    if args.list:
        pending = get_pending_files()
        print(f"Files ready for enrichment: {len(pending)}")
        for item in pending:
            print(f"  - {item['file']}")
            print(f"    {item['year']} {item['type']} {item['version']}, "
                  f"{item['questions']} questions, solutions: {item['solution_provider']}")
    else:
        pending = get_pending_files()
        if pending:
            print(generate_enrichment_batch(pending, args.batch))
        else:
            print("No pending files")
