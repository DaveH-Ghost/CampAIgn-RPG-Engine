"""Shared text formatting for memory module render output."""

from src.memory_modules.base import WitnessedEvent
from src.turn_record import TurnRecord, TurnStep


def format_step(step: TurnStep) -> str:
    label = step.kind
    if step.target:
        label += f" → {step.target}"
    return f"  - {label}: {step.result}"


def format_own_turn(turn: TurnRecord) -> list[str]:
    lines = [f"Turn {turn.turn_number}:"]
    if turn.reasoning:
        lines.append(f"Reasoning: {turn.reasoning}")
    for step in turn.steps:
        lines.append(format_step(step))
    lines.append(f"Result: {turn.result}")
    return lines


def format_witnessed_events(events: list[WitnessedEvent], heading: str) -> list[str]:
    if not events:
        return []
    lines = [heading]
    for event in events:
        pos = f"at {event.actor_position}"
        lines.append(f"  - {event.text} ({event.actor_name} {pos})")
    return lines


def join_lines(lines: list[str]) -> str:
    return "\n".join(lines).rstrip()
