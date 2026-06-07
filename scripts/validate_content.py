"""Content structure validator.

Scans every topic under content/ and reports:
  - Missing required files
  - Empty required files
  - topic.yaml schema violations (missing/wrong-type fields)
  - Folder names that break the snake_case convention
  - Assets referenced via <!-- gif: --> markers that don't exist on disk

Usage:
    python scripts/validate_content.py          # print report
    python scripts/validate_content.py --strict # exit 1 if any issues found
"""
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
CONTENT_DIR = REPO_ROOT / "content"

REQUIRED_FILES = ["topic.yaml", "explanation.md", "examples.py", "quiz.yaml"]
VALID_DIFFICULTIES = {"Beginner", "Intermediate", "Advanced"}
REQUIRED_YAML_FIELDS = {"title", "difficulty", "estimated_time", "tags"}
GIF_MARKER_RE = re.compile(r'<!--\s*gif:\s*(\S+?)\s*-->')


def _is_snake_case(name: str) -> bool:
    """Return True if name is all lowercase with underscores only (no spaces/mixed case)."""
    return name == name.lower() and " " not in name


def validate_topic(topic_path: Path, category: str) -> list[str]:
    """Return a list of issue strings for a single topic. Empty = all good."""
    issues = []
    name = topic_path.name
    label = f"{category}/{name}"

    # ── Folder naming convention ──────────────────────────────────────────────
    if not _is_snake_case(name):
        issues.append(
            f"[naming]   {label}: folder name '{name}' is not snake_case lowercase. "
            f"This WILL break on Linux/Docker (case-sensitive fs)."
        )

    # ── Required files present and non-empty ─────────────────────────────────
    for fname in REQUIRED_FILES:
        fpath = topic_path / fname
        if not fpath.exists():
            issues.append(f"[missing]  {label}: '{fname}' not found")
        elif fpath.stat().st_size == 0:
            issues.append(f"[empty]    {label}: '{fname}' is empty")

    # ── topic.yaml schema ─────────────────────────────────────────────────────
    yaml_path = topic_path / "topic.yaml"
    if yaml_path.exists() and yaml_path.stat().st_size > 0:
        try:
            meta = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            issues.append(f"[yaml]     {label}: topic.yaml parse error — {exc}")
            meta = {}

        for field in REQUIRED_YAML_FIELDS:
            if field not in meta:
                issues.append(f"[schema]   {label}: topic.yaml missing field '{field}'")

        diff = meta.get("difficulty", "")
        if diff and diff not in VALID_DIFFICULTIES:
            issues.append(
                f"[schema]   {label}: difficulty='{diff}' is not one of "
                f"{sorted(VALID_DIFFICULTIES)}"
            )

        tags = meta.get("tags", [])
        if not isinstance(tags, list):
            issues.append(f"[schema]   {label}: 'tags' must be a YAML list, got {type(tags).__name__}")

    # ── Inline gif markers → asset files must exist ───────────────────────────
    explanation = topic_path / "explanation.md"
    if explanation.exists():
        text = explanation.read_text(encoding="utf-8")
        for gif_ref in GIF_MARKER_RE.findall(text):
            gif_name = Path(gif_ref).name  # strip any rogue path components
            gif_path = topic_path / "assets" / gif_name
            if not gif_path.exists():
                issues.append(
                    f"[asset]    {label}: explanation.md references "
                    f"'<!-- gif: {gif_ref} -->' but "
                    f"assets/{gif_name} does not exist"
                )

    return issues


def main(strict: bool = False) -> int:
    all_issues: list[str] = []
    topic_count = 0

    for category_dir in sorted(CONTENT_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        for topic_dir in sorted(category_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            topic_count += 1
            all_issues.extend(validate_topic(topic_dir, category_dir.name))

    print(f"Validated {topic_count} topics across {len(list(CONTENT_DIR.iterdir()))} categories.\n")

    if not all_issues:
        print("✅  No issues found — content structure is clean.")
        return 0

    # Group by issue type for readability
    for issue in all_issues:
        print(issue)

    print(f"\n{'❌' if strict else '⚠️ '}  {len(all_issues)} issue(s) found.")
    return 1 if strict else 0


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv
    sys.exit(main(strict=strict_mode))
