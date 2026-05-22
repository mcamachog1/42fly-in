# src/engine/dijkstra.py

from heapq import heappush, heappop
from src.model.model import Map, Hub, Connection, Drone, ZoneType


def adjacent_zones(network: Map, zone: str, path: list[str]) -> list[str]:
    get_hub_object = {hub.name: hub for hub in network.hubs}
    zones: list[str] = []
    for conn in network.connections:
        z1, z2 = conn.name.split('-')
        if (z1 == zone and
            z2 not in path # and get_hub_object[z2].zone.name != ZoneType.BLOCKED.name
        ):
            zones.append(z2)
        elif (z2 == zone and
                z1 not in path # and get_hub_object[z1].zone.name != ZoneType.BLOCKED.name               
        ):
            zones.append(z1)
    return zones

def min_cost(
        network: Map,
        start: str) -> dict[str, tuple[int, list[str]]]:

    get_hub_object = {hub.name: hub for hub in network.hubs}
    info: tuple[int, str, list[str]] = (0, start, [start])
    lower_cost: dict[str, tuple[int, list[str]]] = {start: (0, [start])}
    heap = []
    heappush(heap, info)

    while len(heap) > 0:
        cost, zone, path  = heappop(heap)
        if cost > lower_cost.get(zone, (float('inf'), None))[0]:
            continue
        neighbours = adjacent_zones(network, zone, path)
        for neighbor in neighbours:
            new_cost = cost + get_hub_object[neighbor].zone.get_cost()
            new_path = path[:]
            new_path.append(neighbor)            
            low_cost = lower_cost.get(neighbor, (float('inf'), None))[0]
            if new_cost < low_cost:
                lower_cost[neighbor] = new_cost, new_path
                heappush(heap, (new_cost, neighbor, new_path))
    return lower_cost


#    print(neighbours)



