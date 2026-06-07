## 🧠 Python Memory Management – From Zero to Hero

> **Think of RAM like a big warehouse.** When Python runs your code, it needs space to store variables, objects, and function info. Python divides this warehouse into two main sections.

---

## 1. 🏗️ The Big Picture — Stack vs Heap

```
┌─────────────────────────────────────────────────────┐
│                   COMPUTER RAM                       │
│                                                      │
│   ┌──────────────┐        ┌───────────────────────┐ │
│   │              │        │                       │ │
│   │   STACK      │        │        HEAP           │ │
│   │  (Small,     │        │   (Large, flexible,   │ │
│   │  organized,  │        │    stores everything) │ │
│   │  fast)       │        │                       │ │
│   └──────────────┘        └───────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

| Feature | Stack 🍽️ | Heap 🏠 |
|---------|----------|---------|
| **What it stores** | Variable *names* (references) + function call info | ALL Python objects (numbers, strings, lists…) |
| **Speed** | ⚡ Very fast | 🐢 Slower |
| **Size** | Small & fixed | Large & dynamic |
| **Managed by** | CPU / OS automatically | Python's Memory Manager |
| **Lifetime** | Destroyed when function returns | Until nobody references the object |

> 💡 **Key insight:** The variable name lives on the **Stack**, but the actual value (object) lives on the **Heap**.

---

## 2. 📦 Stack Memory — The Stack of Plates

Think of the Stack like a **stack of plates 🍽️** — you add on top, and remove from the top (LIFO: Last In, First Out).

Every time you call a function, a new **"frame"** (plate) is pushed onto the stack. When the function returns, that frame is popped off.

```python
def multiply(a, b):
    result = a * b
    return result

def calculate():
    x = 5
    y = 10
    answer = multiply(x, y)
    return answer

final = calculate()
```

### What happens step-by-step:

```
STEP 1: Program starts
┌──────────────────────┐
│  Global Frame        │  ← "final" will live here
└──────────────────────┘  ← Bottom of Stack


STEP 2: calculate() is called → new frame pushed
┌──────────────────────┐
│  calculate() Frame   │  ← x=5, y=10, answer (references)
├──────────────────────┤
│  Global Frame        │
└──────────────────────┘


STEP 3: multiply(x,y) called inside calculate()
┌──────────────────────┐
│  multiply() Frame    │  ← a, b, result (references)
├──────────────────────┤
│  calculate() Frame   │  ← x, y, answer
├──────────────────────┤
│  Global Frame        │
└──────────────────────┘


STEP 4: multiply() returns → frame POPPED (destroyed)
┌──────────────────────┐
│  calculate() Frame   │  ← answer = 50
├──────────────────────┤
│  Global Frame        │
└──────────────────────┘


STEP 5: calculate() returns → frame POPPED
┌──────────────────────┐
│  Global Frame        │  ← final = 50
└──────────────────────┘
```

<!-- gif: 02_stack_frames.gif -->

---

## 3. 🏗️ Heap Memory — Where Objects Actually Live

**EVERY Python object lives on the Heap.** Even a simple `x = 42` creates an object on the heap:

```
        STACK                          HEAP
  ┌──────────────┐          ┌──────────────────────┐
  │              │          │                      │
  │  x ──────────────────►  │  PyObject (int: 42)  │
  │              │          │  - type: int         │
  │              │          │  - refcount: 1       │
  │              │          │  - value: 42         │
  └──────────────┘          └──────────────────────┘
```

### Shared references — the gotcha!

```python
a = [1, 2, 3]
b = a           # b points to the SAME object as a!
b.append(4)
print(a)        # [1, 2, 3, 4]  ← a changed too! 😲
```

```
        STACK                          HEAP
  ┌──────────────┐       ┌──────────────────────────────┐
  │              │       │                              │
  │  a ──────────────┐   │  List Object                 │
  │              │   ├──►│  - refcount: 2               │
  │  b ──────────────┘   │  - items: [1, 2, 3, 4]       │
  │              │       │                              │
  └──────────────┘       └──────────────────────────────┘
  
  Both a and b point to the SAME list on the heap!
```

---

## 4. 🔢 Reference Counting — The Primary Cleanup Method

Every object on the heap carries a **reference count** — a number that says "how many things are pointing at me?". When it hits **0**, the memory is freed **immediately**.

```python
import sys

a = "hello"          # refcount = 1
b = a                # refcount = 2 (both a and b point to it)
c = a                # refcount = 3

