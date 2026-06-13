"""
In-memory Session holder for the realm-studio demo (single-player, one process).
"""

from __future__ import annotations

from realm_fabric import Session, load_profile

_store: SessionStore | None = None


class SessionStore:
    """Owns one engine ``Session`` for the lifetime of the server process."""

    def __init__(self) -> None:
        profile = load_profile("default_compound")
        self._session = Session.from_profile(profile)

    @property
    def session(self) -> Session:
        return self._session


def get_session_store() -> SessionStore:
    """Return the process-wide session store (lazy singleton)."""
    global _store
    if _store is None:
        _store = SessionStore()
    return _store


def reset_session_store() -> None:
    """Reset store (tests only)."""
    global _store
    _store = None
