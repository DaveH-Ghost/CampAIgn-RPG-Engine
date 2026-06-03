"""
speak.py

Implementation of the `speak` action for V0.

Per the checklist:
- Up to 3 sentences (already enforced by the AgentTurn schema).
- Pure verbal dialogue (emotes etc. rejected by schema).
- No direct mechanical effect on the world.
- The exact text is recorded in the action result as: 'You said: "<text>"'
- Words may still influence the simulation indirectly (e.g. via human updating the sign).
"""

from src.agent import Agent
from src.world import World


def speak(agent: Agent, world: World, content: str) -> str:
    """
    The agent speaks the given content.

    The content has already been validated by the schema (length, sentence count,
    no emotes). We simply record it.

    No changes are made to the world or the agent's position/memory here —
    the result string will be turned into a TurnRecord by the simulation loop.
    """
    # content may be None according to schema, but for speak it should be present.
    text = content or ""
    return f'You said: "{text}"'
