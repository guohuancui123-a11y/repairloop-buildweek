# Release Notes Draft

## v0.2.0 - First Public PyPI Release

RepairLoop is now published on PyPI as `repairloop`.

### Highlights

- Published installable packages to PyPI.
- Added `repair-loop` as the console command for normal installs.
- Confirmed `pip install repairloop==0.2.0` works from a clean environment.
- Updated public project positioning under the RepairLoop name.
- Added technical overview and benchmark planning docs.

### Install

```powershell
python -m pip install repairloop
```

### Verified

```text
python -m build
twine check dist/*
pip install repairloop==0.2.0
repair-loop --help
```

## v0.1.2 - JSON Reports for Automation

This release makes RepairLoop easier to use from CI, scripts, and other agent runtimes by adding structured JSON output.

### Highlights

- Added `--json-report` to `run`.
- Added `--json-report` to `repair`.
- Reports include command result, blocking error, suggested fix, preview/apply state, and verification status.
- Human logs are suppressed in JSON mode so output is parseable.
- Test coverage increased from `23 passed` to `25 passed`.

### Why This Matters

The original CLI was human-readable. That is useful for a terminal demo, but less mature for automation. JSON reports make RepairLoop usable as a local repair primitive inside CI jobs, scripts, launchers, and agent systems that need to inspect structured outcomes.

### Verified

```text
python -m pytest -q
25 passed
```

```text
python -m repair_loop run --json-report -- python -c "print('json-ok')"
```

```text
python -m repair_loop repair --json-report -- python demo/missing_file.py
```

## v0.1.1 - First-run CLI Polish

This release upgrades the original v0.1 prototype with fixes found by testing RepairLoop from a normal user/browser perspective.

### Highlights

- Invalid repair options now return friendly CLI errors instead of Python tracebacks.
- Dry-run repair output now clearly marks preview mode with `[PREVIEW] no changes were made`.
- Missing or mistyped target commands are classified as `command_start_error`.
- Command startup failures now include practical PATH and `--` usage guidance.
- README examples were synced with real command output so first-time users see what the docs promise.
- Test coverage increased from `19 passed` to `23 passed`.

### Why This Matters

v0.1 proved the core loop: run broken Python, detect the real failure, apply a small local repair, and verify by rerunning.

v0.1.1 makes that loop feel safer for first-time users. The tool now explains when it is only previewing, avoids scary tracebacks for bad CLI input, and gives clearer guidance when the target command cannot even start.

### Verified

```text
python -m pytest -q
23 passed
```

```text
python -m repair_loop repair -- python demo\missing_file.py
[PREVIEW] no changes were made; rerun with --apply to execute this fix
[VERIFY] not rerun; preview mode only
```

```text
python -m repair_loop repair --apply --max-iterations 2 -- python demo\missing_file.py
[VERIFY] success
```

```text
python -m repair_loop run -- definitely-not-a-real-command-for-RepairLoop-tests
[FIX] command_start_error
[FIX] The target command could not be started.
```

### Still Honest About Limits

- Unknown runtime errors still get conservative guidance only.
- The base engine remains rule-driven and local-first, not a general AI coding agent.
- Broader repair coverage and rollback restore UX are still roadmap items.

## v0.1.0 - Local-first Repair Prototype

RepairLoop is now a runnable local-first Python runtime repair engine.

### Highlights

- CLI entry via `python -m repair_loop`.
- `run` captures stdout, stderr, and exit code.
- `repair` performs RUN → OBSERVE → FIX → APPLY → VERIFY loop.
- Base engine works without external AI APIs or API keys.
- Core logic moved under `repair_loop/core/`.
- Optional `repair_loop/ai/` layer exists but is disabled by default.
- `ModuleNotFoundError` generates pip install suggestions/commands.
- `FileNotFoundError` can safely create missing files/directories.
- `SyntaxError: expected ':'` can apply a narrow missing-colon patch with rollback backup.
- Flask/Werkzeug compatibility errors can suggest compatible Werkzeug downgrade.
- SQLite open errors can create missing local data directories.
- SQLite missing `users` table can create a minimal smoke-test schema.
- Rollback metadata is written under `.repairloop/rollback/` for file edits.
- Demo scripts in `demo/broken_import.py`, `demo/missing_file.py`, and `demo/broken_syntax.py`.
- Productized README with local-first positioning.
- MIT license added.

### Verified

```text
python -m pytest -q
19 passed
```

```text
python -m repair_loop repair --apply --max-iterations 4 -- python smoke_test.py
[VERIFY] success
```

```text
python -m repair_loop repair --apply --max-iterations 2 -- python demo\missing_file.py
[VERIFY] success
```

```text
python -m repair_loop repair --apply --max-iterations 2 -- python demo\broken_syntax.py
[VERIFY] success
```

### Not Yet Done

- No commit or GitHub push yet.
- No GIF/video asset yet.
- More SyntaxError templates are roadmap only.
- TypeError / IndexError guards are roadmap only.
