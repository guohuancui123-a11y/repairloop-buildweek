from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence

from .core.apply_engine import ApplyResult, apply_suggestion
from .core.fix_engine import FixSuggestion, suggest_fix


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


def print_result(result: RunResult) -> None:
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lobster-ai",
        description="Local-first automatic code repair helper for Python runtime errors.",
    )
    subparsers = parser.add_subparsers(dest="command_name")

    run_parser = subparsers.add_parser("run", help="Run a target command and capture output.")
    run_parser.add_argument("target", nargs=argparse.REMAINDER, help="Command to execute. Use -- before the target command.")

    repair_parser = subparsers.add_parser("repair", help="Run, suggest a fix, optionally apply it, and rerun.")
    repair_parser.add_argument("--apply", action="store_true", help="Execute safe automatic fix commands.")
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


def repair_loop(target: Sequence[str], *, apply: bool, max_iterations: int) -> int:
    if max_iterations < 1:
        print("[ERROR] --max-iterations must be at least 1", file=sys.stderr)
        return 2

    last_result: RunResult | None = None
    for iteration in range(1, max_iterations + 1):
        print(f"\n[ITERATION {iteration}]")
        result = run_command(target)
        last_result = result
        print_result(result)
        if result.ok:
            print("\n[VERIFY] success")
            return 0

        error = blocking_error_context(result)
        suggestion = suggest_fix(error)
        apply_result = apply_suggestion(suggestion, enabled=apply)
        print_apply_result(apply_result)
        if not apply_result.ok:
            if not apply and not apply_result.attempted:
                print("\n[VERIFY] not rerun; preview mode only")
            else:
                print("\n[VERIFY] not rerun; apply step did not complete")
            return result.returncode

    print("\n[VERIFY] failed; iteration limit reached")
    return last_result.returncode if last_result else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command_name == "run":
        target = normalize_target(args.target, parser, "run")
        result = run_command(target)
        print_result(result)
        return result.returncode

    if args.command_name == "repair":
        target = normalize_target(args.target, parser, "repair")
        return repair_loop(target, apply=args.apply, max_iterations=args.max_iterations)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
