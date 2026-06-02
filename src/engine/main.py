#!/usr/bin/env python3
# main.py

from sys import stderr
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone, Hub, Connection, ZoneType
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


def get_hub_object(hub: str, network: Map) -> Hub:
    hub_objects: dict[str, Hub] = {hub.name: hub for hub in network.hubs}
    hub_object: Hub = hub_objects[hub]
    return hub_object


def get_conn_object(conn: str, network: Map) -> Connection:
    conn_objects: dict[str, Connection] = {
        c.name: c for c in network.connections
    }
    # Make conmmutative names
    swap_names: dict[str, Connection] = {}
    for name, obj in conn_objects.items():
        z1, z2 = name.split('-')
        swap_names[f"{z2}-{z1}"] = obj
    conn_total = conn_objects | swap_names
    try:
        conn_object: Connection = conn_total[conn]
    except KeyError:
        print(f"Invalid map connection '{conn}'", file=stderr)
        exit(1)
    return conn_object


def free_connection(drone: Drone, network: Map) -> None:
    conn_name = f"{drone.preview_zone.name}-{drone.current_zone.name}"
    connect = get_conn_object(conn_name, network)
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
                preview_zone=get_hub_object(network.start_hub, network),
                current_zone=get_hub_object(network.start_hub, network),
                next_zone=get_hub_object(route[1][1], network),
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
            #if len(drone.path) > 1:            
                try:
                    route: tuple[int, list[str]] = min_cost(
                            network,
                            drone.current_zone.name,
                            network.start_hub
                            )[network.end_hub]
                    drone.cost = route[0]
                    drone.path = route[1]
                except KeyError:
                    continue

    def traffic_flow():
        network.initialize_cost_zone()
        for hub in network.hubs:
            traffic_rate = hub.occupancy / hub.max_drones
            if traffic_rate >= 0.9:
                hub.inner_cost = hub.cost * 4
            elif traffic_rate >= 0.6:
                hub.inner_cost = hub.cost * 2
            elif traffic_rate >= 0.4:
                hub.inner_cost = hub.cost * 1.5
            else:
                hub.inner_cost = hub.cost          

    def prepare_turn() -> None:
        for drone in network.drones:
            if drone.move:
                continue
            if len(drone.path) > 1:
                # Validate connection
                conn_name = f"{drone.path[0]}-{drone.path[1]}"
                connect = get_conn_object(conn_name, network)
                if connect.occupancy >= connect.max_link_capacity:
                    drone.move = False
                    continue
                # Validate zone
                next_zone: Hub = get_hub_object(drone.path[1], network)
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
    plot = Visualizer(network)
    turn: int = 0
    end_hub: Hub = get_hub_object(network.end_hub, network)
    print(f"{network.nb_drones=} {len(network.hubs)=} {len(network.connections)=}")
    while end_hub.occupancy < network.nb_drones:
        turn += 1
        prepare_turn()
        if network.nb_drones / len(network.connections) >= 0.6:
            wait_list = [drone for drone in network.drones if not drone.move]
            if len(wait_list) > 0:
                alternative_simulation(wait_list)
            prepare_turn()
        for drone in network.drones:
            move_drone(drone, network)
        print_map(network, turn)
        plot.draw_simulation()
        traffic_flow()
        reset_simulation()


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
    ]

    for map in maps:
        fly_in(map)
        print(map)
        option: int = int(input('Continue(1) - Quit(0): '))
        if option == 0:
            exit(0)
