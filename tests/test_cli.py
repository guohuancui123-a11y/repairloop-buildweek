from lobster_ai_system.cli import RunResult, first_blocking_error, print_apply_result, repair_loop, run_command
from lobster_ai_system.core.apply_engine import ApplyResult


def test_first_blocking_error_uses_exception_line():
    result = RunResult(
        command=["python"],
        returncode=1,
        stdout="",
        stderr='Traceback\nModuleNotFoundError: No module named \'x\'\n',
    )
    assert first_blocking_error(result) == "ModuleNotFoundError: No module named 'x'"


def test_first_blocking_error_none_when_ok():
    result = RunResult(command=["python"], returncode=0, stdout="ok", stderr="")
    assert first_blocking_error(result) is None


def test_repair_loop_rejects_invalid_iteration_count(capsys):
    code = repair_loop(["python", "-c", "print('should not run')"], apply=False, max_iterations=0)

    captured = capsys.readouterr()
    assert code == 2
    assert "--max-iterations must be at least 1" in captured.err
    assert "Traceback" not in captured.err


def test_print_apply_result_marks_dry_run_preview(capsys):
    result = ApplyResult(
        attempted=False,
        ok=False,
        command=None,
        stdout="",
        stderr="",
        reason="apply disabled; rerun with --apply to execute safe fix commands",
    )

    print_apply_result(result)

    captured = capsys.readouterr()
    assert "[PREVIEW] no changes were made" in captured.out


def test_run_command_reports_startup_errors_without_traceback():
    result = run_command(["definitely-not-a-real-command-for-lobster-tests"])

    assert result.returncode == 127
    assert "Could not start command" in result.stderr
