
import time
import random
import threading
import asyncio
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock
import pytest


# =============================================================================
# 1. TESTES COM DEPENDÊNCIA DE TEMPO
# =============================================================================

def slow_operation():
    """Simula operação que varia em duração"""
    time.sleep(random.uniform(0.8, 1.2))
    return "done"


def test_timeout_flaky():
    """Falha quando a operação demora mais que o esperado"""
    start = time.time()
    result = slow_operation()
    elapsed = time.time() - start
    assert elapsed < 1.0  # Flaky: às vezes demora mais de 1 segundo


def test_performance_threshold():
    """Testa limites de performance que podem variar"""
    start = time.time()
    data = [i ** 2 for i in range(10000)]
    elapsed = time.time() - start
    assert elapsed < 0.01  # Flaky: depende da carga do sistema


# =============================================================================
# 2. TESTES COM SLEEP/DELAYS
# =============================================================================

ASYNC_RESULT = None


def trigger_async_operation():
    """Simula operação assíncrona"""
    def delayed_action():
        time.sleep(random.uniform(0.3, 0.7))
        global ASYNC_RESULT
        ASYNC_RESULT = "completed"
    
    threading.Thread(target=delayed_action).start()


def test_async_with_insufficient_sleep():
    """Falha quando o sleep não é suficiente"""
    global ASYNC_RESULT
    ASYNC_RESULT = None
    
    trigger_async_operation()
    time.sleep(0.4)  # Flaky: às vezes a operação demora mais
    assert ASYNC_RESULT == "completed"


# =============================================================================
# 3. TESTES COM ORDEM ALEATÓRIA
# =============================================================================

def test_random_choice():
    """Falha aleatoriamente baseado em escolha randômica"""
    value = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
    assert value < 5  # Flaky: 50% de chance de falhar


def test_random_shuffle():
    """Falha baseado em ordem aleatória"""
    items = [1, 2, 3, 4, 5]
    random.shuffle(items)
    assert items[0] == 1  # Flaky: primeira posição é aleatória


def test_uuid_collision():
    """Simula teste que assume unicidade"""
    import uuid
    id1 = str(uuid.uuid4())[:8]
    id2 = str(uuid.uuid4())[:8]
    # Extremamente raro mas possível
    assert id1 != id2  # Flaky: colisão muito rara


# =============================================================================
# 4. TESTES COM DEPENDÊNCIA DE REDE (simulado)
# =============================================================================

def unreliable_api_call():
    """Simula chamada de API que falha aleatoriamente"""
    if random.random() < 0.3:  # 30% de chance de falha
        raise ConnectionError("Network timeout")
    return {"status": "ok", "data": [1, 2, 3]}


def test_external_api():
    """Falha quando a API não responde"""
    response = unreliable_api_call()  # Flaky: pode lançar exceção
    assert response["status"] == "ok"


def test_api_with_retry_race():
    """Falha quando retry não é suficiente"""
    attempts = 0
    max_attempts = 2
    
    while attempts < max_attempts:
        try:
            response = unreliable_api_call()
            break
        except ConnectionError:
            attempts += 1
            if attempts >= max_attempts:
                raise
    
    # Flaky: pode não conseguir em 2 tentativas
    assert response["status"] == "ok"


# =============================================================================
# 5. TESTES COM CONDIÇÕES DE CORRIDA (THREADING)
# =============================================================================

