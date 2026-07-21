import json
import subprocess
import sys
from pathlib import Path

from repair_loop.benchmark import discover_cases, run_benchmarks


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"


def test_discover_cases_finds_three_deterministic_cases():
    cases = discover_cases(BENCHMARKS)

    assert [case.case_id for case in cases] == [
        "file-not-found/missing-config",
        "sqlite/missing-users-table",
        "syntax/missing-colon",
    ]
    assert all(case.command[0] == "{python}" for case in cases)


def test_benchmark_runner_verifies_all_seed_cases():
    report = run_benchmarks(BENCHMARKS)

    assert report["schema_version"] == "1.0"
    assert report["summary"] == {"total": 3, "passed": 3, "failed": 0, "verified": 3}
    assert all(case["passed"] and case["verified"] for case in report["cases"])
    assert all(case["repair_time_ms"] >= 0 for case in report["cases"])


def test_benchmark_cli_emits_machine_readable_report():
    completed = subprocess.run(
        [sys.executable, "-m", "repair_loop", "benchmark", "--cases-dir", str(BENCHMARKS), "--json-report"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    payload = json.loads(completed.stdout)
    assert completed.returncode == 0
    assert payload["summary"]["passed"] == 3


def test_module_mode_propagates_failed_target_exit_code():
    completed = subprocess.run(
        [sys.executable, "-m", "repair_loop", "run", "--", sys.executable, "-c", "import sys; sys.exit(7)"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 7
