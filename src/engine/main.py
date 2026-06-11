#!/usr/bin/env python3
# src/engine/main.py

import argparse
from sys import stderr, maxsize
from typing import Any
from src.parser.parse_map import MapParser
from src.model.model import Map, Drone, Hub, ZoneType
from src.ui.print_map import TerminalInterface
from src.ui.visualizer import Visualizer
from src.engine.dijkstra import CostedMap


class FlyIn:

    """Manages the simulation engine loop for Multi-Agent Pathfinding (MAPF).

    Coordinates text map decoding, routing recalculations using edge-weight
    costs, real-time visual output updates, and execution metrics
    consolidation.

    Attributes:
        filename (str): Path targeting the raw map specification file.
        map_parser (MapParser): Utility decoding structural parameters
            from files.
        network (Map): Root object instance holding hubs, links, and
            active drones.
        graph (bool): Toggles whether Pygame GUI canvas frame rendering
            is active.
        all_maps (bool): Toggles brief terminal outputs instead of step breaks.
        terminal_ui (TerminalInterface): Text renderer detailing turn steps.
        plot (Visualizer, optional): Graphical asset viewport painter instance.
        turn (int): Global simulation execution counter tracking clock ticks.
        end_hub (Hub): Destination node object matching targeting parameters.
        statistics (list[dict[Any, Any]]): Tracked simulation profiling
            datasets.
        costed_map (CostedMap): Evaluation proxy resolving minimum
            routing costs.
    """

    def __init__(
        self,
        filename: str,
        gui_active: bool = False,
        all_maps: bool = False
    ) -> None:

        """Initializes runtime components and structural frameworks
        for FlyIn."""
        self.filename = filename
        self.map_parser = MapParser(filename)
        self.network: Map = self.map_parser.load_map()
        self.gui_active = gui_active
        self.all_maps = all_maps
        self.terminal_ui = TerminalInterface(self.network)

        self.plot = None
        if self.gui_active:
            self.plot = Visualizer(self.network, filename)

        self.turn = 0
        self.end_hub = self.network.lookup_hubs[self.network.end_hub]
        self.statistics: list[dict[str, Any]] = []
        self.costed_map = CostedMap(self.network)

    def _free_connection(self, drone: Drone) -> None:
        """Decrements the utilization metric across a traversed
        structural link.

        Args:
            drone (Drone): The specific agent vacating a connection track.
        """
        conn_name = f"{drone.preview_zone.name}-{drone.current_zone.name}"
        connect = self.network.lookup_connections[conn_name]
        connect.occupancy -= 1

    def _move_drone(self, drone: Drone) -> int:
        """Executes position translations or wait penalties for a single agent.

        Args:
            drone (Drone): Target simulation asset whose position is advanced.

        Returns:
            int: 1 if the agent transitioned structural hubs, 0 if it remained
                stationary.
        """

        if drone.move:
            if drone.travel_duration == 1:
                drone.preview_zone = drone.current_zone
                drone.current_zone = drone.next_zone
                drone.path = drone.path[1:]
                drone.accum_cost += drone.current_zone.cost
                drone.move = False
                drone.connection = None
                self._free_connection(drone)

            # wait if drone will be moving to a restricted zone
            elif drone.travel_duration > 1:
                drone.travel_duration -= 1
            return 1
        # drone without move add 1 for wait
        else:
            if drone.current_zone.name != self.end_hub.name:
                drone.cost += 1
                drone.accum_cost += 1
            return 0

    def _begin_simulation(self) -> None:
        """Generates the primary minimum cost routes from start_hub
        to end_hub and allocates drone objects.

        Raises:
            SystemExit: If the network destination node cannot be resolved.
        """

        try:
            route: tuple[int, list[str]] = self.costed_map.lower_cost_path(
                    self.network.start_hub
                    )[self.network.end_hub]
        except KeyError:
            print(
                "ERROR - Map Error: The path to the end "
                "hub is blocked or missing.", file=stderr)
            exit(1)

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
        """Validates if a target connection path contains vacant entry
        capacity.

        Args:
            drone (Drone): Agent requesting connection access permissions.

        Returns:
            bool: True if connection capacity is available, False otherwise.
        """

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
        """Validates if a target hub zone contains vacant docking slots.

        Args:
            drone (Drone): Agent evaluating subsequent segment travel criteria.

        Returns:
            bool: True if destination node slots are open, False otherwise.
        """

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
        """Registers spatial occupancy changes across networks for moving
        agents."""
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
        """Evaluates connection criteria and flags pathing options
        for agents."""
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
        """Recalculates routing matrices dynamically for gridlocked agents."""
        drones_waiting = [d for d in self.network.drones if not d.move]
        new_cost = maxsize
        # Update path
        for drone in drones_waiting:
            try:
                if drone.current_zone.name == self.network.start_hub:
                    new_cost, new_path = self.costed_map.lower_cost_path(
                                    drone.current_zone.name,
                                    )[self.network.end_hub]
                elif drone.next_zone.name != self.network.end_hub:
                    new_cost, new_path = self.costed_map.lower_cost_path(
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

    def calc_statistics(self) -> None:
        """Processes final operational datasets and tracks telemetry
        output maps."""
        # Number of movements per drone
        drone_cost: dict[str, int] = {
            f"D{d.id}": d.cost for d in self.network.drones
        }
        self.statistics.append(drone_cost)

        # Total path cost
        total_path_cost: int = sum(drone_cost.values())
        # Average turns per drone
        avg_turns: float = total_path_cost / self.network.nb_drones
        self.statistics.append({
            'total_path_cost': total_path_cost,
            'avg_turns_per_drone': avg_turns
        })

    def run(self) -> None:
        """Orchestrates runtime operations across map simulation sequences."""
        drones_moved_per_turn: dict[str, int] = {}
        self._begin_simulation()
        while self.end_hub.occupancy < self.network.nb_drones:
            count_drones: int = 0
            self.turn += 1
            self._book_all_drones()
            self._improve_simulation()
            for drone in self.network.drones:
                count_drones += self._move_drone(drone)
            drones_moved_per_turn[f"TURN {self.turn}"] = count_drones
            if not self.all_maps:
                self.terminal_ui.print_turn(self.turn)
            if self.gui_active and self.plot:
                self.plot.draw_simulation()
        self.statistics.append(drones_moved_per_turn)
        if self.gui_active and self.plot:
            self.plot.close()


def main() -> None:
    """Parses environment flag instructions and handles dataset loop
    processes."""
    parser = argparse.ArgumentParser(
        description="Fly-In: Multi-Agent Pathfinding"
    )

    parser.add_argument(
        '--gui-active',
        action='store_true',
        help="Show graphic visualization"
    )

    parser.add_argument(
        '--all-maps',
        action='store_true',
        help="Summarize total turns for each map"
    )

    args = parser.parse_args()
    show_graphics = args.gui_active
    show_total = args.all_maps

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
    ]

    # tests = [
    #     # 'tests/test_data/01_dron_error.txt',
    #     # 'tests/test_data/02_hub_error.txt',
    #     # 'tests/test_data/03_wrong_connection.txt',
    #     # 'tests/test_data/04_config_key_error.txt',
    #     # 'tests/test_data/05_duplicate_start_hub.txt',
    #     #  'tests/test_data/06_duplicate_end_hub.txt',
    #     # 'tests/test_data/07_config_separator_error.txt',
    #     # 'tests/test_data/08_duplicate_coords.txt',
    #     # 'tests/test_data/09_multiple_paths.txt'git add
    # ]

    for map in maps:
        flyin = FlyIn(map, show_graphics, show_total)
        flyin.run()
        flyin.calc_statistics()
        print("=== Statistics ===")
        print(f"file: {map}")
        print(f"=== Total turns ===\n{flyin.turn}")
        if not show_total:
            for index, s in enumerate(flyin.statistics):
                if index == 0:
                    print(f"=== Total movements per turn ===\n{s}")
                if index == 1:
                    print(f"=== Total movements per drone ===\n{s}")
                if index == 2:
                    print(
                        f"=== Total path cost & Avg turns per drone ===\n{s}")
            option: int = int(input('Continue(1) - Quit(0): '))
            if option == 0:
                exit(0)


if __name__ == "__main__":
    main()
