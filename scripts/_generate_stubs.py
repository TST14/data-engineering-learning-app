"""Generate stub content files for all empty topics."""
import yaml
from pathlib import Path

STUBS = {
    "content/python/generators_iterators": ("Python Generators & Iterators", "Intermediate", "15 min", ["python", "generators", "iterators", "yield", "lazy-evaluation"]),
    "content/python/decorators": ("Python Decorators", "Intermediate", "15 min", ["python", "decorators", "higher-order-functions"]),
    "content/python/context_managers": ("Context Managers", "Intermediate", "10 min", ["python", "context-managers", "with-statement"]),
    "content/python/args_kwargs": ("*args and **kwargs", "Beginner", "10 min", ["python", "args", "kwargs", "variadic"]),
    "content/python/list_comprehensions": ("List Comprehensions", "Beginner", "10 min", ["python", "list-comprehensions", "performance"]),
    "content/python/gil": ("The Global Interpreter Lock (GIL)", "Advanced", "20 min", ["python", "GIL", "threading", "concurrency"]),
    "content/python/shallow_vs_deep_copy": ("Shallow vs Deep Copy", "Intermediate", "10 min", ["python", "copy", "memory"]),
    "content/python/dunder_methods": ("Dunder (Magic) Methods", "Intermediate", "15 min", ["python", "dunder", "OOP", "magic-methods"]),
    "content/python/zip_unzip": ("zip() and Unpacking", "Beginner", "10 min", ["python", "zip", "unpacking", "itertools"]),
    "content/python/pickling": ("Python Pickling & Serialization", "Intermediate", "15 min", ["python", "pickle", "serialization"]),
    "content/sql/ctes": ("Common Table Expressions (CTEs)", "Intermediate", "15 min", ["sql", "CTEs", "WITH", "readability"]),
    "content/sql/query_optimization": ("SQL Query Optimization", "Advanced", "25 min", ["sql", "optimization", "performance", "indexes"]),
    "content/sql/indexing": ("Database Indexing", "Intermediate", "20 min", ["sql", "indexes", "B-tree", "performance"]),
    "content/spark/rdd_vs_dataframe": ("RDD vs DataFrame in Spark", "Intermediate", "20 min", ["spark", "RDD", "dataframe", "performance"]),
    "content/spark/lazy_evaluation": ("Spark Lazy Evaluation", "Intermediate", "15 min", ["spark", "lazy-evaluation", "DAG", "transformations"]),
    "content/spark/partitioning": ("Spark Partitioning", "Advanced", "20 min", ["spark", "partitioning", "parallelism", "shuffle"]),
    "content/spark/broadcast_joins": ("Broadcast Joins in Spark", "Advanced", "15 min", ["spark", "broadcast", "joins", "optimization"]),
    "content/concepts/cap_theorem": ("CAP Theorem", "Intermediate", "20 min", ["distributed-systems", "CAP", "consistency", "availability"]),
    "content/concepts/acid_vs_base": ("ACID vs BASE", "Intermediate", "15 min", ["databases", "ACID", "BASE", "transactions"]),
    "content/concepts/star_vs_snowflake": ("Star vs Snowflake Schema", "Beginner", "15 min", ["data-modeling", "star-schema", "snowflake"]),
    "content/concepts/batch_vs_streaming": ("Batch vs Streaming Processing", "Intermediate", "20 min", ["data-engineering", "batch", "streaming"]),
}

for path_str, (title, diff, est_time, tags) in STUBS.items():
    p = Path(path_str)
    p.mkdir(parents=True, exist_ok=True)

    meta_file = p / "topic.yaml"
    if not meta_file.exists():
        with open(meta_file, "w", encoding="utf-8") as f:
            yaml.dump(
                {"title": title, "difficulty": diff, "estimated_time": est_time, "tags": tags, "prerequisites": []},
                f,
                default_flow_style=False,
            )

    expl = p / "explanation.md"
    if not expl.exists():
        expl.write_text(f"## {title}\n\n> Content coming soon!\n", encoding="utf-8")

    ex = p / "examples.py"
    if not ex.exists():
        ex.write_text(
            f'"""Examples for {title} — coming soon."""\n\noutput = "Examples for this topic are being written!"\n',
            encoding="utf-8",
        )

    q = p / "quiz.yaml"
    if not q.exists():
        q.write_text("questions: []\n", encoding="utf-8")

print("Done")
