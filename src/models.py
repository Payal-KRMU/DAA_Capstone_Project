"""
models.py
---------
Data design for the Mini-Courier Planner.

A Parcel is one package that has to be delivered.
A Location is one node (delivery point / depot) of the city road graph.
"""
from dataclasses import dataclass
import csv


@dataclass
class Parcel:
    pid: str          # unique parcel id, e.g. "P01"
    destination: str  # id of the delivery point (graph node) e.g. "L3"
    weight: int       # weight in kg (integer so it can index the DP table)
    value: int        # benefit of delivering it (revenue / importance score)
    deadline: int     # latest delivery time, in hours from the start of the shift
    priority: int     # 1 (low) .. 5 (very urgent)

    @property
    def score(self):
        """Delivery score used by the knapsack = value + 10 x priority.
        Adding the priority bonus makes urgent parcels more attractive to load,
        so a cheap but very urgent parcel is not left behind."""
        return self.value + 10 * self.priority

    def __repr__(self):
        return (f"{self.pid}(to={self.destination}, w={self.weight}kg, "
                f"v={self.value}, dl={self.deadline}h, pr={self.priority})")


@dataclass
class Location:
    lid: str     # node id, e.g. "D" for depot or "L1"
    name: str    # human readable name
    x: float     # map coordinate (km) - only used for drawing the map
    y: float


def load_parcels(path):
    """Read parcels from a CSV file with header:
    pid,destination,weight,value,deadline,priority"""
    parcels = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            parcels.append(Parcel(
                pid=row["pid"],
                destination=row["destination"],
                weight=int(row["weight"]),
                value=int(row["value"]),
                deadline=int(row["deadline"]),
                priority=int(row["priority"]),
            ))
    return parcels


def load_locations(path):
    """Read delivery points from a CSV file with header: lid,name,x,y"""
    locations = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            locations[row["lid"]] = Location(row["lid"], row["name"],
                                             float(row["x"]), float(row["y"]))
    return locations
