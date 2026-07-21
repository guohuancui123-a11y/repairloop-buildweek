from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BENCHMARK_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    case_id: str
    path: Path
    command: list[str]
    expected_error_kind: str
    expected_verified: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"could not read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def discover_cases(cases_dir: Path) -> list[BenchmarkCase]:
    if not cases_dir.exists():
        raise ValueError(f"benchmark cases directory does not exist: {cases_dir}")

    cases: list[BenchmarkCase] = []
    for manifest_path in sorted(cases_dir.rglob("expected.json")):
        case_dir = manifest_path.parent
        before_dir = case_dir / "before"
        command_path = case_dir / "command.txt"
        if not before_dir.is_dir():
            raise ValueError(f"benchmark case is missing before/: {case_dir}")
        if not command_path.is_file():
            raise ValueError(f"benchmark case is missing command.txt: {case_dir}")

        expected = _load_json(manifest_path)
        case_id = str(expected.get("case") or case_dir.relative_to(cases_dir).as_posix())
        expected_error_kind = expected.get("expected_error_kind")
        expected_verified = expected.get("expected_verified")
        if not isinstance(expected_error_kind, str) or not expected_error_kind:
            raise ValueError(f"benchmark case must define expected_error_kind: {case_dir}")
        if not isinstance(expected_verified, bool):
            raise ValueError(f"benchmark case must define boolean expected_verified: {case_dir}")

        command = command_path.read_text(encoding="utf-8").strip().split()
        if not command:
            raise ValueError(f"benchmark command is empty: {command_path}")
        cases.append(
            BenchmarkCase(
                case_id=case_id,
                path=case_dir,
                command=command,
                expected_error_kind=expected_error_kind,
                expected_verified=expected_verified,
            )
        )
    if not cases:
        raise ValueError(f"no expected.json benchmark manifests found in: {cases_dir}")
    return cases


def _file_snapshot(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".repairloop" not in path.parts
    }


def _target_command(command: list[str]) -> list[str]:
    return [sys.executable if token == "{python}" else token for token in command]


def _run_case(case: BenchmarkCase, source_root: Path) -> dict[str, Any]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="repair-loop-benchmark-") as temporary_dir:
        workspace = Path(temporary_dir) / "workspace"
        shutil.copytree(case.path / "before", workspace)
        before_snapshot = _file_snapshot(workspace)
        environment = os.environ.copy()
        python_path = str(source_root)
        if environment.get("PYTHONPATH"):
            python_path = python_path + os.pathsep + environment["PYTHONPATH"]
        environment["PYTHONPATH"] = python_path
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "repair_loop",
                "repair",
                "--apply",
                "--json-report",
                "--",
                *_target_command(case.command),
            ],
            cwd=workspace,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        after_snapshot = _file_snapshot(workspace)

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        return {
            "case": case.case_id,
            "passed": False,
            "verified": False,
            "error": f"RepairLoop did not emit a JSON report: {error}",
            "returncode": completed.returncode,
            "stderr": completed.stderr,
            "repair_time_ms": elapsed_ms,
        }

    iterations = payload.get("iterations") or []
    first_run = iterations[0].get("run", {}) if iterations else {}
    suggestion = first_run.get("suggestion") or {}
    actual_error_kind = suggestion.get("kind")
    verified = payload.get("verified") is True
    created = sorted(str(path) for path in after_snapshot.keys() - before_snapshot.keys())
    modified = sorted(
        str(path)
        for path in before_snapshot.keys() & after_snapshot.keys()
        if before_snapshot[path] != after_snapshot[path]
    )
    passed = actual_error_kind == case.expected_error_kind and verified == case.expected_verified
    return {
        "case": case.case_id,
        "passed": passed,
        "verified": verified,
        "expected": {
            "error_kind": case.expected_error_kind,
            "verified": case.expected_verified,
        },
        "observed": {
            "error_kind": actual_error_kind,
            "returncode": completed.returncode,
        },
        "repair_time_ms": elapsed_ms,
        "patch_size": {
            "files_created": len(created),
            "files_modified": len(modified),
            "created": created,
            "modified": modified,
        },
    }


def run_benchmarks(cases_dir: Path) -> dict[str, Any]:
    source_root = Path(__file__).resolve().parent.parent
    results = [_run_case(case, source_root) for case in discover_cases(cases_dir)]
    passed = sum(result["passed"] for result in results)
    verified = sum(result["verified"] for result in results)
    return {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "verified": verified,
        },
        "cases": results,
    }
