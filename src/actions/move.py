"""
move.py

Coordinate and entity-id move for V0.2 / V0.4.0a.

V0.4.0a: ``move_target`` may be ``x,y`` or ``agent_*`` / ``obj_*`` (teleport).
V0.4.0b will add ``move_speed`` pathing when set.
"""

from src.action_outcome import ActionOutcome
from src.agent import Agent
from src.coordinates import format_coordinate
from src.move_target import (
    MoveTargetError,
    format_move_arrival_message,
    resolve_move_target,
)
from src.area import Area


def move(agent: Agent, area: Area, target: str) -> ActionOutcome:
    """Move the agent to a coordinate or entity-id target tile."""
    try:
        resolved = resolve_move_target(area, target)
    except MoveTargetError as exc:
        return ActionOutcome(
            result=f"This action wasn't recognized, {exc}",
        )

    new_pos = resolved.position
    label = format_coordinate(*new_pos)

    if not area.is_valid_position(new_pos):
        return ActionOutcome(
            result=(
                "This action wasn't recognized, ERR:INVALID_COORDINATES, "
                f"{label} is outside the room."
            ),
        )

    if agent.position == new_pos:
        return ActionOutcome(
            result=f"You are already at {label}.",
        )

    agent.position = new_pos
    return ActionOutcome(
        result=format_move_arrival_message(resolved),
        passive_result=f"{agent.name} moves to {label}.",
    )
