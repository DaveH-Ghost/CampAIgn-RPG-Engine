"""
perception.py

Passive vision and look logic for Version 0.

Responsibilities (per the readiness checklist):
- Build the "Current Passive Vision" text block shown to the agent each turn.
- Handle the special sign change notification in passive vision.
- Provide look logic: determine if a look target is valid (visible in passive vision),
  return the description, and update the agent's memory (mark as looked at).

The agent only sees objects in passive vision; walls/room boundaries are
conveyed via the separate room description from World.
"""

from src.agent import Agent
from src.object import Object
from src.world import World


def build_passive_vision(agent: Agent, world: World) -> str:
    """
    Build the passive vision block for the given agent.

    Format (from checklist):
    You are at (x, y).
    {name} ({id}), {coordinates} - {description}|[?]
    ...

    The agent's own position is stated at the top.
    Objects the agent has not looked at (or whose look was invalidated, e.g. sign
    after update) appear with "[?]" instead of their description.

    For the wooden sign specifically, when not looked at (including after update),
    we append the special "has changed" notification.
    """
    lines = [f"You are at {agent.position}."]

    memory = agent.memory
    for obj in world.get_objects():
        if memory.has_looked_at(obj.id):
            desc = obj.description
        else:
            if obj.id == "obj_sign_01":
                desc = "[?] The wooden sign has changed since you last looked at it."
            else:
                desc = "[?]"

        line = f"{obj.name} ({obj.id}), {obj.position} - {desc}"
        lines.append(line)

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

    - Checks that the target is currently visible in passive vision (runtime check
      per checklist; the schema only validates the ID format).
    - If valid: marks the object as looked-at in the agent's memory,
      and returns the full description result string.
    - If not visible: returns a failure message (the action still "happens"
      but the agent gets no new info).

    Look result format (from checklist examples):
    "You looked at the wooden sign. It reads: \"...\""
    """
    visible_ids = get_visible_object_ids(agent, world)
    if target_id not in visible_ids:
        # The target does not appear in current passive vision.
        # Per docs, only objects currently visible (even with [?]) can be looked at.
        return "You don't see anything like that to look at."

    obj = world.get_object_by_id(target_id)
    if obj is None:
        # Should not happen if visible_ids came from world, but defensive.
        return "You don't see anything like that to look at."

    # Success: update memory and return description
    agent.memory.mark_looked_at(target_id)

    # Result string style from the checklist
    return f'You looked at the {obj.name.lower()}. {obj.description}'


def get_available_look_targets(agent: Agent, world: World) -> list[str]:
    """
    Return the object IDs that the agent can currently use the `look` action on.

    These are exactly the objects that appear in passive vision (the ones with
    [?] or full descriptions). Used when building the "Available Actions" section.
    """
    return get_visible_object_ids(agent, world)
