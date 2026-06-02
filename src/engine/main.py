#!/usr/bin/env python3
# main.py

from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone, Hub, ZoneType
from src.ui.print_map import print_map
from src.ui.visualizer import Visualizer
from src.engine.dijkstra import min_cost


def print_prepared_turn(network: Map) -> None:
    print("DRONES TO MOVE")
    for drone in network.drones:
        if drone.move:
            print
            (
                f"{drone.id=} - "
                f"{drone.current_zone.name=} - {drone.preview_zone.name=} - "
                f"{drone.next_zone.name=}"
            )
    print("DRONES TO WAIT")
    for drone in network.drones:
        if not drone.move:
            print
            (
                f"{drone.id=} - "
                f"{drone.current_zone.name=} - {drone.preview_zone.name=} - "
                f"{drone.next_zone.name=}"
            )


def free_connection(drone: Drone, network: Map) -> None:
    conn_name = f"{drone.preview_zone.name}-{drone.current_zone.name}"
    connect = network.lookup_connections[conn_name]
    connect.occupancy -= 1


def move_drone(drone: Drone, network: Map) -> None:
    if drone.move and drone.travel_duration == 1:
        drone.preview_zone = drone.current_zone
        drone.current_zone = drone.next_zone
        drone.path = drone.path[1:]
        drone.move = False
        drone.connection = None
        free_connection(drone, network)

    # wait if drone will be moving to a restricted zone
    elif drone.move and drone.travel_duration > 1:
        drone.travel_duration -= 1


def fly_in(map_file: str) -> None:
    network: Map = load_map(parse_map(map_file))

    def begin_simulation() -> None:
        # route is the path with min cost from start_hub to end_hub
        route: tuple[int, list[str]] = min_cost(
                network,
                network.start_hub
                )[network.end_hub]
        drones: list[Drone] = []
        for i in range(1, network.nb_drones + 1):
            drone = Drone(
                id=i,
                cost=route[0],
                path=route[1],
                preview_zone=network.lookup_hubs[network.start_hub],
                current_zone=network.lookup_hubs[network.start_hub],
                next_zone=network.lookup_hubs[route[1][1]],
            )
            drones.append(drone)
        network.drones = drones

    # Just for drones waiting after the begin simulation
    def alternative_simulation(drones: list[Drone]) -> None:
        for drone in drones:
            if len(drone.path) > 1:
                try:
                    route: tuple[int, list[str]] = min_cost(
                            network,
                            drone.current_zone.name,
                            [drone.path[1]]
                            )[network.end_hub]
                    drone.cost = route[0]
                    drone.path = route[1]
                except KeyError:
                    continue

    # Search optimal solution again for waited nodes without excluding nodes,
    # (only exclude start node)
    def reset_simulation() -> None:
        for drone in network.drones:
            if not drone.move and len(drone.path) > 1:
                try:
                    route: tuple[int, list[str]] = min_cost(
                            network,
                            drone.current_zone.name,
                            [network.start_hub]
                            )[network.end_hub]
                    drone.cost = route[0]
                    drone.path = route[1]
                except KeyError:
                    continue

    def prepare_turn() -> None:
        for drone in network.drones:
            if drone.move:
                continue
            if len(drone.path) > 1:
                # Validate connection
                conn_name = f"{drone.path[0]}-{drone.path[1]}"
                connect = network.lookup_connections[conn_name]
                if connect.occupancy >= connect.max_link_capacity:
                    drone.move = False
                    continue
                # Validate zone
                next_zone: Hub = network.lookup_hubs[drone.path[1]]
                if next_zone.occupancy >= next_zone.max_drones:
                    drone.move = False
                    continue
                # Drone can move
                connect.occupancy += 1
                next_zone.occupancy += 1
                drone.current_zone.occupancy -= 1
                drone.next_zone = next_zone
                drone.move = True
                # Check for restricted zones
                if next_zone.zone.name == ZoneType.RESTRICTED.name:
                    drone.travel_duration = 2
                    drone.connection = conn_name
            else:
                drone.move = False

    begin_simulation()
    plot = Visualizer(network, map_file)
    turn: int = 0
    end_hub: Hub = network.lookup_hubs[network.end_hub]
    while end_hub.occupancy < network.nb_drones:
        turn += 1
        prepare_turn()
        wait_list = [drone for drone in network.drones if not drone.move]
        if len(wait_list) > 0:
            alternative_simulation(wait_list)
        prepare_turn()
        for drone in network.drones:
            move_drone(drone, network)
        print_map(network, turn)
        plot.draw_simulation()
        reset_simulation()


if __name__ == "__main__":

    maps: list[str] = [
        # 'data/maps/easy/01_linear_path.txt',
        # 'data/maps/easy/02_simple_fork.txt',
        # 'data/maps/easy/03_basic_capacity.txt',
        # 'data/maps/medium/01_dead_end_trap.txt',
        # 'data/maps/medium/02_circular_loop.txt',
        # 'data/maps/medium/03_priority_puzzle.txt',
        # 'data/maps/hard/01_maze_nightmare.txt',
        # 'data/maps/hard/02_capacity_hell.txt',
        'data/maps/hard/03_ultimate_challenge.txt',
        'data/maps/challenger/01_the_impossible_dream.txt',
    ]

    for map in maps:
        fly_in(map)
        print(map)
        option: int = int(input('Continue(1) - Quit(0): '))
        if option == 0:
            exit(0)
