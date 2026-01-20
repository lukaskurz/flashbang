# Subject-Specific Configuration Guide

This guide provides example configurations and best practices for using anki-gen with different academic subjects.

## Table of Contents

- [Mathematics](#mathematics)
- [Computer Science](#computer-science)
- [Physics](#physics)
- [Biology](#biology)
- [Chemistry](#chemistry)
- [History](#history)
- [Language Learning](#language-learning)

---

## Mathematics

### Configuration Example

```yaml
subject:
  name: "Linear Algebra"
  short_name: "LA"
  field: "Mathematics"
  description: "Vector spaces, linear transformations, and eigenanalysis"

prompts:
  system_context: |
    You are generating flashcards for a Mathematics course on Linear Algebra.
    Focus on vector spaces, linear transformations, and eigenanalysis.
    Emphasize geometric intuition alongside algebraic techniques.

  card_quality_focus:
    - "Balance computational and conceptual understanding"
    - "Include geometric interpretations"
    - "Use concrete matrix examples (2x2, 3x3)"
    - "Connect abstract concepts to applications"

  example_cards:
    - front: "Why must every basis for \\(\\mathbb{R}^n\\) contain exactly \\(n\\) vectors?"
      back: "Two key reasons:<br>1. <strong>Span requires \\(n\\) vectors</strong> to cover all \\(n\\) dimensions<br>2. <strong>Linear independence allows maximum \\(n\\) vectors</strong> in \\(n\\)-dimensional space<br><br>Fewer than \\(n\\) can't span; more than \\(n\\) must be dependent."
      tags: "linear-algebra basis dimension"
```

### Card Type Distribution

```yaml
card_distribution:
  conceptual: 0.45        # Heavy on understanding why theorems work
  worked_examples: 0.30   # Many computation examples
  algorithm: 0.15         # Procedures (row reduction, Gram-Schmidt)
  pattern_recognition: 0.05
  visual: 0.05           # Geometric diagrams
```

### Best Practices

- **Include both proof sketches and calculations**
- **Use 2×2 or 3×3 matrices for concrete examples**
- **Always provide geometric interpretation when possible**
- **Tag by topic**: `linear-algebra eigenvalues diagonalization`

---

## Computer Science

### Configuration Example

```yaml
subject:
  name: "Algorithms and Data Structures"
  short_name: "ADS"
  field: "Computer Science"
  description: "Algorithm design, analysis, and fundamental data structures"

prompts:
  system_context: |
    You are generating flashcards for a Computer Science course on Algorithms and Data Structures.
    Focus on algorithm design, complexity analysis, and fundamental data structures.
    Emphasize understanding trade-offs and when to use each approach.

  card_quality_focus:
    - "Explain time/space complexity trade-offs"
    - "Use small examples (arrays of 5-10 elements)"
    - "Focus on algorithmic intuition, not memorizing code"
    - "Include best/average/worst case scenarios"

  example_cards:
    - front: "Why does quicksort have \\(O(n^2)\\) worst case but is often faster than mergesort in practice?"
      back: "Worst case \\(O(n^2)\\) occurs with poor pivot choices (already sorted data).<br><br><strong>Practical advantages:</strong><br>1. In-place sorting (\\(O(1)\\) extra space vs \\(O(n)\\))<br>2. Better cache locality<br>3. Smaller constant factors<br>4. Randomization makes worst case rare"
      tags: "algorithms sorting quicksort complexity"
```

### Card Type Distribution

```yaml
card_distribution:
  conceptual: 0.40        # Why algorithms work
  worked_examples: 0.25   # Trace algorithm on small inputs
  algorithm: 0.25         # Steps and invariants
  pattern_recognition: 0.10  # When to use which structure
  visual: 0.00           # Usually not needed for CS
```

---

## Physics

### Configuration Example

```yaml
subject:
  name: "Classical Mechanics"
  short_name: "CM"
  field: "Physics"
  description: "Newtonian mechanics, energy, momentum, and rotational dynamics"

prompts:
  system_context: |
    You are generating flashcards for a Physics course on Classical Mechanics.
    Focus on Newtonian mechanics, energy, momentum, and rotational dynamics.
    Emphasize physical intuition and problem-solving strategies.

  card_quality_focus:
    - "Connect math to physical intuition"
    - "Use realistic but simple scenarios (blocks, pendulums, etc.)"
    - "Emphasize when to apply which principle"
    - "Include units and typical magnitudes"

  example_cards:
    - front: "A 2kg block slides down a frictionless 30° incline. Why use energy conservation instead of force analysis?"
      back: "<strong>Energy approach is simpler:</strong><br>1. Don't need intermediate accelerations<br>2. Directly connects initial/final states<br>3. Only need: \\(mgh = \\frac{1}{2}mv^2\\)<br><br>Force method requires resolving components and integrating \\(a(t)\\)."
      tags: "mechanics energy conservation problem-solving"
```

### Best Practices

- **Include free-body diagrams in visual cards**
- **Always specify units in worked examples**
- **Explain when to use each conservation law**
- **Use realistic numbers** (masses in kg, distances in m)

---

## Biology

### Configuration Example

```yaml
subject:
  name: "Molecular Biology"
  short_name: "MB"
  field: "Biology"
  description: "DNA replication, transcription, translation, and gene regulation"

prompts:
  system_context: |
    You are generating flashcards for a Biology course on Molecular Biology.
    Focus on DNA replication, transcription, translation, and gene regulation.
    Emphasize mechanisms, key proteins, and regulation.

  card_quality_focus:
    - "Focus on mechanisms and why they matter"
    - "Connect structure to function"
    - "Use specific examples (lac operon, p53, etc.)"
    - "Emphasize regulation and control"

  example_cards:
    - front: "Why does DNA replication require both leading and lagging strands?"
      back: "<strong>Due to antiparallel strands + 5'→3' synthesis:</strong><br>1. DNA polymerase only extends 5'→3'<br>2. Strands are antiparallel (run opposite directions)<br>3. Leading: continuous synthesis toward fork<br>4. Lagging: discontinuous (Okazaki fragments) away from fork"
      tags: "molecular-biology dna-replication mechanisms"
```

### Card Type Distribution

```yaml
card_distribution:
  conceptual: 0.50        # Understanding mechanisms
  worked_examples: 0.10   # Tracing processes
  algorithm: 0.15         # Multi-step processes
  pattern_recognition: 0.15  # Recognizing structures/motifs
  visual: 0.10           # Diagrams of structures
```

---

## Chemistry

### Configuration Example

```yaml
subject:
  name: "Organic Chemistry"
  short_name: "OCHEM"
  field: "Chemistry"
  description: "Organic reactions, mechanisms, and synthesis strategies"

prompts:
  system_context: |
    You are generating flashcards for a Chemistry course on Organic Chemistry.
    Focus on organic reactions, mechanisms, and synthesis strategies.
    Emphasize understanding reaction mechanisms and predicting products.

  card_quality_focus:
    - "Focus on mechanisms, not memorization"
    - "Explain electron flow and why reactions occur"
    - "Use concrete examples with simple molecules"
    - "Connect reactivity to structure"

  example_cards:
    - front: "Why do tertiary carbocations form faster than primary in S_N1 reactions?"
      back: "<strong>Stability determines formation rate:</strong><br>1. Tertiary: stabilized by 3 alkyl groups (hyperconjugation + induction)<br>2. Primary: only 1 alkyl group<br>3. Rate-determining step is carbocation formation<br>4. Lower activation energy → faster reaction"
      tags: "organic-chemistry carbocations sn1 reactivity"
```

### Best Practices

- **Use ChemDraw or similar for structure images**
- **Show electron-pushing arrows in mechanisms**
- **Include reaction conditions** (temp, solvent, catalysts)
- **Focus on patterns** (nucleophile/electrophile, leaving groups)

---

## History

### Configuration Example

```yaml
subject:
  name: "World War II"
  short_name: "WW2"
  field: "History"
  description: "Causes, major events, and consequences of World War II"

prompts:
  system_context: |
    You are generating flashcards for a History course on World War II.
    Focus on causes, major events, and consequences of World War II.
    Emphasize causation, connections between events, and historical significance.

  card_quality_focus:
    - "Focus on why and how, not just dates and names"
    - "Connect events to broader themes"
    - "Use specific examples to illustrate concepts"
    - "Emphasize historical significance and consequences"

  example_cards:
    - front: "Why did the Battle of Stalingrad (1942-43) mark a turning point on the Eastern Front?"
      back: "<strong>Multiple strategic impacts:</strong><br>1. First major German defeat<br>2. Destroyed Germany's 6th Army (330,000 casualties)<br>3. Ended German offensive capability in USSR<br>4. Shifted initiative to Soviets<br>5. Psychological impact on both sides"
      tags: "ww2 eastern-front stalingrad turning-points"
```

### Card Type Distribution

```yaml
card_distribution:
  conceptual: 0.60        # Causation and significance
  worked_examples: 0.05   # Rare for history
  algorithm: 0.00        # Not applicable
  pattern_recognition: 0.20  # Recognizing historical patterns
  visual: 0.15           # Maps, photographs, propaganda
```

---

## Language Learning

### Configuration Example

```yaml
subject:
  name: "German Grammar"
  short_name: "DE"
  field: "Language Learning"
  description: "German grammar, syntax, and common usage patterns"

prompts:
  system_context: |
    You are generating flashcards for a Language Learning course on German Grammar.
    Focus on German grammar, syntax, and common usage patterns.
    Provide clear examples and emphasize practical usage.

  card_quality_focus:
    - "Use concrete example sentences"
    - "Explain usage contexts, not just rules"
    - "Include common exceptions"
    - "Focus on practical communication"

  example_cards:
    - front: "When do you use Perfekt vs Präteritum in spoken German?"
      back: "<strong>Perfekt is standard for spoken German:</strong><br>Example: \"Ich <strong>habe gegessen</strong>\" (I ate)<br><br><strong>Präteritum mainly for:</strong><br>1. Written narratives<br>2. Sein/haben: \"Ich <strong>war</strong>\" (I was)<br>3. Modal verbs: \"Ich <strong>konnte</strong>\" (I could)"
      tags: "german grammar verb-tenses perfekt präteritum"
```

### Best Practices

- **Always include example sentences**
- **Use authentic, practical examples**
- **Tag by grammar concept** (cases, tenses, mood)
- **Include audio if possible** (reference pronunciation)

---

## General Tips Across Subjects

### 1. Tagging Strategy

Use hierarchical tags:
```
[subject] [topic] [subtopic] [concept]
```

Examples:
- `linear-algebra eigenvalues diagonalization`
- `organic-chemistry reactions substitution sn2`
- `algorithms sorting mergesort`

### 2. Adjust Card Distribution

| Subject Type | Conceptual | Worked Examples | Algorithm | Pattern | Visual |
|--------------|-----------|-----------------|-----------|---------|--------|
| Math-heavy   | 40-45%    | 25-30%         | 15-20%    | 5%      | 5-10%  |
| Theory-heavy | 60%       | 10%            | 10%       | 15%     | 5%     |
| Lab-based    | 35%       | 25%            | 20%       | 10%     | 10%    |

### 3. Target Card Counts

- **Per lecture**: 30-50 cards
- **Per chapter**: 50-80 cards
- **Per unit**: 100-150 cards
- **Per course**: 800-1200 cards

### 4. Subject-Specific Tools

- **Math/Physics**: LaTeX math rendering (`\(...\)`, `\[...\]`)
- **Chemistry**: ChemDraw structures saved as PNG
- **CS**: Code blocks with syntax (use `<pre><code>`)
- **Biology**: Pathway diagrams, protein structures
- **History**: Timeline images, maps, photographs

---

## Customization Workflow

1. **Initialize**: `anki-gen init`
2. **Edit `config.yaml`**: Adjust subject info and prompts
3. **Add example cards**: Provide 2-3 high-quality examples
4. **Test with one unit**: Generate cards and review quality
5. **Iterate on prompts**: Refine based on output quality
6. **Scale up**: Process remaining units

---

## Resources

- [Anki Manual](https://docs.ankiweb.net/)
- [SuperMemo 20 Rules](https://www.supermemo.com/en/archives1990-2015/articles/20rules) - Card design principles
- [LaTeX Math Symbols](https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols) - For math formatting
- [HTML Formatting Reference](https://www.w3schools.com/html/) - For card styling

---

## Contributing

Have a great configuration for your subject? Share it!

Create a pull request adding your subject to this guide with:
- Configuration example
- Best practices
- 2-3 example cards
- Any subject-specific tips
