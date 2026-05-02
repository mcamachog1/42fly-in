# read_map.py


from typing import Any
import sys


def read_map(filename: str) -> dict[str, Any]:
    config: dict[str, Any] = {}
    valid_keys: list[str] = [
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

