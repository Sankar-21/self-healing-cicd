# Labeled pipeline log samples for training the RCA classifier

TRAINING_DATA = [
    # (log_snippet, label)

    # test_failure
    ("FAILED tests/test_main.py::test_root AssertionError", "test_failure"),
    ("FAILED tests/ - 3 failed, 1 passed", "test_failure"),
    ("assert response.status_code == 200 AssertionError", "test_failure"),
    ("pytest FAILED test_health assertion failed", "test_failure"),
    ("E AssertionError: assert 404 == 200", "test_failure"),
    ("FAILED tests/test_main.py - assert False", "test_failure"),
    ("test session starts FAILED collecting errors", "test_failure"),

    # dependency_missing
    ("ModuleNotFoundError: No module named 'fastapi'", "dependency_missing"),
    ("ImportError: cannot import name 'TestClient'", "dependency_missing"),
    ("No module named 'uvicorn'", "dependency_missing"),
    ("ERROR: Could not find a version that satisfies the requirement", "dependency_missing"),
    ("pip install failed package not found", "dependency_missing"),
    ("ModuleNotFoundError: No module named 'httpx'", "dependency_missing"),
    ("ImportError: No module named requests", "dependency_missing"),

    # build_error
    ("SyntaxError: invalid syntax line 12", "build_error"),
    ("IndentationError: unexpected indent", "build_error"),
    ("NameError: name 'app' is not defined", "build_error"),
    ("TypeError: unsupported operand type", "build_error"),
    ("SyntaxError: EOL while scanning string literal", "build_error"),
    ("docker build failed exit code 1", "build_error"),
    ("error: command gcc failed with exit code 1", "build_error"),

    # infra_flap
    ("Connection refused localhost:8000", "infra_flap"),
    ("requests.exceptions.ConnectionError timeout", "infra_flap"),
    ("Service unavailable 503 retry", "infra_flap"),
    ("socket.timeout: timed out", "infra_flap"),
    ("Runner lost connection network error", "infra_flap"),
    ("ECONNREFUSED connection refused", "infra_flap"),
    ("ReadTimeoutError HTTPSConnectionPool timed out", "infra_flap"),

    # auth_error
    ("403 Forbidden access denied", "auth_error"),
    ("401 Unauthorized invalid token", "auth_error"),
    ("permission denied git push", "auth_error"),
    ("Authentication failed for https://github.com", "auth_error"),
    ("remote: Invalid username or password", "auth_error"),
    ("ERROR: Permission denied publickey", "auth_error"),
    ("fatal: could not read Username forbidden", "auth_error"),
]