"""Tests for content_loader utilities."""
from pathlib import Path

import pytest

from app.utils.content_loader import list_categories, list_topics, load_topic_meta

CONTENT_DIR = Path(__file__).parent.parent / "content"


def test_list_categories_returns_known_categories():
    categories = list_categories(CONTENT_DIR)
    assert "python" in categories
    assert "sql" in categories


def test_list_topics_returns_known_python_topics():
    topics = list_topics(CONTENT_DIR / "python")
    assert "memory_management" in topics
    assert "sets_vs_lists" in topics


def test_list_topics_empty_for_missing_dir():
    result = list_topics(CONTENT_DIR / "nonexistent_category")
    assert result == []


def test_load_topic_meta_returns_correct_title():
    meta = load_topic_meta(CONTENT_DIR / "python" / "memory_management")
    assert meta["title"] == "Python Memory Management"
    assert meta["difficulty"] == "Intermediate"


def test_load_topic_meta_returns_defaults_when_missing(tmp_path):
    fake_topic = tmp_path / "fake_topic"
    fake_topic.mkdir()
    meta = load_topic_meta(fake_topic)
    assert meta["title"] == "Fake Topic"
    assert meta["difficulty"] == "Unknown"
