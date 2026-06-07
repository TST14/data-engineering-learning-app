"""Streamlit app entry point."""
import random
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

CARDS_PER_PAGE = 20
COLS_PER_ROW = 4


@st.dialog("📋 Pick a Topic", width="large")
def _topic_picker_dialog(cat_topics: list[dict], completed_keys: set[str]) -> None:
    """Full-screen modal listing all topics in the active category."""
    if not cat_topics:
        st.info("No topics found.")
        return

    # In-dialog search to narrow the list further
    q = st.text_input("🔍 Filter", placeholder="Type to filter…", label_visibility="collapsed").strip().lower()
    filtered = [
        t for t in cat_topics
        if not q or q in t["title"].lower() or any(q in tag.lower() for tag in t["tags"])
    ]

    st.caption(f"{len(filtered)} topics")
    st.divider()

    DIFF_ICON = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}
    for entry in filtered:
        tk = f"{entry['category']}/{entry['topic']}"
        is_done = tk in completed_keys
        diff_icon = DIFF_ICON.get(entry["difficulty"].lower(), "⚪")
        icon_col, btn_col, diff_col, time_col = st.columns([1, 8, 3, 2])
        icon_col.markdown(
            "<div style='text-align:center;padding-top:8px;font-size:1.1rem'>✅</div>" if is_done
            else "<div style='text-align:center;padding-top:8px;color:#aaa'>○</div>",
            unsafe_allow_html=True,
        )
        if btn_col.button(entry["title"], key=f"dlg_{entry['category']}_{entry['topic']}", use_container_width=True):
            st.session_state["selected_topic"] = entry["topic"]
            st.session_state["selected_category"] = entry["category"]
            st.rerun()
        diff_col.markdown(
            f"<div style='padding-top:8px'>{diff_icon} {entry['difficulty']}</div>",
            unsafe_allow_html=True,
        )
        time_col.markdown(
            f"<div style='padding-top:8px;color:#888'>⏱️ {entry['estimated_time']}</div>",
            unsafe_allow_html=True,
        )


@st.cache_data
def _build_topic_index(content_dir_str: str) -> list[dict]:
    """Flat list of every topic across all categories — built once and cached.

    Single filesystem scan that powers search, filtering, card grid, and
    progress counts. At 1000+ topics this keeps reruns fast because YAML
    files are only read here, never in the render loop.
    """
    content_dir = Path(content_dir_str)
    index = []
    for cat in list_categories(content_dir):
        for topic in list_topics(content_dir / cat):
            meta = load_topic_meta(content_dir / cat / topic)
            index.append({
                "category": cat,
                "topic": topic,
                "title": meta.get("title", topic.replace("_", " ").title()),
                "difficulty": meta.get("difficulty", ""),
                "estimated_time": meta.get("estimated_time", ""),
                "tags": meta.get("tags", []),
            })
    return index


# ── Progress (load once per rerun) ───────────────────────────────────────────
progress = load_progress()
completed_keys: set[str] = set(progress.get("completed", []))

# ── Session defaults ──────────────────────────────────────────────────────────
if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = None   # None = home screen
if "selected_category" not in st.session_state:
    st.session_state["selected_category"] = None
if "page" not in st.session_state:
    st.session_state["page"] = 0

# ── Sidebar (filters only — no per-topic widgets) ────────────────────────────
st.sidebar.title("📚 Learning Modules")

topic_index = _build_topic_index(str(CONTENT_DIR))
all_categories = list_categories(CONTENT_DIR)

# Search
search_query = st.sidebar.text_input(
    "🔍 Search", placeholder="Search topics, tags…", label_visibility="collapsed"
).strip().lower()

# Category filter
cat_display = ["All"] + [c.replace("_", " ").title() for c in all_categories]
cat_filter_idx = st.sidebar.selectbox(
    "Category", range(len(cat_display)),
    format_func=lambda i: cat_display[i],
    key="cat_filter_idx",
)
filter_cat = None if cat_filter_idx == 0 else all_categories[cat_filter_idx - 1]

st.sidebar.markdown("---")

# ── Jump to topic — opens a full-screen modal showing only the active category ──
_active_cat = st.session_state.get("selected_category") or filter_cat or (all_categories[0] if all_categories else None)
dialog_pool = sorted(
    [t for t in topic_index if t["category"] == _active_cat],
    key=lambda t: t["title"].lower(),
)
_cat_display = _active_cat.replace("_", " ").title() if _active_cat else "Topics"
if st.sidebar.button(f"📄 Browse {_cat_display} ({len(dialog_pool)})", use_container_width=True):
    _topic_picker_dialog(dialog_pool, completed_keys)

st.sidebar.markdown("---")

# Random topic (respects active filters)
if st.sidebar.button("🎲 Random Topic"):
    candidates = [
        t for t in topic_index
        if filter_cat is None or t["category"] == filter_cat
    ]
    if candidates:
        pick = random.choice(candidates)
        st.session_state["selected_topic"] = pick["topic"]
        st.session_state["selected_category"] = pick["category"]
        st.rerun()

