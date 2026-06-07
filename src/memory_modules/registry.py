"""Factory registry for memory modules."""

from __future__ import annotations

from typing import Any, Callable

from src.memory_modules.base import MemoryModule
from src.memory_modules.recent_turns import RecentTurnsModule

ModuleFactory = Callable[..., MemoryModule]

DEFAULT_MODULE_ID = "recent_turns"

_REGISTRY: dict[str, ModuleFactory] = {
    "recent_turns": lambda **cfg: RecentTurnsModule(window=cfg.get("window", 10)),
}


def default_module_id() -> str:
    return DEFAULT_MODULE_ID


def create_module(module_id: str | None = None, **config: Any) -> MemoryModule:
    """Construct a memory module by id. Defaults to recent_turns."""
    resolved = module_id or DEFAULT_MODULE_ID
    factory = _REGISTRY.get(resolved)
    if factory is None:
        known = ", ".join(known_module_ids())
        raise ValueError(f"Unknown memory module {resolved!r}. Known modules: {known}")
    return factory(**config)


def known_module_ids() -> list[str]:
    """Return registered memory module ids (for create-agent and listing)."""
    return sorted(_REGISTRY)


def format_memory_modules_list() -> str:
    """Read-only listing of registered memory modules."""
    lines = ["Registered memory modules:"]
    for module_id in known_module_ids():
        if module_id == "recent_turns":
            desc = "Last N own turns plus witnessed other-agent actions (default)"
        else:
            desc = "(no description)"
        lines.append(f"  - {module_id}: {desc}")
    return "\n".join(lines)
