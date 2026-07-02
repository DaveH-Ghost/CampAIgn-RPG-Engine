"""Pytest fixtures for Realm-Fabric tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_EXAMPLES = _ROOT / "examples"
if str(_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(_EXAMPLES))


@pytest.fixture(autouse=True, scope="session")
def _register_reference_handlers():
    from reference_handlers import register_reference_handlers

    register_reference_handlers()
