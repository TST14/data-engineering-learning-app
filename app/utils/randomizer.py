"""Randomizer utility for selecting topics."""
import random
from pathlib import Path

from utils.content_loader import list_topics


def random_topic(category_dir: Path) -> str:
    """Return a random topic name from the given category directory."""
    topics = list_topics(category_dir)
    return random.choice(topics) if topics else ""
