#!/usr/bin/env python3
# test_parser.py


from typing import Any
from src.parser.parse_map import parse_map
from src.parser.load_model import load_map
from src.model.model import Map
from src.ui.draw import draw_hubs


#MAP02  = 'tests/test_data/02_hub_error.txt'
MAP02 = 'data/maps/easy/01_linear_path.txt'


def test_02() -> None:
    filename: str = MAP02
    my_map: Map = load_map(parse_map(filename))
    draw_hubs(my_map.hubs)


if __name__ == "__main__":
    print(test_02())
 jj