# Launch Drafts

## Hacker News

Title:

```text
Show HN: RepairLoop – a local-first Python tool that repairs failed commands and verifies fixes
```

Post:

```text
Hi HN,

I built RepairLoop because I kept running into small Python failures that did not need a full AI coding agent: missing files, startup errors, CLI mistakes, simple runtime failures.

RepairLoop starts from the failing command. It captures the real error, proposes a minimal local repair, applies it only when explicitly requested, and reruns the same command to verify the result.

The loop is:

Run → Capture → Repair → Verify

The core is local-first:

- no cloud dependency
- no API key required
- no source upload
- dry-run by default
- explicit `--apply` for changes
- JSON reports for CI / automation / agent workflows

The goal is not to replace coding assistants. It is to provide a small, inspectable repair primitive for Python runtime failures where the important question is: can the program run again?

Demo GIF and release are in the repo.

I would love feedback on which Python failure modes would be most useful to support next.
```

## Reddit r/Python

Title:

```text
I built RepairLoop, a local-first tool that repairs failed Python commands and verifies the fix
```

Post:

```text
I built RepairLoop as a small local-first repair loop for Python runtime failures.

Instead of starting with a prompt, it starts with a failing command:

1. run the command
2. capture the real error
3. suggest a minimal repair
4. apply only with `--apply`
5. rerun the same command to verify the fix

Example:

```powershell
repair-loop repair -- python demo/missing_file.py
repair-loop repair --apply -- python demo/missing_file.py
```

The core does not require a cloud service, API key, or source upload. It is dry-run by default and can emit JSON reports for automation.

Current supported repair patterns include missing files/paths, missing modules, command startup failures, simple syntax fixes, and a few SQLite/Flask runtime cases.

Repo: https://github.com/guohuancui123-a11y/repairloop

I would appreciate feedback from Python developers: what runtime failure would you want a tool like this to repair safely?
```

## Reddit r/devops

Title:

```text
RepairLoop: local-first Python command repair with JSON reports and verification
```

Post:

```text
I built RepairLoop as a small repair primitive for failed Python commands in local workflows, CI, and automation.

It follows:

Run → Capture → Repair → Verify

The useful part for automation is that it can emit JSON reports and verifies repairs by rerunning the original command. Changes are dry-run by default and require explicit `--apply`.

It is not a black-box coding agent. The goal is narrower: detect known runtime failure modes, propose minimal repairs, and prove whether the command runs again.

Repo: https://github.com/guohuancui123-a11y/repairloop

I am interested in feedback on CI/dev workflow failure modes that are safe enough for a local repair loop.
```
