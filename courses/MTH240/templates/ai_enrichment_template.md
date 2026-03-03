# EXAM QUESTION JSON TEMPLATE

Process the provided exam question into the following JSON structure. Maintain mathematical rigor, proper LaTeX formatting, and consistent metadata granularity.

## REQUIRED OUTPUT SCHEMA

```json
{
  "question_number": <int>,
  "total_marks": <int>,
  "problem_statement": "<Complete LaTeX exam text with parts (a), (b), etc. as they appear>",
  "metadata": {
    "difficulty": <int 1-5>,
    "tricky": <boolean>,
    "tricky_why": "<2-3 sentences explaining the pedagogical trap>",
    "topics": ["<Topic 1>", "<Topic 2>"],
    "techniques": ["<Technique 1>", "<Technique 2>"],
    "section": "<Course section reference>"
  },
  "first_move": "<The absolute first thing a student should write/do>",
  "common_mistakes": [
    "<Specific error 1 with math context>",
    "<Specific error 2 with math context>",
    "<Minimum 4-5 distinct errors>"
  ],
  "pattern_signal": "<How to recognize this problem type from structure>",
  "trap_check": "<What to verify before proceeding>",
  "exam_tip": "<Strategic advice for exam conditions>",
  "solutions": {
    "part_a": {
      "marks": <int>,
      "solution_steps": [
        {
          "step": 1,
          "text": "<Descriptive text with $math$ variables properly LaTeXed>",
          "math": "<Formal mathematical expression or equation>"
        }
      ],
      "final_answer": "<LaTeX final answer with $ delimiters>"
    },
    "part_b": { "...": "..." }
  }
}
```

## FORMATTING RULES

### LaTeX Requirements:
- ALL mathematical expressions must be in $...$ or $$...$$
- Variables: $x$, $y$, $t$, not "x" or "y"
- Functions: $\sin(x)$, $\ln(x)$, $\arcsin(x)$
- Integrals: $\int_{a}^{b} f(x) \, dx$ (use \, for spacing)
- Fractions: $\frac{numerator}{denominator}$
- Exponents/subscripts: $x^{2}$, $x_{0}$

### Step Granularity:
- Each step should represent ONE logical action (substitution, application of theorem, algebraic simplification)
- 7-mark questions → 5-8 steps
- 2-mark questions → 1-3 steps
- Text explains the reasoning, math shows the execution

### Metadata Standards:
- **Difficulty**: 1=trivial, 2=easy, 3=medium, 4=hard, 5=very challenging
- **Tricky**: True if common errors occur at conceptual level (not just arithmetic)
- **Topics**: Use standard course terminology (e.g., "Integration by Parts", "Improper Integrals")
- **Techniques**: Specific methods (e.g., "u-Substitution", "Cyclic Integration")
- **Section**: Map to syllabus (e.g., "Section 3.1 Integration By Parts")

### Coaching Layer:
- **first_move**: Actionable first line (e.g., "Substitute u=√x ...")
- **common_mistakes**: Must include the mathematical context of the error
- **pattern_signal**: Recognition heuristic
- **trap_check**: The "gotcha" moment
- **exam_tip**: Time-saving or verification strategy

## MTH240 COURSE CONTENT

- **Chapter 3**: Integration Techniques (3.1-3.4, 3.7)
- **Chapter 4**: First-Order Differential Equations (4.1, 4.3, 4.5)
- **Chapter 5**: Sequences and Series (5.1-5.6)
- **Chapter 6**: Power Series (6.1-6.4)
- **Chapter 4 (Vol 3)**: Functions of Several Variables (4.1-4.3, 4.5, 4.7)

References: Calculus by Strang, Herman, et al (2016)

## SOLUTION HANDLING

- **Professor solutions**: Use as ground truth, mark as verified
- **Student solutions**: Verify correctness, flag errors, mark as unverified
- **No solutions**: Leave solution fields empty, mark for AI generation
- **Multiple versions**: Merge solutions from solution file into exam file

## IMPORTANT

- Preserve ALL content exactly as written
- Do not hallucinate missing solutions
- Flag uncertain cases for human review
- Verify LaTeX renders correctly
