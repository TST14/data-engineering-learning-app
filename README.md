# 🚀 Data Engineering Learning Hub

An interactive, self-hosted learning app for Data Engineering concepts — built with Streamlit.

## Features

- 📚 Structured content across Python, SQL, Spark, Airflow, and Data Modeling
- 🧪 Interactive quizzes with explanations
- 💻 Live code examples
- 🎲 Random topic selector
- 📊 Local progress tracking
- 🖼️ Diagrams, GIFs, and visual assets per topic

## Quick Start

```bash
# 1. Clone & enter repo
git clone https://github.com/TST14/data-engineering-learning-app.git
cd data-engineering-learning-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app/main.py
# or
python run.py
```

Open http://localhost:8501 in your browser.

## Docker

```bash
docker build -t de-learning-app .
docker run -p 8501:8501 de-learning-app
```

## Project Structure

```
app/            # Streamlit app source
content/        # Topic content (YAML + Markdown + code)
data/           # Local progress storage
tests/          # Unit tests
```

## Adding a New Topic

1. Create a folder under the appropriate category: `content/<category>/<topic_name>/`
2. Add the required files:
   - `topic.yaml` — metadata (title, difficulty, estimated_time, tags)
   - `explanation.md` — detailed explanation with examples
   - `examples.py` — runnable code examples
   - `quiz.yaml` — quiz questions
   - `assets/` — images, GIFs, diagrams (optional)
3. The app auto-discovers the topic — no code changes needed.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Content | Markdown + YAML |
| Visuals | Plotly, Pillow, Mermaid |
| Storage | JSON (local) |
| Packaging | pip / Docker |