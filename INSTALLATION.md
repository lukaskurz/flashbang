# Installation Guide for anki-gen CLI

## Quick Start

The anki-gen tool is now installed and ready to use! The package has been successfully installed in development mode.

## Verify Installation

Check that the CLI is working:

```bash
anki-gen --version
anki-gen --help
```

## Available Commands

### 1. List Units
View all available units and their status:

```bash
anki-gen list                # Basic list
anki-gen list --detailed     # Show file existence status
anki-gen list --stats        # Show statistics
```

### 2. Extract PDFs
Extract PDFs to markdown with automatic image descriptions:

```bash
anki-gen extract                        # Extract all PDFs
anki-gen extract --unit unit1_intro     # Extract specific unit
anki-gen extract --no-describe          # Skip image descriptions
anki-gen extract --no-images            # Skip image extraction
```

**What happens during extraction:**
- Extracts text from PDFs → `outputs/markdown/*.md`
- Extracts images → `outputs/images/*.png`
- Generates descriptions with Ollama → `outputs/metadata/image_descriptions.json`
- Injects descriptions into markdown for Claude to see

### 3. Generate Flashcards
Generate flashcards using Claude Code:

```bash
anki-gen generate --unit unit1_introduction
anki-gen generate --unit unit3_bayesian_networks --show-images
```

**Output:** `outputs/anki/<unit>_anki.txt` (TSV format)

### 4. Package into .apkg
Create Anki package files:

```bash
anki-gen package --unit unit1_introduction   # Package specific unit
anki-gen package --all                       # Package all units
```

**Output:** `outputs/apkg/<unit>_anki.apkg`

### 5. Configuration
Manage settings:

```bash
anki-gen config                # Show basic info
anki-gen config --show         # Display full config
anki-gen config --validate     # Validate configuration
```

## Ollama Setup (for Image Descriptions)

The tool integrates with Ollama for automatic image description generation.

### Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.com

### Pull Vision Model

```bash
ollama pull ministral-3:8b
```

### Start Ollama Server

```bash
# In a separate terminal:
ollama serve

# Or run in background (macOS/Linux):
ollama serve &
```

### Verify Ollama

```bash
anki-gen config --validate
```

Should show: "✓ Ollama is available"

## Complete Workflow Example

```bash
# 1. Check available units
anki-gen list --detailed

# 2. Extract PDFs (includes automatic image descriptions)
anki-gen extract

# 3. Generate flashcards for a unit
anki-gen generate --unit unit3_bayesian_networks

# 4. (Claude Code will generate the TSV file)

# 5. Package into .apkg
anki-gen package --unit unit3_bayesian_networks

# 6. Import into Anki Desktop
# Open Anki → File → Import → Select outputs/apkg/unit3_bayesian_networks_anki.apkg
```

## Backwards Compatibility

Old scripts still work but show deprecation notices:

```bash
python extract_pdfs.py           # → Calls anki-gen extract
python generate_cards.py --unit  # → Calls anki-gen generate
python generate_apkg.py --all    # → Calls anki-gen package
```

## Configuration File

Edit `config.yaml` to customize:

```yaml
ollama:
  enabled: true
  base_url: http://localhost:11434
  model: ministral-3:8b
  timeout: 30
  batch_size: 5
  max_retries: 3
  description_length: concise  # 50-100 words
```

## Troubleshooting

### "Ollama not available"
1. Check if Ollama is running: `curl http://localhost:11434/api/tags`
2. Start Ollama: `ollama serve`
3. Pull the model: `ollama pull ministral-3:8b`

### "Command not found: anki-gen"
Ensure the package is installed:
```bash
pip install -e .
```

### "Module not found" errors
Reinstall dependencies:
```bash
pip install -r requirements.txt
```

## File Structure

```
project/
├── src/
│   ├── cli/              # CLI commands (new!)
│   ├── ollama/           # Ollama integration (new!)
│   ├── metadata/         # Metadata storage (new!)
│   └── ...               # Existing modules
├── outputs/
│   ├── markdown/         # Extracted text
│   ├── images/           # Extracted images
│   ├── metadata/         # Image descriptions (new!)
│   ├── anki/             # Generated TSV files
│   └── apkg/             # Packaged .apkg files
├── pdfs/                 # Source PDFs
├── config.yaml           # Configuration (updated)
├── setup.py              # Package installation (new!)
└── requirements.txt      # Dependencies (updated)
```

## What's New

1. **Unified CLI** - Single `anki-gen` command replaces 4 scripts
2. **Ollama Integration** - Automatic image descriptions using local vision AI
3. **Metadata Storage** - JSON-based image metadata with descriptions
4. **Enhanced Markdown** - Image descriptions injected for Claude to read
5. **Rich Output** - Beautiful terminal output with progress bars and tables
6. **Better Error Handling** - Helpful error messages and graceful degradation

## Next Steps

1. Extract PDFs: `anki-gen extract`
2. Generate flashcards: `anki-gen generate --unit <name>`
3. Package: `anki-gen package --unit <name>`
4. Import to Anki Desktop

Enjoy your automated flashcard generation! 🎉
