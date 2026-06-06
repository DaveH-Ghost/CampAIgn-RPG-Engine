"""
stepper_commands.py

Reserved stepper command names for agent display-name validation.

Agent names are dispatched via default() when typed at the prompt, so they
must not match any built-in or hyphenated ManualStepper command.

Reserved names are derived from ManualStepper's do_* handlers at runtime so
new commands are picked up automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cmd

# cmd.Cmd help alias; not a do_* method.
_EXTRA_COMMAND_ALIASES: frozenset[str] = frozenset({"?"})

# Internal handlers users do not type at the prompt.
_SKIP_DO_METHODS: frozenset[str] = frozenset({"do_EOF"})

_reserved_cache: frozenset[str] | None = None


def collect_reserved_command_names(cmd_class: type[cmd.Cmd]) -> frozenset[str]:
    """
    Build reserved command names from a cmd.Cmd subclass.

    Maps do_create_object -> create-object (hyphenated, lowercase).
    """
    names = set(_EXTRA_COMMAND_ALIASES)
    for attr in dir(cmd_class):
        if not attr.startswith("do_") or attr in _SKIP_DO_METHODS:
            continue
        names.add(attr[3:].replace("_", "-").lower())
    return frozenset(names)


def get_reserved_stepper_commands() -> frozenset[str]:
    """Return reserved names for ManualStepper (lazy, cached)."""
    global _reserved_cache
    if _reserved_cache is None:
        from src.main import ManualStepper

        _reserved_cache = collect_reserved_command_names(ManualStepper)
    return _reserved_cache


def _name_variants(name: str) -> set[str]:
    """Lowercase name plus hyphen/underscore alternates."""
    n = name.strip().lower()
    return {n, n.replace("-", "_"), n.replace("_", "-")}


def agent_name_conflicts_with_commands(name: str) -> bool:
    """Return True if name would collide with a stepper command (case-insensitive)."""
    variants = _name_variants(name)
    for reserved in get_reserved_stepper_commands():
        if variants & _name_variants(reserved):
            return True
    return False


def reserved_agent_name_message(name: str) -> str:
    return (
        f"Agent name '{name}' conflicts with a stepper command. "
        f"Choose a different display name."
    )
