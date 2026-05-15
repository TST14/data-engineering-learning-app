## 🔵 Sets vs Lists in Python

Both `set` and `list` store collections of items — but their performance characteristics are very different.

---

### 📊 Key Differences

| Feature | `list` | `set` |
|---------|--------|-------|
| Order | Ordered (insertion order) | Unordered |
| Duplicates | Allowed | Not allowed |
| `in` lookup | O(n) — linear scan | O(1) — hash table |
| Indexing | ✅ `lst[0]` | ❌ Not supported |
| Use case | Ordered sequences | Membership tests, deduplication |

---

### ⚡ Membership Testing

The most common reason to choose a `set` over a `list` is **O(1) lookup**:

```python
import timeit

big_list = list(range(1_000_000))
big_set  = set(range(1_000_000))

# List lookup: O(n)
list_time = timeit.timeit(lambda: 999_999 in big_list, number=1000)

# Set lookup: O(1)
set_time  = timeit.timeit(lambda: 999_999 in big_set,  number=1000)

print(f"List: {list_time:.4f}s  |  Set: {set_time:.6f}s")
# List: ~5s  |  Set: ~0.0001s
```

---

### 🔧 Set Operations

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

print(a | b)   # Union:        {1, 2, 3, 4, 5, 6}
print(a & b)   # Intersection: {3, 4}
print(a - b)   # Difference:   {1, 2}
print(a ^ b)   # Symmetric diff: {1, 2, 5, 6}
```

---

### 🧹 Deduplication

```python
data = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(data))   # [1, 2, 3, 4] (order not guaranteed)
```

---

### 💡 When to Use Which

| Scenario | Choice |
|----------|--------|
| Need ordered data | `list` |
| Frequent membership tests | `set` |
| Deduplication | `set` |
| Need to access by index | `list` |
| Set algebra (union, intersect) | `set` |
