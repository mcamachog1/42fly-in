#!/usr/bin/env python3
# test_enum.py



from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map, Color, Hub
from src.ui.draw import draw_map



MAP02 = 'data/maps/easy/01_linear_path.txt'


if __name__ == "__main__":
    filename: str = MAP02
    my_map: Map = load_map(parse_map(filename))
    print(my_map.hubs)
    print(my_map.connections)

