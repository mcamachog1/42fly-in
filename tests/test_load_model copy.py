#!/usr/bin/env python3
# test_parser.py


from typing import Any
from src.parser.load_model import parse_map


MAP01 = 'tests/test_data/01_dron_error.txt'
MAP02  = 'tests/test_data/02_hub_error.txt'
MAP03  = 'tests/test_data/03_load_ok.txt'
MAP04  = 'tests/test_data/04_config_key_error.txt'
MAP05  = 'tests/test_data/05_duplicate_key_error.txt'
MAP06  = 'tests/test_data/06_config_separator_error.txt'
MAP07 = 'data/maps/challenger/01_the_impossible_dream.txt'

def test_07() -> dict[str, Any]:
    filename: str = MAP07
    return parse_map(filename)

def test_05() -> dict[str, Any]:
    filename: str = MAP05
    return parse_map(filename)

def test_04() -> dict[str, Any]:
    filename: str = MAP04
    return parse_map(filename)

def test_03() -> dict[str, Any]:
    filename: str = MAP03
    return parse_map(filename)

def test_02() -> dict[str, Any]:
    filename: str = MAP02
    return parse_map(filename)

def test_01() -> dict[str, Any]:
    filename: str = MAP01
    return parse_map(filename)


if __name__ == "__main__":
    #test_06()
    # test_05()
    # test_04()
    # test_02()
    # print(test_01())
    print(test_02())
