"""
main.py - command-line entry point of the Mini-Courier Planner

Examples
    python main.py                               # small dataset, 20 kg van
    python main.py --dataset medium --capacity 80
    python main.py --dataset large  --capacity 150 --no-2opt
    python main.py --parcels my_parcels.csv --roads my_roads.csv --locations my_locs.csv
"""
import argparse, os
from src.models import load_parcels, load_locations
from src.graph import Graph
from src.planner import plan_trip, format_report

DEFAULT_CAP = {"small": 20, "medium": 80, "large": 150}


def main():
    ap = argparse.ArgumentParser(description="Mini-Courier Planner (DAA Capstone)")
    ap.add_argument("--dataset", default="small", choices=["small", "medium", "large"])
    ap.add_argument("--parcels"); ap.add_argument("--roads"); ap.add_argument("--locations")
    ap.add_argument("--capacity", type=int, help="van capacity in kg")
    ap.add_argument("--depot", default="D")
    ap.add_argument("--speed", type=float, default=30.0, help="average speed km/h")
    ap.add_argument("--no-2opt", action="store_true", help="use plain nearest-neighbour route")
    ap.add_argument("--save", help="save the output trace to this file")
    args = ap.parse_args()

    base = os.path.join(os.path.dirname(__file__), "data", args.dataset)
    parcels = load_parcels(args.parcels or f"{base}_parcels.csv")
    graph = Graph.from_csv(args.roads or f"{base}_roads.csv")
    loc_path = args.locations or f"{base}_locations.csv"
    locations = load_locations(loc_path) if os.path.exists(loc_path) else None
    capacity = args.capacity or DEFAULT_CAP[args.dataset]

    print(f"Loaded {len(parcels)} parcels, graph with {graph.num_nodes} nodes / "
          f"{graph.num_edges} roads, van capacity {capacity} kg\n")
    res = plan_trip(parcels, graph, args.depot, capacity,
                    speed_kmph=args.speed, use_two_opt=not args.no_2opt)
    report = format_report(res, locations if args.dataset == "small" or args.locations else None)
    print(report)
    if args.save:
        with open(args.save, "w") as f:
            f.write(report)
        print(f"\nTrace saved to {args.save}")


if __name__ == "__main__":
    main()
