"""Local progress tracking using a JSON file."""
import json
from pathlib import Path

PROGRESS_FILE = Path(__file__).parent.parent.parent / "data" / "user_progress.json"


def load_progress() -> dict:
    """Load progress from JSON. Returns empty structure if file missing."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"completed": [], "scores": {}}


def save_progress(data: dict) -> None:
    """Persist progress to JSON."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def mark_complete(topic_key: str) -> None:
    """Mark a topic as completed."""
    data = load_progress()
    if topic_key not in data["completed"]:
        data["completed"].append(topic_key)
    save_progress(data)


def save_quiz_score(topic_key: str, score: int, total: int) -> None:
    """Record a quiz score for a topic."""
    data = load_progress()
    data.setdefault("scores", {})[topic_key] = {"score": score, "total": total}
    save_progress(data)


def reset_progress() -> None:
    """Wipe all progress."""
    save_progress({"completed": [], "scores": {}})
