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

def get_metadata(string: str) -> dict[str, str]:
    if string is None:
        return {}
    optionals: list[str] = string.strip("[]").split()
    result: dict[str, str] = {}
    for values in optionals:
        key, value = values.split("=")
        result[key] = value
    return result

def get_zones(zones: list[tuple[str, str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for hub, values in zones:
      
        metadata: str | None = None
        attributes = values.split(maxsplit=3)
        if len(attributes) > 4:
            raise MapParsingError(f"To many arguments for zone: {hub}: {attributes}")                            
        if len(attributes) < 3:
            raise MapParsingError(f"To few arguments for zone: {hub}: {attributes}")
        if len(attributes) == 3:
            name, coord_x, coord_y = attributes
        if len(attributes) == 4:
            name, coord_x, coord_y, metadata = attributes
        try:
            x = int(coord_x)
            y = int(coord_y)
        except ValueError:
            raise MapParsingError(f"Invalid value for coordinates, x: {coord_x} y: {coord_y}")
        results.append(
            {
                'type': hub,
                'name': name,
                'x': x,
                'y': y,
                'metadata': get_metadata(metadata)
            }
        )
    return results
    
def get_connections(connections: list[tuple[str, str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for connection, values in connections:
      
        metadata: str | None = None
        attributes = values.split(maxsplit=1)
        if len(attributes) > 2:
            raise MapParsingError(f"To many arguments for connection: {connection}: {attributes}")                            
        if len(attributes) < 1:
            raise MapParsingError(f"To few arguments for zone: {connection}: {attributes}")
        if len(attributes) == 1:
            name, = attributes
        if len(attributes) == 2:
            name, metadata = attributes
        results.append(
            {
                'type': connection,
                'name': name,
                'metadata': get_metadata(metadata)
            }
        )
    return results


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
    zones = list(filter(lambda line : line[0] == 'hub' or line[0] == 'start_hub' or line[0] == 'end_hub', raw_data))
    data['zones'] = get_zones(zones)

    # connections
    connections = list(filter(lambda line : line[0] == 'connection', raw_data))
    data['connections'] = get_connections(connections)

    return data
    # # Hubs

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
