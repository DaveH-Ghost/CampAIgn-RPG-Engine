"""
move.py

Implementation of the `move` action for V0.
"""

from src.action_outcome import ActionOutcome
from src.agent import Agent
from src.world import World


_DIRECTION_DELTAS = {
    "north": (0, 1),
    "south": (0, -1),
    "east": (1, 0),
    "west": (-1, 0),
}


def move(agent: Agent, world: World, direction: str) -> ActionOutcome:
    """Attempt to move the agent one tile in the given direction."""
    direction = direction.lower().strip()

    if direction not in _DIRECTION_DELTAS:
        return ActionOutcome(
            result=f"You tried to move {direction}, but that is not a valid direction."
        )

    dx, dy = _DIRECTION_DELTAS[direction]
    current_x, current_y = agent.position
    new_x = current_x + dx
    new_y = current_y + dy
    new_pos = (new_x, new_y)

    if not world.is_valid_position(new_pos):
        return ActionOutcome(
            result=(
                f"You tried to move {direction}, but that direction is outside the room."
            )
        )

    agent.position = new_pos
    return ActionOutcome(
        result=f"You moved {direction} to {new_pos}.",
        passive_result=f"{agent.name} moves {direction}.",
    )
