"""Print a cell-by-cell comparison table at the end of every test run."""

import pytest

REPORT = pytest.StashKey[list]()


def pytest_configure(config):
    config.stash[REPORT] = []


@pytest.fixture
def answer_key_report(request):
    return request.config.stash[REPORT]


def _number(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return f"{value:.6g}"


def _relative(expected, difference):
    if difference is None or not expected:
        return ""
    return f"{difference / abs(expected):+.4%}"


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    rows = config.stash[REPORT]
    if not rows:
        return
    write = terminalreporter.write_line
    terminalreporter.section("Answer key comparison (Outputs sheet)")
    header = f"{'Cell':<5} {'Check':<46} {'Excel':>14} {'Python':>14} {'Difference':>13} {'Rel. diff':>10}  Result"
    write(header)
    write("-" * len(header))
    for cell, description, expected, actual, difference, result in rows:
        write(
            f"{cell:<5} {description[:46]:<46} {_number(expected):>14} {_number(actual):>14} "
            f"{_number(difference):>13} {_relative(expected, difference):>10}  {result}"
        )
    skipped = [f"{cell} ({result[6:-1]})" for cell, *_, result in rows if result.startswith("SKIP")]
    write("")
    write(f"Skipped cells: {', '.join(skipped) if skipped else 'none'}")
