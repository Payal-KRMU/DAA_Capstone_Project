"""
knapsack.py  (Phase 2 - Box Filling)
------------------------------------
0/1 Knapsack with Dynamic Programming.

The van has a weight capacity W (kg). Every parcel i has weight w[i] and
score v[i] (= value + 10 x priority, see models.Parcel.score). Each parcel is either taken completely (1) or left (0).
Goal: choose parcels with total weight <= W and MAXIMUM total score.

Recurrence (dp[i][c] = best value using the first i parcels, capacity c):
    dp[0][c] = 0
    dp[i][c] = dp[i-1][c]                                   if w[i] > c
             = max(dp[i-1][c], v[i] + dp[i-1][c - w[i]])    otherwise

Time  O(n * W)     Space O(n * W) for the full table (needed for backtracking).
"""


def knapsack_01(parcels, capacity):
    """Returns (best_value, selected_parcels, dp_table)."""
    n = len(parcels)
    # (n+1) x (W+1) table filled with zeros
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w = parcels[i - 1].weight
        v = parcels[i - 1].score
        prev = dp[i - 1]
        row = dp[i]
        for c in range(capacity + 1):
            row[c] = prev[c]                       # option 1: skip parcel i
            if w <= c and prev[c - w] + v > row[c]:
                row[c] = prev[c - w] + v           # option 2: take parcel i

    # Backtrack: walk from dp[n][W] upwards to find which parcels were taken
    selected = []
    c = capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:               # value changed -> parcel i was taken
            selected.append(parcels[i - 1])
            c -= parcels[i - 1].weight
    selected.reverse()
    return dp[n][capacity], selected, dp


def knapsack_01_value_only(parcels, capacity):
    """Space-optimised version: one 1-D array, O(W) space.
    Iterating capacity backwards makes sure each parcel is used at most once.
    (Used in Phase 4 to show the memory optimisation.)"""
    dp = [0] * (capacity + 1)
    for p in parcels:
        for c in range(capacity, p.weight - 1, -1):
            if dp[c - p.weight] + p.score > dp[c]:
                dp[c] = dp[c - p.weight] + p.score
    return dp[capacity]


def greedy_by_ratio(parcels, capacity):
    """Greedy heuristic (value/weight ratio). O(n log n) but NOT always optimal
    for 0/1 knapsack - used only for comparison with the DP answer."""
    chosen, total_w, total_v = [], 0, 0
    for p in sorted(parcels, key=lambda p: p.score / p.weight, reverse=True):
        if total_w + p.weight <= capacity:
            chosen.append(p)
            total_w += p.weight
            total_v += p.score
    return total_v, chosen
