#!/usr/bin/env python3
# test_parser.py


from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map
from src.ui.draw import draw_map


#MAP02  = 'tests/test_data/02_hub_error.txt'
MAP02 = 'data/maps/easy/01_linear_path.txt'
#MAP02 = 'data/maps/easy/02_simple_fork.txt'
#MAP02 = 'data/maps/easy/03_simple_fork.txt'
#MAP02 = 'data/maps/medium/01_dead_end_trap.txt'
#MAP02 = 'data/maps/medium/02_circular_loop.txt'
#MAP02 = 'data/maps/hard/02_capacity_hell.txt'

def test_02() -> None:
    filename: str = MAP02
    my_map: Map = load_map(parse_map(filename))
    #print(my_map.hubs)
    #print(my_map.connections)
    draw_map(my_map)



if __name__ == "__main__":
    test_02()
 