# load_model.py


import sys
from typing import Any
from src.model.model import Hub, Connection, Map
from src.parser.read_map import read_map
from pydantic import ValidationError

class MapParsingError(Exception):
    """Errors related to parsing maps"""
    pass


def get_numbers_of_drones(lines: list[tuple[str, str]]) -> int:
    for key, value in lines:
        if key == 'nb_drones':
            try:
                nb_drones: int =  int(value)
            except ValueError as e:
                raise MapParsingError(f"Invalid nb_drones value: {value}") from e
            if nb_drones <= 0:
                raise MapParsingError("nb_drones must be greater than 0")                
            return nb_drones
    raise MapParsingError("There is not 'nb_drones'")

def get_zones(zones: list[tuple[str, str]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for zone in zones:
        print(zone)
    return {}
    


def parse_map(filename: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    raw_data: list[tuple[str, str]] = read_map(filename)

    # nb_drones
    try:
        nb_drones = get_numbers_of_drones(raw_data)
    except MapParsingError as e:
        print(f"PARSING ERROR {e}")
        exit(1)
    data['nb_drones'] = nb_drones

    # zones

    zones = filter(lambda line : line[0] == 'hub' or line[0] == 'start_hub' or line[0] == 'end_hub', raw_data)
    get_zones(list(zones))
    return data


    # # Hubs
    # raw_start_hub: tuple[str]= raw_data['start_hub'].split()
    # if len(raw_start_hub) > 4:
    #     print(f"RESPONSE: To many arguments for start_hub: {raw_data['start_hub']}", file=sys.stderr)
    #     exit(1)
    # if len(raw_start_hub) < 3:
    #     print(f"RESPONSE: To few arguments for start_hub: {raw_data['start_hub']}", file=sys.stderr)
    #     exit(1)
    # if len(raw_start_hub) == 3:
    #     hub_name, coord_x, coord_y = raw_start_hub
    #     hub_optionals: list[str] = None
    # if len(raw_start_hub) == 4:
    #     hub_name, coord_x, coord_y, hub_optionals = raw_start_hub
    # try:
    #     start_hub = Hub(name=hub_name, coord_x=int(coord_x), coord_y=int(coord_y), optionals=hub_optionals)
    # except ValidationError as e:
    #     for error in e.errors():
    #         field = error['loc'][0]
    #         msg = error['msg']
    #         input_value = error['input']
    #         print(f"RESPONSE: Error in field '{field}': {msg}, input value: {input_value}")
    #     exit(1)
    # except ValueError:
    #     print(f"RESPONSE: coordinates x and y must be integer, coord_x={coord_x}, coord_y={coord_y}", file=sys.stderr)
    #     exit(1)
            
    # return obj_map, start_hub, None
