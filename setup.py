from setuptools import setup, find_packages

setup(
    name="data-engineering-learning-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.32.0",
        "pyyaml>=6.0.1",
        "plotly>=5.18.0",
        "Pillow>=10.2.0",
    ],
    entry_points={
        "console_scripts": [
            "de-learn=run:main",
        ],
    },
)
