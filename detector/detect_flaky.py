import os
import subprocess
import argparse
import json
import xml.etree.ElementTree as ET


def run_pytest_iteration(iteration_id: int) -> str:
    filename = f"tmp_{iteration_id}.xml"
    cmd = ["pytest", f"--junitxml={filename}"]
    
    print(f"Executing run #{iteration_id}...")
    # capture_output=True esconde o log do pytest no terminal para não poluir
    subprocess.run(cmd, capture_output=True, text=True)
    
    return filename


def parse_junit_xml(path: str) -> dict:
    if not os.path.exists(path):
        return {}

    tree = ET.parse(path)
    root = tree.getroot()
    results = {}

    for testcase in root.iter('testcase'):
        # Reconstrói o nome do teste
        classname = testcase.get('classname')
        name = testcase.get('name')

        if classname:
            test_id = f"{classname}::{name}"
        else:
            test_id = name        
        status = "passed"
        if testcase.find('failure') is not None or testcase.find('error') is not None:
            status = "failed"
        elif testcase.find('skipped') is not None:
            status = "skipped"
            
        results[test_id] = status

    return results


def aggregate_results(list_of_runs: list) -> dict:
    consolidated = {}

    for run_data in list_of_runs:
        for test_name, status in run_data.items():
            if test_name not in consolidated:
                consolidated[test_name] = {"runs": []}
            consolidated[test_name]["runs"].append(status)

    final_data = {}
    
    for test_name, data in consolidated.items():
        runs = data["runs"]
        pass_count = runs.count("passed")
        fail_count = runs.count("failed")
        
        is_flaky = (pass_count > 0) and (fail_count > 0)

        final_data[test_name] = {
            "runs": runs,
            "is_flaky": is_flaky,
            "pass_count": pass_count,
            "fail_count": fail_count
        }

    return {"tests": final_data}


def save_report(data, path="flaky_report.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Report saved to {path}")


parser = argparse.ArgumentParser()
parser.add_argument("--reruns", type=int, default=3, help="Number of times to run tests")
args = parser.parse_args()

list_of_runs = []
temp_files = []

for i in range(1, args.reruns + 1):
    xml_file = run_pytest_iteration(i)
    temp_files.append(xml_file)
    
    run_result = parse_junit_xml(xml_file)
    list_of_runs.append(run_result)

aggregated_data = aggregate_results(list_of_runs)

save_report(aggregated_data)

# Limpeza: remover arquivos tmp
for f in temp_files:
    if os.path.exists(f):
        os.remove(f)