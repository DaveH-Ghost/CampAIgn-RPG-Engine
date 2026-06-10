"""Project packaging and pyproject.toml metadata."""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_pyproject_version_is_semver():
    version = _load_pyproject()["project"]["version"]
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), version


def test_pyproject_declares_realm_console_script():
    data = _load_pyproject()
    assert data["project"]["scripts"]["realm"] == "src.main:main"
    assert data["tool"]["uv"]["package"] is True
    assert "hatchling" in data["build-system"]["requires"]