del b                # refcount = 2
c = "world"          # refcount = 1 (c now points elsewhere)
del a                # refcount = 0 → OBJECT DESTROYED 💥 instantly!
```

### Visual walkthrough:

```
STEP 1: a = "hello"
  a ──────────────────►  ┌──────────────┐
                         │ "hello"      │
                         │ refcount: 1  │
                         └──────────────┘

STEP 2: b = a
  a ──────┐
          ├────────────►  ┌──────────────┐
  b ──────┘               │ "hello"      │
                          │ refcount: 2  │
                          └──────────────┘

STEP 3: del b → refcount drops to 1
  a ──────────────────►  ┌──────────────┐
                         │ "hello"      │
                         │ refcount: 1  │
                         └──────────────┘

STEP 4: del a → refcount = 0 → FREED!
                         ┌──────────────┐
                         │ "hello"      │
                         │ refcount: 0  │  ← Memory returned ♻️
                         └──────────────┘
```

### When does refcount go UP?

```python
x = object()        # +1 (assignment)
y = x               # +1 (alias)
my_list = [x]       # +1 (added to container)
def foo(obj): pass
foo(x)              # +1 while function runs
```

### When does refcount go DOWN?

```python
del x               # -1
x = None            # -1 for old object (reassignment)
my_list.remove(x)   # -1 (removed from container)
# function returns  # -1 (local variable goes out of scope)
```

<!-- gif: 01_reference_counting.gif -->

---

## 5. 🗑️ Garbage Collection — Handling the Hard Cases

### The problem reference counting CANNOT solve: circular references

```python
class Node:
    def __init__(self):
        self.next = None

a = Node()
b = Node()
a.next = b       # a → b
b.next = a       # b → a  ← CIRCULAR!

del a            # refcount of Node(a) drops to 1 (b.next still holds it)
del b            # refcount of Node(b) drops to 1 (a.next still holds it)

# Both objects have refcount = 1 but NOBODY can reach them!
# This would be a MEMORY LEAK without the garbage collector.
```

```
After del a and del b — objects stuck on heap:

    ┌──────────────┐      ┌──────────────┐
    │   Node A     │─────►│   Node B     │
    │ refcount: 1  │◄─────│ refcount: 1  │
    └──────────────┘      └──────────────┘
    
    ☠️ Nobody outside can reach these, but refcount ≠ 0!
```

### Solution: Generational Garbage Collector 🧹

Python's GC uses **3 generations** — the younger, the more often it's checked:

```
┌──────────────────────────────────────────────────────┐
│  Generation 0 (Young — checked MOST often)           │
│  All NEW objects start here                          │
│  Collected after ~700 new allocations                │
├──────────────────────────────────────────────────────┤
│  Generation 1 (Middle-aged)                          │
│  Survived at least 1 GC sweep                        │
│  Collected after 10 Gen-0 sweeps                     │
├──────────────────────────────────────────────────────┤
│  Generation 2 (Old — checked RARELY)                 │
│  Long-lived objects (global state, caches, modules)  │
│  Collected after 10 Gen-1 sweeps                     │
└──────────────────────────────────────────────────────┘
```

> 💡 **Why generations?** Most objects die young (a variable in a loop lives for one iteration). Checking young objects often is cheap and effective.

```python
import gc

print(gc.get_threshold())   # (700, 10, 10)
print(gc.get_count())       # e.g. (354, 5, 2)

gc.collect()                # Force a GC run — returns number freed
```

<!-- gif: 03_gc_generations.gif -->

---

## 6. 🏊 Memory Pools & Arenas (pymalloc)

Asking the OS for memory on every `x = 5` would be very slow. Python pre-allocates **pools** of memory and carves them up internally.

```
┌─────────────────────────────────────────────────────────────┐
│  ARENA (256 KB — requested from OS once)                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  POOL (4 KB) — for objects of one size class          │  │
│  │  ┌──────┬──────┬──────┬──────┬──────┬──────┐         │  │
│  │  │Block │Block │Block │Block │Block │Block │ ...      │  │
│  │  │(obj) │(obj) │(free)│(obj) │(free)│(obj) │         │  │
│  │  └──────┴──────┴──────┴──────┴──────┴──────┘         │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  POOL (4 KB) — for different size class               │  │
│  │  ...                                                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

- Objects **≤ 512 bytes** → go into Python's pre-allocated pools (fast!)
- Objects **> 512 bytes** → go directly to OS `malloc()` (slower)

