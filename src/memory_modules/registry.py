"""Factory registry for memory modules."""

from __future__ import annotations

from typing import Any, Callable

from src.memory_modules.base import MemoryModule
from src.memory_modules.recent_turns import RecentTurnsModule
from src.memory_modules.salient_turns import (
    DEFAULT_CHAR_BUDGET,
    SalientTurnsModule,
    validate_char_budget,
)

ModuleFactory = Callable[..., MemoryModule]

DEFAULT_MODULE_ID = "recent_turns"

_REGISTRY: dict[str, ModuleFactory] = {
    "recent_turns": lambda **cfg: RecentTurnsModule(window=cfg.get("window", 10)),
    "salient_turns": lambda **cfg: SalientTurnsModule(
        char_budget=int(cfg.get("char_budget", DEFAULT_CHAR_BUDGET)),
        storage_window=int(cfg.get("storage_window", 50)),
        recency_floor=int(cfg.get("recency_floor", 2)),
    ),
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
    if resolved != "salient_turns" and "char_budget" in config:
        raise ValueError(
            "memory-budget is only valid with memory salient_turns "
            f"(got memory {resolved!r})."
        )
    if resolved == "salient_turns" and "char_budget" in config:
        validate_char_budget(int(config["char_budget"]))
    return factory(**config)


def known_module_ids() -> list[str]:
    """Return registered memory module ids (for create-agent and listing)."""
    return sorted(_REGISTRY)


def format_memory_module_label(module: MemoryModule) -> str:
    """Short label for agent listings (module id + salient budget when set)."""
    if isinstance(module, SalientTurnsModule):
        return f"memory={module.module_id} budget={module.char_budget}"
    return f"memory={module.module_id}"


def format_memory_modules_list() -> str:
    """Read-only listing of registered memory modules."""
    lines = ["Registered memory modules:"]
    for module_id in known_module_ids():
        if module_id == "recent_turns":
            desc = "Last N own turns plus witnessed other-agent actions (default)"
        elif module_id == "salient_turns":
            desc = (
                f"Salience-weighted retention; render capped by memory-budget "
                f"({DEFAULT_CHAR_BUDGET} default)"
            )
        else:
            desc = "(no description)"
        lines.append(f"  - {module_id}: {desc}")
    return "\n".join(lines)
