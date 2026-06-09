#!/usr/bin/env python3
# test_parser.py


from src.parser.parse_map import MapParser

MAP_1 = 'data/maps/easy/01_linear_path.txt'


def main() -> None:
    filename: str = MAP_1
    map_parser = MapParser(filename)
    my_map = map_parser.load_map()
    print(my_map)


if __name__ == "__main__":
    main()
