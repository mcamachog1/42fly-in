# load_model.py

from src.model.model import Hub, Connection, Map
from pydantic import ValidationError
from typing import Any

UNLIMITED_DRONES = 10000

def load_map(network: dict[str, Any]) -> Map:
    # Format input for zone objects
    zones: list[dict[str, Any]] = network['zones']
    hubs: list[Hub] = []
    for zone in zones:
        if zone['prefix'] == 'start_hub':
            start_hub = zone
            zone['max_drones'] = UNLIMITED_DRONES
        if zone['prefix'] == 'end_hub':
            end_hub = zone
            zone['max_drones'] = UNLIMITED_DRONES
        hubs.append(Hub(**zone))

    # Format input for connections objects
    connections: list[dict[str, Any]] = network['connections']
    connection_objects: list[Connection] = []
    for connection in connections:
        connection_objects.append(Connection(**connection))

    # Format input for map object
    map_input: dict[str, Any] = {}
    map_input['nb_drones'] = network['nb_drones']
    map_input['start_hub'] = start_hub
    map_input['end_hub'] = end_hub
    map_input['hubs'] = hubs
    map_input['connections'] = connection_objects
    try:
        fly_map = Map(**map_input)
    except ValidationError as e:
        for error in e.errors():
            print(
                "CONSTRAINT ERROR: "
                f"{error['msg'].removeprefix('Value error, ')}"
            )
            exit(1)
    return fly_map