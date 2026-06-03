#!/usr/bin/env python3
# test_dijkstra.py

from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map
from src.engine.dijkstra import min_cost


MAP02 = 'data/maps/easy/01_linear_path.txt'

if __name__ == "__main__":
    filename: str = MAP02
    my_map: Map = load_map(parse_map(filename))
    # print(f"\nMy map:{my_map}\n")
    print(min_cost(my_map, my_map.start_hub))
