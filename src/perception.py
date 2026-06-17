"""
perception.py

Passive vision and look logic.

Responsibilities:
- Build the "Current Passive Vision" text block shown to the agent each turn.
- Passive vs detailed rendering for objects and other agents (V0.1+).
- Provide look logic: validate targets, return descriptions, update memory.

The viewing agent sees objects and other agents in passive vision (not itself).
Walls/room boundaries are conveyed via the separate room description from Area.
"""

from src.action_outcome import ActionOutcome
from src.agent import Agent
from src.grid import chebyshev_distance
from src.vision_bearing import format_relative_bearing_phrase
from src.memory import Memory
from src.object import Object
from src.object_action import ObjectAction
from src.area import Area


def format_vision_desc(
    memory: Memory,
    entity_id: str,
    passive: str,
    detailed: str,
) -> str:
    """
    Return the description fragment for one entity in passive vision.

    Shared rules for objects and other agents:
    - Detailed empty: no [?] tag; show passive only (if any).
    - Never examined + detailed present: [?], or [?] {passive} if passive set.
    - Current knowledge (looked_at): detailed if present, else passive.
    - Stale (ever_looked, invalidated): [?] [changed] {passive} (passive omitted if empty).
    """
    if memory.has_looked_at(entity_id):
        return detailed if detailed else passive

    if memory.has_ever_looked_at(entity_id) and detailed:
        if passive:
            return f"[?] [changed] {passive}"
        return "[?] [changed]"

    if not detailed:
        return passive

    if passive:
        return f"[?] {passive}"
    return "[?]"


def format_object_vision_desc(obj: Object, memory: Memory) -> str:
    """Return the description fragment for one object in passive vision."""
    return format_vision_desc(
        memory, obj.id, obj.passive_description, obj.description
    )


def format_agent_vision_desc(other: Agent, memory: Memory) -> str:
    """
    Return the description fragment for another agent in passive vision.

    Static pdesc/desc only ([?] rules). Observable actions (``passive_result``)
    are ingested into memory modules, not repeated here.
    """
    return format_vision_desc(
        memory, other.id, other.passive_description, other.description
    )


def build_passive_vision(
    agent: Agent,
    area: Area,
    *,
    include_you_are_at: bool = True,
    include_entity_coordinates: bool = True,
    include_relative_bearing: bool = False,
    vision_units: str = "",
    units_per_tile: int | None = None,
) -> str:
    """
    Build the passive vision block for the given agent.

    Format:
    You are at (x, y).  (optional)
    {name} ({id}), {coordinates}, {bearing phrase} - {description fragment}
    Entity coordinates apply to objects and other agents, not the you-are-at line.
    """
    bearing_ready = (
        include_relative_bearing
        and units_per_tile is not None
        and units_per_tile > 0
    )
    lines: list[str] = []
    if include_you_are_at:
        lines.append(f"You are at {agent.position}.")

    memory = agent.memory

    for obj in area.get_objects():
        desc = format_object_vision_desc(obj, memory)
        lines.append(
            _format_passive_vision_entity_line(
                obj.name,
                obj.id,
                obj.position,
                desc,
                observer=agent.position,
                include_coordinates=include_entity_coordinates,
                include_relative_bearing=bearing_ready,
                vision_units=vision_units,
                units_per_tile=units_per_tile,
            )
        )

    for other in area.agents:
        if other.id == agent.id:
            continue
        desc = format_agent_vision_desc(other, memory)
        lines.append(
            _format_passive_vision_entity_line(
                other.name,
                other.id,
                other.position,
                desc,
                observer=agent.position,
                include_coordinates=include_entity_coordinates,
                include_relative_bearing=bearing_ready,
                vision_units=vision_units,
                units_per_tile=units_per_tile,
            )
        )

    return "\n".join(lines)


def _format_passive_vision_entity_line(
    name: str,
    entity_id: str,
    position: tuple[int, int],
    desc: str,
    *,
    observer: tuple[int, int],
    include_coordinates: bool,
    include_relative_bearing: bool = False,
    vision_units: str = "",
    units_per_tile: int | None = None,
) -> str:
    parts = [f"{name} ({entity_id})"]
    if include_coordinates:
        parts.append(f"{position}")
    if include_relative_bearing and units_per_tile is not None:
        bearing = format_relative_bearing_phrase(
            observer,
            position,
            units=vision_units,
            units_per_tile=units_per_tile,
        )
        if bearing:
            parts.append(bearing)
    prefix = ", ".join(parts)
    if desc:
        return f"{prefix} - {desc}"
    return prefix


