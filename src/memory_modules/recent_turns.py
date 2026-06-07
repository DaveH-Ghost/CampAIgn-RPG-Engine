"""Recent-turns memory module — last N own turns plus witnessed agent actions."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.turn_record import TurnRecord, TurnStep
from src.memory_modules.base import (
    MemoryObserveContext,
    MemoryRecordContext,
    MemoryRenderContext,
    WitnessedEvent,
)


def _format_step(step: TurnStep) -> str:
    label = step.kind
    if step.target:
        label += f" → {step.target}"
    return f"  - {label}: {step.result}"


def _format_own_turn(turn: TurnRecord) -> list[str]:
    lines = [f"Turn {turn.turn_number}:"]
    if turn.reasoning:
        lines.append(f"Reasoning: {turn.reasoning}")
    for step in turn.steps:
        lines.append(_format_step(step))
    lines.append(f"Result: {turn.result}")
    return lines


def _format_witnessed_events(events: list[WitnessedEvent], heading: str) -> list[str]:
    if not events:
        return []
    lines = [heading]
    for event in events:
        pos = f"at {event.actor_position}"
        lines.append(f"  - {event.text} ({event.actor_name} {pos})")
    return lines


@dataclass
class RecentTurnsModule:
    """
    Keep the last ``window`` own turns and witnessed other-agent actions
    between those turns.
    """

    module_id: str = "recent_turns"
    window: int = 10

    _turns: list[TurnRecord] = field(default_factory=list, repr=False)
    _witnessed_before: list[list[WitnessedEvent]] = field(default_factory=list, repr=False)
    _pending: list[WitnessedEvent] = field(default_factory=list, repr=False)
    _total_turns: int = field(default=0, repr=False)

    def record_turn(self, record: TurnRecord, ctx: MemoryRecordContext) -> None:
        del ctx  # reserved for future module config
        self._witnessed_before.append(list(self._pending))
        self._pending.clear()
        self._turns.append(record)
        self._total_turns += 1
        while len(self._turns) > self.window:
            self._turns.pop(0)
            self._witnessed_before.pop(0)

    def record_observation(self, event: WitnessedEvent, ctx: MemoryObserveContext) -> None:
        del ctx
        self._pending.append(event)

    def render(self, ctx: MemoryRenderContext) -> str:
        del ctx
        if not self._turns and not self._pending:
            return ""

        lines: list[str] = []
        for index, turn in enumerate(self._turns):
            witnessed = self._witnessed_before[index] if index < len(self._witnessed_before) else []
            if witnessed:
                lines.extend(
                    _format_witnessed_events(
                        witnessed,
                        f"Before turn {turn.turn_number}, you observed:",
                    )
                )
                lines.append("")
            lines.extend(_format_own_turn(turn))
            lines.append("")

        if self._pending:
            if self._turns:
                heading = f"Since turn {self._turns[-1].turn_number}, you observed:"
            else:
                heading = "You observed:"
            lines.extend(_format_witnessed_events(self._pending, heading))

        return "\n".join(lines).rstrip()

    @property
    def total_turns(self) -> int:
        return self._total_turns

    @property
    def stored_turns(self) -> list[TurnRecord]:
        return list(self._turns)
