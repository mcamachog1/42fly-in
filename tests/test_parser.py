#!/usr/bin/env python3
# test_parser.py


from typing import Any
from src.parser.read_map import read_map

MAP_1 = 'data/maps/easy/01_linear_path.txt'

def main() -> None:
    file_name: str = MAP_1
    config: dict[str, Any] = read_map(file_name)
    for key, value in config.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
