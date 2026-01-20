# Anki Flashcard Generation from Lecture PDFs

## Project Overview

This project automates the creation of Anki flashcard decks from lecture PDFs. The goal is to create high-quality flashcards that test conceptual understanding, aligned with your learning objectives.

**Subject Configuration**: Edit `config.yaml` to specify your subject name, field, and description. This information is used to customize flashcard generation prompts.

## Input Structure

```
project_folder/
├── CLAUDE.md (this file)
├── config.yaml (subject configuration and settings)
├── pdfs/
│   └── (your PDF files)
└── outputs/
    ├── markdown/
    ├── images/
    ├── anki/
    └── apkg/
```

## Quick Start

1. **Initialize for your subject**:
   ```bash
   anki-gen init
   ```
   This creates `config.yaml` and directory structure.

2. **Configure your units** in `config.yaml`:
   ```yaml
   units:
     "lecture1.pdf":
       unit_name: unit1_introduction
       target_cards: 50
       tags: [unit1, introduction]
   ```

3. **Extract PDFs**:
   ```bash
   anki-gen extract --all
   ```

4. **Generate flashcards**:
   ```bash
   anki-gen generate --unit unit1_introduction
   ```

5. **Package into .apkg**:
   ```bash
   anki-gen package --all
   ```

## Output Format

### File Format
- One `.txt` file per unit in `outputs/anki/`
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

Create cards that:
1. **Test understanding, not memorization** - Focus on "why" and "how"
2. **Use concrete examples** - Embed questions in specific scenarios
3. **Keep calculations simple** - No extensive computation required
4. **Focus on concepts** - Understanding over formula recall

These guidelines are configurable in `config.yaml` under `prompts.card_quality_focus`.

### Card Types (Configurable Distribution)

Default distribution in `config.yaml`:
- **40% Conceptual Understanding**: Why/how questions, test intuition
- **20% Simple Worked Examples**: Tiny scenarios with obvious answers
- **20% Algorithm/Process Comprehension**: Step analysis, key insights
- **10% Pattern Recognition**: Identify reasoning patterns
- **10% Visual/Diagram-Based**: Use extracted images

**IMPORTANT for visual cards**: Place the image in the **Front** (question), not the Back (answer). The question should reference the diagram, and the answer provides the explanation.

## Customization

### Subject-Specific Prompts

Edit `config.yaml` to customize how flashcards are generated:

```yaml
subject:
  name: "Your Subject Name"
  short_name: "YSN"  # Deck prefix
  field: "Your Field"
  description: "Description of what the course covers"

prompts:
  system_context: |
    You are generating flashcards for a {field} course on {name}.
    Focus on {description}.

  card_quality_focus:
    - "Test understanding, not memorization"
    - "Use concrete examples"
    - "Focus on key concepts"

  example_cards:
    - front: "Your example question?"
      back: "Your example answer with <strong>formatting</strong>"
      tags: "your tags here"
```

### Card Distribution

Adjust the card type distribution in `config.yaml`:

```yaml
card_distribution:
  conceptual: 0.50          # Increase conceptual cards to 50%
  worked_examples: 0.20
  algorithm: 0.15
  pattern_recognition: 0.10
  visual: 0.05
```

## Image Handling

### Extraction

Images are automatically extracted from PDFs and can be described using Ollama:

```bash
anki-gen extract --all  # Extracts and describes images
```

### Usage in Cards

Reference images in the **Front** (question):
```html
<img src="diagram_example.png" style="max-width:500px;">
<br>What concept does this diagram illustrate?
```

### Configuration

```yaml
processing:
  extract_images: true
  min_image_size: [100, 100]
  image_format: png

ollama:
  enabled: true  # Set to false to skip image descriptions
  model: ministral-3:8b
```

## Example Card Formatting

### Conceptual Card
```
Front: Why does this algorithm use recursion instead of iteration?
Back: Recursion allows <strong>natural decomposition</strong> of the problem:<br>1. Each step reduces problem size<br>2. Base case provides termination<br>3. Call stack maintains state automatically
Tags: algorithms recursion design
```

