from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence

from .core.apply_engine import ApplyResult, apply_suggestion
from .core.fix_engine import FixSuggestion, suggest_fix
from .metadata import ATTRIBUTION, PROJECT_NAME, PROJECT_URL


@dataclass(slots=True)
class RunResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def first_blocking_error(result: RunResult) -> str | None:
    if result.ok:
        return None
    text = result.stderr or result.stdout
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return f"Process exited with code {result.returncode} without output."
    for line in reversed(lines):
        stripped = line.strip()
        if "Error" in stripped or "Exception" in stripped or "Traceback" in stripped:
            return stripped
    return lines[-1].strip()


def blocking_error_context(result: RunResult) -> str | None:
    if result.ok:
        return None
    text = (result.stderr or result.stdout).strip()
    return text or f"Process exited with code {result.returncode} without output."


def run_command(command: Sequence[str]) -> RunResult:
    try:
        completed = subprocess.run(
            list(command),
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        return RunResult(
            command=list(command),
            returncode=127,
            stdout="",
            stderr=f"Could not start command: {error}",
        )
    return RunResult(
        command=list(command),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def print_suggestion(suggestion: FixSuggestion) -> None:
    print("[FIX]", suggestion.kind.value)
    print("[FIX]", suggestion.summary)
    if suggestion.commands:
        print("[FIX] commands:")
        for command in suggestion.commands:
            print("  -", command)
    if suggestion.actions:
        print("[FIX] actions:")
        for action in suggestion.actions:
            print("  -", action)
    if suggestion.notes:
        print("[FIX] notes:")
        for note in suggestion.notes:
            print("  -", note)


def print_apply_result(result: ApplyResult) -> None:
    if result.command:
        print("\n[APPLY]", result.command)
    else:
        print("\n[APPLY]")
    print("[APPLY] attempted:", result.attempted)
    print("[APPLY] ok:", result.ok)
    if not result.attempted and result.reason and "apply disabled" in result.reason:
        print("[PREVIEW] no changes were made; rerun with --apply to execute this fix")
    if result.reason:
        print("[APPLY] reason:", result.reason)
    if result.stdout:
        print("[APPLY stdout]")
        print(result.stdout.rstrip())
    if result.stderr:
        print("[APPLY stderr]")
        print(result.stderr.rstrip())


def print_attribution() -> None:
    print("[SOURCE]", ATTRIBUTION)


def print_result(result: RunResult) -> None:
    print_attribution()
    print("[RUN]", " ".join(result.command))
    print("[EXIT]", result.returncode)
    if result.stdout:
        print("\n[STDOUT]")
        print(result.stdout.rstrip())
    if result.stderr:
        print("\n[STDERR]")
        print(result.stderr.rstrip())
    if not result.ok:
        error = first_blocking_error(result)
        print("\n[ERROR]", error)
        suggestion = suggest_fix(blocking_error_context(result))
        print_suggestion(suggestion)
    print("\n[SUCCESS]" if result.ok else "\n[FAILED]")


def result_payload(result: RunResult) -> dict[str, object]:
    error = first_blocking_error(result)
    suggestion = suggest_fix(blocking_error_context(result)) if not result.ok else None
    return {
        "tool": {
            "name": PROJECT_NAME,
            "url": PROJECT_URL,
            "attribution": ATTRIBUTION,
        },
        "command": result.command,
        "returncode": result.returncode,
        "ok": result.ok,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "error": error,
        "suggestion": None
        if suggestion is None
        else {
            "kind": suggestion.kind.value,
            "summary": suggestion.summary,
            "commands": suggestion.commands,
            "actions": suggestion.actions or [],
            "notes": suggestion.notes,
        },
    }


def apply_payload(result: ApplyResult) -> dict[str, object]:
    return {
        "attempted": result.attempted,
        "ok": result.ok,
        "command": result.command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "reason": result.reason,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lobster-ai",
        description="Local-first automatic code repair helper for Python runtime errors.",
    )
    subparsers = parser.add_subparsers(dest="command_name")

    run_parser = subparsers.add_parser("run", help="Run a target command and capture output.")
    run_parser.add_argument("--json-report", action="store_true", help="Print a machine-readable JSON report.")
    run_parser.add_argument("target", nargs=argparse.REMAINDER, help="Command to execute. Use -- before the target command.")

    repair_parser = subparsers.add_parser("repair", help="Run, suggest a fix, optionally apply it, and rerun.")
    repair_parser.add_argument("--apply", action="store_true", help="Execute safe automatic fix commands.")
    repair_parser.add_argument("--json-report", action="store_true", help="Print a machine-readable JSON report.")
    repair_parser.add_argument("--max-iterations", type=int, default=2, help="Maximum repair iterations.")
    repair_parser.add_argument("target", nargs=argparse.REMAINDER, help="Command to execute. Use -- before the target command.")

    return parser


def normalize_target(raw_target: Sequence[str], parser: argparse.ArgumentParser, command_name: str) -> list[str]:
    target = list(raw_target)
    if target and target[0] == "--":
        target = target[1:]
    if not target:
        parser.error(f"{command_name} requires a target command")
    return target


def repair_loop(target: Sequence[str], *, apply: bool, max_iterations: int, json_report: bool = False) -> int:
    if max_iterations < 1:
        if json_report:
            print(json.dumps({"ok": False, "error": "--max-iterations must be at least 1"}, indent=2))
        else:
            print("[ERROR] --max-iterations must be at least 1", file=sys.stderr)
        return 2

    last_result: RunResult | None = None
    iterations: list[dict[str, object]] = []
    for iteration in range(1, max_iterations + 1):
        result = run_command(target)
        last_result = result
        iteration_payload: dict[str, object] = {"iteration": iteration, "run": result_payload(result)}
        if not json_report:
            print(f"\n[ITERATION {iteration}]")
            print_result(result)
        if result.ok:
            iterations.append(iteration_payload)
            if json_report:
                print(json.dumps({"ok": True, "verified": True, "iterations": iterations}, indent=2))
            else:
                print("\n[VERIFY] success")
                print_attribution()
            return 0

        error = blocking_error_context(result)
        suggestion = suggest_fix(error)
        apply_result = apply_suggestion(suggestion, enabled=apply)
        iteration_payload["apply"] = apply_payload(apply_result)
        iterations.append(iteration_payload)
        if not json_report:
            print_apply_result(apply_result)
        if not apply_result.ok:
            if json_report:
                print(json.dumps({"ok": False, "verified": False, "preview": not apply, "iterations": iterations}, indent=2))
            else:
                if not apply and not apply_result.attempted:
                    print("\n[VERIFY] not rerun; preview mode only")
                else:
                    print("\n[VERIFY] not rerun; apply step did not complete")
            return result.returncode

    if json_report:
        print(json.dumps({"ok": False, "verified": False, "reason": "iteration limit reached", "iterations": iterations}, indent=2))
    else:
        print("\n[VERIFY] failed; iteration limit reached")
    return last_result.returncode if last_result else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command_name == "run":
        target = normalize_target(args.target, parser, "run")
        result = run_command(target)
        if args.json_report:
            print(json.dumps(result_payload(result), indent=2))
        else:
            print_result(result)
        return result.returncode

    if args.command_name == "repair":
        target = normalize_target(args.target, parser, "repair")
        return repair_loop(target, apply=args.apply, max_iterations=args.max_iterations, json_report=args.json_report)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
