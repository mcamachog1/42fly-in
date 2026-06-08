# read_map.py


import sys


def read_map(filename: str) -> list[tuple[str, str, int]]:
    valid_keys: list[str] = [
        'nb_drones',
        'start_hub',
        'hub',
        'end_hub',
        'connection',
        ]
    # Each line is a tuple (key, value(s), line_number)
    file_lines: list[tuple[str, str, int]] = []
    try:
        with open(filename) as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip().lower()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split(":")
                if key not in valid_keys:
                    raise ValueError(f"Invalid key '{key}'.")
                file_lines.append((key, value, line_num))
            for key in valid_keys:
                if key not in {line[0] for line in file_lines}:
                    raise ValueError(f"'{key}' is missing")
    except FileNotFoundError:
        print(f"READING FILE ERROR: Archive not found {filename}", file=sys.stderr)
        sys.exit()
    except PermissionError:
        print(f"READING FILE ERROR: Archive deny access {filename}", file=sys.stderr)
        sys.exit()
    except ValueError as error:
        print(
            f"READING FILE ERROR: {error} in '{filename}' Error in line {line_num} ",
            file=sys.stderr
        )
        sys.exit()
    except Exception as error:
        print(
            f"READING FILE ERROR:  Unexpected error: {error} Error in line {line_num} "
            f"- Type: {type(error).__name__}", file=sys.stderr)
        sys.exit()
    return file_lines
