# load_model.py


import sys
from typing import Any
from src.model.model import Hub, Connection, Map
from src.parser.read_map import read_map
from pydantic import ValidationError


def parse_map(filename: str) -> tuple[Any, Any, Any]:
    raw_data: list[tuple[str, str]] = read_map(filename)
    for line in raw_data
    print(raw_data)
    exit(0)
    #nb_drones: int = raw_data['nb_drones']
    nb_drones = 2

    # Drone numbers
    try:
        obj_map = Map(nb_drones=nb_drones)
    except ValidationError:
        print(f"RESPONSE: Invalid value: {nb_drones}", file=sys.stderr)
        exit(1)

    # Hubs
    raw_start_hub: tuple[str]= raw_data['start_hub'].split()
    if len(raw_start_hub) > 4:
        print(f"RESPONSE: To many arguments for start_hub: {raw_data['start_hub']}", file=sys.stderr)
        exit(1)
    if len(raw_start_hub) < 3:
        print(f"RESPONSE: To few arguments for start_hub: {raw_data['start_hub']}", file=sys.stderr)
        exit(1)
    if len(raw_start_hub) == 3:
        hub_name, coord_x, coord_y = raw_start_hub
        hub_optionals: list[str] = None
    if len(raw_start_hub) == 4:
        hub_name, coord_x, coord_y, hub_optionals = raw_start_hub
    try:
        start_hub = Hub(name=hub_name, coord_x=int(coord_x), coord_y=int(coord_y), optionals=hub_optionals)
    except ValidationError as e:
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            input_value = error['input']
            print(f"RESPONSE: Error in field '{field}': {msg}, input value: {input_value}")
        exit(1)
    except ValueError:
        print(f"RESPONSE: coordinates x and y must be integer, coord_x={coord_x}, coord_y={coord_y}", file=sys.stderr)
        exit(1)
            
    return obj_map, start_hub, None
