"""
planner.py  - integrates all phases into one pipeline
-----------------------------------------------------
    parcels.csv ──► [1] Merge Sort (deadline, priority)      -> priority list
                    [2] 0/1 Knapsack DP (van capacity)      -> parcels for this trip
    roads.csv   ──► [3] Dijkstra from every stop            -> shortest-path matrix
                    [4] Nearest-Neighbour TSP (+ 2-opt)      -> delivery route
                    [5] Deadline check along the route       -> on-time report
"""
import time
from .sorting import prioritize_parcels
from .knapsack import knapsack_01
from .graph import dijkstra, reconstruct_path
from .tsp import (build_distance_matrix, nearest_neighbor_tour, tour_length,
                  two_opt, expand_tour)


def plan_trip(parcels, graph, depot, capacity, speed_kmph=30.0,
              service_min=6.0, use_two_opt=True):
    timings = {}

    # ---- Step 1: prioritise parcels (Merge Sort) -----------------------
    t = time.perf_counter()
    ordered = prioritize_parcels(parcels)
    timings["Sorting (Merge Sort)"] = time.perf_counter() - t

    # ---- Step 2: choose parcels for one trip (0/1 Knapsack DP) -----------
    t = time.perf_counter()
    best_value, selected, dp = knapsack_01(ordered, capacity)
    timings["Knapsack DP"] = time.perf_counter() - t
    selected_ids = {p.pid for p in selected}
    deferred = [p for p in ordered if p.pid not in selected_ids]   # stays sorted

    # ---- Step 3: shortest paths between all stops (Dijkstra) -------------
    stops = [depot] + sorted({p.destination for p in selected})
    t = time.perf_counter()
    depot_dist, depot_prev = dijkstra(graph, depot)
    matrix, paths = build_distance_matrix(graph, stops)
    timings["Dijkstra (all stops)"] = time.perf_counter() - t

    # ---- Step 4: delivery route (Nearest-Neighbour TSP + 2-opt) ----------
    t = time.perf_counter()
    nn_tour = nearest_neighbor_tour(depot, stops, matrix)
    timings["NN-TSP route"] = time.perf_counter() - t
    nn_len = tour_length(nn_tour, matrix)

    final_tour, final_len = nn_tour, nn_len
    if use_two_opt and len(stops) > 3:
        t = time.perf_counter()
        improved = two_opt(nn_tour, matrix)
        timings["2-opt improvement"] = time.perf_counter() - t
        if tour_length(improved, matrix) < nn_len - 1e-9:
            final_tour, final_len = improved, tour_length(improved, matrix)

    full_path = expand_tour(final_tour, paths)

    # ---- Step 5: arrival times and deadline check ------------------------
    schedule, clock, travelled = [], 0.0, 0.0
    for i in range(1, len(final_tour) - 1):
        leg = matrix[final_tour[i - 1]][final_tour[i]]
        travelled += leg
        clock += leg / speed_kmph
        stop = final_tour[i]
        for p in (q for q in selected if q.destination == stop):
            schedule.append({"parcel": p, "stop": stop, "km": travelled,
                             "arrival_h": clock, "on_time": clock <= p.deadline})
        clock += service_min / 60.0           # time spent handing over the parcel

    return {
        "ordered": ordered, "selected": selected, "deferred": deferred,
        "best_value": best_value, "dp": dp, "capacity": capacity,
        "stops": stops, "depot_dist": depot_dist, "depot_prev": depot_prev,
        "matrix": matrix, "paths": paths,
        "nn_tour": nn_tour, "nn_len": nn_len,
        "final_tour": final_tour, "final_len": final_len,
        "full_path": full_path, "schedule": schedule, "timings": timings,
    }


# ------------------------------------------------------------- pretty printing
def _line(ch="=", n=78):
    return ch * n