DEFAULT_PASSIVE_VISION_OPTIONS: dict[str, bool] = {
    "include_you_are_at": True,
    "include_entity_coordinates": True,
    "include_relative_bearing": False,
}


def normalize_passive_vision_options(
    options: dict[str, object] | None,
) -> dict[str, bool]:
    """Merge *options* with defaults for passive vision slot rendering."""
    merged = dict(DEFAULT_PASSIVE_VISION_OPTIONS)
    if options:
        for key in DEFAULT_PASSIVE_VISION_OPTIONS:
            if key in options:
                merged[key] = bool(options[key])
    return merged


def get_visible_look_target_ids(agent: Agent, area: Area) -> list[str]:
    """
    Return entity IDs (objects and other agents) visible in passive vision.

    Used to validate look targets, including entries marked with [?].
    """
    ids = [obj.id for obj in area.get_objects()]
    ids.extend(other.id for other in area.agents if other.id != agent.id)
    return ids


def get_visible_object_ids(agent: Agent, area: Area) -> list[str]:
    """Return object IDs visible in passive vision."""
    return [obj.id for obj in area.get_objects()]


def is_object_in_passive_vision(agent: Agent, area: Area, object_id: str) -> bool:
    """Return True if the object appears in the agent's passive vision."""
    return object_id in get_visible_object_ids(agent, area)


def get_available_interactions(
    agent: Agent, area: Area
) -> list[tuple[str, str, Object, ObjectAction]]:
    """
    Return in-range object interactions for the action-phase prompt.

    Each entry is (action_name, object_id, object, action).
    """
    results: list[tuple[str, str, Object, ObjectAction]] = []
    visible = set(get_visible_object_ids(agent, area))
    for obj in area.get_objects():
        if obj.id not in visible:
            continue
        for action_name, action in obj.actions.items():
            if chebyshev_distance(agent.position, obj.position) <= action.range:
                results.append((action_name, obj.id, obj, action))
    results.sort(key=lambda item: (item[2].name.lower(), item[0], item[1]))
    return results


def perform_look(agent: Agent, area: Area, target_id: str) -> ActionOutcome:
    """
    Execute the "look" action on an object or another agent.

    Returns first-person result for the actor and third-person passive_result
    when the target is visible (even if there is no detailed text to learn).
    """
    visible_ids = get_visible_look_target_ids(agent, area)
    if target_id not in visible_ids:
        return ActionOutcome(result="You don't see anything like that to look at.")

    if target_id.startswith("obj_"):
        obj = area.get_object_by_id(target_id)
        if obj is None:
            return ActionOutcome(result="You don't see anything like that to look at.")
        name = obj.name
        detailed = obj.description
    elif target_id.startswith("agent_"):
        other = area.get_agent_by_id(target_id)
        if other is None or other.id == agent.id:
            return ActionOutcome(result="You don't see anything like that to look at.")
        name = other.name
        detailed = other.description
    else:
        return ActionOutcome(result="You don't see anything like that to look at.")

    passive_result = f"{agent.name} examines {name}."

    if not detailed:
        if agent.memory.has_ever_looked_at(target_id):
            agent.memory.clear_examination(target_id)
        return ActionOutcome(
            result=f"You don't notice anything more about the {name.lower()}.",
            passive_result=passive_result,
        )

    agent.memory.mark_looked_at(target_id)
    return ActionOutcome(
        result=f"You looked at the {name.lower()}. {detailed}",
        passive_result=passive_result,
    )


def _vision_desc_shows_question_mark(
    memory: Memory, entity_id: str, passive: str, detailed: str
) -> bool:
    """True when passive vision would prefix the entity with [?]."""
    return format_vision_desc(memory, entity_id, passive, detailed).startswith(
        "[?]"
    )


def get_available_look_targets(agent: Agent, area: Area) -> list[str]:
    """Return entity IDs marked [?] in passive vision (hidden detail to examine)."""
    memory = agent.memory
    targets: list[str] = []
    for obj in area.get_objects():
        if _vision_desc_shows_question_mark(
            memory, obj.id, obj.passive_description, obj.description
        ):
            targets.append(obj.id)
    for other in area.agents:
        if other.id == agent.id:
            continue
        if _vision_desc_shows_question_mark(
            memory, other.id, other.passive_description, other.description
        ):
            targets.append(other.id)
    targets.sort()
    return targets
