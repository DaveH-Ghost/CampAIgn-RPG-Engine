"""Protocol and shared types for memory modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from src.turn_record import TurnRecord

if TYPE_CHECKING:
    from src.agent import Agent
    from src.world import World


@dataclass(frozen=True)
class WitnessedEvent:
    """Something the observer saw another agent do (from passive_result at commit time)."""

    session_turn: int
    actor_id: str
    actor_name: str
    text: str
    actor_position: tuple[int, int]


@dataclass(frozen=True)
class MemoryRecordContext:
    agent_id: str
    turn_number: int


@dataclass(frozen=True)
class MemoryObserveContext:
    observer_id: str


@dataclass(frozen=True)
class MemoryRenderContext:
    agent: Agent
    world: World


class MemoryModule(Protocol):
    """Prompt memory for one agent. Look knowledge stays on Memory facade."""

    module_id: str

    def record_turn(self, record: TurnRecord, ctx: MemoryRecordContext) -> None:
        """Ingest the observer's own committed turn."""

    def record_observation(self, event: WitnessedEvent, ctx: MemoryObserveContext) -> None:
        """Ingest another agent's observable action this observer witnessed."""

    def render(self, ctx: MemoryRenderContext) -> str:
        """Body text for the Memory: prompt section (no header)."""

    @property
    def total_turns(self) -> int:
        """Monotonic count of this agent's own turns (for TurnRecord numbering)."""

    @property
    def stored_turns(self) -> list[TurnRecord]:
        """Own turns kept in the module window (debug / state command)."""
