"""
perception.py

Passive vision and look logic.

Responsibilities:
- Build the "Current Passive Vision" text block shown to the agent each turn.
- Generalized "has changed" notification for stale object knowledge (V0.1).
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

    Three states:
    - Current knowledge: full description
    - Never looked at: [?]
    - Stale (looked before, invalidated): [?] The {name} has changed...
    """
    if memory.has_looked_at(obj.id):
        return obj.description
    if memory.has_ever_looked_at(obj.id):
        return f"[?] The {obj.name} has changed since you last looked at it."
    return "[?]"


def build_passive_vision(agent: Agent, world: World) -> str:
    """
    Build the passive vision block for the given agent.

    Format:
    You are at (x, y).
    {name} ({id}), {coordinates} - {description}|[?]|changed notice
    """
    lines = [f"You are at {agent.position}."]
    memory = agent.memory

    for obj in world.get_objects():
        desc = format_object_vision_desc(obj, memory)
        lines.append(f"{obj.name} ({obj.id}), {obj.position} - {desc}")

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
    - If valid: marks the object as looked-at and returns the full description.
    - If not visible: returns a failure message.
    """
    visible_ids = get_visible_object_ids(agent, world)
    if target_id not in visible_ids:
        return "You don't see anything like that to look at."

    obj = world.get_object_by_id(target_id)
    if obj is None:
        return "You don't see anything like that to look at."

    agent.memory.mark_looked_at(target_id)
    return f'You looked at the {obj.name.lower()}. {obj.description}'


def get_available_look_targets(agent: Agent, world: World) -> list[str]:
    """
    Return the object IDs that the agent can currently use the `look` action on.
    """
    return get_visible_object_ids(agent, world)
