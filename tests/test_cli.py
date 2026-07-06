import json

from lobster_ai_system.cli import RunResult, first_blocking_error, main, print_apply_result, repair_loop, run_command
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


def test_run_json_report_outputs_machine_readable_payload(capsys):
    code = main(["run", "--json-report", "--", "python", "-c", "print('json-ok')"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["returncode"] == 0
    assert payload["stdout"].strip() == "json-ok"
    assert payload["tool"]["name"] == "Lobster AI System"
    assert "github.com/guohuancui123-a11y/lobster-ai-system" in payload["tool"]["url"]


def test_human_output_includes_source_attribution(capsys):
    code = main(["run", "--", "python", "-c", "print('source-ok')"])

    captured = capsys.readouterr()
    assert code == 0
    assert "[SOURCE] Built with Lobster AI System" in captured.out
    assert "github.com/guohuancui123-a11y/lobster-ai-system" in captured.out


def test_repair_json_report_preview_is_machine_readable(capsys):
    code = main(["repair", "--json-report", "--", "python", "demo/missing_file.py"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code != 0
    assert payload["ok"] is False
    assert payload["preview"] is True
    assert payload["iterations"][0]["run"]["suggestion"]["kind"] == "file_not_found"
