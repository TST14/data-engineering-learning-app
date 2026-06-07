"""Python Memory Management – interactive examples.

Run each section to see memory behaviour live.
"""
import gc
import sys

print("=" * 60)
print("EXAMPLE 1: Reference Counting")
print("=" * 60)

class MyObj:
    pass

obj = MyObj()
print(f"After obj = MyObj()         → refcount: {sys.getrefcount(obj)}")
# Note: getrefcount itself adds 1 temporary reference, so always shows +1

lst = [obj]
print(f"After lst = [obj]           → refcount: {sys.getrefcount(obj)}")

alias = obj
print(f"After alias = obj           → refcount: {sys.getrefcount(obj)}")

del alias
print(f"After del alias             → refcount: {sys.getrefcount(obj)}")

lst.pop()
print(f"After lst.pop()             → refcount: {sys.getrefcount(obj)}")

print()
print("=" * 60)
print("EXAMPLE 2: Integer Caching (-5 to 256)")
print("=" * 60)

a, b = 100, 100
print(f"a = 100, b = 100  →  a is b: {a is b}   (same object, cached!)")
print(f"  id(a) = {id(a)}")
print(f"  id(b) = {id(b)}")

c, d = 1000, 1000
print(f"a = 1000, b = 1000  →  a is b: {c is d}  (different objects, outside cache)")
print(f"  id(c) = {id(c)}")
print(f"  id(d) = {id(d)}")

print()
print("=" * 60)
print("EXAMPLE 3: Mutable vs Immutable — id() tells the story")
print("=" * 60)

# Immutable: new object on every change
x = 10
print(f"x = 10          → id: {id(x)}")
x = x + 1
print(f"x = x + 1       → id: {id(x)}  ← DIFFERENT (new object!)")

# Mutable: same object modified in place
nums = [1, 2, 3]
print(f"nums = [1,2,3]  → id: {id(nums)}")
nums.append(4)
print(f"nums.append(4)  → id: {id(nums)}  ← SAME (in-place change!)")

print()
print("=" * 60)
print("EXAMPLE 4: Shared references gotcha")
print("=" * 60)

a = [1, 2, 3]
b = a               # b and a point to the SAME list
b.append(99)
print(f"a = [1,2,3]; b = a; b.append(99)")
print(f"  a → {a}    ← a also changed! (same object)")
print(f"  b → {b}")

# Fix: copy the list
a = [1, 2, 3]
b = a.copy()        # b is a NEW list
b.append(99)
print(f"\na = [1,2,3]; b = a.copy(); b.append(99)")
print(f"  a → {a}    ← a is unchanged (different object)")
print(f"  b → {b}")

print()
print("=" * 60)
print("EXAMPLE 5: Circular references & Garbage Collector")
print("=" * 60)

class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None
    def __repr__(self):
        return f"Node({self.name})"

n1 = Node("A")
n2 = Node("B")
n1.ref = n2
n2.ref = n1   # circular: A → B → A

before = gc.get_count()
print(f"GC count before del: {before}")

del n1, n2
# Both nodes still have refcount=1 from each other's .ref — not freed yet!

collected = gc.collect()
after = gc.get_count()
print(f"Objects freed by gc.collect(): {collected}")
print(f"GC count after collect:  {after}")

print()
print("=" * 60)
print("EXAMPLE 6: Object sizes")
print("=" * 60)

print(f"sys.getsizeof(1)          = {sys.getsizeof(1)} bytes")
print(f"sys.getsizeof(10**100)    = {sys.getsizeof(10**100)} bytes  (big int)")
print(f"sys.getsizeof('')         = {sys.getsizeof('')} bytes  (empty string)")
print(f"sys.getsizeof('hello')    = {sys.getsizeof('hello')} bytes")
print(f"sys.getsizeof([])         = {sys.getsizeof([])} bytes  (empty list)")
print(f"sys.getsizeof([1,2,3])    = {sys.getsizeof([1,2,3])} bytes")
print(f"sys.getsizeof({{}})         = {sys.getsizeof({})} bytes  (empty dict)")

print()
print("=" * 60)
print("EXAMPLE 7: GC generations & thresholds")
print("=" * 60)

thresholds = gc.get_threshold()
counts = gc.get_count()
print(f"Thresholds (gen0, gen1, gen2): {thresholds}")
print(f"Current counts  (gen0, gen1, gen2): {counts}")
print("  → Gen-0 collected after ~700 new allocs")
print("  → Gen-1 collected after 10 Gen-0 sweeps")
print("  → Gen-2 collected after 10 Gen-1 sweeps")

