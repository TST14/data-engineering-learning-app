## 🧠 How Python Memory Management Works

Python uses **automatic memory management** with a private heap containing all objects and data structures.

---

### 🏗️ Stack vs Heap

| Feature | Stack | Heap |
|---------|-------|------|
| Stores | Function calls, references | Objects, data |
| Speed | ⚡ Fast | 🐢 Slower |
| Size | Limited | Dynamic |
| Managed by | OS | Python Memory Manager |

---

### 📌 Key Concepts

#### 1. Reference Counting
Every Python object has a counter tracking how many references point to it.  
When the count hits **0**, memory is freed immediately.

```python
import sys

x = [1, 2, 3]
print(sys.getrefcount(x))  # 2 (x + the argument itself)

y = x
print(sys.getrefcount(x))  # 3
```

#### 2. Garbage Collection
The `gc` module handles **circular references** that reference counting can't detect:

```python
import gc

class Node:
    def __init__(self):
        self.ref = None

a = Node()
b = Node()
a.ref = b
b.ref = a   # circular reference

del a, b
gc.collect()  # GC detects and clears the cycle
```

#### 3. Memory Pool (PyMalloc)
Python pre-allocates memory pools for small objects (< 512 bytes) to avoid frequent `malloc`/`free` system calls — making allocation much faster.

---

### 🔢 Integer Caching

> 💡 **Fun Fact:** Python caches integers from **-5 to 256** for performance!

```python
a = 256
b = 256
print(a is b)  # True ✅ (same cached object)

a = 257
b = 257
print(a is b)  # False ❌ (new objects created)
```

---

### 🔄 Garbage Collection Cycle

```
Python Code
    │
    ▼
Reference Counting ──► Count == 0? ──► Free Memory immediately
    │
    │  (circular refs survive)
    ▼
Garbage Collector (gc module)
    │
    ▼
Detect cycles ──► Mark unreachable ──► Free Memory
```

---

### 🛠️ Useful Tools

| Tool | Purpose |
|------|---------|
| `sys.getrefcount(obj)` | Check reference count |
| `gc.collect()` | Force GC run |
| `tracemalloc` | Trace memory allocations |
| `objgraph` | Visualize object graphs |
