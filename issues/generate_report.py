import json
import argparse
from datetime import datetime


def load_report(path):
    with open(path, "r") as f:
        return json.load(f)


def generate_html(report_path="flaky_report.json", out_path="report.html"):
    data = load_report(report_path)

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Flaky Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #eee; }
        .flaky { background: #ffb3b3; }
        .stable { background: #b3ffb3; }
    </style>
</head>
<body>
    <h1>Relatório de Testes Flaky</h1>
    <p>Gerado em: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>

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

    for test_name, info in data["tests"].items():

        fails = info["fail_count"]
        passes = info["pass_count"]
        total = fails + passes

        fail_rate = (fails / total) * 100 if total > 0 else 0
        is_flaky = info["is_flaky"]

        row_class = "flaky" if is_flaky else "stable"

        html += f"""
        <tr class="{row_class}">
            <td>{test_name}</td>
            <td>{passes}</td>
            <td>{fails}</td>
            <td>{info["runs"]}</td>
            <td>{fail_rate:.1f}%</td>
            <td>{"Flaky" if is_flaky else "Estável"}</td>
        </tr>
"""

    html += """
    </table>
</body>
</html>
"""

    with open(out_path, "w") as f:
        f.write(html)

    print(f"Relatório gerado em: {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="flaky_report.json")
    parser.add_argument("--out", default="report.html")
    args = parser.parse_args()

    generate_html(args.report, args.out)


if __name__ == "__main__":
    main()
