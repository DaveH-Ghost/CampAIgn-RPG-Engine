"""
look.py

Implementation of the `look` action for V0.

The look action allows the agent to examine an object that appears in its
current passive vision (even if marked with [?]). On success, the detailed
description is returned and the object is marked as "looked at" in the
agent's memory (so future passive vision shows the detailed text). Objects
with no detailed description return a no-detail message without updating memory.
"""

from src.agent import Agent
from src.perception import perform_look
from src.world import World


def look(agent: Agent, world: World, target: str) -> str:
    """
    Perform the look action.

    Delegates to perception.perform_look which handles:
    - Checking that the target object is currently visible in passive vision.
    - Updating the agent's memory (mark_looked_at) when detailed text exists.
    - Returning the detailed description or a no-detail message.

    The target must be a valid object ID (e.g. "obj_ball_01").
    Runtime validation that it is visible happens inside perform_look
    (per the checklist: only objects currently visible in passive vision
    can be looked at).
    """
    return perform_look(agent, world, target)