# Back to home (only shown when in topic detail view)
if st.session_state.get("selected_topic"):
    if st.sidebar.button("← Back to Topics", use_container_width=True):
        st.session_state["selected_topic"] = None
        st.session_state["selected_category"] = None
        st.rerun()

# ── Progress ──────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Progress")
total_topics = len(topic_index)
done_count = len(completed_keys)
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

# ── Main Content ──────────────────────────────────────────────────────────────
if show_dev_docs:
    st.title("🏛️ Architecture & Developer Guide")
    st.caption("Technical reference for contributors and maintainers.")
    st.divider()
    if ARCH_DOC.exists():
        st.markdown(ARCH_DOC.read_text(encoding="utf-8"))
    else:
        st.error("ARCHITECTURE.md not found in repo root.")

elif st.session_state.get("selected_topic") and st.session_state.get("selected_category"):
    # ── Topic detail view ─────────────────────────────────────────────────────
    selected_topic = st.session_state["selected_topic"]
    selected_category = st.session_state["selected_category"]
    topic_path = CONTENT_DIR / selected_category / selected_topic
    topic_key = f"{selected_category}/{selected_topic}"
    completed = topic_key in completed_keys
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

    tab_learn, tab_code, tab_quiz = st.tabs(["📖 Learn", "💻 Code Example", "🧪 Quiz"])

    with tab_learn:
        explanation_path = topic_path / "explanation.md"
        assets_dir = topic_path / "assets"
        shown_inline: set[str] = set()

        if explanation_path.exists():
            content = explanation_path.read_text(encoding="utf-8")
            # Split on <!-- gif: filename --> HTML comment markers.
            parts = re.split(r'<!--\s*gif:\s*(\S+?)\s*-->', content)
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
                                width="stretch",
                            )
                        shown_inline.add(gif_name)
        else:
            st.info("No explanation available yet.")

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

else:
    # ── Home screen — paginated topic card grid ───────────────────────────────
    filtered = topic_index

    if search_query:
        filtered = [
            t for t in filtered
            if search_query in t["title"].lower()
            or search_query in t["category"].lower()
            or any(search_query in tag.lower() for tag in t["tags"])
        ]
    if filter_cat:
        filtered = [t for t in filtered if t["category"] == filter_cat]

    # Reset to page 0 when filters change
    filter_sig = f"{search_query}|{filter_cat}"
    if st.session_state.get("_filter_sig") != filter_sig:
        st.session_state["page"] = 0
        st.session_state["_filter_sig"] = filter_sig

    total = len(filtered)
    total_pages = max(1, (total + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE)
    page = min(st.session_state.get("page", 0), total_pages - 1)
    st.session_state["page"] = page

    done_pct = int(done_count / max(total_topics, 1) * 100)
    st.title("🧠 Data Engineering Learning Hub")
    st.caption(f"**{total}** topics  ·  **{done_count}/{total_topics}** completed ({done_pct}%)")
    st.divider()

    if not filtered:
        st.info("No topics match your filters. Try a different search or category.")
    else:
        page_topics = filtered[page * CARDS_PER_PAGE : (page + 1) * CARDS_PER_PAGE]
        DIFF_ICON = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}

        for row_start in range(0, len(page_topics), COLS_PER_ROW):
            row = page_topics[row_start : row_start + COLS_PER_ROW]
            cols = st.columns(COLS_PER_ROW)
            for col, entry in zip(cols, row):
                with col:
                    tk = f"{entry['category']}/{entry['topic']}"
                    is_done = tk in completed_keys
                    with st.container(border=True):
                        st.markdown(
                            f"{'✅' if is_done else '○'} **{entry['title']}**  \n"
                            f"<small>📂 {entry['category'].replace('_', ' ').title()}</small>",
                            unsafe_allow_html=True,
                        )
                        diff_icon = DIFF_ICON.get(entry["difficulty"].lower(), "⚪")
                        st.caption(f"{diff_icon} {entry['difficulty']}  ·  ⏱️ {entry['estimated_time']}")
                        if st.button(
                            "Open →",
                            key=f"card_{entry['category']}_{entry['topic']}",
                            use_container_width=True,
                            type="primary" if is_done else "secondary",
                        ):
                            st.session_state["selected_topic"] = entry["topic"]
                            st.session_state["selected_category"] = entry["category"]
                            st.rerun()

        # Pagination controls
        if total_pages > 1:
            st.divider()
            prev_col, info_col, next_col = st.columns([1, 3, 1])
            if prev_col.button("← Prev", disabled=page == 0, use_container_width=True):
                st.session_state["page"] = page - 1
                st.rerun()
            info_col.markdown(
                f"<div style='text-align:center;padding-top:8px'>Page {page + 1} of {total_pages}</div>",
                unsafe_allow_html=True,
            )
            if next_col.button("Next →", disabled=page >= total_pages - 1, use_container_width=True):
                st.session_state["page"] = page + 1
                st.rerun()
                