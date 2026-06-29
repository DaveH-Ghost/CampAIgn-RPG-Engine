"""
object_effects.py

Central registry for declarative object interaction effects (V0.2 Section 3).
V0.4.0d adds parameterized ``EffectSpec`` and session-aware ``move_area``.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from src.effect_spec import EffectSpec
from src.object import object_footprint_tiles

if TYPE_CHECKING:
    from src.agent import Agent
    from src.area import Area
    from src.object import Object
    from src.session import Session

EffectHandler = Callable[["EffectContext", "Agent", "Object", EffectSpec], None]


@dataclass
class EffectContext:
    """Runtime context for effect handlers (V0.4.0d+)."""

    area: Area
    session: Session | None = None
    source_area_id: str | None = None


def _delete_self(ctx: EffectContext, _agent: Agent, obj: Object, _spec: EffectSpec) -> None:
    ctx.area.remove_object(obj.id)


def _random_move_self(
    ctx: EffectContext, _agent: Agent, obj: Object, _spec: EffectSpec
) -> None:
    area = ctx.area
    occupied = set(object_footprint_tiles(obj))
    positions = [
        (x, y)
        for x in range(area.min_x, area.max_x + 1)
        for y in range(area.min_y, area.max_y + 1)
        if (x, y) not in occupied
    ]
    if not positions:
        return
    obj.position = random.choice(positions)


def _move_area(ctx: EffectContext, agent: Agent, _obj: Object, spec: EffectSpec) -> str | None:
    if ctx.session is None:
        return "move_area requires a multi-area session."
    dest_area_id = spec.params.get("dest-area", "").strip()
    dest_at = spec.params.get("dest-at", "").strip()
    if not dest_area_id or not dest_at:
        return "move_area effect is missing dest-area or dest-at."

    from src.area_edit import parse_position

    position, err = parse_position(dest_at)
    if err:
        return err
    assert position is not None

    result = ctx.session.transfer_agent(agent.id, dest_area_id, position)
    if not result.ok:
        return result.message
    return None


_PARAMETRIC_HANDLERS: dict[str, Callable[[EffectContext, Agent, Object, EffectSpec], str | None]] = {
    "move_area": _move_area,
}


_REGISTRY: dict[str, tuple[str, EffectHandler]] = {
    "delete_self": (
        "Remove the interacted object from the area",
        _delete_self,
    ),
    "random_move_self": (
        "Move the interacted object to a different random in-bounds grid position",
        _random_move_self,
    ),
    "move_area": (
        "Transfer the interacting agent to another area at dest-at (requires dest-area, dest-at)",
        lambda ctx, agent, obj, spec: None,
    ),
}

EFFECT_DESCRIPTIONS: dict[str, str] = {
    name: description for name, (description, _handler) in _REGISTRY.items()
}

_EFFECT_HANDLERS: dict[str, EffectHandler] = {
    name: handler for name, (_description, handler) in _REGISTRY.items()
}


def known_effect_names() -> frozenset[str]:
    """Return all registered effect keys."""
    return frozenset(_REGISTRY)


def validate_effect_name(name: str) -> str | None:
    """Return an error message if the effect name is unknown."""
    if name not in _REGISTRY:
        known = ", ".join(sorted(_REGISTRY))
        return f"Unknown effect '{name}'. Known effects: {known}."
    return None


def validate_effect_params(name: str, params: dict[str, str]) -> str | None:
    """Validate params for a named effect. Returns an error message or None."""
    err = validate_effect_name(name)
    if err:
        return err
    if name == "move_area":
        dest_area = params.get("dest-area", "").strip()
        dest_at = params.get("dest-at", "").strip()
        if not dest_area:
            return "move_area effect requires dest-area <area_id>."
        if not dest_at:
            return "move_area effect requires dest-at x,y."
        from src.area_edit import parse_position

        _, perr = parse_position(dest_at)
        if perr:
            return perr
    elif params:
        return f"Effect '{name}' does not accept parameters."
    return None


def apply_effects(
    ctx: EffectContext,
    agent: Agent,
    obj: Object,
    effects: list[EffectSpec],
) -> str | None:
    """Run registered effects in order. Returns an error message if any effect fails."""
    for spec in effects:
        err = validate_effect_params(spec.name, spec.params)
        if err:
            return err
        parametric = _PARAMETRIC_HANDLERS.get(spec.name)
        if parametric is not None:
            fail = parametric(ctx, agent, obj, spec)
            if fail:
                return fail
            continue
        handler = _EFFECT_HANDLERS[spec.name]
        handler(ctx, agent, obj, spec)
    return None


def format_effects_list() -> str:
    """Format the read-only effects listing for the stepper."""
    lines = ["Registered object effects:"]
    if not _REGISTRY:
        lines.append("  (none)")
    else:
        for name in sorted(_REGISTRY):
            lines.append(f"  - {name}: {EFFECT_DESCRIPTIONS[name]}")
    return "\n".join(lines)
