"""
benchmark.py  (Phase 4 - Performance Testing and Optimization)
--------------------------------------------------------------
Measures the runtime of every major step for growing input sizes,
saves the numbers to outputs/benchmark_results.csv and draws charts in outputs/charts/.

Run:  python benchmark.py
"""
import csv, math, os, random, time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models import Parcel, load_parcels
from src.sorting import SORTERS, parcel_key
from src.knapsack import knapsack_01, knapsack_01_value_only, greedy_by_ratio
from src.graph import Graph, dijkstra
from src.tsp import (build_distance_matrix, nearest_neighbor_tour, tour_length,
                     two_opt, brute_force_tour)
from src.planner import plan_trip

OUT = os.path.join(os.path.dirname(__file__), "outputs")
CH = os.path.join(OUT, "charts")
os.makedirs(CH, exist_ok=True)
rows = []                      # every measurement goes into the CSV
plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": .3})


def timeit(fn, repeat=3):
    """Best of `repeat` runs, in milliseconds (minimum = least noise)."""
    best = float("inf")
    for _ in range(repeat):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best * 1000


def rand_parcels(n, seed=0):
    r = random.Random(seed)
    return [Parcel(f"P{i}", "N1", r.randint(1, 15), r.randint(10, 100),
                   r.randint(1, 12), r.randint(1, 5)) for i in range(n)]


