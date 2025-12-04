import random

def test_flaky():
    assert random.choice([True, False, True])