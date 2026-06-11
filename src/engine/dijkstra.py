# src/engine/dijkstra.py

from typing import Optional
from heapq import heappush, heappop
from src.model.model import Map, ZoneType


class CostedMap:
    """Manages routing network costs and evaluates minimal path algorithms.

    This class serves as a utility wrapper around the simulation Map model
    to perform core pathfinding calculations, tracking node traversal expenses
    and applying custom tie-breaking rules.

    Attributes:
        network (Map): The baseline network simulation map.
    """

    def __init__(self, network: Map) -> None:
        """Initializes the CostedMap with a simulation network framework."""
        self.network = network

    def _adjacent_zones(
        self,
        zone: str,
        exclude: Optional[list[str]] = None
    ) -> list[str]:
        """Finds all zones directly connected to the specified zone.

        Iterates through the map connection records to find bidirectional
        links linked to the given zone, filtering out any globally or
        temporarily blacklisted hub names.

        Args:
            zone (str): The name of the target zone to analyze.
            exclude (list[str], optional): A list of zone names to completely
                ignore during link evaluation. Defaults to None.

        Returns:
            list[str]: A list containing the names of all valid adjacent zones.
        """

        zones: list[str] = []
        for conn in self.network.connections:
            z1, z2 = conn.name.split('-')
            if exclude:
                if z1 in exclude or z2 in exclude:
                    continue
            if z1 == zone:
                zones.append(z2)
            elif z2 == zone:
                zones.append(z1)
        return zones

    def lower_cost_path(
            self,
            start: str,
            exclude: Optional[list[str]] = None
    ) -> dict[str, tuple[int, list[str]]]:
        """Calculates the lowest cost path mapping from a single start node.

            Implements a modified variant of Dijkstra's algorithm using a
            heap queue. It evaluates path costs across hubs while adhering to a
            custom tie-breaking specification that favors PRIORITY zones over
            NORMAL ones when total costs match.

            Args:
                start (str): The starting zone name for path evaluation.
                exclude (list[str], optional): A list of zone names to bypass
                    during the pathfinding execution. Defaults to None.

            Returns:
                dict[str, tuple[int, list[str]]]: A dictionary where keys are
                    destination zone names and values are tuples containing:
                    - int: The total minimum cost to reach that zone.
                    - list[str]: The sequential list of zones representing
                    the path.
            """
        self.exclude = exclude
        info: tuple[int, str, list[str]] = (0, start, [start])
        lower_cost: dict[str, tuple[int, list[str]]] = {start: (0, [start])}
        # list of tuples (cost, zone, path-until-this-zone)
        heap: list[tuple[int, str, list[str]]] = []
        heappush(heap, info)

        while len(heap) > 0:
            cost, zone, path = heappop(heap)
            if cost > lower_cost.get(zone, (float('inf'), None))[0]:
                continue
            neighbours = self._adjacent_zones(zone, exclude)
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
                    self.network.lookup_hubs[neighbor]
                    .zone.name == ZoneType.PRIORITY.name
                ):
                    lower_cost[neighbor] = new_cost, new_path
                    heappush(heap, (new_cost, neighbor, new_path))
        return lower_cost
