#!/usr/bin/env python3
# test_parser.py


from typing import Any
from src.parser.load_model import parse_map


MAP_1 = 'data/maps/easy/01_linear_path.txt'

def main() -> None:
    filename: str = MAP_1
    m, c, h = parse_map(filename)
    print(f"nb_drones = {m.nb_drones}")


if __name__ == "__main__":
    main()
