def func(x):
    return x + 1


def test_ok():
    assert func(3) == 4


def test_wrong():
    assert func(3) == 5