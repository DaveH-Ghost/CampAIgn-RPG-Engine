"""
move.py

Implementation of the `move` action for V0.

Movement rules (from readiness checklist):
- 1 tile per turn.
- Only 4 cardinal directions: north, east, south, west.
- Cannot move outside the 0-4 grid.
- No blocking objects (agent can share tile with ball).
- On success: position is updated, result = "You moved {direction} to ({x}, {y})."
- On failure: position unchanged, result describes why (blocked by wall or off map).
- Failed move still counts as the turn (reasoning + result recorded).
"""

from src.agent import Agent
from src.world import World


_DIRECTION_DELTAS = {
    "north": (0, 1),
    "south": (0, -1),
    "east": (1, 0),
    "west": (-1, 0),
}


def move(agent: Agent, world: World, direction: str) -> str:
    """
    Attempt to move the agent one tile in the given direction.

    Direction must be one of 'north', 'east', 'south', 'west' (case-insensitive).
    The schema should have already validated this, but we handle gracefully.
    """
    direction = direction.lower().strip()

    if direction not in _DIRECTION_DELTAS:
        # Should not happen if schema validated, but defensive.
        return f"You tried to move {direction}, but that is not a valid direction."

    dx, dy = _DIRECTION_DELTAS[direction]
    current_x, current_y = agent.position
    new_x = current_x + dx
    new_y = current_y + dy
    new_pos = (new_x, new_y)

    if not world.is_valid_position(new_pos):
        # In V0 there are no inner walls or blocking objects.
        # Any invalid move is hitting the boundary of the room.
        # Use the "outside the room" phrasing from the spec (preferred over
        # wall in some examples; the wall phrasing is also acceptable).
        return f"You tried to move {direction}, but that direction is outside the room."

    # Success
    agent.position = new_pos
    return f"You moved {direction} to {new_pos}."
