"""SQL Window Functions – demonstration using sqlite3."""
import sqlite3

# ── Setup in-memory DB ────────────────────────────────────────────────────────
conn = sqlite3.connect(":memory:")
conn.execute("""
    CREATE TABLE sales (
        employee_id INTEGER,
        department  TEXT,
        sales_amount REAL
    )
""")
conn.executemany("INSERT INTO sales VALUES (?,?,?)", [
    (1, "Engineering", 120000),
    (2, "Engineering", 95000),
    (3, "Engineering", 110000),
    (4, "Marketing",   80000),
    (5, "Marketing",   85000),
    (6, "Marketing",   80000),
])
conn.commit()

# ── Window function query ─────────────────────────────────────────────────────
rows = conn.execute("""
    SELECT
        employee_id,
        department,
        sales_amount,
        RANK()       OVER (PARTITION BY department ORDER BY sales_amount DESC) AS dept_rank,
        ROW_NUMBER() OVER (ORDER BY sales_amount DESC)                         AS overall_rank,
        SUM(sales_amount) OVER (PARTITION BY department)                       AS dept_total
    FROM sales
    ORDER BY overall_rank
""").fetchall()

lines = ["emp | dept        | sales   | dept_rank | overall | dept_total"]
lines.append("-" * 65)
for r in rows:
    lines.append(f"{r[0]:<4}| {r[1]:<12}| {r[2]:<8.0f}| {r[3]:<10}| {r[4]:<8}| {r[5]:.0f}")

output = "\n".join(lines)
conn.close()
