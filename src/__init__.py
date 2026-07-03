"""
Realm Fabric — grid-based agent simulation engine.

Public API: import from ``realm_fabric`` (``Session``, ``GameProfile``, …).
``src.*`` modules are used by the CLI and tests; prefer ``realm_fabric`` in apps.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def _read_version() -> str:
    try:
        from importlib.metadata import version as _pkg_version

        return _pkg_version("realm-fabric")
    except Exception:
        pass
    pyproject_path = _ROOT / "pyproject.toml"
    if pyproject_path.is_file():
        return tomllib.loads(pyproject_path.read_text(encoding="utf-8"))["project"]["version"]
    return "0.0.0"


__version__ = _read_version()

__all__ = ["__version__"]
