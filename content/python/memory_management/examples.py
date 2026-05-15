"""Python Memory Management – live examples."""
import gc
import sys

# ── 1. Reference counting ────────────────────────────────────────────────────
x = [1, 2, 3]
ref_count_initial = sys.getrefcount(x)  # 2 (x + function arg)

y = x
ref_count_after = sys.getrefcount(x)   # 3

del y
ref_count_final = sys.getrefcount(x)   # back to 2

# ── 2. Integer caching ───────────────────────────────────────────────────────
a, b = 256, 256
cached = a is b         # True – same object

c, d = 257, 257
not_cached = c is d     # False – distinct objects

# ── 3. Circular reference & GC ───────────────────────────────────────────────
class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None

n1 = Node("A")
n2 = Node("B")
n1.ref = n2
n2.ref = n1  # circular reference

del n1, n2
collected = gc.collect()  # GC clears the cycle

output = (
    f"Ref count (initial): {ref_count_initial}\n"
    f"Ref count (after y=x): {ref_count_after}\n"
    f"Ref count (after del y): {ref_count_final}\n"
    f"256 is cached: {cached}\n"
    f"257 is cached: {not_cached}\n"
    f"Objects collected by GC: {collected}"
)
