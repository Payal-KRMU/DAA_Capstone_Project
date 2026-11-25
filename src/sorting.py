"""
sorting.py  (Phase 2 - Package Prioritization)
----------------------------------------------
Parcels are ordered by:
    1. earliest deadline first (smaller deadline = more urgent)
    2. higher priority first   (ties broken by priority)
    3. parcel id               (final tie-break so the order is deterministic)

Merge Sort is chosen as the main ("best") algorithm because:
    * it is O(n log n) in the best, average AND worst case,
    * it is STABLE (equal keys keep their input order),
    * its running time does not depend on how the input is arranged.
Quick Sort and Insertion Sort (from the earlier labs) are kept for comparison (Phase 4).
"""
import random


def parcel_key(p):
    """Sort key: (deadline ascending, priority descending, id ascending)."""
    return (p.deadline, -p.priority, p.pid)


# ---------------------------------------------------------------- Merge Sort
def merge_sort(items, key=lambda x: x):
    """Stable divide-and-conquer sort. Time O(n log n), extra space O(n)."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)      # sort left half
    right = merge_sort(items[mid:], key)     # sort right half
    return _merge(left, right, key)          # combine


def _merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        # "<=" keeps the element from the left half first -> stability
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])                  # copy whatever is left over
    result.extend(right[j:])
    return result


# ---------------------------------------------------------------- Quick Sort
def quick_sort(items, key=lambda x: x):
    """Randomized Quick Sort (3-way partition).
    Average O(n log n), worst O(n^2), not stable."""
    if len(items) <= 1:
        return list(items)
    pivot = key(random.choice(items))        # random pivot avoids sorted-input worst case
    less = [x for x in items if key(x) < pivot]
    equal = [x for x in items if key(x) == pivot]
    greater = [x for x in items if key(x) > pivot]
    return quick_sort(less, key) + equal + quick_sort(greater, key)


# ------------------------------------------------------------ Insertion Sort
def insertion_sort(items, key=lambda x: x):
    """Simple stable sort. O(n^2) worst/average, O(n) on nearly-sorted input."""
    arr = list(items)
    for i in range(1, len(arr)):
        current = arr[i]
        k = key(current)
        j = i - 1
        while j >= 0 and key(arr[j]) > k:    # shift bigger elements right
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr


SORTERS = {
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Insertion Sort": insertion_sort,
}


def prioritize_parcels(parcels):
    """Return parcels in delivery-priority order using Merge Sort."""
    return merge_sort(parcels, key=parcel_key)