---

## 7. ✨ Python's Smart Optimizations

### Integer Caching (-5 to 256)

Python pre-creates small integers and **reuses** them — no new object needed:

```python
a = 256
b = 256
print(a is b)   # True ✅  ← Same object in memory!

a = 257
b = 257
print(a is b)   # False ❌ ← Different objects (outside cache range)
```

### String Interning

```python
a = "hello"
b = "hello"
print(a is b)   # True ✅  ← Python reuses the same string

a = "hello world"
b = "hello world"
print(a is b)   # False ❌ ← Strings with spaces are not interned
```

### Mutable vs Immutable — id() tells the story

```python
# IMMUTABLE (int, str, tuple) → new object created on every change
a = 10
print(id(a))    # e.g. 140234866351408
a = a + 1
print(id(a))    # e.g. 140234866351440 ← DIFFERENT address!

# MUTABLE (list, dict, set) → same object modified in place
b = [1, 2, 3]
print(id(b))    # e.g. 140234861234567
b.append(4)
print(id(b))    # e.g. 140234861234567 ← SAME address!
```

---

## 8. ⚠️ Common Memory Pitfalls

### Pitfall 1: Global list that never shrinks

```python
# BAD — big_data is NEVER freed because results holds a reference
results = []

def process():
    big_data = [0] * 10_000_000  # 80 MB!
    results.append(big_data)     # keeps refcount > 0 forever!

for _ in range(100):
    process()   # Memory grows to 8 GB 💀
```

### Pitfall 2: Mutable default argument

```python
# BAD — the [] is created once and shared across ALL calls!
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2]  ← Surprise! Same list object.

# GOOD — use None as default
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### Pitfall 3: String concatenation in a loop

```python
# BAD — each += creates a brand new string object (immutable!)
result = ""
for i in range(100_000):
    result += str(i)    # Very slow — lots of allocations!

# GOOD — collect parts, join once
result = "".join(str(i) for i in range(100_000))
```

---

## 9. 🔬 Complete Memory Walkthrough

```python
def greet(name):
    message = "Hello, " + name
    return message

result = greet("Alice")
print(result)
```

| Step | Stack | Heap | Notes |
|------|-------|------|-------|
| `greet("Alice")` called | Global + greet frame pushed | `"Alice"` object created | New frame on stack |
| `name` binds | `name` in greet frame | Points to `"Alice"` on heap | refcount of "Alice" +1 |
| `"Hello, " + name` | temp reference | `"Hello, Alice"` created | Concatenation = new object |
| `message` binds | `message` in greet frame | Points to `"Hello, Alice"` | refcount = 1 |
| `return message` | greet frame **POPPED** | `"Hello, Alice"` survives | Stack shrinks |
| `result` binds | `result` in global frame | Points to `"Hello, Alice"` | refcount stays 1 |
| Program ends | All frames cleared | All heap objects freed | Final cleanup |

---

## 🎯 Summary Cheat Sheet

```
┌──────────────────────────────────────────────────────────────┐
│                  PYTHON MEMORY SUMMARY                        │
├──────────────────────────────────────────────────────────────┤
│  STACK:                                                       │
│  • Stores variable NAMES (references) + function frames      │
│  • Automatic cleanup (frame destroyed when function returns) │
│  • Fast, small, LIFO order                                   │
│                                                               │
│  HEAP:                                                        │
│  • Stores ALL Python objects (int, str, list, custom…)       │
│  • Managed by Python's memory manager                        │
│  • Large, unordered, dynamic                                 │
│                                                               │
│  CLEANUP MECHANISMS:                                          │
│  1️⃣  Reference Counting  → immediate, handles 99% of cases  │
│  2️⃣  Garbage Collector   → handles circular references       │
│       3 generations: young (frequent) → old (rare)           │
│                                                               │
│  OPTIMIZATIONS:                                               │
│  • pymalloc: pools/arenas for small objects (≤ 512 bytes)    │
│  • Integer cache: -5 to 256 pre-created                      │
│  • String interning: simple strings reused                   │
│                                                               │
│  HANDY TOOLS:                                                 │
│  • sys.getrefcount(obj)   → check reference count            │
│  • sys.getsizeof(obj)     → object size in bytes             │
│  • gc.collect()           → force GC run                     │
│  • tracemalloc            → trace memory allocations         │
└──────────────────────────────────────────────────────────────┘
```
