<div align="center">
  <img src="logo_transparent.png" alt="flashbang" width="400">

  # flashbang

  Bang out flashcards from PDFs instantly

  <sub>(if you have an AI datacenter worth six figures, otherwise it's gonna take some minutes)</sub>
</div>

## Features

- 🚀 **Lightning Fast**: Generate hundreds of flashcards in seconds
- 🎓 **Subject Agnostic**: Works for any academic subject
- 🤖 **AI-Powered**: Uses Claude API or local Ollama for quality generation
- 📄 **PDF Processing**: Auto-extracts text and images
- 🖼️ **Image Support**: Optional image descriptions with Ollama
- 📦 **Ready to Import**: Direct .apkg output for Anki

## Quick Start

### Installation

```bash
# Clone or download this repository
cd flashbang

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Setup

```bash
# Interactive setup
flashbang init
```

This creates `config.yaml` with your subject settings and directory structure.

### Set Up API Key

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Workflow

```bash
# 1. Place PDFs in pdfs/ directory
cp ~/my-lectures/*.pdf pdfs/

# 2. Extract PDFs to markdown and images
flashbang extract --all

# 3. Generate flashcards (uses Claude API)
flashbang generate --unit unit_intro

# 4. Package into .apkg files
flashbang package --all

# 5. Import into Anki Desktop
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
```

### Unit Configuration

#### Auto-Discovery (Recommended)

Simply place PDFs in the `pdfs/` directory and they will be auto-discovered:

```bash
pdfs/
├── Intro.pdf
├── Unit_1.pdf
├── Unit_2.pdf
└── Unit_3.pdf
```

Units are auto-configured with sensible defaults.

```yaml
# Optional: Set defaults for all auto-discovered units
defaults:
  target_cards: 50  # Default number of cards per unit
```

#### Custom Configuration (Optional)

Override specific units in `config.yaml`:

```yaml
defaults:
  target_cards: 50  # Default for all units

units:
  # Only configure units that need custom settings
  "Intro.pdf":
    unit_name: unit0_intro  # Custom name
    target_cards: 30        # Custom target
    tags: [unit0, introduction, overview]

  "Unit_1.pdf":
    target_cards: 60  # Override just target_cards
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

### Generation Providers

Choose between Claude API or local Ollama:

```yaml
generation:
  provider: "claude"  # Options: "claude", "ollama"

  claude:
    model: "claude-sonnet-4-20250514"
    api_key_env: "ANTHROPIC_API_KEY"
    max_tokens: 16000

  ollama:
    base_url: "http://localhost:11434"
    model: "ministral-3:14b"
    timeout: 120
```

**Claude (Default)**
- High quality, excellent instruction following
- API costs: ~$0.10-0.30 per unit

**Ollama (Local, Free)**
- Free, local, privacy-focused
- Requires local setup, may need prompt tuning

```bash
# Use Claude (default)
flashbang generate --unit unit1_intro

# Use Ollama (override)
flashbang generate --unit unit1 --provider ollama
```

## CLI Commands

### Command Reference

**`flashbang init`** - Initialize configuration for a new subject
```bash
flashbang init
```

**`flashbang extract`** - Extract PDFs to markdown and images
```bash
flashbang extract --all              # Extract all units
flashbang extract --unit unit1       # Extract specific unit
flashbang extract --all --no-images  # Skip image extraction
```

**`flashbang generate`** - Generate flashcards using Claude or Ollama
```bash
flashbang generate --unit unit1_introduction
flashbang generate --unit unit2 --show-images
flashbang generate --unit unit3 --provider ollama
```

**`flashbang package`** - Package flashcards into .apkg files
```bash
flashbang package --all              # Package all units
flashbang package --unit unit1       # Package specific unit
```

**`flashbang list`** - List configured units and their status
```bash
flashbang list
flashbang list --detailed
```

**`flashbang config`** - View or validate configuration
```bash
flashbang config --show              # Display current config
flashbang config --validate          # Validate config file
```

## Card Quality

Generated flashcards follow learning science best practices:

- ✅ **Conceptual Focus**: Tests understanding, not memorization
- ✅ **Active Recall**: Questions require retrieval
- ✅ **Concrete Examples**: Uses specific scenarios
- ✅ **Simple Calculations**: Mental math only
- ✅ **Visual Integration**: Includes diagrams when relevant

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
└── src/
    ├── cli/                # CLI commands
    ├── flashcards/         # Flashcard generation
    ├── ollama/             # Image description (optional)
    └── ...
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
# 1. Install Ollama (ollama.ai)
# 2. Pull model
ollama pull ministral-3:8b

# 3. Start Ollama
ollama serve

# 4. Extract with descriptions
flashbang extract --all
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
flashbang --version
```

### Configuration Errors
```bash
# Validate config
flashbang config --validate

# Show current config
flashbang config --show
```

### Ollama Not Working
```bash
# Start Ollama
ollama serve

# Verify model is installed
ollama list

# Pull required model
ollama pull ministral-3:8b
```

### Import Errors in Anki

Common issues:
- **Tab separation**: Must use actual tab characters, not spaces
- **Column count**: Exactly 3 columns (Front, Back, Tags)
- **UTF-8 encoding**: File must be UTF-8
- **HTML tags**: Verify `<strong>`, `<br>` tags are closed

## API Costs

Approximate costs using Claude API:

- **Per unit** (50 cards): ~$0.10-0.30
- **Full course** (10 units, 500 cards): ~$1-3

## Requirements

- Python 3.8+
- Anthropic API key (for Claude)
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

## License

MIT License - See LICENSE file for details.

## Credits

Created as a tool for automating Anki flashcard creation from educational materials. Uses:
- [Anthropic Claude](https://www.anthropic.com/) for intelligent flashcard generation
- [Ollama](https://ollama.ai/) for optional image descriptions
- [genanki](https://github.com/kerrickstaley/genanki) for Anki deck creation
