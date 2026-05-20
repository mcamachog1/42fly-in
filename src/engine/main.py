#!/usr/bin/env python3
# main.py


import heapq
from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone, Hub
from src.ui.draw import draw_map
from src.ui.print_map import print_map
from src.engine.dijkstra import min_cost


MAPFILE = 'data/maps/easy/01_linear_path.txt'

def print_helper(network: Map) -> None:
    for drone in network.drones:
        print(f"{drone.id} - path: {drone.path} - cost: {drone.cost}")    


def fly_in(map_file: str) -> None:
    network: Map = load_map(parse_map(map_file))
    which_hub: dict[str, Hub] = {hub.name: hub for hub in network.hubs}
    which_connect: dict[str, Hub] = {connect.name: connect for connect in network.connections}    

    def begin_simulation() -> None:
        route = min_cost(network, network.start_hub.name)[network.end_hub.name]
        drones: list[Drone] = []
        for i in range(1, network.nb_drones + 1):
            drone = Drone(id=i,
                          current_zone=network.start_hub,
                          next_zone=network.start_hub,
                          cost=route[0],
                          path=route[1])
            drones.append(drone)
        network.drones = drones


    def execute_turn() -> None:
        for d in network.drones:
            if d.current_zone.name == network.end_hub.name:
                print(f"\nDrone id: {d.id} current zone: {d.current_zone.name}\n")
                continue
            index = d.path.index(d.current_zone.name)
            d.next_zone = which_hub[d.path[index + 1]]
            # Validate connection
            conn_name = f"{d.current_zone.name}-{d.next_zone.name}"
            connect = which_connect[conn_name]
            print(f"Continuó con drone id: {d.id} connect: {conn_name} conn occupancy:{connect.occupancy} conn capacity: {connect.max_link_capacity}")
            if connect.occupancy >= connect.max_link_capacity:
                continue
            # Validate zone
            zone = d.next_zone
            if zone.occupancy >= zone.max_drones and zone.name != network.end_hub.name:
                continue
            # Make move - update next objects
            connect.occupancy += 1
            zone.occupancy += 1
            # Make move - free previews objects
            if d.current_zone.name != network.start_hub.name:     
                pre_zone = which_hub[d.path[index -1]]
                pre_conn_name = f"{pre_zone.name}-{d.current_zone.name}"
                pre_connect = which_connect[pre_conn_name]
                pre_connect.occupancy -= 1
                d.current_zone.occupancy -= 1
                print(f"conn anterior: {pre_conn_name} conenct occupancy: {pre_connect.occupancy} current zone: {d.current_zone.name} zone occupancy: {d.current_zone.occupancy}")
            d.current_zone = d.next_zone

    #draw_map(network)
    begin_simulation()
    print_map(network)
    execute_turn()
    print_map(network)    
    execute_turn()
    print_map(network)
    execute_turn()
    print_map(network)
    execute_turn()
    print_map(network)
    execute_turn()
    print_map(network)      

if __name__ == "__main__":
    fly_in(MAPFILE)
