import sqlite3
from algorithms.sorting import ALL_SORTS


conn = sqlite3.connect("books.db")
cur = conn.cursor()
cur.execute("SELECT title, author, year FROM books LIMIT 5000")
rows = cur.fetchall()
conn.close()

print(f"Loaded {len(rows)} rows for testing\n")
print(f"{'Algorithm':<18}{'Time (ms)':<12}{'Comparisons':<15}{'Swaps':<12}")
print("-" * 60)

# Column 0 = title
for name, func in ALL_SORTS.items():
    result = func(rows, 0)
    print(f"{result.algorithm:<18}{result.time_ms:>8.2f}    "
          f"{result.comparisons:>10,}    {result.swaps:>8,}")

print("\n--- First 3 sorted titles (by Merge Sort) ---")
merge_result = ALL_SORTS["Merge Sort"](rows, 0)
for r in merge_result.sorted_data[:3]:
    print(" ", r[0])