def rand_graph(v, seed=0, k=3):
    """Random connected planar-ish road graph with about k*v edges."""
    r = random.Random(seed)
    pts = [(r.uniform(0, 100), r.uniform(0, 100)) for _ in range(v)]
    cell = {}
    for i, p in enumerate(pts):                     # grid buckets for fast neighbour search
        cell.setdefault((int(p[0] // 5), int(p[1] // 5)), []).append(i)
    g = Graph()
    for i, p in enumerate(pts):
        if i:   # tree edge to nearest of a window of earlier nodes -> connected
            j = min(range(max(0, i - 40), i), key=lambda j: math.dist(p, pts[j]))
            g.add_edge(i, j, round(math.dist(p, pts[j]) * 1.2, 2))
        cx, cy = int(p[0] // 5), int(p[1] // 5)
        near = [j for dx in (-1, 0, 1) for dy in (-1, 0, 1) for j in cell.get((cx + dx, cy + dy), []) if j != i]
        for j in sorted(near, key=lambda j: math.dist(p, pts[j]))[:k]:
            g.add_edge(i, j, round(math.dist(p, pts[j]) * 1.2, 2))
    return g, pts


# ------------------------------------------------------------------ 1. sorting
print("1) Sorting ...")
sizes = [100, 500, 1000, 2000, 4000]
sort_res = {name: [] for name in SORTERS}
for n in sizes:
    ps = rand_parcels(n, n)
    for name, fn in SORTERS.items():
        ms = timeit(lambda: fn(ps, key=parcel_key), repeat=1 if name == "Insertion Sort" else 3)
        sort_res[name].append(ms); rows.append(("sorting", name, n, round(ms, 4)))
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
for name, ys in sort_res.items():
    ax[0].plot(sizes, ys, marker="o", label=name)
    ax[1].plot(sizes, ys, marker="o", label=name)
ax[0].set_xlabel("number of parcels (n)"); ax[0].set_ylabel("time (ms)")
ax[0].set_title("Sorting runtime (linear scale)"); ax[0].legend()
ax[1].set_yscale("log"); ax[1].set_xlabel("number of parcels (n)"); ax[1].set_ylabel("time (ms, log scale)")
ax[1].set_title("Same data, log scale - O(n log n) vs O(n^2)")
plt.tight_layout(); plt.savefig(f"{CH}/1_sorting_runtime.png"); plt.close()

# ---------------------------------------------------------------- 2. knapsack
print("2) Knapsack ...")
ns = [50, 100, 200, 400, 800]; W = 200
dp_t, dp1_t, gr_t, ratio = [], [], [], []
for n in ns:
    ps = rand_parcels(n, n + 1)
    dp_t.append(timeit(lambda: knapsack_01(ps, W)))
    dp1_t.append(timeit(lambda: knapsack_01_value_only(ps, W)))
    gr_t.append(timeit(lambda: greedy_by_ratio(ps, W)))
    ratio.append(greedy_by_ratio(ps, W)[0] / knapsack_01(ps, W)[0] * 100)
    rows += [("knapsack", "DP full table O(nW)", n, round(dp_t[-1], 4)),
             ("knapsack", "DP 1-D array O(W) space", n, round(dp1_t[-1], 4)),
             ("knapsack", "Greedy ratio", n, round(gr_t[-1], 4)),
             ("knapsack_quality", "greedy % of optimal", n, round(ratio[-1], 2))]
caps = [50, 100, 200, 400, 800]; cap_t = []
ps400 = rand_parcels(300, 99)
for c in caps:
    cap_t.append(timeit(lambda: knapsack_01(ps400, c)))
    rows.append(("knapsack_capacity", "DP n=300", c, round(cap_t[-1], 4)))
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
ax[0].plot(ns, dp_t, "o-", label="DP (full table)")
ax[0].plot(ns, dp1_t, "s-", label="DP (1-D, space-optimised)")
ax[0].plot(ns, gr_t, "^-", label="Greedy by ratio")
ax[0].set_xlabel(f"number of parcels (n), W = {W} kg"); ax[0].set_ylabel("time (ms)")
ax[0].set_title("Knapsack runtime vs n"); ax[0].legend()
ax[1].plot(caps, cap_t, "o-", color="tab:red")
ax[1].set_xlabel("van capacity W (kg), n = 300"); ax[1].set_ylabel("time (ms)")
ax[1].set_title("DP runtime grows linearly with W")
plt.tight_layout(); plt.savefig(f"{CH}/2_knapsack_runtime.png"); plt.close()
plt.figure(figsize=(6, 3.6))
plt.bar([str(n) for n in ns], ratio, color="tab:orange")
plt.axhline(100, color="k", ls="--", lw=1); plt.ylim(min(ratio) - 3, 101)
plt.xlabel("n"); plt.ylabel("greedy score as % of DP optimum")
plt.title("Greedy is fast but not always optimal")
plt.tight_layout(); plt.savefig(f"{CH}/3_knapsack_quality.png"); plt.close()

# ---------------------------------------------------------------- 3. dijkstra
print("3) Dijkstra ...")
vs = [500, 1000, 2000, 5000, 10000]; dj = []; es = []
for v in vs:
    g, _ = rand_graph(v, v)
    dj.append(timeit(lambda: dijkstra(g, 0))); es.append(g.num_edges)
    rows.append(("dijkstra", f"V={v},E={g.num_edges}", v, round(dj[-1], 4)))
theory = [(v + e) * math.log2(v) for v, e in zip(vs, es)]
scale = dj[-1] / theory[-1]
plt.figure(figsize=(7, 4.2))
plt.plot(vs, dj, "o-", label="measured Dijkstra (binary heap)")
plt.plot(vs, [t * scale for t in theory], "--", label="c·(V+E)·log V (theory)")
plt.xlabel("number of nodes V"); plt.ylabel("time (ms)")
plt.title("Dijkstra single-source runtime"); plt.legend()
plt.tight_layout(); plt.savefig(f"{CH}/4_dijkstra_runtime.png"); plt.close()

# --------------------------------------------------------------------- 4. TSP
print("4) TSP ...")
g, _ = rand_graph(3000, 5)
ks = [10, 25, 50, 100, 200]; nn_t, op_t, gain = [], [], []
r = random.Random(3)
for k in ks:
    stops = [0] + r.sample(range(1, 3000), k)
    m, _ = build_distance_matrix(g, stops)
    nn_t.append(timeit(lambda: nearest_neighbor_tour(0, stops, m)))
    tour = nearest_neighbor_tour(0, stops, m)
    t = time.perf_counter(); imp = two_opt(tour, m); op_t.append((time.perf_counter() - t) * 1000)
    gain.append((1 - tour_length(imp, m) / tour_length(tour, m)) * 100)
    rows += [("tsp", "Nearest neighbour", k, round(nn_t[-1], 4)),
             ("tsp", "2-opt", k, round(op_t[-1], 4)),
             ("tsp_gain", "2-opt % shorter", k, round(gain[-1], 2))]
approx = []
for k in range(4, 10):
    vals = []
    for trial in range(5):
        stops = [0] + random.Random(k * 10 + trial).sample(range(1, 3000), k)
        m, _ = build_distance_matrix(g, stops)
        vals.append(tour_length(nearest_neighbor_tour(0, stops, m), m) / brute_force_tour(0, stops, m)[1])
    approx.append(sum(vals) / len(vals))
    rows.append(("tsp_ratio", "NN / optimal (avg of 5)", k, round(approx[-1], 4)))
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
ax[0].plot(ks, nn_t, "o-", label="Nearest neighbour O(k²)")
ax[0].plot(ks, op_t, "s-", label="2-opt improvement")
ax[0].set_yscale("log"); ax[0].set_xlabel("number of stops k"); ax[0].set_ylabel("time (ms, log)")
ax[0].set_title("Route construction runtime"); ax[0].legend()
ax[1].bar([str(k) for k in range(4, 10)], approx, color="tab:green")
ax[1].axhline(1, color="k", ls="--", lw=1); ax[1].set_ylim(0.95, max(approx) + .05)
ax[1].set_xlabel("stops k (brute force = exact optimum)"); ax[1].set_ylabel("NN length / optimal")
ax[1].set_title("Nearest-neighbour approximation ratio")
plt.tight_layout(); plt.savefig(f"{CH}/5_tsp_runtime_quality.png"); plt.close()

# ------------------------------------------------- 5. full pipeline per dataset
print("5) Pipeline ...")
caps = {"small": 20, "medium": 80, "large": 150}
steps = {}
for ds, cap in caps.items():
    ps = load_parcels(f"data/{ds}_parcels.csv"); gg = Graph.from_csv(f"data/{ds}_roads.csv")
    plan_trip(ps, gg, "D", cap)                      # warm-up
    res = plan_trip(ps, gg, "D", cap)
    for k, v in res["timings"].items():
        steps.setdefault(k, []).append(v * 1000)
        rows.append(("pipeline", k, ds, round(v * 1000, 4)))
plt.figure(figsize=(7, 4.2))
bottom = [0] * 3
for k, vals in steps.items():
    plt.bar(list(caps), vals, bottom=bottom, label=k)
    bottom = [b + v for b, v in zip(bottom, vals)]
plt.ylabel("time (ms)"); plt.title("Runtime of each major step per dataset")
plt.legend(fontsize=8); plt.tight_layout(); plt.savefig(f"{CH}/6_pipeline_breakdown.png"); plt.close()

with open(f"{OUT}/benchmark_results.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["experiment", "variant", "input_size", "time_ms_or_metric"]); w.writerows(rows)
for r_ in rows:
    print(f"  {r_[0]:<18}{r_[1]:<28}{str(r_[2]):>8}{r_[3]:>12}")
print("charts saved in outputs/charts/")
