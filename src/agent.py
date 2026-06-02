from dataclasses import dataclass, field
from typing import Optional

from .memory import Memory, TurnRecord


@dataclass
class Agent:
    """
    Represents the single agent in the V0 simulation.

    The agent maintains its own position, personality description,
    and short-term memory.
    """

    id: str
    """Unique identifier for the agent."""

    name: str
    """Display name of the agent (used in prompts and logging)."""

    description: str
    """
    Core personality / character description.

    This text is injected into the prompt every turn so the agent
    stays in character and behaves consistently.
    """

    position: tuple[int, int]
    """Current grid position of the agent as (x, y)."""

    memory: Memory = field(default_factory=Memory)
    """
    The agent's memory.

    This is a Memory instance that holds:
    - The last 10 turns (as TurnRecord objects)
    - The set of objects the agent has looked at

    Each agent gets its own Memory instance so that in future versions
    with multiple agents, one agent's observations do not affect another's.
    """

    last_action: Optional[str] = None
    """
    The action the agent took on the previous turn.

    This field is retained for potential future use (e.g. richer memory
    systems or prompt conditioning), but is currently underutilized in V0.
    """
