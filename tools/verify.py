"""Reproduce tests and branch coverage, retaining the evidence as files."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"


def run(arguments, cwd, log):
    environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=str(ROOT / "tools/runtime_compat"))
    result = subprocess.run([sys.executable, *arguments], cwd=cwd, env=environment,
                            capture_output=True, text=True, encoding="utf-8")
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    return result.returncode


def junit_summary(path):
    suites = ET.parse(path).getroot()
    return {key: sum(int(suite.get(key, 0)) for suite in suites)
            for key in ("tests", "failures", "errors", "skipped")}


def main():
    OUT.mkdir(exist_ok=True)
    old = OUT / "mutation_work" / "v1_0_tests"
    old.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "versions/v1_0/core.py", old / "core.py")
    shutil.copytree(ROOT / "tests_initial", old / "tests_initial", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "pytest.ini", old / "pytest.ini")
    code = run(["-m", "pytest", "tests_initial", "-q", "--tb=short",
                f"--junitxml={OUT / 'v1_0_initial.xml'}"], old, OUT / "v1_0_initial.log")
    if code != 1:
        raise RuntimeError(f"Expected v1.0 tests to fail, exit status: {code}")
    summary = {"v1_0_initial": junit_summary(OUT / "v1_0_initial.xml")}
    for name, suites in (("initial", ["tests_initial"]),
                         ("improved", ["tests_initial", "tests_improved"])):
        if name == "improved" and not list((ROOT / "tests_improved").glob("test_*.py")):
            continue
        code = run(["-m", "coverage", "run", "--branch", "--source=core", "-m", "pytest",
                    *suites, "-q", f"--junitxml={OUT / f'v1_1_{name}.xml'}"],
                   ROOT, OUT / f"v1_1_{name}.log")
        if code:
            raise RuntimeError(f"v1.1 {name} tests failed; inspect log")
        run(["-m", "coverage", "json", "-o", str(OUT / f"coverage_{name}.json")],
            ROOT, OUT / f"coverage_{name}_export.log")
        run(["-m", "coverage", "report", "-m"], ROOT, OUT / f"coverage_{name}.log")
        coverage = json.loads((OUT / f"coverage_{name}.json").read_text(encoding="utf-8"))
        summary[f"v1_1_{name}"] = junit_summary(OUT / f"v1_1_{name}.xml")
        summary[f"coverage_{name}"] = coverage["files"]["core.py"]["summary"]
    (OUT / "test_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
