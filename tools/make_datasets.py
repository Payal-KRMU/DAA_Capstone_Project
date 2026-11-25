"""
make_datasets.py - creates the sample datasets in data/
    small  : hand-made Gurugram map (11 nodes) + 12 parcels  (easy to trace by hand)
    medium : random city, 60 nodes, 40 parcels
    large  : random city, 400 nodes, 250 parcels
Random datasets use a fixed seed so results are reproducible.
"""
import csv, math, random, os

ROOT = os.path.join(os.path.dirname(__file__), "..", "data")


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)


def road(a, b, pos, factor=1.2):
    (x1, y1), (x2, y2) = pos[a], pos[b]
    return round(math.hypot(x1 - x2, y1 - y2) * factor, 1)   # roads are ~20% longer than straight line


def small():
    locs = [
        ("D", "KRMU Depot, Sohna Road", 10, 2),
        ("L1", "Huda City Centre", 9, 8),
        ("L2", "Cyber City", 5, 12),
        ("L3", "MG Road", 8, 11),
        ("L4", "Golf Course Road", 12, 10),
        ("L5", "Sector 56", 14, 7),
        ("L6", "Udyog Vihar", 3, 14),
        ("L7", "DLF Phase 3", 6, 14),
        ("L8", "Palam Vihar", 1, 10),
        ("L9", "Sector 14", 5, 7),
        ("L10", "Badshahpur", 13, 3),
    ]
    pos = {l[0]: (l[2], l[3]) for l in locs}
    pairs = [("D", "L10"), ("D", "L1"), ("D", "L9"), ("L10", "L5"), ("L1", "L5"),
             ("L1", "L9"), ("L1", "L3"), ("L1", "L4"), ("L4", "L5"), ("L4", "L3"),
             ("L3", "L2"), ("L3", "L7"), ("L2", "L7"), ("L2", "L6"), ("L7", "L6"),
             ("L2", "L9"), ("L9", "L8"), ("L8", "L6"), ("L8", "L2")]
    write_csv(f"{ROOT}/small_locations.csv", ["lid", "name", "x", "y"], locs)
    write_csv(f"{ROOT}/small_roads.csv", ["u", "v", "distance"],
              [(a, b, road(a, b, pos)) for a, b in pairs])
    parcels = [
        ("P01", "L2", 4, 40, 3, 5), ("P02", "L5", 3, 25, 2, 4),
        ("P03", "L8", 6, 50, 6, 3), ("P04", "L1", 2, 18, 1, 5),
        ("P05", "L7", 5, 30, 4, 2), ("P06", "L9", 7, 45, 5, 3),
        ("P07", "L4", 3, 28, 2, 4), ("P08", "L6", 8, 42, 7, 1),
        ("P09", "L10", 2, 15, 3, 2), ("P10", "L3", 4, 35, 3, 4),
        ("P11", "L5", 5, 20, 8, 1), ("P12", "L2", 3, 22, 4, 3),
    ]
    write_csv(f"{ROOT}/small_parcels.csv",
              ["pid", "destination", "weight", "value", "deadline", "priority"], parcels)


def random_city(tag, n_nodes, n_parcels, seed, size=40.0, k=3):
    rnd = random.Random(seed)
    ids = ["D"] + [f"N{i}" for i in range(1, n_nodes)]
    pos = {i: (round(rnd.uniform(0, size), 2), round(rnd.uniform(0, size), 2)) for i in ids}
    pos["D"] = (size / 2, size / 2)                       # depot in the centre
    edges = set()
    for idx, a in enumerate(ids):
        # connect to nearest earlier node -> guarantees the graph is connected
        if idx > 0:
            b = min(ids[:idx], key=lambda b: math.dist(pos[a], pos[b]))
            edges.add(tuple(sorted((a, b))))
        # plus k nearest neighbours -> realistic road mesh
        for b in sorted((b for b in ids if b != a), key=lambda b: math.dist(pos[a], pos[b]))[:k]:
            edges.add(tuple(sorted((a, b))))
    write_csv(f"{ROOT}/{tag}_locations.csv", ["lid", "name", "x", "y"],
              [(i, f"Point {i}", *pos[i]) for i in ids])
    write_csv(f"{ROOT}/{tag}_roads.csv", ["u", "v", "distance"],
              [(a, b, road(a, b, pos)) for a, b in sorted(edges)])
    parcels = []
    for p in range(1, n_parcels + 1):
        parcels.append((f"P{p:03d}", rnd.choice(ids[1:]), rnd.randint(1, 15),
                        rnd.randint(10, 100), rnd.randint(1, 12), rnd.randint(1, 5)))
    write_csv(f"{ROOT}/{tag}_parcels.csv",
              ["pid", "destination", "weight", "value", "deadline", "priority"], parcels)


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    small()
    random_city("medium", 60, 40, seed=7)
    random_city("large", 400, 250, seed=42)
    print("datasets written to data/")
