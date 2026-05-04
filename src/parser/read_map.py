# read_map.py


from typing import Any
import sys


def read_map(filename: str) -> list[tuple[str, str]]:
    #config: dict[str, Any] = {}
    valid_keys: list[str] = [
        'nb_drones',
        'start_hub',
        'hub',
        'end_hub',
        'connection',
        ]
    # Each line is a tuple
    file_lines: list[tuple[str, str]] = []
    try:
        with open(filename) as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split(":")
                if key not in valid_keys:
                    raise ValueError(f"Invalid key '{key}'.")
                file_lines.append((key, value))
            for key in valid_keys:
                if key not in {line[0] for line in file_lines}:
                    raise ValueError(f"'{key}' is missing.")
    except FileNotFoundError:
        print(f"RESPONSE: Archive not found {filename}", file=sys.stderr)
        sys.exit()
    except PermissionError:
        print(f"RESPONSE: Archive deny access {filename}", file=sys.stderr)
        sys.exit()
    except ValueError as error:
        print(
            f"RESPONSE: Incorrect imput format in '{filename}' "
            f"at line {line_num}. Expected 'key: name x y optional[k=v]' "
            f"format, but found: '{line.strip()}'",
            file=sys.stderr
        )
        sys.exit()
    except Exception as error:
        print(
            f"RESPONSE:  Unexpected error: {error} "
            f"at line {line_num} "
            f"- Type: {type(error).__name__}", file=sys.stderr)
        sys.exit()
    return file_lines

