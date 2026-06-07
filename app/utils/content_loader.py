"""Content loader utilities."""
from pathlib import Path

import yaml


def list_categories(content_dir: Path) -> list[str]:
    """Return sorted list of category folder names."""
    return sorted((d.name for d in content_dir.iterdir() if d.is_dir()), key=str.lower)


def list_topics(category_dir: Path) -> list[str]:
    """Return sorted list of topic folder names within a category."""
    if not category_dir.exists():
        return []
    return sorted((d.name for d in category_dir.iterdir() if d.is_dir()), key=str.lower)


def load_topic_meta(topic_path: Path) -> dict:
    """Load topic.yaml metadata. Returns safe defaults if file missing."""
    meta_file = topic_path / "topic.yaml"
    if meta_file.exists():
        with open(meta_file, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {
        "title": topic_path.name.replace("_", " ").title(),
        "difficulty": "Unknown",
        "estimated_time": "?",
        "tags": [],
    }
