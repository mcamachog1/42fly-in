# parse_map.py

import re
from typing import Any
from src.parser.read_map import read_map
from src.model.model import Hub, Connection, Color



class MapParsingError(Exception):
    """Errors related to parsing maps"""
    pass


def get_numbers_of_drones(lines: list[tuple[str, str]]) -> int:
    key, value = lines[0]
    if key == 'nb_drones':
        try:
            nb_drones: int = int(value)
        except ValueError as e:
            raise MapParsingError(f"Invalid nb_drones value: {value}") from e
        if nb_drones <= 0:
            raise MapParsingError("nb_drones must be greater than 0")
        return nb_drones
    else:
        raise MapParsingError(
            "There is not value for 'nb_drones' "
            "in the first line"
        )


def get_metadata(string: str, prefix: str) -> dict[str, str]:
    valid_colors = {c.value for c in Color}
    result: dict[str, str] = {}
    if string == "":
        return result
    pattern = r"\[([a-z_0-9]+=[a-z_0-9]+\s*)*\]"
    if not re.search(pattern, string):
        raise MapParsingError(f"Invalid format for metadata '{string}'")
    optionals: list[str] = string.strip("[]").split()
    pattern_color = r"^[a-z]{3,8}$"
    for values in optionals:
        key, value = values.split("=")
        if prefix.lower() == 'hub' and key not in Hub.META_DATA_KEYS:
            raise MapParsingError(f"Invalid key '{key}' for hub metadata '{string}'")            
        if prefix.lower() == 'connection' and key not in Connection.META_DATA_KEYS:
            raise MapParsingError(f"Invalid key '{key}' for connection metadata '{string}'")            
        if key == 'color' and value not in valid_colors:
            if not re.search(pattern_color, value):
                raise MapParsingError(f"Invalid color for metadata '{string}'")
            value = 'white'
        result[key] = value
    return result


def get_zones(zones: list[tuple[str, str]]) -> list[dict[str, Any]]:

    # Validate unique start_hub
    start_hubs: list[str] = [key for key, value in zones if key == 'start_hub']
    if len(start_hubs) > 1:
        raise MapParsingError("There must be exactly one start_hub: zone")
    # Validate unique end_hub
    end_hubs: list[str] = [key for key, value in zones if key == 'end_hub']
    if len(end_hubs) > 1:
        raise MapParsingError("There must be exactly one end_hub: zone")

    results: list[dict[str, Any]] = []
    for hub, values in zones:

        metadata: str = ""
        attributes = values.split(maxsplit=3)
        if len(attributes) > 4:
            raise MapParsingError(
                    f"To many arguments for zone: '{hub}': "
                    f"'{attributes}'"
            )
        if len(attributes) < 3:
            raise MapParsingError(
                f"To few arguments for zone: '{hub}': "
                f"'{attributes}'"
            )
        if len(attributes) == 3:
            name, coord_x, coord_y = attributes
        if len(attributes) == 4:
            name, coord_x, coord_y, metadata = attributes
        try:
            x = int(coord_x)
            y = int(coord_y)
        except ValueError:
            raise MapParsingError(
                "Invalid values or format in zone: "
                f"{hub}, name: {name}, x: {coord_x}, y: {coord_y}, "
                f"metadata: {metadata}"
            )
        parsed_metadata: dict[str, str] = get_metadata(metadata, 'hub')
        results.append(
            {
                'prefix': hub,
                'name': name,
                'x': x,
                'y': y,
                'zone_type': parsed_metadata.get('zone', 'normal'),
                'color': parsed_metadata.get('color', 'white'),
                'max_drones': parsed_metadata.get('max_drones', 1),                
            }
        )
    return results


def get_connections(
        connections: list[tuple[str, str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for connection, values in connections:
        metadata: str = ""
        attributes = values.split(maxsplit=1)
        if len(attributes) > 2:
            raise MapParsingError(
                "To many arguments for connection: "
                f"{connection}: {attributes}"
            )
        if len(attributes) < 1:
            raise MapParsingError(
                "To few arguments for connection: "
                f"{connection}: {attributes}"
            )
        if len(attributes) == 1:
            name, = attributes
        if len(attributes) == 2:
            name, metadata = attributes
        # Validate <zone1>-<zone2> format
        if name.count('-') != 1 or name.startswith('-') or name.endswith('-'):
            raise MapParsingError(
                f"Invalid name for connection: '{name}' "
                "expected: <zone1>-<zone2>"
            )
        parsed_metadata: dict[str, str] = get_metadata(metadata, 'connection')        
        results.append(
            {
                'prefix': connection,
                'name': name,
                'max_link_capacity': parsed_metadata.get('max_link_capacity', 1),
            }
        )
    return results


def parse_map(filename: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    raw_data: list[tuple[str, str]] = read_map(filename)

    # nb_drones
    try:
        nb_drones = get_numbers_of_drones(raw_data)
        data['nb_drones'] = nb_drones
    except MapParsingError as e:
        print(f"PARSING ERROR {e}")
        exit(1)

    # zones
    try:
        zones = [
            line for line in raw_data
            if line[0] in ('hub', 'start_hub', 'end_hub')
        ]
        data['zones'] = get_zones(zones)
    except MapParsingError as e:
        print(f"PARSING ERROR {e}")
        exit(1)

    # connections
    try:
        connections = [
            line for line in raw_data
            if line[0] == 'connection'
        ]
        data['connections'] = get_connections(connections)
    except MapParsingError as e:
        print(f"PARSING ERROR {e}")
        exit(1)

    return data
