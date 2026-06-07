from dataclasses import dataclass, field
from typing import Literal, Optional


StepKind = Literal["move", "look", "speak", "interact"]


@dataclass
class TurnStep:
    """One sub-step inside a compound agent turn (V0.2.5 ingestion hook)."""

    kind: StepKind
    reasoning: str
    target: Optional[str]
    content: Optional[str]
    result: str
    passive_result: str = ""


@dataclass
class TurnRecord:
    """
    A record of one compound agent turn in the agent's history.

    V0.2: one TurnRecord per agent turn (move + optional look + optional turn action).
    """

    turn_number: int
    steps: list[TurnStep]
    result: str
    reasoning: str


@dataclass
class Memory:
    """
    Encapsulates everything an agent remembers in Version 0.

    This includes three main parts:

    1. Recent turn history (last 10 compound turns, stored as full TurnRecord objects).
    2. `looked_at` — objects the agent has up-to-date knowledge of.
    3. `ever_looked` — objects the agent has looked at at least once (V0.1).

    Look knowledge controls passive vision (see `perception.format_vision_desc`):
    - `looked_at` → detailed `desc` (or passive if no detailed).
    - `ever_looked` without `looked_at` (and detailed exists) → stale `[?] [changed]` (+ passive if set).
    - Otherwise → `[?]` or `[?] {passive}` / passive only, depending on object fields.

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
    """Object IDs the agent has up-to-date knowledge of."""

    _ever_looked: set[str] = field(default_factory=set, repr=False)
    """Object IDs the agent has looked at at least once (never cleared on invalidate)."""

    def __post_init__(self):
        if len(self._turns) > 10:
            self._turns = self._turns[-10:]

    @property
    def turns(self) -> list[TurnRecord]:
        """Return a copy of the recent turn history (never more than 10 entries)."""
        return list(self._turns)

    @property
    def looked_at(self) -> set[str]:
        """Return a copy of object IDs with up-to-date knowledge."""
        return set(self._looked_at)

    @property
    def ever_looked(self) -> set[str]:
        """Return a copy of object IDs the agent has ever successfully looked at."""
        return set(self._ever_looked)

    @property
    def turn_count(self) -> int:
        """How many turns are currently remembered (max 10 in V0)."""
        return len(self._turns)

    def get_recent_turns(self, count: int = 10) -> list[TurnRecord]:
        """Return up to the last `count` turns (useful when building prompts)."""
        return list(self._turns[-count:])

    def add_turn(self, record: TurnRecord) -> None:
        """Record a new turn. Keeps only the most recent 10 turns."""
        self._turns.append(record)
        if len(self._turns) > 10:
            self._turns.pop(0)

    def mark_looked_at(self, object_id: str) -> None:
        """Mark that the agent has successfully looked at this object."""
        self._looked_at.add(object_id)
        self._ever_looked.add(object_id)

    def has_looked_at(self, object_id: str) -> bool:
        """Return whether the agent has up-to-date knowledge of this object."""
        return object_id in self._looked_at

    def has_ever_looked_at(self, object_id: str) -> bool:
        """Return whether the agent has ever successfully looked at this object."""
        return object_id in self._ever_looked

    def invalidate_look(self, object_id: str) -> None:
        """Remove up-to-date knowledge for an object (e.g. after its description changed)."""
        self._looked_at.discard(object_id)

    def clear_examination(self, object_id: str) -> None:
        """Remove both current and historical look knowledge for an object."""
        self._looked_at.discard(object_id)
        self._ever_looked.discard(object_id)

    def reset_looked_at(self) -> None:
        """Clear all look knowledge (useful for testing)."""
        self._looked_at.clear()
        self._ever_looked.clear()