def test_race_condition():
    """Falha devido a race condition clássica"""
    counter = [0]
    
    def increment():
        for _ in range(1000):
            current = counter[0]
            time.sleep(0.000001)  # Aumenta chance de race condition
            counter[0] = current + 1
    
    threads = [threading.Thread(target=increment) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Flaky: resultado varia por race condition
    assert counter[0] == 5000


shared_list = []


def test_shared_state_race():
    """Falha devido a acesso concorrente a estado compartilhado"""
    shared_list.clear()
    
    def append_items():
        for i in range(100):
            shared_list.append(i)
    
    threads = [threading.Thread(target=append_items) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Flaky: ordem e contagem podem variar
    assert len(shared_list) == 300
    assert shared_list == sorted(shared_list)


# =============================================================================
# 6. TESTES COM DEPENDÊNCIA DE DATA/HORA ATUAL
# =============================================================================

def test_business_hours():
    """Falha fora do horário comercial"""
    now = datetime.now()
    # Flaky: depende do horário de execução
    assert 9 <= now.hour < 18, "Teste só funciona em horário comercial"


def test_weekday_only():
    """Falha em finais de semana"""
    now = datetime.now()
    # Flaky: falha aos sábados e domingos
    assert now.weekday() < 5, "Teste não funciona em finais de semana"


def test_date_boundary():
    """Falha perto da meia-noite"""
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Flaky: falha se executar exatamente à meia-noite
    assert now != start_of_day


def test_time_dependent_calculation():
    """Falha baseado em timestamp"""
    timestamp = int(time.time())
    # Flaky: depende se timestamp é par ou ímpar
    assert timestamp % 2 == 0


# =============================================================================
# 7. TESTES COM ESTADO COMPARTILHADO
# =============================================================================

cache = {}


def test_cache_write():
    """Modifica estado global"""
    cache['test_key'] = 'value1'
    assert cache['test_key'] == 'value1'


def test_cache_read():
    """Falha se test_cache_write não rodou antes ou se cache foi limpo"""
    # Flaky: depende da ordem de execução dos testes
    assert 'test_key' in cache
    assert cache['test_key'] == 'value1'


global_counter = 0


def test_increment_counter():
    """Incrementa contador global"""
    global global_counter
    global_counter += 1
    assert global_counter > 0


def test_counter_value():
    """Assume valor específico do contador"""
    global global_counter
    # Flaky: depende de quantos testes rodaram antes
    assert global_counter == 1


# =============================================================================
# 8. TESTES COM DEPENDÊNCIA DE BANCO DE DADOS (simulado)
# =============================================================================

fake_database = {}


def test_database_insert():
    """Insere dados no banco"""
    fake_database['user_1'] = {'name': 'João', 'email': 'joao@test.com'}
    assert 'user_1' in fake_database


def test_database_query():
    """Assume que dados existem"""
    # Flaky: falha se test_database_insert não rodou antes
    user = fake_database.get('user_1')
    assert user is not None
    assert user['name'] == 'João'


def test_database_count():
    """Assume quantidade específica de registros"""
    # Flaky: depende de quantos testes de inserção rodaram
    assert len(fake_database) == 1


# =============================================================================
# 9. TESTES COM FILESYSTEM
# =============================================================================

def test_temp_file_creation():
    """Falha se arquivo já existe ou foi deletado"""
    filename = '/tmp/test_flaky_file.txt'
    
    # Flaky: pode falhar se outro processo usar o mesmo nome
    with open(filename, 'w') as f:
        f.write('test content')
    
    time.sleep(0.1)
    assert os.path.exists(filename)
    
    # Cleanup que pode falhar
    os.remove(filename)


def test_file_race_condition():
    """Falha devido a race condition no filesystem"""
    filename = '/tmp/race_test.txt'
    
    def write_file():
        with open(filename, 'w') as f:
            f.write('data')
        time.sleep(0.01)
        if os.path.exists(filename):
            os.remove(filename)
    
    thread = threading.Thread(target=write_file)
    thread.start()
    
    time.sleep(0.005)
    # Flaky: arquivo pode ou não existir dependendo do timing
    assert os.path.exists(filename)
    
    thread.join()


def test_directory_listing():
    """Falha se outros processos modificarem diretório"""
    temp_dir = tempfile.gettempdir()
    initial_count = len(os.listdir(temp_dir))
    
    # Cria arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    final_count = len(os.listdir(temp_dir))
    
    # Flaky: outros processos podem criar/deletar arquivos
    assert final_count == initial_count + 1
    
    os.unlink(temp_file.name)


# =============================================================================
# 10. TESTES COM ASYNC/AWAIT MAL IMPLEMENTADOS
# =============================================================================

async def flaky_async_operation():
    """Operação assíncrona com tempo variável"""
    await asyncio.sleep(random.uniform(0.05, 0.15))
    return "done"


def test_async_without_proper_loop():
    """Falha por não usar event loop corretamente"""
    async def run_test():
        result = await flaky_async_operation()
        return result
    
    # Flaky: pode não completar corretamente
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(run_test())
    
    # Não espera o suficiente
    loop.run_until_complete(asyncio.sleep(0.08))
    
    # Flaky: task pode não ter completado
    assert task.done()
    
    loop.close()


@pytest.mark.asyncio
async def test_concurrent_async_operations():
    """Falha devido a condições de corrida em async"""
    shared_data = []
    
    async def append_data(value):
        await asyncio.sleep(random.uniform(0.001, 0.01))
        shared_data.append(value)
    
    # Executa operações concorrentemente
    await asyncio.gather(*[append_data(i) for i in range(10)])
    
    # Flaky: ordem pode variar
    assert shared_data == list(range(10))


# =============================================================================
# 11. TESTES COM DEPENDÊNCIA DE RECURSOS DO SISTEMA
# =============================================================================

def test_memory_availability():
    """Falha quando memória está baixa"""
    import sys
    
    # Tenta alocar muita memória
    try:
        large_list = [0] * (10 ** 7)
        # Flaky: pode falhar se sistema está com pouca memória
        assert sys.getsizeof(large_list) > 0
    except MemoryError:
        pytest.fail("Sem memória disponível")


def test_cpu_load_dependent():
    """Falha quando CPU está sobrecarregada"""
    start = time.time()
    
    # Operação CPU-intensiva
    result = sum(i ** 2 for i in range(100000))
    
    elapsed = time.time() - start
    # Flaky: tempo varia com carga da CPU
    assert elapsed < 0.1


# =============================================================================
# 12. TESTES COM FLOATING POINT
# =============================================================================

def test_floating_point_precision():
    """Falha devido a imprecisão de ponto flutuante"""
    result = 0.1 + 0.2
    # Flaky em diferentes arquiteturas/compiladores
    assert result == 0.3  # Na verdade é 0.30000000000000004


def test_floating_point_accumulation():
    """Falha devido a acumulação de erros"""
    total = 0.0
    for _ in range(10):
        total += 0.1
    
    # Flaky: erro acumula de forma não-determinística
    assert total == 1.0
