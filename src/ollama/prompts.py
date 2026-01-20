"""
Prompt templates for image description using vision models.
"""


def get_image_description_prompt(
    page_number: int = None,
    page_context: str = None,
    subject_context: str = "lecture slides"
) -> str:
    """
    Get prompt template for describing lecture images.

    Args:
        page_number: Optional page number where image appears
        page_context: Optional text content from the page for context
        subject_context: Subject/course context (e.g., "Machine Learning lecture")

    Returns:
        Formatted prompt string
    """
    # Build contextual prompt if page context is available
    if page_context:
        prompt = f"""This image appears on page {page_number if page_number else 'N'} of {subject_context}.

Page context: {page_context[:300]}

Describe this image in 50-100 words, focusing on how it illustrates the concepts from this page. Include the image type and key visual elements."""
    else:
        # Fallback to basic prompt
        page_info = f"(page {page_number})" if page_number else ""
        prompt = f"""Describe this image from {subject_context} {page_info} in 50-100 words.

Include:
- Type (diagram, network architecture, algorithm, graph, formula, or table)
- Main concept shown
- Key visual elements

Be concise and technical."""

    return prompt


def get_detailed_description_prompt(subject_context: str = "lecture slides") -> str:
    """
    Get prompt for more detailed image analysis.

    Args:
        subject_context: Subject/course context (e.g., "Machine Learning lecture")

    Returns:
        Detailed prompt string
    """
    prompt = f"""Provide a detailed technical analysis of this image from {subject_context}.

Include:
1. Image Type: (network diagram, algorithm flowchart, mathematical formula, example problem, comparison table)
2. Core Concept: What key concept does this illustrate?
3. Visual Elements: Describe all nodes, edges, variables, equations, or steps shown
4. Mathematical Content: List any formulas, expressions, or mathematical notation
5. Pedagogical Purpose: What understanding does this image build?

Response should be 100-150 words, technical and precise."""

    return prompt


def get_quick_categorization_prompt() -> str:
    """
    Get prompt for quick image categorization.

    Returns:
        Quick categorization prompt
    """
    prompt = """Classify this lecture image in 20-30 words:

1. Type: [network|flowchart|formula|table|example|graph]
2. Topic: [brief topic name]
3. Contains math: [yes|no]

Be concise and specific."""

    return prompt


def get_custom_prompt(
    focus: str,
    word_count: str = "50-100",
    include_math: bool = True
) -> str:
    """
    Create a custom prompt with specific focus.

    Args:
        focus: What to focus on (e.g., "Bayesian networks", "algorithm steps")
        word_count: Target word count
        include_math: Whether to request mathematical details

    Returns:
        Custom prompt string
    """
    math_instruction = "Include any mathematical notation or formulas." if include_math else ""

    prompt = f"""Analyze this image focusing on {focus}.

Provide a {word_count} word description that includes:
1. Main concept or purpose
2. Key visual elements
3. How it relates to {focus}
{math_instruction}

Be technical and precise."""

    return prompt
