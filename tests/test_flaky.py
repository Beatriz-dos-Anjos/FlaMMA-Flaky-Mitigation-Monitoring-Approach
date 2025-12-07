import random

state = {"initialized": False}

def test_initialize_state():
    if random.random() < 0.5:
        state["initialized"] = True
    assert state["initialized"]

def test_use_state():
    assert state["initialized"]
