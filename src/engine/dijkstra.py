# src/engine/dijkstra.py

from typing import Optional
from heapq import heappush, heappop
from src.model.model import Map, ZoneType


class MinCost():
    def __init__(self, network: Map, start: str) -> None:
        self.network = network
        self.start = start


    def _adjacent_zones(
        self,
        zone: str,
        exclude: Optional[list[str]] = None
    ) -> list[str]:

        zones: list[str] = []
        for conn in self.network.connections:
            z1, z2 = conn.name.split('-')
            if exclude is not None:
                if z1 in exclude or z2 in exclude:
                    continue
            if z1 == zone:
                zones.append(z2)
            elif z2 == zone:
                zones.append(z1)
        return zones


    def lower_cost_path(self, exclude: Optional[list[str]] = None) -> dict[str, tuple[int, list[str]]]:

        get_hub_object = {hub.name: hub for hub in network.hubs}
        info: tuple[int, str, list[str]] = (0, self.start, [self.start])
        lower_cost: dict[str, tuple[int, list[str]]] = {self.start: (0, [self.start])}
        # list of tuples (cost, zone, path-until-this-zone)
        heap: list[tuple[int, str, list[str]]] = []
        heappush(heap, info)

        while len(heap) > 0:
            cost, zone, path = heappop(heap)
            if cost > lower_cost.get(zone, (float('inf'), None))[0]:
                continue
            neighbours = self._adjacent_zones(self, zone, exclude)
            for neighbor in neighbours:
                new_cost = cost + self.network.lookup_hubs[neighbor].cost
                new_path = path[:]
                new_path.append(neighbor)
                low_cost = lower_cost.get(neighbor, (float('inf'), None))[0]
                if new_cost < low_cost:
                    lower_cost[neighbor] = new_cost, new_path
                    heappush(heap, (new_cost, neighbor, new_path))
                # Condition to give priority to PRIORITY TypeZone
                elif (
                    new_cost == low_cost and
                    get_hub_object[neighbor].zone.name == ZoneType.PRIORITY.name
                ):
                    lower_cost[neighbor] = new_cost, new_path
                    heappush(heap, (new_cost, neighbor, new_path))
        return lower_cost



def min_cost(
    network: Map,
    start: str,
    exclude: Optional[list[str]] = None
) -> dict[str, tuple[int, list[str]]]:

    get_hub_object = {hub.name: hub for hub in network.hubs}
    info: tuple[int, str, list[str]] = (0, start, [start])
    lower_cost: dict[str, tuple[int, list[str]]] = {start: (0, [start])}
    heap: list[tuple[int, str, list[str]]] = []
    heappush(heap, info)

    while len(heap) > 0:
        cost, zone, path = heappop(heap)
        if cost > lower_cost.get(zone, (float('inf'), None))[0]:
            continue
        neighbours = adjacent_zones(network, zone, exclude)
        for neighbor in neighbours:
            new_cost = cost + get_hub_object[neighbor].cost
            new_path = path[:]
            new_path.append(neighbor)
            low_cost = lower_cost.get(neighbor, (float('inf'), None))[0]
            if new_cost < low_cost:
                lower_cost[neighbor] = new_cost, new_path
                heappush(heap, (new_cost, neighbor, new_path))
            # Condition to give priority to PRIORITY TypeZone
            elif (
                new_cost == low_cost and
                get_hub_object[neighbor].zone.name == ZoneType.PRIORITY.name
            ):
                lower_cost[neighbor] = new_cost, new_path
                heappush(heap, (new_cost, neighbor, new_path))
    return lower_cost
