"""
tsp.py  (Phase 3 - overall delivery route)
------------------------------------------
Visiting every delivery stop exactly once and returning to the depot is the
Travelling Salesman Problem (NP-hard). We use the Nearest-Neighbour heuristic:

    start at the depot
    repeat: go to the closest stop that is not visited yet
    finally return to the depot

Distances between stops are the SHORTEST ROAD distances from Dijkstra
(the "metric closure" of the road graph), so the heuristic works on real roads.

Nearest Neighbour: Time O(k^2) for k stops.
2-opt (optional improvement) and brute force (exact, only for small k) are
included for Phase 4 comparison.
"""
from itertools import permutations
from .graph import dijkstra, reconstruct_path


def build_distance_matrix(graph, stops):
    """Run Dijkstra once from every stop. Returns
    matrix[a][b] = shortest distance, paths[a][b] = list of nodes on that path."""
    matrix, paths = {}, {}
    for s in stops:
        dist, prev = dijkstra(graph, s)
        matrix[s] = {t: dist[t] for t in stops}
        paths[s] = {t: reconstruct_path(prev, s, t) for t in stops}
    return matrix, paths


def nearest_neighbor_tour(depot, stops, matrix):
    """Greedy tour depot -> nearest unvisited stop -> ... -> depot."""
    unvisited = [s for s in stops if s != depot]
    tour = [depot]
    current = depot
    while unvisited:
        nxt = min(unvisited, key=lambda s: (matrix[current][s], s))
        tour.append(nxt)
        unvisited.remove(nxt)
        current = nxt
    tour.append(depot)                       # come back to the depot
    return tour


def tour_length(tour, matrix):
    return sum(matrix[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))


def two_opt(tour, matrix):
    """Local improvement: reverse a segment whenever it makes the tour shorter.
    Repeats until no improving move exists."""
    best = tour[:]
    improved = True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                a, b = best[i - 1], best[i]
                c, d = best[j], best[j + 1]
                delta = (matrix[a][c] + matrix[b][d]) - (matrix[a][b] + matrix[c][d])
                if delta < -1e-9:
                    best[i:j + 1] = reversed(best[i:j + 1])
                    improved = True
    return best


def brute_force_tour(depot, stops, matrix):
    """Exact optimum by trying every order. O(k!) - only for k <= 9."""
    others = [s for s in stops if s != depot]
    best_tour, best_len = None, float("inf")
    for perm in permutations(others):
        t = [depot, *perm, depot]
        L = tour_length(t, matrix)
        if L < best_len:
            best_tour, best_len = t, L
    return best_tour, best_len


def expand_tour(tour, paths):
    """Turn the stop-to-stop tour into the full road-by-road path."""
    full = [tour[0]]
    for i in range(len(tour) - 1):
        full.extend(paths[tour[i]][tour[i + 1]][1:])
    return full
