# Anki Flashcard Generation from Lecture PDFs

## Project Overview

This project automates the creation of Anki flashcard decks from lecture PDFs for any academic course. The goal is to create high-quality flashcards that test conceptual understanding and algorithm comprehension, aligned with exam requirements.

## Input Structure

```
project_folder/
├── claude.md (this file)
├── anki_flashcard_creation_guide.md (reference document)
├── exam_faq.txt (exam guidelines)
├── pdfs/
└── outputs/
    └── (generated .txt files will go here)
```

## Output Requirements

### File Format
- One `.txt` file per unit/topic
- Tab-separated values with headers:
  ```
  #separator:tab
  #html:true
  #tags column:3
  Front	Back	Tags
  ```
- UTF-8 encoding
- Proper MathJax notation: `\(...\)` for inline, `\[...\]` for display math

### Card Quality Guidelines

Based on exam requirements, cards should:
1. **Test understanding, not memorization** - Focus on "why" and "how"
2. **Use concrete examples** - Embed questions in specific scenarios
3. **Keep calculations simple** - No extensive computation required
4. **Focus on concepts** - Algorithm understanding, not formula recall
5. **Use visual aids** - Extract and embed relevant diagrams

### Card Types to Create

**Type 1: Conceptual Understanding** (40% of cards)
- Why does a concept work?
- What is the intuition behind an algorithm?
- When would you use approach X vs Y?

**Type 2: Simple Worked Examples** (20% of cards)
- Tiny networks/scenarios
- Obvious answers that demonstrate understanding
- No calculator needed

**Type 3: Algorithm Comprehension** (20% of cards)
- What does this step accomplish?
- Why does the algorithm avoid problem X?
- Trace through a trivial example

**Type 4: Pattern Recognition** (10% of cards)
- Identify reasoning patterns
- Recognize independence structures
- Classify problem types

**Type 5: Visual/Diagram-Based** (10% of cards)
- Network structures
- Algorithm flowcharts
- Conceptual diagrams
- **IMPORTANT**: For visual cards, place the image in the **Front** (question), not the Back (answer)
- The question should reference the diagram (e.g., "What does this diagram show?", "Identify the independence in this network")
- The answer provides the explanation without repeating the image

## Content Extraction Strategy

### From PDFs

1. **Read and parse** each PDF to extract:
   - Section headings and structure
   - Key concepts and definitions
   - Algorithms and their explanations
   - Examples and their solutions
   - Formulas and mathematical relationships
   - Diagrams and figures

2. **Identify high-value content**:
   - Core concepts (not crossed-out sections)
   - Algorithms with clear steps
   - Examples that illustrate principles
   - Comparison tables
   - Diagrams showing structures/processes

3. **Extract images**:
   - Diagrams and network structures
   - Algorithm flowcharts
   - Example scenarios with graphs
   - Comparison tables as images
   - Save as PNG files with descriptive names

### Image Handling

Use `pdfimages` or PyMuPDF to extract:
```python
import fitz  # PyMuPDF
doc = fitz.open("lecture.pdf")
page = doc[page_num]
images = page.get_images()
# Extract and save with descriptive names
```

For images, use external file references:
```html
<img src="unit3_student_network.png" style="max-width:500px;">
```

## Content Guidelines per Unit

### General Approach

For each unit, extract content that includes:

- **Core Concepts**: Fundamental ideas and definitions
- **Key Principles**: Important rules, theorems, or relationships
- **Methods and Techniques**: Algorithms, procedures, or approaches
- **Applications**: Practical uses and examples
- **Common Patterns**: Recurring themes or structures

### Content to Prioritize

- Main topics covered in the unit
- Important definitions and terminology
- Key algorithms or procedures
- Worked examples that illustrate concepts
- Diagrams showing relationships or structures
- Comparison tables showing differences between approaches
- Common pitfalls or misconceptions to address

## Card Creation Process

### For Each PDF:

1. **Extract structure**: Identify main sections and subsections
2. **Identify key concepts**: 15-25 concepts per unit
3. **Create cards**: 3-5 cards per major concept = 50-80 cards per unit
4. **Extract relevant images**: 5-10 diagrams per unit
5. **Format properly**: Ensure MathJax, HTML, tabs
6. **Tag appropriately**: Use hierarchical tags (e.g., `unit3 core-topics key-concept`)

### Example Card Creation Workflow:

**Source Content (from PDF):**
```
The recursive algorithm computes solutions by:
1. Breaking down into smaller subproblems
2. Combining results from subproblems
3. Storing intermediate results
```

**Generated Card (Conceptual):**
```
Front: Why is this recursive algorithm more efficient than solving the problem directly?
Back: It uses <strong>dynamic programming</strong>:<br>1. Breaks complex problem into simpler subproblems<br>2. Stores intermediate results to avoid redundant calculations<br>3. Combines solutions systematically<br><br>Only needs to solve each subproblem once!
Tags: algorithms recursion optimization
```

**Generated Card (Visual - IMAGE IN FRONT):**
```
Front: <img src="diagram_example.png" style="max-width:500px;"><br>What relationships are shown in this diagram?
Back: The diagram shows:<br>1. <strong>Components A and B interact through interface C</strong><br>2. <strong>Information flows from top to bottom</strong><br>3. Each component has distinct responsibilities and dependencies
Tags: concepts structure relationships
```

## Quality Checklist

Before generating each deck, ensure:
- [ ] Cards test understanding, not memorization
- [ ] Examples are concrete and simple
- [ ] Math uses MathJax syntax `\(...\)` and `\[...\]`
- [ ] Images are extracted and properly referenced
- [ ] **Images are placed in the FRONT (question), not the BACK (answer)**
- [ ] Tags are consistent and hierarchical
- [ ] File uses TAB separators
- [ ] Headers are present
- [ ] No extensive calculations required
- [ ] Each card focuses on one concept
- [ ] Answers explain "why" not just "what"

## Reference Documents

1. **anki_flashcard_creation_guide.md**: Complete formatting reference
2. **exam_faq.txt**: Exam question style guidelines
3. **Existing knowledge base files**: Unit summaries for context

## Output Deliverables

Generate one file per unit:
- `unit0_intro_anki.txt` (30-50 cards)
- `unit1_fundamentals_anki.txt` (40-60 cards)
- `unit2_concepts_anki.txt` (50-70 cards)
- `unit3_core_topics_anki.txt` (60-80 cards)
- `unit4_methods_anki.txt` (60-80 cards)
- `unit5_techniques_anki.txt` (50-70 cards)
- `unit6_advanced_topics_anki.txt` (60-80 cards)
- `unit7_special_topics_anki.txt` (40-60 cards)
- `unit8_applications_anki.txt` (50-70 cards)

Plus extracted images in `outputs/images/` folder.

## Success Criteria

The generated decks should:
1. Cover all major concepts from each unit
2. Follow the exam-aligned question style
3. Include proper MathJax formatting
4. Incorporate relevant visual diagrams
5. Use consistent, hierarchical tagging
6. Be immediately importable into Anki
7. Test understanding through concrete examples
8. Require no extensive calculation to answer

## Notes

- Prioritize quality over quantity
- Cross-reference concepts between units where appropriate
- Use existing markdown knowledge base files for context
- Extract only high-quality, clear diagrams
- Keep answers concise but complete
- Include "why" explanations in answers
