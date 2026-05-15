"""Entry point for the Data Engineering Learning App."""
import subprocess
import sys


def main():
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app/main.py"],
        check=True,
    )


if __name__ == "__main__":
    main()
