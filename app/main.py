"""Streamlit app entry point."""
import re
from pathlib import Path

import streamlit as st

from components.quiz import render_quiz
from components.code_runner import render_code_runner
from components.progress_tracker import load_progress, mark_complete, reset_progress
from utils.content_loader import load_topic_meta, list_categories, list_topics
from utils.randomizer import random_topic

st.set_page_config(
    page_title="🧠 Data Engineering Learning Hub",
    page_icon="🚀",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
with open(Path(__file__).parent / "themes" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

CONTENT_DIR = Path(__file__).parent.parent / "content"
ARCH_DOC = Path(__file__).parent.parent / "ARCHITECTURE.md"


@st.cache_data
def _topic_titles(category_path_str: str) -> dict[str, str]:
    """Return {folder_name: display_title} for every topic in a category.

    Results are cached per category path so repeated sidebar renders do
    not re-read YAML files from disk on every interaction.
    """
    category_dir = Path(category_path_str)
    return {
        folder: load_topic_meta(category_dir / folder).get(
            "title", folder.replace("_", " ").title()
        )
        for folder in list_topics(category_dir)
    }


# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("📚 Learning Modules")

categories = list_categories(CONTENT_DIR)
default_cat_index = categories.index("python") if "python" in categories else 0
selected_category = st.sidebar.selectbox(
    "Category",
    categories,
    index=default_cat_index,
    format_func=lambda c: c.replace("_", " ").title(),
)

topics = list_topics(CONTENT_DIR / selected_category)
topic_titles = _topic_titles(str(CONTENT_DIR / selected_category))
# Re-sort by human title (case-insensitive) so sidebar matches what the user reads
topics = sorted(topics, key=lambda t: topic_titles.get(t, t).lower())

if st.sidebar.button("🎲 Random Topic"):
    rand_topic = random_topic(CONTENT_DIR / selected_category)
    if rand_topic:
        st.session_state["selected_topic"] = rand_topic

selected_topic = st.sidebar.selectbox(
    "Topic",
    topics,
    index=topics.index(st.session_state.get("selected_topic", topics[0]))
    if st.session_state.get("selected_topic") in topics
    else 0,
    format_func=lambda t: topic_titles.get(t, t.replace("_", " ").title()),
)
st.session_state["selected_topic"] = selected_topic

# ── Progress ─────────────────────────────────────────────────────────────────
progress = load_progress()
topic_key = f"{selected_category}/{selected_topic}"
completed = topic_key in progress.get("completed", [])

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Progress")
total_topics = sum(len(list_topics(CONTENT_DIR / c)) for c in categories)
done_count = len(progress.get("completed", []))
st.sidebar.progress(done_count / max(total_topics, 1), text=f"{done_count}/{total_topics} topics done")

if st.sidebar.button("🗑️ Reset Progress"):
    st.session_state["confirm_reset"] = True

if st.session_state.get("confirm_reset"):
    st.sidebar.warning("This will clear all completed topics and scores.")
    col_yes, col_no = st.sidebar.columns(2)
    if col_yes.button("Yes, reset", type="primary"):
        reset_progress()
        st.session_state["confirm_reset"] = False
        st.rerun()
    if col_no.button("Cancel"):
        st.session_state["confirm_reset"] = False
        st.rerun()

st.sidebar.markdown("---")
show_dev_docs = st.sidebar.toggle("📐 Developer Docs", value=False)

# ── Main Content ─────────────────────────────────────────────────────────────
if show_dev_docs:
    st.title("🏛️ Architecture & Developer Guide")
    st.caption("Technical reference for contributors and maintainers.")
    st.divider()
    if ARCH_DOC.exists():
        st.markdown(ARCH_DOC.read_text(encoding="utf-8"))
    else:
        st.error("ARCHITECTURE.md not found in repo root.")
else:
    topic_path = CONTENT_DIR / selected_category / selected_topic
    meta = load_topic_meta(topic_path)

    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"📖 {meta['title']}")
        st.caption(
            f"**Difficulty:** {meta['difficulty']}  |  ⏱️ {meta['estimated_time']}  |  "
            f"🏷️ {', '.join(meta.get('tags', []))}"
        )
    with col2:
        if completed:
            st.success("✅ Completed")
        elif st.button("Mark Complete ✔️"):
            mark_complete(topic_key)
            st.rerun()

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_learn, tab_code, tab_quiz = st.tabs(["📖 Learn", "💻 Code Example", "🧪 Quiz"])

    with tab_learn:
        explanation_path = topic_path / "explanation.md"
        assets_dir = topic_path / "assets"
        shown_inline: set[str] = set()

        if explanation_path.exists():
            content = explanation_path.read_text(encoding="utf-8")
            # Split on <!-- gif: filename --> HTML comment markers.
            # These are invisible in rendered markdown but let authors
            # control exactly where an image appears in the explanation.
            parts = re.split(r'<!--\s*gif:\s*(\S+?)\s*-->', content)
            # parts layout: [text, gif_name, text, gif_name, text, ...]
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part.strip():
                        st.markdown(part)
                else:
                    # Sanitise: strip directory components to prevent path traversal
                    gif_name = Path(part.strip()).name
                    gif_path = assets_dir / gif_name
                    if gif_path.exists():
                        _, col, _ = st.columns([1, 4, 1])
                        with col:
                            st.image(
                                str(gif_path),
                                caption=gif_path.stem.replace("_", " ").title(),
                                use_column_width=True,
                            )
                        shown_inline.add(gif_name)
        else:
            st.info("No explanation available yet.")

        # Show any assets that were not embedded inline
        if assets_dir.exists():
            remaining = sorted(
                img for img in (
                    list(assets_dir.glob("*.gif"))
                    + list(assets_dir.glob("*.png"))
                    + list(assets_dir.glob("*.jpg"))
                )
                if img.name not in shown_inline
            )
            if remaining:
                st.divider()
                st.subheader("🖼️ Visual Aids")
                for img in remaining:
                    st.image(str(img), caption=img.stem.replace("_", " ").title())

    with tab_code:
        examples_path = topic_path / "examples.py"
        if examples_path.exists():
            code = examples_path.read_text(encoding="utf-8")
            render_code_runner(code, filename=str(examples_path))
        else:
            st.info("No code example available yet.")

    with tab_quiz:
        quiz_path = topic_path / "quiz.yaml"
        if quiz_path.exists():
            render_quiz(quiz_path)
        else:
            st.info("No quiz available yet.")

