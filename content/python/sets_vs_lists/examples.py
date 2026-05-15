"""Sets vs Lists – live examples."""
import timeit

# ── Membership test comparison ────────────────────────────────────────────────
N = 100_000
big_list = list(range(N))
big_set  = set(range(N))

list_time = timeit.timeit(lambda: (N - 1) in big_list, number=500)
set_time  = timeit.timeit(lambda: (N - 1) in big_set,  number=500)

speedup = list_time / set_time

# ── Set operations ────────────────────────────────────────────────────────────
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

union        = a | b
intersection = a & b
difference   = a - b
sym_diff     = a ^ b

# ── Deduplication ─────────────────────────────────────────────────────────────
data    = [1, 2, 2, 3, 3, 3, 4]
unique  = sorted(set(data))

output = (
    f"List lookup (500 runs): {list_time:.4f}s\n"
    f"Set  lookup (500 runs): {set_time:.6f}s\n"
    f"Set is ~{speedup:.0f}x faster\n\n"
    f"Union:         {union}\n"
    f"Intersection:  {intersection}\n"
    f"Difference:    {difference}\n"
    f"Symmetric diff:{sym_diff}\n\n"
    f"Deduplicated:  {unique}"
)
