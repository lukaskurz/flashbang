#!/usr/bin/env python3
"""
Setup script for anki-gen CLI tool.

Install with:
    pip install -e .

This creates the 'anki-gen' command.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="anki-gen",
    version="1.0.0",
    description="Anki flashcard generation tool for automatic deck creation from lecture PDFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lukas Kurz",
    author_email="",
    url="",
    packages=find_packages(exclude=["tests", "venv", "outputs", "pdfs", "exam"]),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'anki-gen=src.cli.main:cli',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="anki flashcards education automation pdf-extraction",
)
