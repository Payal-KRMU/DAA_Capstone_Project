"""
visualize.py - draws the system design diagram and the delivery-route map.
Run:  python visualize.py      (images saved in outputs/charts/)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from src.models import load_parcels, load_locations
from src.graph import Graph
from src.planner import plan_trip

CH = os.path.join(os.path.dirname(__file__), "outputs", "charts")
os.makedirs(CH, exist_ok=True)


def design_diagram():
    fig, ax = plt.subplots(figsize=(11, 4.6)); ax.axis("off")
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.6)
    boxes = [
        (0.2, 2.6, "INPUT\nparcels.csv\nroads.csv\nlocations.csv", "#e8eef7"),
        (2.4, 2.6, "STEP 1\nMerge Sort\n(deadline ↑, priority ↓)\nO(n log n)", "#fde9d9"),
        (4.6, 2.6, "STEP 2\n0/1 Knapsack DP\n(van capacity W)\nO(n·W)", "#fde9d9"),
        (6.8, 2.6, "STEP 3\nDijkstra from\nevery stop\nO(k(V+E)log V)", "#e2f0d9"),
        (9.0, 2.6, "STEP 4\nNearest-Neighbour\nTSP + 2-opt\nO(k²)", "#e2f0d9"),
    ]
    for x, y, t, c in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 1.8, 1.6, boxstyle="round,pad=0.05", fc=c, ec="#333"))
        ax.text(x + .9, y + .8, t, ha="center", va="center", fontsize=8.6)
    for x in (2.0, 4.2, 6.4, 8.6):
        ax.annotate("", (x + .4, 3.4), (x + .02, 3.4), arrowprops=dict(arrowstyle="->", lw=1.6))
    outs = [(2.4, "Priority list\n(dispatch order)"), (4.6, "Selected parcels\n+ packing plan\n+ deferred list"),
            (6.8, "Shortest-path\ndistance matrix"), (9.0, "Final route,\nlength, schedule,\ndeadline check")]
    for x, t in outs:
        ax.add_patch(FancyBboxPatch((x, .35), 1.8, 1.3, boxstyle="round,pad=0.05", fc="white", ec="#888", ls="--"))
        ax.text(x + .9, 1.0, t, ha="center", va="center", fontsize=8.2)
        ax.annotate("", (x + .9, 1.7), (x + .9, 2.55), arrowprops=dict(arrowstyle="->", color="#888"))
    ax.text(5.5, 4.45, "Mini-Courier Planner - how the algorithms work together", ha="center",
            fontsize=12, weight="bold")
    ax.text(1.1, 1.0, "STEP 5\nPhase 4 benchmark\nmeasures every step", ha="center", va="center",
            fontsize=8.2, style="italic")
    plt.tight_layout(); plt.savefig(f"{CH}/0_system_design.png", dpi=150); plt.close()


def route_map():
    locs = load_locations("data/small_locations.csv")
    g = Graph.from_csv("data/small_roads.csv")
    res = plan_trip(load_parcels("data/small_parcels.csv"), g, "D", 20)
    fig, ax = plt.subplots(figsize=(8, 7))
    drawn = set()
    for u, nbrs in g.adj.items():                    # all roads, grey
        for v, w in nbrs:
            if (v, u) in drawn: continue
            drawn.add((u, v))
            a, b = locs[u], locs[v]
            ax.plot([a.x, b.x], [a.y, b.y], color="#bbb", lw=1.2, zorder=1)
            ax.text((a.x + b.x) / 2, (a.y + b.y) / 2, f"{w:g}", fontsize=7, color="#777")
    path = res["full_path"]                          # chosen route, coloured arrows
    for i in range(len(path) - 1):
        a, b = locs[path[i]], locs[path[i + 1]]
        ax.annotate("", (b.x, b.y), (a.x, a.y),
                    arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.2, shrinkA=9, shrinkB=9), zorder=2)
    stops = set(res["stops"])
    for lid, l in locs.items():
        c = "black" if lid == "D" else ("tab:red" if lid in stops else "tab:blue")
        ax.scatter(l.x, l.y, s=260 if lid == "D" else 140, c=c, marker="s" if lid == "D" else "o", zorder=3)
        ax.text(l.x + .3, l.y + .35, f"{lid}\n{l.name}", fontsize=7.5, zorder=4)
    order = res["final_tour"]
    ax.set_title(f"Delivery route (red): {' → '.join(order)}\nlength = {res['final_len']:.1f} km   "
                 f"(red = stop on this trip, blue = no parcel this trip)", fontsize=10)
    ax.set_xlabel("x (km)"); ax.set_ylabel("y (km)"); ax.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(f"{CH}/7_small_route_map.png", dpi=140); plt.close()


if __name__ == "__main__":
    design_diagram(); route_map(); print("design diagram and route map saved")
