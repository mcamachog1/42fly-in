#!/usr/bin/env python3
# main.py


from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Drone
from src.ui.draw import draw_map


MAP02 = 'data/maps/easy/01_linear_path.txt'


def begin_simulation() -> None:
    filename: str = MAP02
    network: Map = load_map(parse_map(filename))
    drones: list[Drone] = []
    for i in range(1, network.nb_drones + 1):
        drone = Drone(id=i)
        drones.append(drone)
    draw_map(network)



if __name__ == "__main__":
    begin_simulation()
 