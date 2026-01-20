# Anki Flashcard Generator

Subject-agnostic tool to automatically generate high-quality Anki flashcards from lecture PDFs using Claude API.

## Features

- 🎓 **Multi-Subject Support**: Works for any academic subject (Math, CS, Physics, Biology, etc.)
- 🤖 **AI-Powered**: Uses Claude to generate conceptual, exam-aligned flashcards
- 📄 **PDF Processing**: Automatically extracts text and images from PDFs
- 🖼️ **Image Descriptions**: Optional Ollama integration for automatic image captioning
- 📦 **Ready to Import**: Generates .apkg files directly importable into Anki
- ⚙️ **Highly Configurable**: Customize card types, distributions, and generation prompts per subject

## Quick Start

### Installation

```bash
# Clone or download this repository
cd anki-flashcard-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Initialize for Your Subject

```bash
# Interactive setup
anki-gen init
```

This creates `config.yaml` with subject-specific settings and directory structure.

### Set Up API Key

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Workflow

```bash
# 1. Place PDFs in pdfs/ directory
cp ~/my-lectures/*.pdf pdfs/

# 2. Edit config.yaml to define your units
vim config.yaml

# 3. Extract PDFs to markdown and images
anki-gen extract --all

# 4. Generate flashcards (uses Claude API)
anki-gen generate --unit unit1_introduction

# 5. Package into .apkg files
anki-gen package --all

# 6. Import into Anki Desktop
# File → Import → select .apkg file
```

## Configuration

### Subject Configuration

Edit `config.yaml` to customize for your course:

```yaml
subject:
  name: "Linear Algebra"
  short_name: "LA"
  field: "Mathematics"
  description: "Vector spaces and linear transformations"

prompts:
  system_context: |
    You are generating flashcards for a {field} course on {name}.
    Focus on {description}.

  card_quality_focus:
    - "Test understanding, not memorization"
    - "Use concrete examples"
    - "Keep calculations simple"

  example_cards:
    - front: "Why must every basis for \\(\\mathbb{R}^n\\) have exactly \\(n\\) vectors?"
      back: "Because spanning requires \\(n\\) vectors..."
      tags: "linear-algebra basis"
```

### Unit Configuration

Define your course units:

```yaml
units:
  "lecture1.pdf":
    unit_name: unit1_introduction
    target_cards: 50
    tags: [unit1, introduction]

  "lecture2.pdf":
    unit_name: unit2_foundations
    target_cards: 60
    tags: [unit2, foundations]
```

### Card Distribution

Customize card type distribution:

```yaml
card_distribution:
  conceptual: 0.40          # Why/how questions
  worked_examples: 0.20     # Simple calculations
  algorithm: 0.20           # Step-by-step procedures
  pattern_recognition: 0.10 # Recognize patterns
  visual: 0.10             # Image-based cards
```

## CLI Commands

### `anki-gen init`
Initialize configuration for a new subject.

```bash
anki-gen init
```

### `anki-gen extract`
Extract PDFs to markdown and images.

```bash
anki-gen extract --all              # Extract all units
anki-gen extract --unit unit1       # Extract specific unit
anki-gen extract --all --no-images  # Skip image extraction
```

### `anki-gen generate`
Generate flashcards using Claude API.

```bash
anki-gen generate --unit unit1_introduction
anki-gen generate --unit unit2 --show-images
```

**Note**: This command uses the Claude API and requires an API key.

### `anki-gen package`
Package flashcards into .apkg files.

```bash
anki-gen package --all              # Package all units
anki-gen package --unit unit1       # Package specific unit
```

### `anki-gen list`
List configured units and their status.

```bash
anki-gen list
anki-gen list --detailed
```

### `anki-gen config`
View or validate configuration.

```bash
anki-gen config --show              # Display current config
anki-gen config --validate          # Validate config file
```

## Project Structure

```
project/
├── config.yaml              # Subject configuration
├── pdfs/                    # Source PDF files
├── outputs/
│   ├── markdown/            # Extracted text content
│   ├── images/              # Extracted images
│   ├── anki/               # Generated .txt flashcard files
│   ├── apkg/               # Packaged .apkg files
│   └── metadata/            # Image descriptions (if using Ollama)
├── src/
│   ├── cli/                # CLI commands
│   ├── flashcards/         # Flashcard generation
│   ├── ollama/             # Image description (optional)
│   └── ...
└── docs/
    └── SUBJECT_GUIDE.md    # Examples for different subjects
```

## Multi-Subject Usage

This tool works for any academic subject. See `docs/SUBJECT_GUIDE.md` for detailed examples:

- **Mathematics**: Linear Algebra, Calculus, Statistics
- **Computer Science**: Algorithms, Data Structures, Systems
- **Physics**: Mechanics, E&M, Quantum
- **Biology**: Molecular Biology, Genetics
- **Chemistry**: Organic Chemistry, Biochemistry
- **History**: World War II, Ancient Rome
- **Languages**: German Grammar, Spanish Vocabulary

Each subject has specific configuration recommendations and example cards.

## Card Quality Features

Generated flashcards follow learning science best practices:

- ✅ **Conceptual Focus**: Tests understanding, not memorization
- ✅ **Active Recall**: Questions require retrieval
- ✅ **Concrete Examples**: Uses specific scenarios
- ✅ **Simple Calculations**: Mental math only
- ✅ **Visual Integration**: Includes diagrams when relevant
- ✅ **Proper Formatting**: MathJax for math, HTML for structure

### Example Cards

**Conceptual (Mathematics)**:
```
Front: Why does every basis for ℝⁿ contain exactly n vectors?
Back: Two requirements:
      1. Span requires ≥n vectors to cover n dimensions
      2. Linear independence allows ≤n vectors
      Conclusion: exactly n vectors needed.
Tags: linear-algebra basis dimension
```

**Visual (Biology)**:
```
Front: [image: DNA replication fork]
       What are the two types of strands and why do they differ?
Back: 1. Leading strand: continuous synthesis toward fork
      2. Lagging strand: discontinuous (Okazaki fragments)
      Difference: DNA polymerase only extends 5'→3'
Tags: molecular-biology dna-replication
```

## Advanced Features

### Image Descriptions with Ollama

Enable automatic image captioning:

```yaml
ollama:
  enabled: true
  model: ministral-3:8b
  base_url: http://localhost:11434
```

```bash
# Ensure Ollama is running
ollama serve

# Extract with descriptions
anki-gen extract --all
```

### Programmatic Usage

Use as a Python library:

```python
from src.config import Config
from src.flashcards.generator import FlashcardGenerator

# Load configuration
config = Config('config.yaml')

# Create generator
generator = FlashcardGenerator(config=config)

# Generate flashcards
output_path = generator.generate_flashcards(
    unit_name='unit1_introduction',
    target_cards=50
)

# Validate output
validation = generator.validate_output(output_path)
print(f"Generated {validation['card_count']} cards")
```

### Custom Card Types

Modify `config.yaml` for subject-specific card types:

```yaml
card_distribution:
  conceptual: 0.50          # More conceptual for theory-heavy subjects
  worked_examples: 0.30     # More examples for math-heavy subjects
  algorithm: 0.10
  pattern_recognition: 0.05
  visual: 0.05
```

## Troubleshooting

### API Key Issues
```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Set key (Linux/Mac)
export ANTHROPIC_API_KEY='sk-ant-...'

# Set key (Windows)
set ANTHROPIC_API_KEY=sk-ant-...
```

### Missing Dependencies
```bash
# Reinstall dependencies
pip install -e .

# Verify installation
anki-gen --version
```

### Configuration Errors
```bash
# Validate config
anki-gen config --validate

# Show current config
anki-gen config --show
```

### Ollama Not Working
```bash
# Start Ollama
ollama serve

# Verify model is installed
ollama list

# Pull required model
ollama pull ministral-3:8b

# Disable if not needed
# In config.yaml: ollama.enabled: false
```

### Import Errors in Anki

Check these common issues:
- **Tab separation**: Must use actual tab characters, not spaces
- **Column count**: Exactly 3 columns (Front, Back, Tags)
- **UTF-8 encoding**: File must be UTF-8
- **HTML tags**: Verify `<strong>`, `<br>` tags are closed

## API Costs

This tool uses the Claude API for flashcard generation. Approximate costs:

- **Per unit** (50 cards): ~$0.10-0.30
- **Full course** (10 units, 500 cards): ~$1-3

Costs depend on:
- Markdown length
- Number of cards requested
- Model used (Sonnet 4.5 by default)

## Requirements

- Python 3.8+
- Anthropic API key (for flashcard generation)
- Ollama (optional, for image descriptions)

## Dependencies

Core dependencies:
- `anthropic` - Claude API client
- `PyMuPDF` - PDF processing
- `genanki` - Anki deck generation
- `click` - CLI framework
- `rich` - Terminal formatting
- `pyyaml` - Configuration

See `requirements.txt` for full list.

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## Contributing

Contributions welcome! Areas for improvement:

- Additional subject configurations (see `docs/SUBJECT_GUIDE.md`)
- Enhanced image processing
- Alternative LLM integrations
- Card quality metrics
- Web interface

## Resources

- [Anki Manual](https://docs.ankiweb.net/)
- [Claude API Documentation](https://docs.anthropic.com/)
- [Subject Configuration Guide](docs/SUBJECT_GUIDE.md)
- [LaTeX Math Guide](https://www.overleaf.com/learn/latex/Mathematical_expressions)

## License

MIT License - See LICENSE file for details.

## Credits

Created as a tool for automating Anki flashcard creation from educational materials. Uses:
- [Anthropic Claude](https://www.anthropic.com/) for intelligent flashcard generation
- [Ollama](https://ollama.ai/) for optional image descriptions
- [genanki](https://github.com/kerrickstaley/genanki) for Anki deck creation

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check `docs/SUBJECT_GUIDE.md` for subject-specific help
- Review `CLAUDE_TEMPLATE.md` for detailed usage guide
