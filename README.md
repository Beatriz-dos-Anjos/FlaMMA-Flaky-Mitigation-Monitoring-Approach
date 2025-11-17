Visão Geral

FlaMMA é uma abordagem automatizada para detecção, quarentena e monitoramento de testes flaky integrada a pipelines de CI/CD.
O objetivo é manter pipelines estáveis sem esconder problemas — isolando testes instáveis, mas registrando e reportando tudo para que a equipe possa corrigir depois.

O projeto investiga:

* como detectar flaky tests automaticamente,
* como colocar esses testes em quarentena sem quebrar o build,
* como reportá-los de forma rastreável (issues, logs),
*  qual é o impacto disso no tempo do pipeline e na estabilidade geral.

Este repositório contém a implementação modular da abordagem.

🎯 Objetivos do Projeto

-> Detectar automaticamente testes flaky por meio de reexecuções e análise de inconsistência.
->Isolar temporariamente (quarentena) os testes encontrados.
->Gerar issues automáticas com detalhes e logs dos testes instáveis.
->Integrar todo o fluxo ao CI/CD (ex.: GitHub Actions).

Avaliar eficiência, overhead e estabilidade da solução proposta.

🧱 Estrutura do Projeto
project/
 ├── ci/               # Configurações do pipeline (GitHub Actions)
 ├── detector/         # Lógica de detecção de flaky tests
 ├── quarantine/       # Módulo que gerencia testes em quarentena
 ├── issues/           # Geração de issues e relatórios automáticos
 ├── contracts/        # Schemas JSON para padronização dos módulos
 ├── tests/            # Testes usados para demonstração e validação
 │    ├── test_stable.py
 │    └── test_flaky.py
 ├── requirements.txt  # Dependências gerais do projeto
 └── README.md         # Este documento


Cada módulo é independente e segue contratos definidos por schemas JSON localizados em contracts/.

🧪 Testes de Demonstração

O repositório inclui dois testes básicos:

test_stable.py – sempre passa

test_flaky.py – falha aleatoriamente (simula cenário real)

Esses testes servem de base para os módulos de detecção e quarentena.

📦 Instalação das Dependências

Para instalar as bibliotecas necessárias:

pip install -r requirements.txt


Dependências incluídas:

pytest — execução de testes

requests — envio de issues via API

jsonschema — validação dos contratos JSON

▶️ Executando os Testes

Após instalar as dependências, execute:

pytest -q