"""Streamlit app entry point."""
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

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("📚 Learning Modules")

categories = list_categories(CONTENT_DIR)
default_cat_index = categories.index("python") if "python" in categories else 0
selected_category = st.sidebar.selectbox("Category", categories, index=default_cat_index)

topics = list_topics(CONTENT_DIR / selected_category)

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

# ── Main Content ─────────────────────────────────────────────────────────────
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

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_learn, tab_code, tab_quiz = st.tabs(["📖 Learn", "💻 Code Example", "🧪 Quiz"])

with tab_learn:
    explanation_path = topic_path / "explanation.md"
    if explanation_path.exists():
        st.markdown(explanation_path.read_text(encoding="utf-8"))
    else:
        st.info("No explanation available yet.")

    assets_dir = topic_path / "assets"
    if assets_dir.exists():
        image_files = list(assets_dir.glob("*.gif")) + list(assets_dir.glob("*.png")) + list(assets_dir.glob("*.jpg"))
        if image_files:
            st.subheader("🖼️ Visual Aids")
            for img in image_files:
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
