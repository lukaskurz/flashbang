#!/usr/bin/env python3
"""
DEPRECATED: Use 'anki-gen extract' instead.

This script is maintained for backwards compatibility.
It now calls the new unified CLI internally.

New usage:
    anki-gen extract
    anki-gen extract --unit unit1_introduction
    anki-gen extract --no-images
    anki-gen extract --no-describe
"""

import sys
import time
import logging
from pathlib import Path

# Print deprecation notice
print("=" * 80)
print("DEPRECATION NOTICE")
print("=" * 80)
print("This script (extract_pdfs.py) is deprecated.")
print("Please use the new unified CLI instead:")
print()
print("  anki-gen extract")
print()
print("The new CLI provides the same functionality with better features:")
print("  - Automatic image descriptions with Ollama")
print("  - Rich progress bars and output")
print("  - Better error handling")
print()
print("Calling new CLI now...")
print("=" * 80)
print()

from src.config import load_config
from src.pdf_processor import PDFProcessor
from src.markdown_generator import MarkdownGenerator
from src import utils


def extract_all_pdfs():
    """Extract all PDFs to markdown files."""
    start_time = time.time()

    # Setup logging
    logger = utils.setup_logging()
    logger.info("="*60)
    logger.info("PDF Extraction to Markdown")
    logger.info("="*60)

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return False

    # Ensure output directories exist
    utils.ensure_dir(config.markdown_dir)
    utils.ensure_dir(config.images_dir)

    # Get all units
    units = config.get_all_units()
    total_units = len(units)
    logger.info(f"Found {total_units} PDFs to process\n")

    # Statistics tracking
    stats = {
        'total_pdfs': 0,
        'successful_pdfs': 0,
        'failed_pdfs': 0,
        'total_images': 0,
        'errors': []
    }

    # Process each PDF
    for idx, (pdf_filename, unit_info) in enumerate(units.items(), 1):
        unit_name = unit_info['unit_name']

        logger.info(f"[{idx}/{total_units}] Processing: {pdf_filename}")
        logger.info(f"  Unit: {unit_name}")

        stats['total_pdfs'] += 1

        # Paths
        pdf_path = f"pdfs/{pdf_filename}"
        markdown_path = f"{config.markdown_dir}/{unit_name}.md"

        try:
            # Extract PDF content
            with PDFProcessor(pdf_path, unit_name) as processor:
                # Extract text
                logger.info(f"  Extracting text...")
                pages_data = processor.extract_text_by_page()
                logger.info(f"    {len(pages_data)} pages")

                # Extract images (if configured)
                images = []
                if config.extract_images:
                    logger.info(f"  Extracting images...")
                    images = processor.extract_images(
                        output_dir=config.images_dir,
                        min_size=config.min_image_size
                    )
                    logger.info(f"    {len(images)} images")
                    stats['total_images'] += len(images)

            # Generate markdown
            logger.info(f"  Generating markdown...")
            md_gen = MarkdownGenerator(pages_data, images, unit_name)
            markdown = md_gen.generate_markdown()

            # Save markdown
            utils.save_file(markdown_path, markdown)
            logger.info(f"  ✓ Saved: {markdown_path}")
            logger.info(f"    Size: {len(markdown)} characters\n")

            stats['successful_pdfs'] += 1

        except Exception as e:
            logger.error(f"  ✗ Failed: {e}\n")
            stats['failed_pdfs'] += 1
            stats['errors'].append(f"{pdf_filename}: {str(e)}")

    # Final summary
    elapsed = time.time() - start_time

    logger.info("\n" + "="*60)
    logger.info("EXTRACTION COMPLETE")
    logger.info("="*60)
    logger.info(f"Total PDFs: {stats['total_pdfs']}")
    logger.info(f"Successful: {stats['successful_pdfs']}")
    logger.info(f"Failed: {stats['failed_pdfs']}")
    logger.info(f"Total images extracted: {stats['total_images']}")
    logger.info(f"Processing time: {elapsed:.2f} seconds")

    if stats['errors']:
        logger.warning(f"\nErrors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            logger.warning(f"  - {error}")

    logger.info("\n" + "="*60)
    logger.info("NEXT STEPS:")
    logger.info("="*60)
    logger.info("1. Review markdown files in: outputs/markdown/")
    logger.info("2. Check extracted images in: outputs/images/")
    logger.info("3. Generate flashcards with:")
    logger.info("   python generate_cards.py --unit unit1_introduction")
    logger.info("="*60)

    return stats['failed_pdfs'] == 0


def main():
    """Main entry point - calls new CLI."""
    # Use new CLI instead
    from src.cli.extract import extract_command

    try:
        success = extract_command(unit_filter=None, no_images=False, no_describe=False)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nFalling back to old implementation...")
        success = extract_all_pdfs()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
