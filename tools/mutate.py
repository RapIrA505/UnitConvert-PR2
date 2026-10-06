"""Automatically mutate an isolated copy of core.py with Cosmic Ray."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import toml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("initial", "improved"))
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "mutation_work" / args.stage
    destination.mkdir(parents=True, exist_ok=True)
    original_hash = hashlib.sha256((ROOT / "core.py").read_bytes()).hexdigest()
    shutil.copy2(ROOT / "core.py", destination / "core.py")
    shutil.copy2(ROOT / "pytest.ini", destination / "pytest.ini")
    shutil.copy2(ROOT / "tools/runtime_compat/sitecustomize.py", destination / "sitecustomize.py")
    suites = ["tests_initial"] + (["tests_improved"] if args.stage == "improved" else [])
    for suite in suites:
        shutil.copytree(ROOT / suite, destination / suite, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
    configuration = {"cosmic-ray": {
        "module-path": "core.py", "timeout": 20.0, "excluded-modules": [],
        "test-command": f'"{Path(sys.executable).as_posix()}" -m pytest {" ".join(suites)} -q -x',
        "distributor": {"name": "local"}}}
    config = destination / "cosmic-ray.toml"
    config.write_text(toml.dumps(configuration), encoding="utf-8")
    database = output / f"mutations_{args.stage}.sqlite"
    if database.exists():
        raise FileExistsError(f"Preserving previous evidence: {database}")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=str(ROOT / "tools/runtime_compat"))
    for command, tail in (("baseline", [str(config)]),
                          ("init", [str(config), str(database)]),
                          ("exec", [str(config), str(database)])):
        with (output / f"mutations_{args.stage}_{command}.log").open("w", encoding="utf-8") as log:
            completed = subprocess.run([sys.executable, "-c", "import sys; from cosmic_ray.cli import main; sys.exit(main())",
                                        command, *tail], cwd=destination, env=env, stdout=log, stderr=log)
        if completed.returncode:
            raise RuntimeError(f"Cosmic Ray {command} failed. See log.")
    from cosmic_ray.work_db import WorkDB, use_db
    with use_db(database, WorkDB.Mode.open) as work:
        records = []
        for item, result in work.completed_work_items:
            mutation = item.mutations[0]
            records.append({"id": item.job_id, "operator": mutation.operator_name,
                            "line": mutation.start_pos[0], "occurrence": mutation.occurrence,
                            "outcome": result.test_outcome.value if result.test_outcome else None,
                            "worker": result.worker_outcome.value, "diff": result.diff,
                            "output": result.output})
        counts = {key: sum(row["outcome"] == key for row in records)
                  for key in ("killed", "survived", "incompetent")}
        report = {"stage": args.stage, "total": work.num_work_items, "completed": len(records),
                  **counts, "core_sha256": original_hash,
                  "initial_tests_sha256": hashlib.sha256((destination / "tests_initial/test_core.py").read_bytes()).hexdigest(),
                  "mutation_score_percent": 100 * counts["killed"] / len(records),
                  "survivors": [r for r in records if r["outcome"] == "survived"]}
    (output / f"mutations_{args.stage}_all.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / f"mutations_{args.stage}_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if hashlib.sha256((ROOT / "core.py").read_bytes()).hexdigest() != original_hash:
        raise RuntimeError("Production core.py was modified unexpectedly")
    print(json.dumps({key: value for key, value in report.items() if key != "survivors"}, indent=2))


if __name__ == "__main__":
    main()
