from lobster_ai_system.fix_engine import ErrorKind, classify_error, suggest_fix


def test_classify_module_not_found():
    error = "ModuleNotFoundError: No module named 'requests'"
    assert classify_error(error) == ErrorKind.MODULE_NOT_FOUND


def test_suggest_module_install_command():
    suggestion = suggest_fix("ModuleNotFoundError: No module named 'yaml'")
    assert suggestion.kind == ErrorKind.MODULE_NOT_FOUND
    assert suggestion.commands == ["python -m pip install yaml"]


def test_classify_syntax_error():
    assert classify_error("SyntaxError: invalid syntax") == ErrorKind.SYNTAX_ERROR


def test_command_start_error_gives_cli_guidance():
    suggestion = suggest_fix("Could not start command: [WinError 2] system cannot find the file")

    assert suggestion.kind == ErrorKind.COMMAND_START_ERROR
    assert "could not be started" in suggestion.summary
    assert any("PATH" in note for note in suggestion.notes)


def test_classify_file_not_found():
    assert classify_error("FileNotFoundError: [Errno 2] No such file or directory: 'config.json'") == ErrorKind.FILE_NOT_FOUND


def test_file_not_found_suggests_create_path_action():
    suggestion = suggest_fix("FileNotFoundError: [Errno 2] No such file or directory: 'config.json'")
    assert suggestion.kind == ErrorKind.FILE_NOT_FOUND
    assert suggestion.actions == ["create_path:config.json"]


def test_syntax_error_missing_colon_suggests_local_action():
    error = '  File "demo.py", line 1\n    def main()\n              ^\nSyntaxError: expected \':\''
    suggestion = suggest_fix(error)
    assert suggestion.kind == ErrorKind.SYNTAX_ERROR
    assert suggestion.actions == ["append_missing_colon:demo.py:1"]


def test_import_error_werkzeug_url_quote_suggests_compatible_downgrade():
    error = "ImportError: cannot import name 'url_quote' from 'werkzeug.urls'"
    suggestion = suggest_fix(error)
    assert suggestion.kind == ErrorKind.IMPORT_ERROR
    assert suggestion.commands == ['python -m pip install "Werkzeug<2.1"']


def test_type_error_flask_werkzeug_test_client_suggests_compatible_downgrade():
    error = "TypeError: EnvironBuilder.__init__() got an unexpected keyword argument 'as_tuple'"
    suggestion = suggest_fix(error)
    assert suggestion.kind == ErrorKind.IMPORT_ERROR
    assert suggestion.commands == ['python -m pip install "Werkzeug<2.1"']


def test_sqlite_open_error_suggests_data_directory_creation():
    error = "sqlite3.OperationalError: unable to open database file"
    suggestion = suggest_fix(error)
    assert suggestion.kind == ErrorKind.SQLITE_OPEN_ERROR
    assert suggestion.actions == ["create_path:data"]


def test_sqlite_missing_users_table_suggests_schema_action():
    error = "sqlite3.OperationalError: no such table: users"
    suggestion = suggest_fix(error)
    assert suggestion.kind == ErrorKind.SQLITE_MISSING_TABLE
    assert suggestion.actions == ["sqlite_create_users_table"]
