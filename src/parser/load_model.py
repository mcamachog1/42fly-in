# load_model.py


import sys
from typing import Any
from src.model.model import Hub, Connection, Map
from src.parser.read_map import read_map
from pydantic import ValidationError


def parse_map(filename: str) -> tuple[Any, Any, Any]:
    raw_data: dict[str, Any] = read_map(filename)
    nb_drones: int = raw_data['nb_drones']

    try:
        map = Map(nb_drones=nb_drones)
    except ValidationError:
        print(f"RESPONSE: Invalid value: {nb_drones}", file=sys.stderr)
        exit(1)

    return map, None, None