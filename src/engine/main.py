#!/usr/bin/env python3
# main.py


import heapq
from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone, Hub
from src.ui.draw import draw_map
from src.ui.print_map import print_map


MAPFILE = 'data/maps/easy/01_linear_path.txt'

def fly_in(map_file: str) -> None:
    network: Map = load_map(parse_map(map_file))
    start_hub: Hub = [hub for hub in network.hubs if hub.prefix.value == 'start_hub'][0]
    end_hub: Hub = [hub for hub in network.hubs if hub.prefix.value == 'end_hub'][0]
    hubs_dict: dict[str, Hub] = {hub.name: hub for hub in network.hubs}
    neighbours: dict[str, list] = {}

    def begin_simulation() -> None:
        drones: list[Drone] = []
        for i in range(1, network.nb_drones + 1):
            drone = Drone(id=i,
                          current_zone=start_hub,
                          next_zone=start_hub,
                          path=[start_hub])
            drones.append(drone)
        network.drones = drones

        #draw_map(network)
    def adjacent_zones(zone_name: str) -> None:
        zones: list[tuple[int, str]] = []
        for conn in network.connections:
            z1, z2 = conn.name.split('-')
            if z1 == zone_name:
                cost = hubs_dict[z2].zone.get_cost()
                heapq.heappush(zones, (cost, z2))                
#                zones.append((cost, z2))
            elif z2 == zone_name:
                cost = hubs_dict[z1].zone.get_cost()
                heapq.heappush(zones, (cost, z1))                
#                zones.append((cost, z1))
        neighbours[zone_name] = zones



    begin_simulation()

#   Turno 1
    for hub in network.hubs:
        adjacent_zones(hub.name)
#    print(neighbours)

    for drone in network.drones:
        if drone.current_zone.name == end_hub.name:
            continue
        adjacent_zones(drone.current_zone.name)
        drone.next_zone = heapq.heappop(neighbours[drone.current_zone.name])[1]
            # drone.next_zone = hubs_dict[zone_name]
            # print(heapq.heappop(neighbours[drone.current_zone.name]))
            # while zone_name in drone.path:
            #     lower_cost, zone_name = heapq.heappop(neighbours[drone.current_zone.name])

            # drone.next_zone = hubs_dict[zone_name]
#       else:
#            print("case in-connection")
#    print(network.drones)

    # MOVEMENTS
    for drone in network.drones:
        print(drone)
    #     if drone.next_zone.num_drones < drone.next_zone.max_drones:
    #         drone.next_zone.num_drones += 1
    #         drone.current_zone.num_drones -= 1
    #         drone.current_zone = drone.next_zone
    print_map(network)

if __name__ == "__main__":
    fly_in(MAPFILE)
