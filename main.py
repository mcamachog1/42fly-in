#!/usr/bin/env python3
# main.py


from typing import Any
from read_map import read_map

MAP_1 = 'maps/easy/01_linear_path.txt'

def main() -> None:
    file_name: str = MAP_1
    config: dict[str, Any] = read_map(file_name)
    print(config)


if __name__ == "__main__":
    main()

