from dataclasses import dataclass
from typing import Optional


@dataclass
class TurnRecord:
    """
    A record of one turn in the agent's history.

    This stores everything the agent needs to remember about what happened
    on a single turn, including both its private reasoning and the result
    returned by the simulation.

    In V0, the agent keeps the last 10 TurnRecords in full detail
    (no summarization or compression).
    """

    turn_number: int
    """The turn number this record belongs to (starting from 1)."""

    action: str
    """The action the agent chose ('move', 'look', or 'speak')."""

    target: Optional[str]
    """What the action was directed at. Meaning depends on the action type."""

    content: Optional[str]
    """Additional content for the action (mainly used for 'speak')."""

    reasoning: str
    """The agent's private internal reasoning at the time of the decision."""

    result: str
    """The feedback string returned to the agent after the action was executed."""


@dataclass
class Agent:
    """
    Represents the single agent in the V0 simulation.

    The agent maintains its own position, personality description,
    and short-term memory of recent turns.
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

    memory: list[TurnRecord]
    """
    The agent's short-term memory.

    In V0 this contains the last 10 turns in full detail.
    Older turns are discarded (no summarization in V0).
    """

    last_action: Optional[str] = None
    """
    The action the agent took on the previous turn.

    This field is retained for potential future use (e.g. richer memory
    systems or prompt conditioning), but is currently underutilized in V0.
    """
