# estado global compartilhado entre testes
estado = {
    "contador": 0,
    "flag": False,
    "valor": 0
}

# -----------------------------------
# Teste 1: falha se contador ainda for 0
def test_incremento_contador():
    """
    Falha sutil dependendo do contador.
    Pode gerar ~33% de falhas dependendo da ordem.
    """
    if estado["contador"] == 0:
        estado["contador"] += 1
    assert estado["contador"] > 0

# -----------------------------------
# Teste 2: falha se flag não foi ativada
def test_ativar_flag():
    """
    Falha sutil se outro teste não ativou a flag.
    Pode gerar ~50% de falhas em reruns.
    """
    if estado["contador"] > 0:
        estado["flag"] = True
    assert estado["flag"]

# -----------------------------------
# Teste 3: falha se valor não for múltiplo de 2
def test_valor_par():
    """
    Falha sutil dependendo do valor.
    Percentual variável (~66%) dependendo da sequência de execução.
    """
    if estado["valor"] % 2 == 0:
        estado["valor"] += 1
    assert estado["valor"] % 2 == 1

# -----------------------------------
# Teste 4: depende de flag e valor
def test_dependencia_multipla():
    """
    Falha se flag não foi ativada ou valor ainda for par.
    Percentual aleatório natural dependendo dos reruns.
    """
    assert estado["flag"] is True
    assert estado["valor"] % 2 == 1
    # incrementa valor para influenciar próximos reruns
    estado["valor"] += 1
