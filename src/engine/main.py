#!/usr/bin/env python3
# main.py


import heapq
from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone, Hub, Connection
from src.ui.draw import draw_map
from src.ui.print_map import print_map
from src.engine.dijkstra import min_cost


MAPFILE = 'data/maps/easy/01_linear_path.txt'

def print_helper(network: Map) -> None:
    for drone in network.drones:
        print(f"{drone.id} - path: {drone.path} - cost: {drone.cost}")    

def get_hub_object(hub: str, network: Map) -> Hub:
    hub_objects: dict[str, Hub] = {hub.name: hub for hub in network.hubs}
    hub_object: Hub = hub_objects[hub]
    return hub_object

def get_conn_object(conn: str, network: Map) -> Connection:
    conn_objects: dict[str, Connection] = {conn.name: conn for conn in network.connections}
    conn_object: Connection = conn_objects[conn]
    return conn_object


def free_connection(drone: Drone, network: Map) -> None:
    conn_name = f"{drone.preview_zone.name}-{drone.current_zone.name}"
    connect = get_conn_object(conn_name, network)
    connect.occupancy -= 1



def move_drone(drone: Drone, network: Map) -> None:
    drone.current_zone.occupancy  -= 1
    drone.next_zone.occupancy += 1
    drone.preview_zone = drone.current_zone
    drone.current_zone = drone.next_zone
    drone.path = drone.path[1:]
    free_connection(drone, network)



def fly_in(map_file: str) -> None:
    network: Map = load_map(parse_map(map_file))

    def begin_simulation() -> None:

        # route with min cost from start_hub to end_hub
        route: tuple[int, list[str]] = min_cost(network, network.start_hub.name)[network.end_hub.name]
        drones: list[Drone] = []
        for i in range(1, network.nb_drones + 1):
            drone = Drone(id=i,
                          current_zone=network.start_hub,
                          next_zone=network.start_hub,
                          preview_zone=network.start_hub,
                          cost=route[0],
                          path=route[1])
            drones.append(drone)
        network.drones = drones


    def prepare_turn(network: Map) -> None:
        for drone in network.drones:
            if len(drone.path) > 1:
                new_path: list[str] = drone.path[1:]
                # Validate connection
                conn_name = f"{drone.current_zone.name}-{new_path[0]}"
                connect = get_conn_object(conn_name, network)
                if connect.occupancy >= connect.max_link_capacity:
                    drone.move = False
                    continue
                # Validate zone
                if drone.next_zone.occupancy >= drone.next_zone.max_drones:
                    drone.move = False                    
                    continue
                # Drone can move
                connect.occupancy += 1
                drone.next_zone = get_hub_object(new_path[0], network)                
                drone.move = True
            else:
                drone.move = False

    begin_simulation()
    turn: int = 0
    while network.end_hub.occupancy < network.nb_drones:
        breakpoint()
        #draw_map(network)
        turn += 1
        prepare_turn(network)
        for drone in network.drones:
            if drone.move:
                move_drone(drone, network)
        print_map(network, turn)
if __name__ == "__main__":
    fly_in(MAPFILE)
