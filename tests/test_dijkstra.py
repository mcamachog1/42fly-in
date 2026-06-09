#!/usr/bin/env python3
# test_dijkstra.py


from src.parser.parse_map import MapParser
from src.model.model import Map
from src.engine.dijkstra import CostedMap


MAP02 = 'data/maps/easy/01_linear_path.txt'

if __name__ == "__main__":
    filename: str = MAP02
    map_parser = MapParser(filename)
    my_map: Map = map_parser.load_map()
    # print(f"\nMy map:{my_map}\n")
    costed_map = CostedMap(my_map)
    print(costed_map.lower_cost_path(my_map.start_hub))
    print(costed_map.lower_cost_path(my_map.hubs[1].name, [my_map.start_hub]))
