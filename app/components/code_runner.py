"""Live code runner component (placeholder for sandboxed execution)."""
import streamlit as st


def render_code_runner(code: str, filename: str = "<topic>") -> None:
    """Render a code block with a run button."""
    st.code(code, language="python")
    if st.button("▶️ Run Code", key=f"run_{filename}"):
        st.subheader("Output")
        try:
            exec_globals: dict = {}
            exec(compile(code, filename, "exec"), exec_globals)  # noqa: S102
            if "output" in exec_globals:
                st.code(str(exec_globals["output"]), language=None)
            else:
                st.info("Code executed successfully (no `output` variable set).")
        except Exception as exc:
            st.error(f"Error: {exc}")
