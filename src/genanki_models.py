"""
Anki model definitions for genanki.

Defines the note type (model) used for flashcards, with support for custom subjects.
"""

import genanki


def create_model(model_name: str = "Anki Flashcards", model_id: int = None) -> genanki.Model:
    """
    Create a genanki model with configurable name and ID.

    Args:
        model_name: Name of the model/note type
        model_id: Optional model ID (generates one from name hash if not provided)

    Returns:
        genanki.Model instance
    """
    if model_id is None:
        # Generate stable ID from model name hash
        model_id = abs(hash(model_name)) % (2 ** 31)

    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
            {'name': 'Tags'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '<div class="front">{{Front}}</div>',
                'afmt': '''<div class="front">{{Front}}</div>
<hr id="answer">
<div class="back">{{Back}}</div>
<div class="tags">{{Tags}}</div>''',
            },
        ],
        css='''.card {
    font-family: arial, sans-serif;
    font-size: 20px;
    text-align: left;
    color: black;
    background-color: white;
    padding: 20px;
}

.front {
    margin-bottom: 10px;
    font-weight: normal;
    text-align: center;
}

.back {
    margin-top: 10px;
    text-align: center;
}

.tags {
    margin-top: 20px;
    font-size: 12px;
    color: #888;
    font-style: italic;
    text-align: left;
}

/* Image handling */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 10px auto;
}

/* MathJax/LaTeX support */
.MathJax {
    font-size: 1em;
}

/* Code blocks if any */
code {
    background-color: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: monospace;
}

pre {
    background-color: #f4f4f4;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
}

/* Strong emphasis */
strong {
    font-weight: bold;
}

/* Lists */
ul, ol {
    margin-left: 20px;
}

li {
    margin: 5px 0;
}

/* Horizontal rule between question and answer */
hr#answer {
    margin: 15px 0;
    border: none;
    border-top: 2px solid #ccc;
}
'''
    )


# Use a stable model ID so all decks share the same note type
# This allows cards from different decks to be recognized as the same type
DEFAULT_MODEL_ID = 1894532617


# Define the default model for flashcards (backward compatibility)
DEFAULT_MODEL = create_model('Anki Flashcards', DEFAULT_MODEL_ID)

# Legacy alias for backward compatibility
PGM_MODEL_ID = DEFAULT_MODEL_ID
PGM_MODEL = DEFAULT_MODEL
