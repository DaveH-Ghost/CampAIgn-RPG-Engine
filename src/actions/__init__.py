"""
Actions package.

Contains the implementation for the three V0 actions:
- move
- look
- speak

Each action is currently in its own module for clarity during early development.

Typical usage (from the simulation loop):
    from src.actions import do_move, do_look, do_speak

    result = do_move(agent, world, action.target)
    # then record TurnRecord with the result
"""

from src.actions.look import look as do_look
from src.actions.move import move as do_move
from src.actions.speak import speak as do_speak

__all__ = ["do_move", "do_look", "do_speak"]
