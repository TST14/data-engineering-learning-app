"""Entry point for the Data Engineering Learning App."""
import subprocess
import sys


def main():
    subprocess.run(
        [
            sys.executable,
            # Suppress Streamlit 1.32 internal RuntimeWarning:
            # "coroutine 'expire_cache' was never awaited" originates in
            # streamlit/util.py and is unrelated to application code.
            "-W", "ignore::RuntimeWarning:streamlit.util",
            "-m", "streamlit", "run", "app/main.py",
            "--server.runOnSave=true",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
