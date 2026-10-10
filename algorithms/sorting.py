"""
Sorting algorithms with metrics tracking.
Each function returns a SortResult containing sorted data, time, comparisons, swaps.
"""

import time
from dataclasses import dataclass


@dataclass
class SortResult:
    """Container for the result of a sort operation."""
    sorted_data: list
    time_ms: float
    comparisons: int
    swaps: int
    algorithm: str
    complexity: str
    stable: bool


def _get_key(row, col_index):
    """Extract sort key from a row; handles None and mixed types."""
    val = row[col_index]
    if val is None:
        return ""
    return val


# ----------------------------------------------------------------
# 1. BUBBLE SORT — O(n²), stable
# ----------------------------------------------------------------
def bubble_sort(data, col_index):
    arr = list(data)
    n = len(arr)
    comparisons = 0
    swaps = 0
    start = time.perf_counter()

    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            comparisons += 1
            if _get_key(arr[j], col_index) > _get_key(arr[j + 1], col_index):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break

    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(arr, elapsed, comparisons, swaps,
                      "Bubble Sort", "O(n²)", True)


# ----------------------------------------------------------------
# 2. INSERTION SORT — O(n²), stable
# ----------------------------------------------------------------
def insertion_sort(data, col_index):
    arr = list(data)
    comparisons = 0
    swaps = 0
    start = time.perf_counter()

    for i in range(1, len(arr)):
        key = arr[i]
        key_val = _get_key(key, col_index)
        j = i - 1
        while j >= 0:
            comparisons += 1
            if _get_key(arr[j], col_index) > key_val:
                arr[j + 1] = arr[j]
                swaps += 1
                j -= 1
            else:
                break
        arr[j + 1] = key

    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(arr, elapsed, comparisons, swaps,
                      "Insertion Sort", "O(n²)", True)


# ----------------------------------------------------------------
# 3. SELECTION SORT — O(n²), not stable
# ----------------------------------------------------------------
def selection_sort(data, col_index):
    arr = list(data)
    n = len(arr)
    comparisons = 0
    swaps = 0
    start = time.perf_counter()

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if _get_key(arr[j], col_index) < _get_key(arr[min_idx], col_index):
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1

    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(arr, elapsed, comparisons, swaps,
                      "Selection Sort", "O(n²)", False)


# ----------------------------------------------------------------
# 4. MERGE SORT — O(n log n), stable
# ----------------------------------------------------------------
def merge_sort(data, col_index):
    arr = list(data)
    counters = {"comparisons": 0, "swaps": 0}
    start = time.perf_counter()

    def _merge(left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            counters["comparisons"] += 1
            if _get_key(left[i], col_index) <= _get_key(right[j], col_index):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    def _merge_sort(a):
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = _merge_sort(a[:mid])
        right = _merge_sort(a[mid:])
        return _merge(left, right)

    arr = _merge_sort(arr)
    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(arr, elapsed, counters["comparisons"], counters["swaps"],
                      "Merge Sort", "O(n log n)", True)


# ----------------------------------------------------------------
# 5. QUICK SORT — O(n log n) avg, not stable
# ----------------------------------------------------------------
def quick_sort(data, col_index):
    arr = list(data)
    counters = {"comparisons": 0, "swaps": 0}
    start = time.perf_counter()

    def _partition(low, high):
        pivot = _get_key(arr[high], col_index)
        i = low - 1
        for j in range(low, high):
            counters["comparisons"] += 1
            if _get_key(arr[j], col_index) <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                if i != j:
                    counters["swaps"] += 1
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        counters["swaps"] += 1
        return i + 1

    def _quick_sort(low, high):
        if low < high:
            pi = _partition(low, high)
            _quick_sort(low, pi - 1)
            _quick_sort(pi + 1, high)

    _quick_sort(0, len(arr) - 1)
    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(arr, elapsed, counters["comparisons"], counters["swaps"],
                      "Quick Sort", "O(n log n)", False)


# ----------------------------------------------------------------
# 6. HEAP SORT — O(n log n), not stable
# ----------------------------------------------------------------
def heap_sort(data, col_index):
    arr = list(data)
    n = len(arr)
    counters = {"comparisons": 0, "swaps": 0}
    start = time.perf_counter()

    def _heapify(size, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < size:
            counters["comparisons"] += 1
            if _get_key(arr[left], col_index) > _get_key(arr[largest], col_index):
                largest = left
        if right < size:
            counters["comparisons"] += 1
            if _get_key(arr[right], col_index) > _get_key(arr[largest], col_index):
                largest = right
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            counters["swaps"] += 1
            _heapify(size, largest)

    for i in range(n // 2 - 1, -1, -1):
        _heapify(n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        counters["swaps"] += 1
        _heapify(i, 0)

    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(arr, elapsed, counters["comparisons"], counters["swaps"],
                      "Heap Sort", "O(n log n)", False)


# ----------------------------------------------------------------
# 7. SHELL SORT — O(n log² n) avg, not stable (EXTRA #1)
# ----------------------------------------------------------------
def shell_sort(data, col_index):
    arr = list(data)
    n = len(arr)
    counters = {"comparisons": 0, "swaps": 0}
    start = time.perf_counter()

    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            temp_val = _get_key(temp, col_index)
            j = i
            while j >= gap:
                counters["comparisons"] += 1
                if _get_key(arr[j - gap], col_index) > temp_val:
                    arr[j] = arr[j - gap]
                    counters["swaps"] += 1
                    j -= gap
                else:
                    break
            arr[j] = temp
        gap //= 2

    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(arr, elapsed, counters["comparisons"], counters["swaps"],
                      "Shell Sort", "O(n log² n)", False)


# ----------------------------------------------------------------
# 8. COUNTING SORT — O(n + k), stable (EXTRA #2)
# Only works for integer-ish keys — falls back to string hashing if needed
# ----------------------------------------------------------------
def counting_sort(data, col_index):
    arr = list(data)
    start = time.perf_counter()
    comparisons = 0
    swaps = 0

    # Extract keys as integers when possible
    def to_int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    keys = [to_int(_get_key(row, col_index)) for row in arr]

    if any(k is None for k in keys):
        # Fallback: sort by string key using dict counting
        buckets = {}
        for row in arr:
            k = str(_get_key(row, col_index))
            buckets.setdefault(k, []).append(row)
        sorted_arr = []
        for k in sorted(buckets.keys()):
            sorted_arr.extend(buckets[k])
    else:
        # Standard counting sort
        if not keys:
            sorted_arr = arr
        else:
            min_k = min(keys)
            max_k = max(keys)
            size = max_k - min_k + 1
            count = [0] * size
            for k in keys:
                count[k - min_k] += 1
            for i in range(1, size):
                count[i] += count[i - 1]
            sorted_arr = [None] * len(arr)
            for i in range(len(arr) - 1, -1, -1):
                k = keys[i]
                count[k - min_k] -= 1
                sorted_arr[count[k - min_k]] = arr[i]

    elapsed = (time.perf_counter() - start) * 1000
    return SortResult(sorted_arr, elapsed, comparisons, swaps,
                      "Counting Sort", "O(n + k)", True)


# ----------------------------------------------------------------
# REGISTRY — for UI dropdowns and benchmark
# ----------------------------------------------------------------
ALL_SORTS = {
    "Bubble Sort":    bubble_sort,
    "Insertion Sort": insertion_sort,
    "Selection Sort": selection_sort,
    "Merge Sort":     merge_sort,
    "Quick Sort":     quick_sort,
    "Heap Sort":      heap_sort,
    "Shell Sort":     shell_sort,
    "Counting Sort":  counting_sort,
}