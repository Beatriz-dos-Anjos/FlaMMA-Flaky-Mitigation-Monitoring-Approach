#!/usr/bin/env python3
"""
issues/create_github_issue.py

- Cria issues no GitHub a partir de um flaky_report.json.
- Comportamento:
  - evita duplicar issues (checa issues abertas com label "flaky")
  - admite modo --dry-run (não cria nada, só imprime o que faria)
  - tenta usar PyGithub; se não houver, cai para requests (fallback)
  - opcional: embutir conteúdo HTML/mini-relatório na issue via --embed-html PATH
  - compatível com execução local e com GitHub Actions
"""

import os
import json
import argparse
import sys

# Tenta PyGithub primeiro
try:
    from github import Github  # type: ignore
    _HAS_PYGITHUB = True
except Exception:
    _HAS_PYGITHUB = False

# fallback para requests
try:
    import requests  # type: ignore
    _HAS_REQUESTS = True
except Exception:
    _HAS_REQUESTS = False


def diagnosticar_causa(runs):
    if "failed" in runs and "passed" in runs:
        return (
            "- Execução intermitente → típico de flakiness\n"
            "- Possíveis causas:\n"
            "  • Dependência de tempo (sleep, delays)\n"
            "  • Estado global/compartilhado entre testes\n"
            "  • Acesso à rede/arquivos sem isolamento\n"
            "  • Uso de aleatoriedade sem seed\n"
        )
    if all(r == "failed" for r in runs):
        return (
            "- O teste falhou em todas as execuções → provável bug/expectativa incorreta\n"
            "- Investigar logs, stacktrace e pré-condições do teste."
        )
    return "Não foi possível identificar uma causa provável automaticamente."


def build_issue_body(test_name, passes, fails, runs, embed_html_path=None):
    fail_rate = (fails / (passes + fails)) * 100 if (passes + fails) > 0 else 0.0
    is_flaky = (passes > 0 and fails > 0)

    tabela = (
        "| Campo | Valor |\n"
        "|-------|-------|\n"
        f"| Teste | `{test_name}` |\n"
        f"| Passes | {passes} |\n"
        f"| Fails | {fails} |\n"
        f"| Runs | {runs} |\n"
        f"| Falhas (%) | {fail_rate:.1f}% |\n"
        f"| Status | {'Flaky' if is_flaky else '✅ Estável'} |\n"
    )

    diagnostico = diagnosticar_causa(runs)

    body_lines = [
        "### Relatório Automático do Teste Flaky",
        "",
        tabela,
        "",
        "---",
        "",
        "### Diagnóstico Automático",
        "",
        diagnostico,
        "",
        "---",
        "",
        "### Execuções detalhadas",
        "```",
        str(runs),
        "```",
    ]

    # embutir HTML opcionalmente
    if embed_html_path:
        try:
            with open(embed_html_path, "r", encoding="utf-8") as h:
                html_content = h.read()
            body_lines += [
                "",
                "---",
                "",
                "### Relatório HTML (conteúdo embutido)",
                "",
                "```html",
                html_content,
                "```",
            ]
        except Exception as e:
            body_lines += ["", f"_Não foi possível ler {embed_html_path}: {e}_"]

    body_lines += ["", "### Observação", "Este relatório foi gerado automaticamente pelo módulo de flakiness."]
    return "\n".join(body_lines)


def issue_exists_pygithub(repo, title):
    try:
        issues = repo.get_issues(state="open", labels=["flaky"])
        for issue in issues:
            if issue.title.strip() == title.strip():
                return True
    except Exception:
        try:
            issues = repo.get_issues(state="open")
            for issue in issues:
                if issue.title.strip() == title.strip():
                    return True
        except Exception:
            pass
    return False


def create_issue_pygithub(repo, title, body, labels, dry_run=False):
    if dry_run:
        print("[DRY RUN] Criaria issue (PyGithub):", title)
        return None
    issue = repo.create_issue(title=title, body=body, labels=labels)
    return issue.html_url


