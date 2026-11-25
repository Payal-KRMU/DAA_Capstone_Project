"""
Correctness tests for every algorithm.   Run:  python -m unittest -v
Each fast algorithm is checked against a simple, obviously-correct reference.
"""
import random, unittest
from itertools import combinations
from src.models import Parcel
from src.sorting import SORTERS, parcel_key, merge_sort
from src.knapsack import knapsack_01, knapsack_01_value_only, greedy_by_ratio
from src.graph import Graph, dijkstra, reconstruct_path
from src.tsp import (build_distance_matrix, nearest_neighbor_tour, tour_length,
                     two_opt, brute_force_tour)


def random_parcels(n, seed=1):
    r = random.Random(seed)
    return [Parcel(f"P{i}", f"N{r.randint(1, 5)}", r.randint(1, 10), r.randint(5, 60),
                   r.randint(1, 8), r.randint(1, 5)) for i in range(n)]


class TestSorting(unittest.TestCase):
    def test_all_sorters_match_python_sorted(self):
        for n in (0, 1, 2, 10, 200):
            ps = random_parcels(n, seed=n)
            expected = sorted(ps, key=parcel_key)
            for name, fn in SORTERS.items():
                self.assertEqual(fn(ps, key=parcel_key), expected, name)

    def test_earliest_deadline_first_then_priority(self):
        a = Parcel("A", "L1", 1, 1, deadline=3, priority=1)
        b = Parcel("B", "L1", 1, 1, deadline=1, priority=1)
        c = Parcel("C", "L1", 1, 1, deadline=3, priority=5)
        self.assertEqual([p.pid for p in merge_sort([a, b, c], parcel_key)], ["B", "C", "A"])

    def test_merge_sort_is_stable(self):
        data = [(1, "x"), (0, "a"), (1, "y"), (0, "b")]
        self.assertEqual(merge_sort(data, key=lambda t: t[0]),
                         [(0, "a"), (0, "b"), (1, "x"), (1, "y")])


class TestKnapsack(unittest.TestCase):
    def brute(self, ps, W):
        best = 0
        for r in range(len(ps) + 1):
            for combo in combinations(ps, r):
                if sum(p.weight for p in combo) <= W:
                    best = max(best, sum(p.score for p in combo))
        return best

    def test_dp_equals_brute_force(self):
        for seed in range(8):
            ps = random_parcels(10, seed)
            for W in (0, 5, 15, 30):
                val, sel, _ = knapsack_01(ps, W)
                self.assertEqual(val, self.brute(ps, W))
                self.assertLessEqual(sum(p.weight for p in sel), W)
                self.assertEqual(sum(p.score for p in sel), val)
                self.assertEqual(knapsack_01_value_only(ps, W), val)

    def test_greedy_never_beats_dp(self):
        for seed in range(20):
            ps = random_parcels(12, seed)
            self.assertLessEqual(greedy_by_ratio(ps, 25)[0], knapsack_01(ps, 25)[0])

    def test_classic_example(self):
        # weights 1,3,4,5  scores 1,4,5,7  capacity 7  -> best = 9 (items 3+4)
        ps = [Parcel(f"P{i}", "L", w, v, 1, 0) for i, (w, v) in enumerate([(1, 1), (3, 4), (4, 5), (5, 7)])]
        self.assertEqual(knapsack_01(ps, 7)[0], 9)


class TestGraph(unittest.TestCase):
    def setUp(self):
        g = Graph()
        for u, v, w in [("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5), ("C", "D", 8)]:
            g.add_edge(u, v, w)
        self.g = g

    def test_dijkstra_distances(self):
        dist, prev = dijkstra(self.g, "A")
        self.assertEqual(dist, {"A": 0, "B": 3, "C": 1, "D": 8})
        self.assertEqual(reconstruct_path(prev, "A", "D"), ["A", "C", "B", "D"])

    def test_unreachable_node(self):
        self.g.add_node("Z")
        dist, prev = dijkstra(self.g, "A")
        self.assertEqual(dist["Z"], float("inf"))
        self.assertEqual(reconstruct_path(prev, "A", "Z"), [])


class TestTSP(unittest.TestCase):
    def test_tour_is_valid_and_close_to_optimal(self):
        g = Graph.from_csv("data/small_roads.csv")
        stops = ["D", "L2", "L4", "L6", "L8", "L10"]
        m, _ = build_distance_matrix(g, stops)
        nn = nearest_neighbor_tour("D", stops, m)
        self.assertEqual(nn[0], "D"); self.assertEqual(nn[-1], "D")
        self.assertEqual(sorted(nn[1:-1]), sorted(stops[1:]))       # every stop exactly once
        _, opt = brute_force_tour("D", stops, m)
        self.assertGreaterEqual(tour_length(nn, m) + 1e-9, opt)       # heuristic >= optimum
        self.assertLessEqual(tour_length(two_opt(nn, m), m), tour_length(nn, m) + 1e-9)


if __name__ == "__main__":
    unittest.main()
