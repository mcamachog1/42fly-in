#!/usr/bin/env python3
# main.py

from sys import stderr, maxsize
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone, Hub, ZoneType
from src.ui.print_map import print_map
from src.ui.visualizer import Visualizer
from src.engine.dijkstra import min_cost


class FlyIn:
    def __init__(self, map_file: str, graph: bool = False) -> None:
        self.map_file = map_file
        self.graph = graph
        self.network: Map = load_map(parse_map(map_file))
        if self.graph:
            self.plot = Visualizer(self.network, map_file)
        self.turn: int = 0
        self.end_hub: Hub = self.network.lookup_hubs[self.network.end_hub]

    def _free_connection(self, drone: Drone) -> None:
        conn_name = f"{drone.preview_zone.name}-{drone.current_zone.name}"
        connect = self.network.lookup_connections[conn_name]
        connect.occupancy -= 1

    def _move_drone(self, drone: Drone) -> None:
        if drone.move and drone.travel_duration == 1:
            drone.preview_zone = drone.current_zone
            drone.current_zone = drone.next_zone
            drone.path = drone.path[1:]
            drone.accum_cost += drone.current_zone.cost
            drone.move = False
            drone.connection = None
            self._free_connection(drone)

        # wait if drone will be moving to a restricted zone
        elif drone.move and drone.travel_duration > 1:
            drone.travel_duration -= 1
        else:
            if drone.current_zone.name != self.end_hub.name:
                drone.cost += 1
                drone.accum_cost += 1

    def _begin_simulation(self) -> None:
        # route is the path with min cost from start_hub to end_hub
        route: tuple[int, list[str]] = min_cost(
                self.network,
                self.network.start_hub
                )[self.network.end_hub]
        drones: list[Drone] = []

        for i in range(1, self.network.nb_drones + 1):
            drone = Drone(
                id=i,
                cost=route[0],
                path=route[1],
                preview_zone=self.network.lookup_hubs[self.network.start_hub],
                current_zone=self.network.lookup_hubs[self.network.start_hub],
                next_zone=self.network.lookup_hubs[route[1][1]],
            )
            drones.append(drone)
        self.network.drones = drones

    def _book_connection(self, drone: Drone) -> bool:
        try:
            conn_name = f"{drone.path[0]}-{drone.path[1]}"
            connect = self.network.lookup_connections[conn_name]
            if connect.occupancy >= connect.max_link_capacity:
                drone.move = False
                return False
            return True
        except IndexError as e:
            print(f"ERROR in function '_book_connection' {e}", file=stderr)
            exit(1)

    def _book_hub(self, drone: Drone) -> bool:
        try:
            next_zone: Hub = self.network.lookup_hubs[drone.path[1]]
            if next_zone.occupancy >= next_zone.max_drones:
                drone.move = False
                return False
            return True
        except IndexError as e:
            print(f"ERROR in function '_book_hub' {e}", file=stderr)
            exit(1)

    def _book(self, drone: Drone) -> None:
        try:
            conn_name = f"{drone.path[0]}-{drone.path[1]}"
            connect = self.network.lookup_connections[conn_name]
            next_zone: Hub = self.network.lookup_hubs[drone.path[1]]

            connect.occupancy += 1
            next_zone.occupancy += 1
            drone.current_zone.occupancy -= 1
            drone.next_zone = next_zone
            drone.move = True
            # Check for restricted zones
            if next_zone.zone.name == ZoneType.RESTRICTED.name:
                drone.travel_duration = 2
                drone.connection = conn_name
        except IndexError as e:
            print(f"ERROR in function '_book' {e}", file=stderr)
            exit(1)

    def _book_all_drones(self) -> None:
        for drone in self.network.drones:
            if drone.move:
                continue
            if len(drone.path) > 1:
                if not self._book_connection(drone):
                    continue
                if not self._book_hub(drone):
                    continue
                self._book(drone)
            else:
                drone.move = False

    def _improve_simulation(self) -> None:
        drones_waiting = [d for d in self.network.drones if not d.move]
        new_cost = maxsize
        # Update path
        for drone in drones_waiting:
            try:
                if drone.current_zone.name == self.network.start_hub:
                    new_cost, new_path = min_cost(
                                    self.network,
                                    drone.current_zone.name,
                                    )[self.network.end_hub]
                elif drone.next_zone.name != self.network.end_hub:
                    new_cost, new_path = min_cost(
                                    self.network,
                                    drone.current_zone.name,
                                    [self.network.start_hub, drone.path[1]]
                                    )[self.network.end_hub]
            except KeyError:
                # Case in which there are not alternative path, it is ignore.
                pass
            except IndexError as e:
                print(
                    f"ERROR in function '_improve_simulation' {e}",
                    file=stderr
                )
                exit(1)
            finally:
                if (drone.cost - drone.accum_cost) + 1 > new_cost:
                    drone.path = new_path
                    drone.cost = drone.accum_cost + new_cost
        self._book_all_drones()

    def statistics(self) -> dict[str, int]:
        drone_cost: dict[str, int] = {
            f"D{d.id}": d.cost for d in self.network.drones
        }
        return drone_cost

    def run(self) -> None:
        self._begin_simulation()
        while self.end_hub.occupancy < self.network.nb_drones:
            self.turn += 1
            self._book_all_drones()
            self._improve_simulation()
            for drone in self.network.drones:
                self._move_drone(drone)
            print_map(self.network, self.turn)
            if self.graph:
                self.plot.draw_simulation()

        if self.graph:
            self.plot.close()


if __name__ == "__main__":

    maps: list[str] = [
        'data/maps/easy/01_linear_path.txt',
        'data/maps/easy/02_simple_fork.txt',
        'data/maps/easy/03_basic_capacity.txt',
        'data/maps/medium/01_dead_end_trap.txt',
        'data/maps/medium/02_circular_loop.txt',
        'data/maps/medium/03_priority_puzzle.txt',
        'data/maps/hard/01_maze_nightmare.txt',
        'data/maps/hard/02_capacity_hell.txt',
        'data/maps/hard/03_ultimate_challenge.txt',
        'data/maps/challenger/01_the_impossible_dream.txt',
        'data/maps/challenger/02_multiple_paths.txt',
    ]

    show_graphics = False
    for map in maps:
        flyin = FlyIn(map, show_graphics)
        flyin.run()
        print(f"file name: {map}")
        print("=== Statistics ===")
        print(flyin.statistics())
        option: int = int(input('Continue(1) - Quit(0): '))
        if option == 0:
            exit(0)
