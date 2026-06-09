#!/usr/bin/env python3
# test_parser.py


from src.model.model import Map
from src.parser.parse_map import MapParser


# MAP02  = 'tests/test_data/02_hub_error.txt'
MAP02 = 'data/maps/easy/01_linear_path.txt'
# MAP02 = 'data/maps/easy/02_simple_fork.txt'
# MAP02 = 'data/maps/easy/03_simple_fork.txt'
# MAP02 = 'data/maps/medium/01_dead_end_trap.txt'
# MAP02 = 'data/maps/medium/02_circular_loop.txt'
# MAP02 = 'data/maps/hard/02_capacity_hell.txt'


def test_02() -> None:
    filename: str = MAP02
    map_parser = MapParser(filename)
    my_map: Map = map_parser.load_map()
    print(my_map.hubs)
    # print(my_map.connections)


if __name__ == "__main__":
    test_02()