def format_report(res, locations=None, show_dp=True):
    """Builds the readable output trace that is printed and saved."""
    name = (lambda lid: f"{lid} ({locations[lid].name})") if locations else (lambda lid: lid)
    out = []
    w = out.append

    w(_line()); w("MINI-COURIER PLANNER - OUTPUT TRACE"); w(_line())

    w("\n[PHASE 2-A] PARCELS SORTED BY (deadline ASC, priority DESC) - Merge Sort")
    w(f"{'#':>3} {'ID':<6}{'Dest':<6}{'Wt(kg)':>7}{'Value':>7}{'Deadline(h)':>12}{'Priority':>9}{'Score':>7}")
    for i, p in enumerate(res["ordered"], 1):
        w(f"{i:>3} {p.pid:<6}{p.destination:<6}{p.weight:>7}{p.value:>7}{p.deadline:>12}{p.priority:>9}{p.score:>7}")

    w("Score = value + 10 x priority (used as the knapsack value)")
    w(f"\n[PHASE 2-B] 0/1 KNAPSACK (Dynamic Programming)  capacity = {res['capacity']} kg")
    dp, n = res["dp"], len(res["ordered"])
    if show_dp and res["capacity"] <= 30 and n <= 20:
        W = res["capacity"]
        w("DP table  dp[i][c] = best score using first i parcels with capacity c")
        w("i/item   " + "".join(f"{c:>4}" for c in range(W + 1)))
        for i in range(n + 1):
            label = "0 (none)" if i == 0 else f"{i} {res['ordered'][i-1].pid}"
            w(f"{label:<9}" + "".join(f"{v:>4}" for v in dp[i]))
    tw = sum(p.weight for p in res["selected"])
    w(f"Selected parcels ({len(res['selected'])}): " + ", ".join(p.pid for p in res["selected"]))
    w(f"Total weight = {tw} / {res['capacity']} kg   Total score = {res['best_value']}   "
      f"(revenue value = {sum(p.value for p in res['selected'])})")
    w("Packing plan (load in REVERSE delivery order so first drop is at the door):")
    order = {s: i for i, s in enumerate(res["final_tour"])}
    for slot, p in enumerate(sorted(res["selected"], key=lambda p: -order[p.destination]), 1):
        w(f"   slot {slot:>2}: {p.pid} -> {name(p.destination)}  [{p.weight} kg]")
    w("Deferred to next trip: " + (", ".join(p.pid for p in res["deferred"]) or "none"))

    w("\n[PHASE 3-A] DIJKSTRA - shortest paths from depot " + res["stops"][0])
    for s in res["stops"][1:]:
        path = reconstruct_path(res["depot_prev"], res["stops"][0], s)
        w(f"   {s:<5} {res['depot_dist'][s]:>7.2f} km   path: {' -> '.join(path)}")

    w("\n[PHASE 3-B] SHORTEST-DISTANCE MATRIX BETWEEN STOPS (km)")
    st = res["stops"]
    if len(st) <= 14:
        w("       " + "".join(f"{s:>7}" for s in st))
        for a in st:
            w(f"{a:<7}" + "".join(f"{res['matrix'][a][b]:>7.1f}" for b in st))
    else:
        w(f"   ({len(st)} stops - matrix omitted from trace)")

    w("\n[PHASE 3-C] DELIVERY ROUTE")
    w("Nearest-Neighbour tour : " + " -> ".join(res["nn_tour"]) + f"   = {res['nn_len']:.2f} km")
    w("Final tour (after 2-opt): " + " -> ".join(res["final_tour"]) + f"   = {res['final_len']:.2f} km")
    w("Full road path         : " + " -> ".join(res["full_path"]))

    w("\n[PHASE 3-D] DELIVERY SCHEDULE & DEADLINE CHECK")
    w(f"{'Parcel':<8}{'Stop':<28}{'Cum km':>8}{'Arrive(h)':>10}{'Deadline':>9}  Status")
    for e in res["schedule"]:
        p = e["parcel"]
        w(f"{p.pid:<8}{name(e['stop'])[:27]:<28}{e['km']:>8.2f}{e['arrival_h']:>10.2f}"
          f"{p.deadline:>9}  {'ON TIME' if e['on_time'] else 'LATE'}")
    late = sum(1 for e in res["schedule"] if not e["on_time"])
    w(f"On-time deliveries: {len(res['schedule']) - late}/{len(res['schedule'])}")

    w("\n[PHASE 4] RUNTIME OF MAJOR STEPS")
    for k, v in res["timings"].items():
        w(f"   {k:<24}{v * 1000:>10.3f} ms")
    w(_line())
    return "\n".join(out)
