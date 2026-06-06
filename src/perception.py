"""
perception.py

Passive vision and look logic.

Responsibilities:
- Build the "Current Passive Vision" text block shown to the agent each turn.
- Passive vs detailed rendering for objects and other agents (V0.1+).
- Provide look logic: validate targets, return descriptions, update memory.

The viewing agent sees objects and other agents in passive vision (not itself).
Walls/room boundaries are conveyed via the separate room description from World.
"""

from src.action_outcome import ActionOutcome
from src.agent import Agent
from src.memory import Memory
from src.object import Object
from src.world import World


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

    Static pdesc/desc follow object [?] rules. passive_result (last successful
    action) is always appended so other agents can see recent speech and movement.
    """
    fragment = format_vision_desc(
        memory, other.id, other.passive_description, other.description
    )
    if other.passive_result:
        if fragment:
            return f"{fragment} {other.passive_result}"
        return other.passive_result
    return fragment


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

    for other in world.agents:
        if other.id == agent.id:
            continue
        desc = format_agent_vision_desc(other, memory)
        if desc:
            lines.append(f"{other.name} ({other.id}), {other.position} - {desc}")
        else:
            lines.append(f"{other.name} ({other.id}), {other.position}")

    return "\n".join(lines)


def get_visible_look_target_ids(agent: Agent, world: World) -> list[str]:
    """
    Return entity IDs (objects and other agents) visible in passive vision.

    Used to validate look targets, including entries marked with [?].
    """
    ids = [obj.id for obj in world.get_objects()]
    ids.extend(other.id for other in world.agents if other.id != agent.id)
    return ids


def get_visible_object_ids(agent: Agent, world: World) -> list[str]:
    """Backward-compatible alias: object IDs only."""
    return [obj.id for obj in world.get_objects()]


def perform_look(agent: Agent, world: World, target_id: str) -> ActionOutcome:
    """
    Execute the "look" action on an object or another agent.

    Returns first-person result for the actor and third-person passive_result
    when the target is visible (even if there is no detailed text to learn).
    """
    visible_ids = get_visible_look_target_ids(agent, world)
    if target_id not in visible_ids:
        return ActionOutcome(result="You don't see anything like that to look at.")

    if target_id.startswith("obj_"):
        obj = world.get_object_by_id(target_id)
        if obj is None:
            return ActionOutcome(result="You don't see anything like that to look at.")
        name = obj.name
        detailed = obj.description
    elif target_id.startswith("agent_"):
        other = world.get_agent_by_id(target_id)
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


def get_available_look_targets(agent: Agent, world: World) -> list[str]:
    """Return entity IDs the agent can currently use the look action on."""
    return get_visible_look_target_ids(agent, world)
