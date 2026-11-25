# Mini-Courier Planner — DAA Capstone Assignment

**Course:** Design & Analysis of Algorithms (ETCCDA302) · K.R. Mangalam University
**Student:** Payal · Roll No. 2501730224 · B.Tech CSE, Sem 3, Section A
**Faculty:** Dr. Shweta Agarwal

A Python prototype that takes a list of parcels and a city road map and produces
1. a **priority order** of parcels (Merge Sort),
2. the **optimal set of parcels** that fits in the van for one trip (0/1 Knapsack, Dynamic Programming),
3. **shortest road paths** between all stops (Dijkstra),
4. an **ordered delivery route** (Nearest-Neighbour TSP approximation + 2-opt improvement),
5. a **delivery schedule with deadline check** and **runtime measurements** of every step.

```
parcels.csv ─► Merge Sort ─► 0/1 Knapsack DP ─► selected parcels ─┐
roads.csv   ─────────────────────────────────► Dijkstra (each stop) ─► NN-TSP + 2-opt ─► route + schedule
```

## Project structure
```
courier_planner/
├── main.py                 # run the full planner (Phases 2 + 3)
├── benchmark.py            # Phase 4 runtime tests + charts
├── visualize.py            # design diagram + route map
├── requirements.txt
├── src/
│   ├── models.py           # Parcel / Location data design, CSV loaders
│   ├── sorting.py          # Merge, Quick, Insertion sort
│   ├── knapsack.py         # 0/1 knapsack DP (+ 1-D version, greedy for comparison)
│   ├── graph.py            # adjacency-list graph + Dijkstra
│   ├── tsp.py              # distance matrix, nearest neighbour, 2-opt, brute force
│   └── planner.py          # integrates all steps + prints the output trace
├── data/                   # small / medium / large sample datasets (CSV)
├── tests/test_algorithms.py# correctness tests
├── tools/                  # dataset generator, screenshot renderer
├── outputs/
│   ├── traces/             # saved program outputs
│   ├── charts/             # runtime charts, design diagram, route map
│   ├── screenshots/        # terminal screenshots of the runs
│   └── benchmark_results.csv
└── docs/DESIGN.md          # Phase 1 design document
```

## How to run
```bash
pip install -r requirements.txt

python main.py                                   # small dataset (Gurugram map, 20 kg van)
python main.py --dataset medium --capacity 80    # 60 nodes, 40 parcels
python main.py --dataset large  --capacity 150   # 400 nodes, 250 parcels
python main.py --no-2opt                         # plain nearest-neighbour route
python main.py --save outputs/traces/run.txt     # also save the trace

python -m unittest -v                            # correctness tests
python benchmark.py                              # runtime tests -> outputs/charts/*.png
python visualize.py                              # design diagram + route map
python tools/make_datasets.py                    # regenerate the datasets
```
Use your own data: `python main.py --parcels p.csv --roads r.csv --locations l.csv --capacity 30`

## Input formats
| File | Columns | Example |
|------|---------|---------|
| parcels | `pid,destination,weight,value,deadline,priority` | `P01,L2,4,40,3,5` |
| roads | `u,v,distance` (undirected, km) | `D,L1,7.3` |
| locations | `lid,name,x,y` (node `D` = depot) | `L2,Cyber City,5,12` |

## Results on the small dataset (20 kg van)
* Sorted order: P04, P02, P07, P01, P10, P09, P12, P05, P06, P03, P08, P11
* Knapsack picks **P04, P02, P07, P01, P10, P12** → 19/20 kg, score 418 (greedy would get only 401)
* Route: **D → L1 → L3 → L2 → L4 → L5 → D = 36.6 km** (equal to the brute-force optimum)
* All 6 parcels delivered on time.

## Complexity summary
| Step | Algorithm | Time | Space |
|------|-----------|------|-------|
| Prioritise | Merge Sort | O(n log n) | O(n) |
| Box filling | 0/1 Knapsack DP | O(n·W) | O(n·W) (O(W) value-only) |
| Shortest paths | Dijkstra, binary heap | O((V+E) log V) per source | O(V) |
| Distance matrix | Dijkstra from k stops | O(k (V+E) log V) | O(k²) |
| Route | Nearest Neighbour | O(k²) | O(k) |
| Improvement | 2-opt | O(k²) per pass | O(k) |
