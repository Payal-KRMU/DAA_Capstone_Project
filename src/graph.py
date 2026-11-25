"""
graph.py  (Phase 3 - Route Maker and Graph Processing)
------------------------------------------------------
The city is an UNDIRECTED WEIGHTED graph:
    vertices = depot + delivery points
    edges    = roads, weight = distance in km
It is stored as an ADJACENCY LIST: {node: [(neighbour, distance), ...]}
which uses O(V + E) memory and is ideal for sparse road networks.
"""
import csv
import heapq


class Graph:
    def __init__(self):
        self.adj = {}

    def add_node(self, u):
        self.adj.setdefault(u, [])

    def add_edge(self, u, v, w):
        """Add an undirected road u <-> v of length w km."""
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append((v, w))
        self.adj[v].append((u, w))

    @property
    def num_nodes(self):
        return len(self.adj)

    @property
    def num_edges(self):
        return sum(len(n) for n in self.adj.values()) // 2

    @classmethod
    def from_csv(cls, path):
        """CSV header: u,v,distance"""
        g = cls()
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                g.add_edge(row["u"], row["v"], float(row["distance"]))
        return g


def dijkstra(graph, source):
    """Single-source shortest paths (all edge weights >= 0).
    Uses a binary heap (priority queue): Time O((V + E) log V), Space O(V).
    Returns (dist, prev) where prev[v] is the node before v on the best path."""
    dist = {node: float("inf") for node in graph.adj}
    prev = {node: None for node in graph.adj}
    dist[source] = 0.0
    heap = [(0.0, source)]
    visited = set()

    while heap:
        d, u = heapq.heappop(heap)          # closest unvisited node
        if u in visited:
            continue                        # stale heap entry, skip it
        visited.add(u)
        for v, w in graph.adj[u]:           # relax every outgoing edge
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, prev


def reconstruct_path(prev, source, target):
    """Follow the prev[] pointers backwards from target to source."""
    path = []
    node = target
    while node is not None:
        path.append(node)
        if node == source:
            break
        node = prev[node]
    path.reverse()
    return path if path and path[0] == source else []
