from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ErrorKind(StrEnum):
    COMMAND_START_ERROR = "command_start_error"
    MODULE_NOT_FOUND = "module_not_found"
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    FILE_NOT_FOUND = "file_not_found"
    SQLITE_OPEN_ERROR = "sqlite_open_error"
    SQLITE_MISSING_TABLE = "sqlite_missing_table"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class FixSuggestion:
    kind: ErrorKind
    summary: str
    commands: list[str]
    notes: list[str]
    actions: list[str] | None = None


_MODULE_RE = re.compile(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]")
_IMPORT_RE = re.compile(r"ImportError: cannot import name ['\"]([^'\"]+)['\"] from ['\"]([^'\"]+)['\"]")
_FILE_RE = re.compile(r"(?:FileNotFoundError|No such file or directory).*['\"]([^'\"]+)['\"]")
_SYNTAX_LOCATION_RE = re.compile(r'File "([^"]+)", line (\d+)')


def classify_error(error: str | None) -> ErrorKind:
    if not error:
        return ErrorKind.UNKNOWN
    if "Could not start command:" in error:
        return ErrorKind.COMMAND_START_ERROR
    if _MODULE_RE.search(error):
        return ErrorKind.MODULE_NOT_FOUND
    if _IMPORT_RE.search(error):
        return ErrorKind.IMPORT_ERROR
    if "SyntaxError:" in error:
        return ErrorKind.SYNTAX_ERROR
    if "EnvironBuilder.__init__() got an unexpected keyword argument 'as_tuple'" in error:
        return ErrorKind.IMPORT_ERROR
    if "sqlite3.OperationalError: unable to open database file" in error:
        return ErrorKind.SQLITE_OPEN_ERROR
    if "sqlite3.OperationalError: no such table:" in error:
        return ErrorKind.SQLITE_MISSING_TABLE
    if "FileNotFoundError" in error or "No such file or directory" in error:
        return ErrorKind.FILE_NOT_FOUND
    return ErrorKind.UNKNOWN


def _requirement_for_module(module: str) -> str | None:
    requirements = Path("requirements.txt")
    if not requirements.exists():
        return None
    normalized = module.replace("_", "-").lower()
    for raw_line in requirements.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        package_name = re.split(r"[<>=!~;\[]", line, maxsplit=1)[0].strip().lower().replace("_", "-")
        if package_name == normalized:
            return line
    return None


def suggest_fix(error: str | None) -> FixSuggestion:
    kind = classify_error(error)
    if kind == ErrorKind.COMMAND_START_ERROR:
        return FixSuggestion(
            kind=kind,
            summary="The target command could not be started.",
            commands=[],
            notes=[
                "Check that the command is installed and available on PATH.",
                "If the command has arguments, put -- before it, for example: lobster-ai run -- python app.py.",
            ],
        )
    if kind == ErrorKind.MODULE_NOT_FOUND:
        match = _MODULE_RE.search(error or "")
        module = match.group(1) if match else "<module>"
        package = _requirement_for_module(module) or module.split(".")[0].replace("_", "-")
        return FixSuggestion(
            kind=kind,
            summary=f"Missing Python module: {module}",
            commands=[f"python -m pip install {package}"],
            notes=["Verify the package name before installing if the import name differs from the PyPI name."],
        )
    if kind == ErrorKind.IMPORT_ERROR:
        match = _IMPORT_RE.search(error or "")
        symbol = match.group(1) if match else "<symbol>"
        source = match.group(2) if match else "<package>"
        if symbol == "url_quote" and source == "werkzeug.urls":
            return FixSuggestion(
                kind=kind,
                summary="Flask 2.0.x is incompatible with newer Werkzeug releases.",
                commands=["python -m pip install \"Werkzeug<2.1\""],
                notes=["Downgrade Werkzeug to a Flask 2.0 compatible version."],
            )
        if "EnvironBuilder.__init__() got an unexpected keyword argument 'as_tuple'" in (error or ""):
            return FixSuggestion(
                kind=kind,
                summary="Flask 2.0.x test client is incompatible with this Werkzeug version.",
                commands=["python -m pip install \"Werkzeug<2.1\""],
                notes=["Downgrade Werkzeug to a Flask 2.0 compatible version."],
            )
        return FixSuggestion(
            kind=kind,
            summary=f"Import error: cannot import {symbol} from {source}",
            commands=[],
            notes=["Check dependency versions or update the import path."],
        )
    if kind == ErrorKind.SYNTAX_ERROR:
        match = _SYNTAX_LOCATION_RE.search(error or "")
        if "expected ':'" in (error or "") and match:
            file_path, line_number = match.group(1), match.group(2)
            return FixSuggestion(
                kind=kind,
                summary="Python syntax error detected: missing colon.",
                commands=[],
                notes=["Append a colon to the reported line if it is still missing."],
                actions=[f"append_missing_colon:{file_path}:{line_number}"],
            )
        return FixSuggestion(
            kind=kind,
            summary="Python syntax error detected.",
            commands=[],
            notes=["Open the file and line shown in the traceback, then apply the smallest syntax correction."],
        )
    if kind == ErrorKind.FILE_NOT_FOUND:
        match = _FILE_RE.search(error or "")
        missing = match.group(1) if match else "<path>"
        return FixSuggestion(
            kind=kind,
            summary=f"Missing file or path: {missing}",
            commands=[],
            notes=["Create the missing file/path or correct the command/config path."],
            actions=[f"create_path:{missing}"],
        )
    if kind == ErrorKind.SQLITE_OPEN_ERROR:
        return FixSuggestion(
            kind=kind,
            summary="SQLite cannot open the database file. The parent data directory may be missing.",
            commands=[],
            notes=["Create the local data directory before connecting to SQLite."],
            actions=["create_path:data"],
        )
    if kind == ErrorKind.SQLITE_MISSING_TABLE:
        table_match = re.search(r"no such table: ([A-Za-z_][A-Za-z0-9_]*)", error or "")
        table = table_match.group(1) if table_match else "<table>"
        if table == "users":
            return FixSuggestion(
                kind=kind,
                summary="SQLite users table is missing.",
                commands=[],
                notes=["Create a minimal users table and seed user id 1 for local smoke tests."],
                actions=["sqlite_create_users_table"],
            )
        return FixSuggestion(
            kind=kind,
            summary=f"SQLite table is missing: {table}",
            commands=[],
            notes=["Create the missing table schema before querying it."],
        )
    return FixSuggestion(
        kind=kind,
        summary="Unknown blocking error.",
        commands=[],
        notes=["Inspect stderr and fix the first blocking traceback line."],
    )
