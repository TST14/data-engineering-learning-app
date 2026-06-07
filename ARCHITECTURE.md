# 🏛️ Architecture & Developer Guide

This document explains the full technical structure of the **Data Engineering Learning Hub** for anyone who wants to maintain, extend, or deploy the application.

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Repository Layout](#2-repository-layout)
3. [Application Layer — `app/`](#3-application-layer--app)
4. [Content System — `content/`](#4-content-system--content)
5. [Data Flow — End-to-End](#5-data-flow--end-to-end)
6. [Content Conventions (must read before adding topics)](#6-content-conventions-must-read-before-adding-topics)
7. [How to Add a New Topic](#7-how-to-add-a-new-topic)
8. [How to Add a New Category](#8-how-to-add-a-new-category)
9. [How to Add Animated GIFs or Images](#9-how-to-add-animated-gifs-or-images)
10. [Tooling — Scripts](#10-tooling--scripts)
11. [Testing](#11-testing)
12. [Deployment — Docker](#12-deployment--docker)
13. [Known Limitations & Roadmap](#13-known-limitations--roadmap)

---

## 1. High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Browser (localhost:8501)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │  HTTP
┌────────────────────────────▼────────────────────────────────────┐
│                    Streamlit Runtime                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  app/main.py   (entry point — sidebar + tab routing)     │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  components/                                              │   │
│  │    quiz.py          — interactive Q&A                    │   │
│  │    code_runner.py   — live Python execution              │   │
│  │    progress_tracker.py — read/write progress JSON        │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  utils/                                                   │   │
│  │    content_loader.py — filesystem discovery + YAML parse │   │
│  │    randomizer.py     — random topic picker               │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │  reads files
┌────────────────────────────▼────────────────────────────────────┐
│                    content/  (pure file system)                   │
│   <category>/<topic>/                                             │
│     topic.yaml        explanation.md    examples.py              │
│     quiz.yaml         assets/           generate_assets.py       │
└─────────────────────────────────────────────────────────────────┘
                             │  reads/writes
┌────────────────────────────▼────────────────────────────────────┐
│                    data/user_progress.json                        │
└─────────────────────────────────────────────────────────────────┘
```

**Design principle: the application code is completely data-driven.** No code change is ever needed to add a new topic or category — the app auto-discovers everything from the filesystem at startup.

---

## 2. Repository Layout

```
data-engineering-learning-app/
│
├── app/                        # All Streamlit application code
│   ├── main.py                 # Single entry point — sidebar, tabs, routing
│   ├── components/
│   │   ├── code_runner.py      # Renders + executes examples.py
│   │   ├── progress_tracker.py # Reads/writes data/user_progress.json
│   │   └── quiz.py             # Renders quiz.yaml as interactive Q&A
│   ├── themes/
│   │   └── style.css           # Global custom CSS injected at startup
│   └── utils/
│       ├── content_loader.py   # Filesystem scan + YAML parsing
│       └── randomizer.py       # Random topic selection
│
├── content/                    # All learning content — NO Python app code here
│   ├── concepts/               # Category folder
│   │   ├── acid_vs_base/       # Topic folder (always snake_case lowercase)
│   │   │   ├── topic.yaml      # Required — metadata
│   │   │   ├── explanation.md  # Required — the learning content
│   │   │   ├── examples.py     # Required — runnable code
│   │   │   ├── quiz.yaml       # Required — quiz questions
│   │   │   └── assets/         # Optional — images, GIFs
│   │   ├── batch_vs_streaming/
│   │   ├── cap_theorem/
│   │   └── star_vs_snowflake/
│   ├── python/
│   │   ├── memory_management/
│   │   │   ├── generate_assets.py  # Topic-specific GIF generator (optional)
│   │   │   └── ...
│   │   └── ...
│   ├── spark/
│   └── sql/
│
├── data/
│   └── user_progress.json      # Local progress (completed topics + quiz scores)
│
├── scripts/                    # Repo-wide developer tooling only
│   ├── validate_content.py     # Content structure auditor (run in CI)
│   └── _generate_stubs.py      # One-time stub creator for new topic skeletons
│
├── tests/
│   └── test_content_loader.py  # Unit tests for content discovery utilities
│
├── Dockerfile                  # Production container — python:3.11-slim
├── run.py                      # Convenience launcher (calls streamlit run)
├── requirements.txt            # Runtime deps: streamlit, pyyaml, Pillow
├── requirements-dev.txt        # Dev deps: pytest
├── setup.py                    # Installable package entry point (de-learn CLI)
├── README.md                   # Quick-start for end users
└── ARCHITECTURE.md             # This file
```

---

## 3. Application Layer — `app/`

### `app/main.py` — The Single Entry Point

All routing and page assembly lives here. The file is deliberately **one flat script** — Streamlit reruns it top-to-bottom on every user interaction.

**Execution order:**
1. Page config + CSS injection
2. `@st.cache_data` cached title loader (`_topic_titles`) — loads `topic.yaml` for every topic in the active category once; cached per category path
3. **Sidebar** — category selectbox → topic selectbox (both show human-readable titles via `format_func`) → progress bar → reset button
4. **Main area** — topic metadata header + 3 tabs:
   - `📖 Learn` — renders `explanation.md` with inline GIF injection (see §4)
   - `💻 Code Example` — renders `examples.py` via `code_runner`
   - `🧪 Quiz` — renders `quiz.yaml` via `quiz` component

**Key architectural decision — `format_func` on selectboxes:**
Streamlit selectboxes store the *option value* (folder name) internally while displaying a *formatted string* (human title). This means `selected_category` and `selected_topic` are always folder names and safe to use as path segments, while the UI shows clean titles.

### `app/components/code_runner.py`

Renders the code with `st.code()` and executes it via `exec()` when the Run button is pressed. The executed module's namespace is inspected for an `output` variable — **all `examples.py` files should set `output = ...`** to surface results without relying on `print()` capture.

```python
# examples.py convention — always set output
output = f"Result: {some_value}"
```

> ⚠️ **Security note:** `exec()` runs arbitrary Python in the same process. This is acceptable for a self-hosted personal learning tool. Do NOT expose this to untrusted users without a proper sandbox.

### `app/components/quiz.py`

Reads `quiz.yaml`, renders one radio button per question, and stores answers in `st.session_state` keyed by the quiz file path (so different topics don't collide). Answers persist within a session but reset on browser refresh.

### `app/components/progress_tracker.py`

Reads/writes `data/user_progress.json`. Progress keys are `"<category>/<topic_folder_name>"` (e.g. `"python/memory_management"`).

> ⚠️ **Known limitation:** Keys are folder-path based. Renaming a topic folder silently orphans its progress entry. See §13 for the planned fix.

### `app/utils/content_loader.py`

The only module that directly touches the filesystem for content. Two important behaviours:

- `list_categories` / `list_topics` — both use **case-insensitive sort** (`key=str.lower`) so topics appear alphabetically regardless of capitalisation
- `load_topic_meta` — returns safe defaults if `topic.yaml` is missing, so partially-built topics don't crash the app

---

## 4. Content System — `content/`

### Directory structure rules

| Rule | Reason |
|------|--------|
| Category folders: `snake_case` lowercase | Case-sensitive Linux filesystems (Docker) |
| Topic folders: `snake_case` lowercase | Same; also used as progress keys |
| Every topic must have all 4 required files | `validate_content.py` enforces this |
| `assets/` is optional but must exist before adding `<!-- gif: -->` markers | Renderer checks `exists()` |
| `generate_assets.py` lives **inside the topic folder**, not in `scripts/` | Keeps content self-contained; at 100 topics `scripts/` would become noise |

### `topic.yaml` — Schema

```yaml
title: Human Readable Title          # string — shown in sidebar and page header
difficulty: Beginner                 # one of: Beginner | Intermediate | Advanced
estimated_time: 15 min              # free string — shown in header caption
tags:                                # list of strings — shown in header caption
- python
- memory
prerequisites: []                    # list — reserved for future dependency graph
```

All fields are required. `validate_content.py` will flag any missing fields or non-standard `difficulty` values.

### `explanation.md` — Inline Image Markers

The Learn tab renderer supports `<!-- gif: filename -->` HTML comment markers embedded anywhere in the markdown. These are **invisible** in rendered markdown but intercepted by the renderer to inject `st.image()` calls at the exact position.

```markdown
## 4. Reference Counting

... prose and ASCII diagrams ...

<!-- gif: 01_reference_counting.gif -->

---

## 5. Garbage Collection
```

**How it works in `main.py`:**

```python
parts = re.split(r'<!--\s*gif:\s*(\S+?)\s*-->', content)
# parts = [text_chunk, gif_name, text_chunk, gif_name, ...]
```

Each odd-indexed part is a filename. The filename is sanitised with `Path(name).name` (strips any `../` path traversal attempts) before being joined to the topic's `assets/` directory.

Assets NOT referenced by any marker are shown in a fallback **Visual Aids** section at the bottom of the Learn tab.

### `examples.py` — Code Runner Contract

```python
# Must set the `output` variable with a string to display results.
# Use print() statements freely — they also appear if captured.
output = f"Answer: {result}"
```

### `quiz.yaml` — Schema

```yaml
questions:
  - question: "Question text?"
    options:
      - "Option A"
      - "Option B"
      - "Option C"
      - "Option D"
    answer: 1          # 0-based index of the correct option
    explanation: "Why this answer is correct."
```

---

## 5. Data Flow — End-to-End

A user selects **Python → memory_management** and clicks the **Learn** tab:

```
User selects category "python"
  └─► list_categories(CONTENT_DIR)            → ['concepts', 'python', 'spark', 'sql']
  └─► _topic_titles("…/python")  [cached]     → {'memory_management': 'Python Memory Management', …}
  └─► format_func applied to selectbox        → shows "Python Memory Management" in UI

User selects topic "Python Memory Management"
  └─► selected_topic = "memory_management"    (folder name, not display title)
  └─► topic_path = CONTENT_DIR / "python" / "memory_management"
  └─► load_topic_meta(topic_path)             → {title, difficulty, estimated_time, tags}

Learn tab renders:
  └─► explanation.md read from disk
  └─► re.split(GIF_MARKER_RE, content)        → [chunk, "01_reference_counting.gif", chunk, …]
  └─► for each chunk: st.markdown(chunk)
  └─► for each gif_name:
        gif_path = topic_path / "assets" / gif_name   (sanitised)
        if gif_path.exists(): st.image(…) in centred columns
  └─► any non-inline assets → "Visual Aids" section at bottom

User clicks "Mark Complete":
  └─► mark_complete("python/memory_management")
  └─► data/user_progress.json updated
  └─► sidebar progress bar recalculates
```

---

## 6. Content Conventions (must read before adding topics)

### Folder naming
- ✅ `memory_management`, `cap_theorem`, `acid_vs_base`
- ❌ `CAP_theorem`, `ACID_vs_BASE`, `GIL` — breaks on Linux/Docker

### `topic.yaml` difficulty values
Only three valid values: `Beginner`, `Intermediate`, `Advanced`

### `examples.py` output contract
Always assign the `output` variable. If the code produces no meaningful output, set `output = "Done."`.

### GIF / image naming in `assets/`
Prefix with a two-digit number to control display order: `01_reference_counting.gif`, `02_stack_frames.gif`. The renderer sorts files alphabetically before displaying them.

### `generate_assets.py` placement
If a topic needs programmatic asset generation (GIF scripts, diagram renderers), the script lives **inside the topic folder**:
```
content/python/memory_management/
  generate_assets.py    ← here, not in scripts/
  assets/
    01_reference_counting.gif
```
Run it directly: `python content/python/memory_management/generate_assets.py`

---

## 7. How to Add a New Topic

```bash
# 1. Create the folder (all lowercase snake_case)
mkdir content/python/my_new_topic
mkdir content/python/my_new_topic/assets

# 2. Create topic.yaml
cat > content/python/my_new_topic/topic.yaml << EOF
title: My New Topic
difficulty: Intermediate
estimated_time: 15 min
tags:
- python
- my-tag
prerequisites: []
EOF

# 3. Create the three content files
touch content/python/my_new_topic/explanation.md
touch content/python/my_new_topic/examples.py
touch content/python/my_new_topic/quiz.yaml

# 4. Validate — must pass before committing
python scripts/validate_content.py --strict
```

The app auto-discovers the topic on next load — no code changes needed.

---

## 8. How to Add a New Category

```bash
# Just create a folder — the app discovers it automatically
mkdir content/airflow

# Add topics inside it (follow §7 for each topic)
mkdir content/airflow/dag_basics
```

The category appears in the sidebar on next app load. The display name is the folder name with `_` replaced by spaces and title-cased (e.g. `airflow` → `Airflow`).

---

## 9. How to Add Animated GIFs or Images

### Option A — Static image/GIF (just drop the file)
```
content/<category>/<topic>/assets/01_my_diagram.gif
```
It will appear in the **Visual Aids** section at the bottom of the Learn tab.

### Option B — Inline image (appears mid-explanation)
1. Add the file to `assets/` with a numeric prefix
2. Add a marker in `explanation.md` exactly where you want it:
   ```markdown
   ...end of a section...

   <!-- gif: 01_my_diagram.gif -->

   ---

   ## Next Section
   ```
The marker is invisible in rendered markdown. The renderer injects the image at that exact position in a centred column layout.

### Option C — Programmatic GIF generation
1. Create `generate_assets.py` inside the topic folder
2. Use `ASSETS_DIR = Path(__file__).parent / "assets"` for the output path
3. Run it once to generate; commit the generated GIFs
4. See `content/python/memory_management/generate_assets.py` as a reference

---

## 10. Tooling — Scripts

### `scripts/validate_content.py` — Content Auditor

Scans all 24+ topics and reports:
- Missing required files (`topic.yaml`, `explanation.md`, `examples.py`, `quiz.yaml`)
- Empty required files
- `topic.yaml` schema violations (missing fields, invalid difficulty)
- `<!-- gif: -->` markers referencing non-existent asset files
- Folder names that violate `snake_case` lowercase convention

```bash
python scripts/validate_content.py            # advisory (exit 0 always)
python scripts/validate_content.py --strict   # exit 1 if any issues (use in CI)
```

### `scripts/_generate_stubs.py` — Stub Generator

Creates skeleton files for topics that don't exist yet. Useful when scaffolding multiple new topics at once. Update the `STUBS` dict to include the new topic, then run once.

---

## 11. Testing

```bash
pip install -r requirements-dev.txt
pytest tests/
```

Tests cover `content_loader` utilities. When adding a significant new utility, add a corresponding test in `tests/`.

The content validator (`validate_content.py`) is the main regression guard for the content layer and should be run as part of any CI pipeline:

```yaml
# Example GitHub Actions step
- name: Validate content
  run: python scripts/validate_content.py --strict
```

---

## 12. Deployment — Docker

```bash
docker build -t de-learning-app .
docker run -p 8501:8501 de-learning-app
```

The `Dockerfile` uses `python:3.11-slim` and runs `streamlit run app/main.py` on port 8501. The `data/user_progress.json` file lives inside the container — to persist progress across container restarts, mount it as a volume:

```bash
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  de-learning-app
```

> ⚠️ The `--server.runOnSave=true` flag is for local development only. Do not include it in the Dockerfile `CMD`.

---

## 13. Known Limitations & Roadmap

| # | Issue | Impact | Suggested fix |
|---|-------|--------|---------------|
| 1 | **Progress keys are folder-path based** — renaming a topic folder orphans its `user_progress.json` entry | Low now (personal use), High if multi-user | Add `id: python.memory_management` stable field to every `topic.yaml`; migrate progress tracker to use `id` instead of folder path |
| 2 | **`exec()` in code_runner** — runs Python in the same process | Acceptable for self-hosted personal use | Replace with `subprocess` sandbox or `RestrictedPython` for any public deployment |
| 3 | **No ordering within a category** — topics sort alphabetically by folder name | Cosmetic; meaningful learning paths can't be expressed | Add `order: 3` field to `topic.yaml`; update `list_topics` to sort by it |
| 4 | **Single-user only** — progress stored in a single flat JSON file | Fine for personal use | Replace with SQLite + user sessions for multi-user deployment |
| 5 | **`@st.cache_data` on titles** — cache invalidates only when the category path string changes, not when `topic.yaml` changes on disk | During development, edited titles don't appear until Streamlit is restarted | Add a file-mtime hash as a cache key, or just call `st.cache_data.clear()` after editing a `topic.yaml` |
