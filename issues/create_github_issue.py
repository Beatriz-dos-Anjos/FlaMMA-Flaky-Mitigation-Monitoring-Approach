#!/usr/bin/env python3
"""
issues/create_github_issue.py

Cria issues no GitHub a partir de um flaky_report.json.
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


# ============================================================
#  Função corrigida — AGORA ESTÁ FORA do main()
# ============================================================
def generate_html_report(data, out_path="issues/report.html"):
    from datetime import datetime
    import os

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Flaky Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background: #eee; }}
        .flaky {{ background: #ffb3b3; }}
    </style>
</head>
<body>
    <h1>Relatório de Testes Flaky</h1>
    <p>Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <table>
        <tr>
            <th>Teste</th>
            <th>Passes</th>
            <th>Fails</th>
            <th>Runs</th>
            <th>Porcentagem Falhas</th>
            <th>Status</th>
        </tr>
"""

    for test_name, info in data.get("tests", {}).items():
        passes = info.get("pass_count", 0)
        fails = info.get("fail_count", 0)
        is_flaky = info.get("is_flaky", False)

        if not is_flaky:
            continue

        total = passes + fails
        fail_rate = (fails / total) * 100 if total > 0 else 0

        html += f"""
        <tr class="flaky">
            <td>{test_name}</td>
            <td>{passes}</td>
            <td>{fails}</td>
            <td>{info.get("runs", [])}</td>
            <td>{fail_rate:.1f}%</td>
            <td>Flaky</td>
        </tr>
"""

    html += """
    </table>
</body>
</html>
"""

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Relatório HTML gerado em: {out_path}")


# ============================================================
# Funções auxiliares originais
# ============================================================

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
            body_lines.append(f"_Não foi possível ler {embed_html_path}: {e}_")

    body_lines.append("")
    body_lines.append("### Observação")
    body_lines.append("Este relatório foi gerado automaticamente pelo módulo de flakiness.")

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
    if not _HAS_REQUESTS:
        return False

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
        pass
    return False


def create_issue_requests(repo_full_name, token, title, body, labels, dry_run=False):
    if not _HAS_REQUESTS:
        raise RuntimeError("Biblioteca 'requests' não instalada.")

    if dry_run:
        print("[DRY RUN] Criaria issue (HTTP):", title)
        return None

    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    resp = requests.post(url, headers=headers, json={"title": title, "body": body, "labels": labels}, timeout=15)

    if resp.status_code in (200, 201):
        return resp.json().get("html_url")

    raise RuntimeError(f"Erro criando issue via REST API: {resp.status_code} {resp.text}")


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Criar issues automáticas a partir de flaky_report.json")
    parser.add_argument("--report", required=True, help="Caminho para flaky_report.json")
    parser.add_argument("--repository", help="Repo user/repo. Se omitido, usa GITHUB_REPOSITORY")
    parser.add_argument("--dry-run", action="store_true", help="Apenas simula")
    parser.add_argument("--embed-html", help="Embed de issues/report.html")
    parser.add_argument("--generate-html", action="store_true", help="Gera issues/report.html automaticamente")
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

    if args.generate_html:
        generate_html_report(data)

    # PyGithub?
    use_pygithub = _HAS_PYGITHUB
    repo = None
    if use_pygithub:
        try:
            gh = Github(token)
            repo = gh.get_repo(repo_name)
        except Exception as e:
            print(f"Erro PyGithub: {e}")
            use_pygithub = False

    # ------------------------------------------------------------
    # PROCESSAR TESTES FLAKY
    # ------------------------------------------------------------
    for test_name, info in tests.items():
        passes = info.get("pass_count", 0)
        fails = info.get("fail_count", 0)
        runs = info.get("runs", [])

        is_flaky = passes > 0 and fails > 0
        if not is_flaky:
            print(f"[INFO] Teste estável ignorado: {test_name}")
            continue

        title = f"Flaky test detected: {test_name}"
        body = build_issue_body(test_name, passes, fails, runs, embed_html_path=args.embed_html)
        labels = ["flaky", "ci-auto"]

        # Checar duplicidade
        exists = False
        try:
            if use_pygithub and repo:
                exists = issue_exists_pygithub(repo, title)
            else:
                exists = issue_exists_requests(repo_name, token, title)
        except Exception as e:
            print(f"WARNING ao checar duplicata: {e}")

        if exists:
            print(f"[INFO] Issue já existe: {title}")
            continue

        # Criar issue
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
