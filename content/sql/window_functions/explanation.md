## 🪟 SQL Window Functions

Window functions perform calculations **across a set of rows related to the current row** — without collapsing them like `GROUP BY` does.

---

### 📐 Syntax

```sql
function_name(expression)
OVER (
    [PARTITION BY column, ...]
    [ORDER BY column [ASC|DESC]]
    [ROWS/RANGE BETWEEN ...]
)
```

---

### 🔑 Common Window Functions

| Function | Purpose |
|----------|---------|
| `ROW_NUMBER()` | Unique sequential row number per partition |
| `RANK()` | Rank with gaps on ties |
| `DENSE_RANK()` | Rank without gaps |
| `LAG(col, n)` | Value from n rows before |
| `LEAD(col, n)` | Value from n rows after |
| `SUM() OVER` | Running/partition total |
| `AVG() OVER` | Running/partition average |
| `NTILE(n)` | Divide rows into n buckets |

---

### 💡 Example: Sales Ranking

```sql
SELECT
    employee_id,
    department,
    sales_amount,
    RANK()       OVER (PARTITION BY department ORDER BY sales_amount DESC) AS dept_rank,
    ROW_NUMBER() OVER (ORDER BY sales_amount DESC)                         AS overall_rank,
    SUM(sales_amount) OVER (PARTITION BY department)                       AS dept_total,
    LAG(sales_amount, 1) OVER (PARTITION BY department ORDER BY sale_date) AS prev_sale
FROM sales;
```

---

### 🆚 Window Functions vs GROUP BY

| | `GROUP BY` | Window Function |
|-|------------|-----------------|
| Rows returned | One per group | All rows preserved |
| Access other columns | ❌ (must aggregate) | ✅ |
| Running totals | ❌ | ✅ |

---

### 🎯 Common Patterns

**Top-N per group (deduplicated)**
```sql
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT * FROM ranked WHERE rn <= 3;
```

**Running total**
```sql
SELECT date, amount,
       SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM transactions;
```
