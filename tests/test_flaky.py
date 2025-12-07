state = {"initialized": False}

def test_initialize_state():
    state["initialized"] = True
    assert state["initialized"]

def test_use_state():
    # flakiness ocorre quando esse executa ANTES do de cima
    assert state["initialized"]
