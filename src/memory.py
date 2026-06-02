from dataclasses import dataclass, field
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
class Memory:
    """
    Encapsulates everything an agent remembers in Version 0.

    This includes two main parts (as defined in the readiness checklist):

    1. Recent turn history (last 10 turns, stored as full TurnRecord objects).
    2. Set of objects the agent has "looked at".

    The looked-at set controls passive vision:
    - If an object ID is in the set → the agent sees its full description.
    - Otherwise → the agent sees "[?]" (or the special "has changed" message for the sign).

    By giving each Agent its own Memory instance, we ensure that in future
    versions with multiple agents, one agent's observations do not leak
    to another (e.g. Agent1 looking at the sign does not update Agent2's knowledge).

    This class lives in its own module (memory.py) per the design docs,
    so that the looked-at tracking (and invalidate_look) has clear ownership,
    separate from the Agent dataclass itself.
    """

    _turns: list[TurnRecord] = field(default_factory=list, repr=False)
    """Internal storage for recent history. Use .turns to access a copy."""

    _looked_at: set[str] = field(default_factory=set, repr=False)
    """Internal set of looked-at object IDs."""

    def __post_init__(self):
        # Enforce the V0 limit if someone constructs with more than 10 turns
        if len(self._turns) > 10:
            self._turns = self._turns[-10:]

    # ------------------------------------------------------------------
    # Read-only access to history and looked-at state
    # ------------------------------------------------------------------

    @property
    def turns(self) -> list[TurnRecord]:
        """
        Return a copy of the recent turn history (never more than 10 entries
        in V0).
        """
        return list(self._turns)

    @property
    def looked_at(self) -> set[str]:
        """Return a copy of the set of object IDs the agent has looked at."""
        return set(self._looked_at)

    @property
    def turn_count(self) -> int:
        """How many turns are currently remembered (max 10 in V0)."""
        return len(self._turns)

    def get_recent_turns(self, count: int = 10) -> list[TurnRecord]:
        """
        Return up to the last `count` turns (useful when building prompts
        that include recent history).
        """
        return list(self._turns[-count:])

    # ------------------------------------------------------------------
    # Mutation API
    # ------------------------------------------------------------------

    def add_turn(self, record: TurnRecord) -> None:
        """
        Record a new turn.

        Keeps only the most recent 10 turns (per V0 spec).
        Older turns are discarded (no summarization or compression).
        """
        self._turns.append(record)
        if len(self._turns) > 10:
            self._turns.pop(0)

    def mark_looked_at(self, object_id: str) -> None:
        """
        Mark that the agent has successfully looked at this object.

        After this, passive vision should show the object's real description
        instead of "[?]".
        """
        self._looked_at.add(object_id)

    def has_looked_at(self, object_id: str) -> bool:
        """Return whether the agent has previously looked at this object."""
        return object_id in self._looked_at

    def invalidate_look(self, object_id: str) -> None:
        """
        Remove an object from the looked-at set.

        This is the key method for the special sign update mechanic (see
        readiness checklist "Sign Change Special Case Containment Strategy").

        When the human updates the sign via the debug command, we call this
        so the sign reappears with the "[?]" marker (and the "has changed"
        notification) the next time passive vision is built.
        """
        self._looked_at.discard(object_id)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def reset_looked_at(self) -> None:
        """
        Clear all looked-at knowledge.

        Not expected to be used in normal V0 flow, but useful for testing
        or resetting an agent's observations.
        """
        self._looked_at.clear()
