#!/usr/bin/env python3
# test_parser.py


from typing import Any
from src.parser.load_model import parse_map


# MAP = 'tests/test_data/01_dron_error.txt'
# MAP  = 'tests/test_data/02_hub_error.txt'
# MAP  = 'tests/test_data/03_load_ok.txt'
# MAP  = 'tests/test_data/04_config_key_error.txt'
MAP05  = 'tests/test_data/05_duplicate_key_error.txt'
MAP06  = 'tests/test_data/06_config_separator_error.txt'

def test_06() -> tuple[Any, Any, Any]:
    filename: str = MAP06
    return parse_map(filename)

def test_05() -> tuple[Any, Any, Any]:
    filename: str = MAP05
    return parse_map(filename)

def main() -> None:

    obj_map, obj_hub, obj_connection = test_1()

    print(f"nb_drones = {obj_map.nb_drones}")
    print(f"hub name = {obj_hub.name}")    



if __name__ == "__main__":
    #test_06()

    test_05()
