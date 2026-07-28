"""Smoke tests for the package scaffold."""

from pysiebanxico import __version__


def test_version_is_exposed() -> None:
    assert __version__ == "0.1.0.dev0"
