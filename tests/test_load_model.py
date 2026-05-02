#!/usr/bin/env python3
# test_parser.py


from typing import Any
from src.parser.load_model import parse_map


# MAP_1 = 'tests/test_data/01_drones_12.txt'
# MAP_1 = 'tests/test_data/02_hub_parameters.txt'
MAP_1 = 'tests/test_data/03_hub_ok.txt'


def main() -> None:
    filename: str = MAP_1
    obj_map, obj_hub, obj_connection = parse_map(filename)

    print(f"nb_drones = {obj_map.nb_drones}")
    print(f"hub name = {obj_hub.name}")    



if __name__ == "__main__":
    main()
