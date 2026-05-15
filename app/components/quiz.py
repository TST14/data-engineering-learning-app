"""Quiz rendering component."""
from pathlib import Path

import streamlit as st
import yaml


def render_quiz(quiz_path: Path) -> tuple[int, int]:
    """Render an interactive quiz from a YAML file. Returns (score, total)."""
    with open(quiz_path, encoding="utf-8") as f:
        quiz_data = yaml.safe_load(f)

    questions = quiz_data.get("questions", [])
    if not questions:
        st.info("No questions found in quiz file.")
        return 0, 0

    st.subheader("🧪 Quick Quiz")

    total = len(questions)
    # Namespace results per quiz file so different topics don't collide
    state_key = f"quiz_results_{quiz_path}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {}

    results: dict = st.session_state[state_key]

    for i, q in enumerate(questions):
        st.markdown(f"**Q{i + 1}: {q['question']}**")
        user_answer = st.radio(
            f"Select answer for Q{i + 1}:",
            q["options"],
            index=None,
            key=f"radio_{quiz_path}_{i}",
        )

        if st.button(f"Check Q{i + 1}", key=f"check_{quiz_path}_{i}"):
            if user_answer is None:
                st.warning("Please select an answer first.")
            else:
                correct = q["options"].index(user_answer) == q["answer"]
                results[i] = {"correct": correct, "explanation": q["explanation"],
                               "correct_option": q["options"][q["answer"]]}

        if i in results:
            if results[i]["correct"]:
                st.success(f"✅ Correct! {results[i]['explanation']}")
            else:
                st.error(
                    f"❌ Wrong. Correct answer: **{results[i]['correct_option']}**\n\n"
                    f"{results[i]['explanation']}"
                )

        st.markdown("---")

    score = sum(1 for r in results.values() if r["correct"])

    if results:
        st.info(f"**Score so far: {score} / {total}**")

    if st.button("🔄 Reset Quiz", key=f"reset_{quiz_path}"):
        st.session_state[state_key] = {}
        st.rerun()

    return score, total