### Visual Card (IMAGE IN FRONT)
```
Front: <img src="process_diagram.png" style="max-width:500px;"><br>What are the three main stages shown in this process?
Back: 1. <strong>Input validation</strong><br>2. <strong>Data transformation</strong><br>3. <strong>Output generation</strong><br><br>Each stage has distinct error handling.
Tags: processes architecture diagrams
```

### Mathematical Card
```
Front: What is the time complexity of binary search and why?
Back: <strong>\(O(\log n)\)</strong><br><br>Each comparison eliminates half the remaining elements:<br>\[T(n) = T(n/2) + O(1)\]<br>Solving this recurrence gives \(O(\log n)\).
Tags: algorithms complexity analysis
```

## Workflow Details

### 1. PDF Extraction
```bash
anki-gen extract --unit unit1_intro        # Single unit
anki-gen extract --all                     # All units
anki-gen extract --all --no-images         # Skip images
anki-gen extract --all --no-describe       # Skip Ollama descriptions
```

Outputs:
- Markdown: `outputs/markdown/unit1_intro.md`
- Images: `outputs/images/*.png`
- Metadata: `outputs/metadata/image_descriptions.json`

### 2. Flashcard Generation

Uses Claude API to generate flashcards from markdown:

```bash
anki-gen generate --unit unit1_intro
```

The generation uses prompts configured in `config.yaml` to ensure subject-appropriate cards.

### 3. Packaging

Creates importable .apkg files:

```bash
anki-gen package --unit unit1_intro        # Single unit
anki-gen package --all                     # All units
```

Output: `outputs/apkg/unit1_intro_anki.apkg`

### 4. Import to Anki

In Anki Desktop: **File → Import** → Select `.apkg` file

## CLI Commands Reference

```bash
anki-gen init                    # Initialize new subject configuration
anki-gen list                    # List configured units
anki-gen config --show           # Show current configuration
anki-gen extract --all           # Extract all PDFs
anki-gen generate --unit <name>  # Generate flashcards for unit
anki-gen package --all           # Package all units to .apkg
```

## Advanced: Programmatic Usage

Generate flashcards programmatically:

```python
from src.config import Config
from src.flashcards.generator import FlashcardGenerator

# Load config
config = Config('config.yaml')

# Create generator
generator = FlashcardGenerator(config=config)

# Generate flashcards
output_path = generator.generate_flashcards(
    unit_name='unit1_intro',
    target_cards=50
)

# Validate
validation = generator.validate_output(output_path)
print(f"Generated {validation['card_count']} cards")
```

## Troubleshooting

### Images not extracting
- Check `config.yaml`: `processing.extract_images: true`
- Verify PDFs contain extractable images (not scanned/OCR)
- Lower `min_image_size` threshold

### Ollama descriptions failing
- Ensure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Set `ollama.enabled: false` to skip descriptions

### Cards not generating
- Verify `ANTHROPIC_API_KEY` environment variable is set
- Check markdown file exists: `outputs/markdown/<unit_name>.md`
- Review Claude API rate limits

### .apkg import errors
- Validate .txt format: all 3 columns present, tab-separated
- Check for tab characters in card content (use `<br>` instead)
- Ensure UTF-8 encoding

## File Organization

```
outputs/
├── markdown/           # Extracted text from PDFs
│   └── unit1_intro.md
├── images/             # Extracted images
│   └── unit1_page5_img1.png
├── metadata/           # Image descriptions
│   └── image_descriptions.json
├── anki/              # Generated flashcard .txt files
│   └── unit1_intro_anki.txt
└── apkg/              # Packaged .apkg files
    └── unit1_intro_anki.apkg
```

## Tips for Quality Flashcards

1. **Review and edit**: Generated flashcards are a starting point; review and refine them
2. **Consistent tagging**: Use hierarchical tags (e.g., `unit1 concept-name sub-concept`)
3. **One concept per card**: Break complex topics into multiple simple cards
4. **Active recall**: Frame questions to require retrieval, not recognition
5. **Spaced repetition**: Trust Anki's algorithm; review regularly

## See Also

- `docs/SUBJECT_GUIDE.md` - Examples for different subjects
- `config.yaml` - Your subject configuration
- [Anki Manual](https://docs.ankiweb.net/) - Official Anki documentation
