# Contributing to Data Engineering Learning Hub

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup](#setup)
3. [Running the App](#running-the-app)
4. [Adding a New Topic](#adding-a-new-topic)
5. [Generating GIF Assets](#generating-gif-assets)
6. [Validating Content](#validating-content)
7. [Generating Topic Stubs](#generating-topic-stubs)
8. [Running Tests](#running-tests)
9. [Content Conventions](#content-conventions)
10. [Project Structure](#project-structure)

---

## Project Overview

The app is a self-hosted Streamlit learning platform. Content is file-based — each topic lives in its own folder under `content/<category>/<topic_name>/`. The app **auto-discovers** all topics at startup; no code changes are needed when adding content.

---

## Setup

```bash
# Clone the repo
git clone https://github.com/TST14/data-engineering-learning-app.git
cd data-engineering-learning-app

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install runtime dependencies
pip install -r requirements.txt

# Install dev dependencies (for running tests)
pip install -r requirements-dev.txt
```

---

## Running the App

```bash
# Standard — auto-reloads on file save
streamlit run app/main.py --server.runOnSave=true

# Alternative — suppresses a benign Streamlit internal warning
python run.py
```

Open http://localhost:8501 in your browser.

### Docker

```bash
docker build -t de-learning-app .
docker run -p 8501:8501 de-learning-app
```

---

## Adding a New Topic

1. **Create the folder** under the right category:
   ```
   content/<category>/<topic_name>/
   ```
   - `<category>` must be an existing folder: `python`, `sql`, `spark`, `concepts`
   - `<topic_name>` must be **snake_case lowercase** (e.g. `list_comprehensions`)

2. **Add the required files** (all four are mandatory):

   | File | Purpose |
   |------|---------|
   | `topic.yaml` | Metadata — title, difficulty, time, tags |
   | `explanation.md` | Full written explanation with code blocks |
   | `examples.py` | Runnable Python code shown in the Code tab |
   | `quiz.yaml` | Quiz questions shown in the Quiz tab |

3. **Optionally add an `assets/` folder** for images and GIFs:
   ```
   content/<category>/<topic_name>/assets/
   ```

4. **That's it.** The app picks up the new topic automatically on next rerun.

### topic.yaml format

```yaml
title: Your Topic Title
difficulty: Beginner        # Beginner | Intermediate | Advanced
estimated_time: 15 min
tags:
  - python
  - tag2
prerequisites: []           # optional list of related topic folder names
```

### quiz.yaml format

```yaml
questions:
  - question: "What does X do?"
    options:
      - "Option A"
      - "Option B"
      - "Option C"
      - "Option D"
    answer: "Option A"
    explanation: "Because..."
```

### Embedding GIFs inline in explanation.md

Place an HTML comment marker exactly where you want the GIF to appear:

```markdown
Some text above...

<!-- gif: your_animation.gif -->

Some text below...
```

The app renders the GIF from `assets/your_animation.gif` at that position. The marker is invisible in plain markdown renderers.

---

## Generating GIF Assets

Each topic that needs animated GIFs includes a `generate_assets.py` script inside its folder. Run it once to produce or regenerate the GIF files into the `assets/` directory.

```bash
# Example: regenerate all GIFs for the memory_management topic
python content/python/memory_management/generate_assets.py
```

GIFs are built using **Pillow** (already in `requirements.txt`). The script uses only stdlib + Pillow — no other dependencies.

**When to regenerate:**
- After editing the `generate_assets.py` script itself
- After changing canvas dimensions, colours, or frame content
- GIFs are committed to git alongside the content — they do not regenerate automatically at runtime

**Adding GIF generation to a new topic:**
- Create `content/<category>/<topic>/generate_assets.py`
- Use the memory_management script as a reference template
- Call `_save(frames, "filename.gif")` at the end to write each animation

---

## Validating Content

The validator checks all topics for structural and schema issues before you commit.

```bash
# Print a report (exit 0 always)
python scripts/validate_content.py

# Strict mode — exits with code 1 if any issues are found (useful in CI)
python scripts/validate_content.py --strict
```

**What it checks:**

| Check | Description |
|-------|-------------|
| Missing files | All four required files must exist |
| Empty files | Required files must not be zero bytes |
| snake_case naming | Folder names must be lowercase with underscores |
| topic.yaml schema | Required fields: `title`, `difficulty`, `estimated_time`, `tags` |
| Valid difficulty | Must be `Beginner`, `Intermediate`, or `Advanced` |
| GIF markers | Every `<!-- gif: filename.gif -->` in explanation.md must have a matching file in `assets/` |

Run this before every commit that touches `content/`.

---

## Generating Topic Stubs

When adding many topics at once, use the stub generator to create the folder structure and minimal placeholder files automatically.

```bash
python scripts/_generate_stubs.py
```

Edit the `STUBS` dict in the script to add new entries before running. Each stub creates:
- `topic.yaml` with metadata
- Empty `explanation.md`, `examples.py`, `quiz.yaml`
- Empty `assets/` folder

Then fill in the actual content for each stub.

---

## Running Tests

```bash
pytest
# or with verbose output
pytest -v
```

Tests live in `tests/`. Currently covers content loading utilities (`test_content_loader.py`).

---

## Content Conventions

- **Folder names:** `snake_case` lowercase only — Linux/Docker filesystems are case-sensitive
- **Difficulty levels:** exactly `Beginner`, `Intermediate`, or `Advanced` (sentence case)
- **Estimated time:** format as `"15 min"` or `"1 hr 30 min"`
- **Tags:** lowercase, hyphenated (e.g. `garbage-collection`, not `GarbageCollection`)
- **GIF filenames:** use `snake_case` with a numeric prefix for ordering (e.g. `01_reference_counting.gif`)
- **examples.py:** should be standalone runnable Python — no app imports, no side effects at module level

---

## Project Structure

```
app/
  main.py                  # Streamlit entry point
  components/
    code_runner.py         # Renders the Code tab with live execution
    progress_tracker.py    # Reads/writes data/user_progress.json
    quiz.py                # Renders the Quiz tab
  utils/
    content_loader.py      # Filesystem helpers: list_categories, list_topics, load_topic_meta
    randomizer.py          # random_topic() helper
  themes/
    style.css              # Custom CSS injected into every page

content/
  python/                  # Category folder
    decorators/            # Topic folder
      topic.yaml
      explanation.md
      examples.py
      quiz.yaml
      assets/              # Optional: GIFs, PNGs
      generate_assets.py   # Optional: script to regenerate GIFs

data/
  user_progress.json       # Local progress storage (gitignored)

scripts/
  validate_content.py      # Content structure validator
  _generate_stubs.py       # Bulk stub creator for new topics

tests/
  test_content_loader.py

ARCHITECTURE.md            # Technical design reference
CONTRIBUTING.md            # This file
README.md                  # Quick start for end users
requirements.txt           # Runtime deps: streamlit, pyyaml, Pillow
requirements-dev.txt       # Dev deps: pytest
```