def issue_exists_requests(repo_full_name, token, title):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    params = {"state": "open", "labels": "flaky", "per_page": 100}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        for it in resp.json():
            if it.get("title", "").strip() == title.strip():
                return True
    except Exception:
        try:
            resp = requests.get(url, headers=headers, params={"state": "open", "per_page": 100}, timeout=15)
            resp.raise_for_status()
            for it in resp.json():
                if it.get("title", "").strip() == title.strip():
                    return True
        except Exception:
            pass
    return False


def create_issue_requests(repo_full_name, token, title, body, labels, dry_run=False):
    if dry_run:
        print("[DRY RUN] Criaria issue (HTTP):", title)
        return None

    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    data = {"title": title, "body": body, "labels": labels}

    resp = requests.post(url, headers=headers, json=data, timeout=15)

    if resp.status_code in (200, 201):
        return resp.json().get("html_url")
    else:
        raise RuntimeError(f"Erro criando issue via REST API: {resp.status_code} {resp.text}")


def main():
    parser = argparse.ArgumentParser(description="Criar issues automáticas a partir de flaky_report.json")
    parser.add_argument("--report", required=True, help="Caminho para flaky_report.json")
    parser.add_argument("--repository", help="Repo user/repo. Se omitido, usa GITHUB_REPOSITORY")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula")
    parser.add_argument("--embed-html", help="Embed de issues/report.html")
    args = parser.parse_args()

    repo_name = args.repository or os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("Erro: GITHUB_TOKEN ausente.", file=sys.stderr)
        sys.exit(1)
    if not repo_name:
        print("Erro: GITHUB_REPOSITORY ausente.", file=sys.stderr)
        sys.exit(1)

    # Load JSON
    try:
        with open(args.report, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erro ao abrir {args.report}: {e}", file=sys.stderr)
        sys.exit(1)

    tests = data.get("tests", {})
    if not tests:
        print("Nenhum teste em 'tests'. Nada a fazer.")
        return

    use_pygithub = _HAS_PYGITHUB
    use_requests = _HAS_REQUESTS

    if use_pygithub:
        gh = Github(token)
        try:
            repo = gh.get_repo(repo_name)
        except Exception as e:
            print(f"Erro PyGithub: {e}", file=sys.stderr)
            repo = None
            use_pygithub = False
    else:
        repo = None

    if not use_pygithub and not use_requests:
        print("Instale: pip install PyGithub requests", file=sys.stderr)
        sys.exit(1)

    # PROCESSAR TESTES
    for test_name, info in tests.items():
        passes = info.get("pass_count", 0)
        fails = info.get("fail_count", 0)
        runs = info.get("runs", [])

        # -------------------------------
        #   ⛔ NOVA LÓGICA CORRETA:
        #   SO-MEN-TE criar issue se flaky
        # -------------------------------
        is_flaky = passes > 0 and fails > 0
        if not is_flaky:
            print(f"[INFO] Teste estável ignorado: {test_name}")
            continue
        # -------------------------------

        title = f"Flaky test detected: {test_name}"
        body = build_issue_body(test_name, passes, fails, runs, embed_html_path=args.embed_html)
        labels = ["flaky", "ci-auto"]

        # checar duplicidade
        exists = False
        try:
            if use_pygithub and repo:
                exists = issue_exists_pygithub(repo, title)
            elif use_requests:
                exists = issue_exists_requests(repo_name, token, title)
        except Exception as e:
            print(f"Warning ao checar duplicata: {e}")
            exists = False

        if exists:
            print(f"[INFO] Issue já existe: {title}")
            continue

        # criar issue
        try:
            if use_pygithub and repo:
                url = create_issue_pygithub(repo, title, body, labels, dry_run=args.dry_run)
            else:
                url = create_issue_requests(repo_name, token, title, body, labels, dry_run=args.dry_run)

            if url:
                print(" Issue criada:", url)
            else:
                print("[DRY RUN] Nenhuma issue criada.")
        except Exception as e:
            print(f"Erro criando issue para {test_name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
