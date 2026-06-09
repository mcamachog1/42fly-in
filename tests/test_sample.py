def func(x: int) -> int:
    return x + 1


def test_ok() -> None:
    assert func(3) == 4


def test_wrong() -> None:
    assert func(3) == 5
