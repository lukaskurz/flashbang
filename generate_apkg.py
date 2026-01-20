#!/usr/bin/env python3
"""
DEPRECATED: Use 'anki-gen package' instead.

This script is maintained for backwards compatibility.

New usage:
    anki-gen package --unit <unit_name>
    anki-gen package --all
"""

import genanki
import argparse
import logging
from pathlib import Path

# Print deprecation notice
print("=" * 80)
print("DEPRECATION NOTICE")
print("=" * 80)
print("This script (generate_apkg.py) is deprecated.")
print("Please use the new unified CLI instead:")
print()
print("  anki-gen package --unit <unit_name>")
print("  anki-gen package --all")
print()
print("Calling new CLI now...")
print("=" * 80)
print()

from src.config import Config
from src.tsv_parser import parse_anki_tsv
from src.image_extractor import prepare_card_for_apkg
from src.genanki_models import PGM_MODEL
from src.utils import setup_logging, ensure_dir


def generate_apkg_for_unit(unit_name: str, config: Config) -> dict:
    """
    Generate .apkg file for a single unit.

    Args:
        unit_name: Name of the unit (e.g., 'unit3_bayesian_networks')
        config: Configuration object

    Returns:
        Dictionary with generation statistics

    Raises:
        FileNotFoundError: If .txt file doesn't exist
        ValueError: If parsing fails
    """
    logger = logging.getLogger(__name__)

    # Parse TSV file
    txt_path = Path(config.anki_dir) / f"{unit_name}_anki.txt"
    logger.info(f"Parsing {txt_path}")

    deck_data = parse_anki_tsv(str(txt_path))

    # Create deck with unique ID based on unit name
    # Use hash to generate consistent ID for same unit
    deck_id = abs(hash(unit_name)) % (2 ** 31)
    deck = genanki.Deck(deck_id, deck_data['deck_name'])

    logger.info(f"Creating deck: {deck_data['deck_name']} (ID: {deck_id})")

    # Track all media files
    all_media = set()

    # Create notes
    for i, card in enumerate(deck_data['cards'], 1):
        # Process front and back for images
        front_html, front_media = prepare_card_for_apkg(card['front'], config.images_dir)
        back_html, back_media = prepare_card_for_apkg(card['back'], config.images_dir)

        all_media.update(front_media)
        all_media.update(back_media)

        # Create note
        tags_str = ' '.join(card['tags'])
        note = genanki.Note(
            model=PGM_MODEL,
            fields=[front_html, back_html, tags_str],
            tags=card['tags']
        )
        deck.add_note(note)

    logger.info(f"Created {len(deck_data['cards'])} notes with {len(all_media)} unique images")

    # Create package with media
    package = genanki.Package(deck)
    package.media_files = list(all_media)

    # Ensure output directory exists
    ensure_dir(config.apkg_dir)

    # Write .apkg file
    output_path = Path(config.apkg_dir) / f"{unit_name}_anki.apkg"
    package.write_to_file(str(output_path))

    logger.info(f"Generated {output_path}")

    return {
        'unit': unit_name,
        'deck_name': deck_data['deck_name'],
        'cards': len(deck_data['cards']),
        'media': len(all_media),
        'output': output_path
    }


def main():
    """Main entry point - calls new CLI."""
    parser = argparse.ArgumentParser(
        description='Generate .apkg Anki decks with embedded images from .txt files'
    )
    parser.add_argument(
        '--unit',
        help='Generate for specific unit (e.g., unit3_bayesian_networks)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all units'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    args = parser.parse_args()

    # Use new CLI instead
    from src.cli.package import package_command

    try:
        success = package_command(unit=args.unit, package_all=args.all)
        return 0 if success else 1
    except Exception as e:
        print(f"\nError: {e}")
        print("\nFalling back to old implementation...")

        # Setup logging
        log_level = logging.DEBUG if args.verbose else logging.INFO
        setup_logging('outputs/apkg_generation.log', log_level)

        logger = logging.getLogger(__name__)

        # Load configuration
        config = Config()

        if args.all:
            # Generate for all units
            logger.info("Generating .apkg files for all units...")

            all_units = config.get_all_units()
            stats_list = []

            for pdf_filename, unit_info in all_units.items():
                unit_name = unit_info['unit_name']
                try:
                    stats = generate_apkg_for_unit(unit_name, config)
                    stats_list.append(stats)
                    print(f"✓ {stats['unit']}: {stats['cards']} cards, {stats['media']} images → {stats['output'].name}")
                except Exception as e:
                    logger.error(f"Failed to generate {unit_name}: {e}")
                    print(f"✗ {unit_name}: FAILED - {e}")

            # Summary
            total_cards = sum(s['cards'] for s in stats_list)
            total_media = sum(s['media'] for s in stats_list)
            print(f"\nTotal: {len(stats_list)} decks, {total_cards} cards, {total_media} images")

        elif args.unit:
            # Generate for specific unit
            try:
                stats = generate_apkg_for_unit(args.unit, config)
                print(f"✓ Generated {stats['output']}")
                print(f"  Deck: {stats['deck_name']}")
                print(f"  Cards: {stats['cards']}")
                print(f"  Images: {stats['media']}")
            except Exception as e:
                logger.error(f"Failed to generate {args.unit}: {e}", exc_info=True)
                print(f"✗ FAILED: {e}")
                return 1

        else:
            # No arguments provided
            parser.print_help()
            print("\nExamples:")
            print("  python generate_apkg.py --unit unit3_bayesian_networks")
            print("  python generate_apkg.py --all")
            return 1

        return 0


if __name__ == '__main__':
    exit(main())
