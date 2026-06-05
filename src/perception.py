"""
perception.py

Passive vision and look logic.

Responsibilities:
- Build the "Current Passive Vision" text block shown to the agent each turn.
- Passive vs detailed description rendering (V0.1 perception extension).
- Provide look logic: validate targets, return descriptions, update memory.

The agent only sees objects in passive vision; walls/room boundaries are
conveyed via the separate room description from World.
"""

from src.agent import Agent
from src.memory import Memory
from src.object import Object
from src.world import World


def format_object_vision_desc(obj: Object, memory: Memory) -> str:
    """
    Return the description fragment for one object in passive vision.

    V0.1 perception extension rules:
    - Detailed empty: no [?] tag; show passive only (if any).
    - Never examined + detailed present: [?], or [?] {passive} if passive set.
    - Current knowledge (looked_at): detailed if present, else passive.
    - Stale (ever_looked, invalidated): [?] [changed] {passive} (passive omitted if empty).
    """
    passive = obj.passive_description
    detailed = obj.description

    if memory.has_looked_at(obj.id):
        return detailed if detailed else passive

    if memory.has_ever_looked_at(obj.id) and detailed:
        if passive:
            return f"[?] [changed] {passive}"
        return "[?] [changed]"

    if not detailed:
        return passive

    if passive:
        return f"[?] {passive}"
    return "[?]"


def build_passive_vision(agent: Agent, world: World) -> str:
    """
    Build the passive vision block for the given agent.

    Format:
    You are at (x, y).
    {name} ({id}), {coordinates} - {description fragment}
    """
    lines = [f"You are at {agent.position}."]
    memory = agent.memory

    for obj in world.get_objects():
        desc = format_object_vision_desc(obj, memory)
        if desc:
            lines.append(f"{obj.name} ({obj.id}), {obj.position} - {desc}")
        else:
            lines.append(f"{obj.name} ({obj.id}), {obj.position}")

    return "\n".join(lines)


def get_visible_object_ids(agent: Agent, world: World) -> list[str]:
    """
    Return the list of object IDs that currently appear in the agent's
    passive vision.

    This is used by the action layer to validate whether a `look` target
    is currently visible (even if marked with [?]).
    """
    return [obj.id for obj in world.get_objects()]


def perform_look(agent: Agent, world: World, target_id: str) -> str:
    """
    Execute the "look" action for the agent on the given target object ID.

    - Checks that the target is currently visible in passive vision.
    - If detailed description is empty, returns a no-detail message (no memory update).
    - If valid: marks the object as looked-at and returns the detailed description.
    """
    visible_ids = get_visible_object_ids(agent, world)
    if target_id not in visible_ids:
        return "You don't see anything like that to look at."

    obj = world.get_object_by_id(target_id)
    if obj is None:
        return "You don't see anything like that to look at."

    if not obj.description:
        if agent.memory.has_ever_looked_at(target_id):
            agent.memory.clear_examination(target_id)
        return f"You don't notice anything more about the {obj.name.lower()}."

    agent.memory.mark_looked_at(target_id)
    return f"You looked at the {obj.name.lower()}. {obj.description}"


def get_available_look_targets(agent: Agent, world: World) -> list[str]:
    """
    Return the object IDs that the agent can currently use the `look` action on.
    """
    return get_visible_object_ids(agent, world)
