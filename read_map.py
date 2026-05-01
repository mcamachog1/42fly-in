# read_map.py


from typing import Any
import sys
try:
    from pydantic import BaseModel, Field, ValidationError
except Exception as e:
    print("Pydantic Module not Found!")
    sys.exit()


def read_map(filename: str) -> dict[str, Any]:
    config: dict[str, Any] = {}
    valid_keys: List[str] = [
        'nb_drones',
        'start_hub',
        'hub',
        'end_hub',
        'connection',
        ]
    try:
        with open(filename) as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split(":")
                if key not in valid_keys:
                    raise ValueError(f"Invalid key '{key}'.")
                config[key] = value
            for key in valid_keys:
                if key not in config.keys():
                    raise ValueError(f"'{key}' is missing.")
    except FileNotFoundError:
        print(f"RESPONSE: Archive not found {filename}", file=sys.stderr)
        sys.exit()
    except PermissionError:
        print(f"RESPONSE: Archive deny access {filename}", file=sys.stderr)
        sys.exit()
    except ValueError as error:
        print(
            f"RESPONSE: Incorrect config format. "
            f"{error} Check '{filename}' file",
            file=sys.stderr
        )
        sys.exit()
    except Exception as error:
        print(
            f"RESPONSE:  Unexpected error: {error}"
            f"- Type: {type(error).__name__}", file=sys.stderr)
        sys.exit()
    return config


class Hub(BaseModel):


class Map(BaseModel):
    nb_drones: int = Field(ge=1, le=10)
    start_hub: Hub
    hubs: list[Hub]
    end_hub: Hub
    connections: list[connections] 

def parse_map(config: dict[str, Any]) -> dict[str, Any]):

