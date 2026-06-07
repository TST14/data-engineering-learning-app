"""Live code runner component."""
import contextlib
import io

import streamlit as st


def render_code_runner(code: str, filename: str = "<topic>") -> None:
    """Render a code block with a run button."""
    st.code(code, language="python")
    if st.button("▶️ Run Code", key=f"run_{filename}"):
        st.subheader("Output")
        try:
            exec_globals: dict = {}
            stdout_buf = io.StringIO()
            with contextlib.redirect_stdout(stdout_buf):
                exec(compile(code, filename, "exec"), exec_globals)  # noqa: S102

            printed = stdout_buf.getvalue()
            explicit = exec_globals.get("output")

            if printed:
                st.code(printed, language=None)
            if explicit is not None:
                st.code(str(explicit), language=None)
            if not printed and explicit is None:
                st.info("Code executed successfully (no output).")
        except Exception as exc:
            st.error(f"Error: {exc}")
