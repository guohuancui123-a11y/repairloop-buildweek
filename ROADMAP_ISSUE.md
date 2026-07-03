# Roadmap: from v0.1 repair loop to broader Python runtime fixes

Lobster v0.1 proves the core loop:

```text
RUN → OBSERVE ERROR → FIX → APPLY → VERIFY
```

The next goal is to make the local-first repair engine broader, safer, and easier to trust.

## Near-term priorities

- Improve patch previews before `--apply`.
- Add a rollback restore command for `.lobster/rollback/` records.
- Expand narrow `SyntaxError` repair templates.
- Add conservative guards for selected `TypeError` and `IndexError` patterns.
- Improve dependency repair when import names differ from package names.
- Add more real broken-project demos with before/after logs.
- Keep the base engine fully usable without API keys or cloud services.

## Product principles

- Start from a real failing command, not a prompt.
- Apply the smallest safe repair.
- Verify by rerunning the original command.
- Prefer clear refusal over pretending to fix unknown errors.
- Keep dry-run mode as the default.

## Current status

- `v0.1.1` is live.
- First-run CLI polish is done.
- Current tests: `23 passed`.

Feedback, broken examples, and small reproducible failure cases are welcome.
