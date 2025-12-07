import random

estado = {"ativado": False}

def test_flaky_sutil():
    # O comportamento muda de forma sutil, sem mostrar porcentagem
    valor = random.choice([True, True, False])
    if valor:
        estado["ativado"] = True
    assert estado["ativado"]
