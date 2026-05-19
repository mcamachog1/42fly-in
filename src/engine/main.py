#!/usr/bin/env python3
# main.py


from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone
from src.ui.draw import draw_map
from src.ui.print_map import print_map


MAP02 = 'data/maps/easy/01_linear_path.txt'


def begin_simulation() -> None:
    filename: str = MAP02
    network: Map = load_map(parse_map(filename))
    drones: list[Drone] = []
    start_hub: Hub = [hub for hub in network.hubs if hub.prefix.value == 'start_hub'][0]
    for i in range(1, network.nb_drones + 1):
        drone = Drone(id=i, current_zone=start_hub, next_zone=start_hub)
        drones.append(drone)
    network.drones = drones
    print_map(network)
    #draw_map(network)



if __name__ == "__main__":
    begin_simulation()
 