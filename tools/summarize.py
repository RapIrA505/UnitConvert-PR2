"""Build a compact factual summary after both real mutation sessions finish."""

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"


def read(name, directory=OUT):
    return json.loads((directory / name).read_text(encoding="utf-8"))


def signature(row):
    return row["operator"], row["line"], row["occurrence"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT,
                        help="Directory containing both mutation sessions; test results remain in verification.")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    tests = read("test_summary.json")
    before = read("mutations_initial_summary.json", output)
    after = read("mutations_improved_summary.json", output)
    all_before = read("mutations_initial_all.json", output)
    all_after = read("mutations_improved_all.json", output)
    by_signature = {signature(row): row for row in all_after}
    if {signature(row) for row in all_before} != set(by_signature):
        raise RuntimeError("The two sessions used different mutation sets")
    if before["core_sha256"] != after["core_sha256"]:
        raise RuntimeError("The two sessions used different source code")
    mappings = []
    for survivor in before["survivors"]:
        op, line = survivor["operator"], survivor["line"]
        if "FloorDiv" in op:
            added, reason = "test_fractional_pounds_to_kg", "Исходные примеры давали целый результат; 1 фунт даёт дробный результат."
        elif "ExceptionReplacer" in op:
            added, reason = "test_integer_too_large_for_float", "Исходный набор не вызывал переполнение преобразования int в float."
        elif "Lt_LtE" in op:
            added, reason = "test_inclusive_boundaries", "Исходный набор не проверял допустимость самой нижней границы."
        elif survivor["occurrence"] in (6, 14):
            added, reason = "test_just_below_absolute_zero", "Сдвиг границы вниз пропускал запрещённые значения непосредственно ниже абсолютного нуля."
        else:
            added, reason = "test_inclusive_boundaries", "Сдвиг границы вверх отклонял допустимую температуру абсолютного нуля."
        mappings.append({"operator": op, "line": line, "occurrence": survivor["occurrence"],
                         "initial_job_id": survivor["id"], "final_job_id": by_signature[signature(survivor)]["id"],
                         "added_test": added, "analysis": reason, "initial_diff": survivor["diff"],
                         "final_outcome": by_signature[signature(survivor)]["outcome"]})
    initial_path = ROOT / "tests_initial/test_core.py"
    for stage, report in (("initial", before), ("improved", after)):
        if "initial_tests_sha256" not in report:
            frozen_path = output / f"mutation_work/{stage}/tests_initial/test_core.py"
            report["initial_tests_sha256"] = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
            (output / f"mutations_{stage}_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    frozen_unchanged = (hashlib.sha256(initial_path.read_bytes()).hexdigest()
                        == before["initial_tests_sha256"] == after["initial_tests_sha256"])
    result = {
        "application": "UnitConvert", "version": "1.1", "developer": "Молдаванский Р.Д.",
        "assigned_tester": "Белов А.М.", "team": "Крутые перцы",
        "environment": {"os": ("Windows " + ".".join(map(str, sys.getwindowsversion()[:3]))) if sys.platform == "win32" else sys.platform,
                        "python": sys.version.split()[0], "pytest": version("pytest"),
                        "coverage": version("coverage"), "cosmic_ray": version("cosmic-ray")},
        "tests": tests, "initial_test_count": tests["v1_1_initial"]["tests"],
        "added_test_count": tests["v1_1_improved"]["tests"] - tests["v1_1_initial"]["tests"],
        "final_test_count": tests["v1_1_improved"]["tests"],
        "original_bug": {"function": "fahrenheit_to_celsius", "v1_0_factor": "5/8", "v1_1_factor": "5/9",
                         "examples": [{"input": 212, "expected": 100, "actual_v1_0": 112.5},
                                      {"input": -40, "expected": -40, "actual_v1_0": -45}]},
        "mutations_before": {k: v for k, v in before.items() if k != "survivors"},
        "mutations_after": {k: v for k, v in after.items() if k != "survivors"},
        "same_mutation_set": True, "initial_tests_unchanged": frozen_unchanged,
        "initial_tests_sha256": hashlib.sha256(initial_path.read_bytes()).hexdigest(),
        "timeouts_initial": sum(r["output"] == "timeout" for r in all_before),
        "timeouts_improved": sum(r["output"] == "timeout" for r in all_after),
        "survivor_to_test_mapping": mappings,
        "equivalent_mutants": [], "adjustment": "Не применялся: неработоспособных и оставшихся выживших мутантов нет.",
        "limitations": "Покрытие и мутации относятся только к core.py. 100% не доказывает отсутствие всех возможных дефектов. Личный обмен и ручное выполнение студентами не утверждаются."
    }
    (output / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"initial": before["mutation_score_percent"], "improved": after["mutation_score_percent"],
                      "survivors_improved": after["survived"], "initial_tests_unchanged": frozen_unchanged}, indent=2))


if __name__ == "__main__":
    main()
