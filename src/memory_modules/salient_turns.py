"""Salient-turns memory — retain important turns, render under a character budget."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.memory_modules.base import (
    MemoryObserveContext,
    MemoryRecordContext,
    MemoryRenderContext,
    WitnessedEvent,
)
from src.memory_modules.formatting import (
    format_own_turn,
    format_witnessed_events,
    join_lines,
)
from src.turn_record import TurnRecord

DEFAULT_CHAR_BUDGET = 2500
MIN_CHAR_BUDGET = 200
MAX_CHAR_BUDGET = 8000
DEFAULT_STORAGE_WINDOW = 50
DEFAULT_RECENCY_FLOOR = 2

OMISSION_LINE = "…earlier memories omitted."


def validate_char_budget(value: int) -> None:
    if value < MIN_CHAR_BUDGET or value > MAX_CHAR_BUDGET:
        raise ValueError(
            f"memory-budget must be between {MIN_CHAR_BUDGET} and {MAX_CHAR_BUDGET} "
            f"(got {value})."
        )


def score_turn(turn: TurnRecord, witnessed_before: list[WitnessedEvent]) -> int:
    """Higher score = more important to retain."""
    score = 0
    if witnessed_before:
        score += 1
    for step in turn.steps:
        if step.kind in ("speak", "interact"):
            score += 3
        elif step.kind == "look":
            score += 2
    return score


@dataclass
class _RenderBlock:
    order: int
    text: str
    salience: int
    in_recency_floor: bool


@dataclass
class SalientTurnsModule:
    """
    Ingest like recent_turns; retain by salience in storage; render chronologically
    within ``char_budget`` (recency floor first, then highest salience).
    """

    module_id: str = "salient_turns"
    char_budget: int = DEFAULT_CHAR_BUDGET
    storage_window: int = DEFAULT_STORAGE_WINDOW
    recency_floor: int = DEFAULT_RECENCY_FLOOR

    _turns: list[TurnRecord] = field(default_factory=list, repr=False)
    _witnessed_before: list[list[WitnessedEvent]] = field(default_factory=list, repr=False)
    _salience_scores: list[int] = field(default_factory=list, repr=False)
    _pending: list[WitnessedEvent] = field(default_factory=list, repr=False)
    _total_turns: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        validate_char_budget(self.char_budget)
        if self.recency_floor < 1:
            raise ValueError("recency_floor must be at least 1")
        if self.storage_window < self.recency_floor:
            raise ValueError("storage_window must be >= recency_floor")

    def record_turn(self, record: TurnRecord, ctx: MemoryRecordContext) -> None:
        del ctx
        witnessed = list(self._pending)
        self._pending.clear()
        self._witnessed_before.append(witnessed)
        self._turns.append(record)
        self._salience_scores.append(score_turn(record, witnessed))
        self._total_turns += 1
        self._evict_storage_if_needed()

    def record_observation(self, event: WitnessedEvent, ctx: MemoryObserveContext) -> None:
        del ctx
        self._pending.append(event)

    def render(self, ctx: MemoryRenderContext) -> str:
        del ctx
        blocks = self._build_render_blocks()
        if not blocks:
            return ""
        selected = self._select_blocks_for_budget(blocks)
        if not selected:
            return blocks[-1].text if blocks else ""

        selected.sort(key=lambda block: block.order)
        lines: list[str] = []
        if selected[0].order > 0:
            lines.append(OMISSION_LINE)
            lines.append("")

        for index, block in enumerate(selected):
            if index > 0:
                lines.append("")
            lines.append(block.text)

        return join_lines(lines)

    def _build_render_blocks(self) -> list[_RenderBlock]:
        blocks: list[_RenderBlock] = []
        order = 0
        recency_start = max(0, len(self._turns) - self.recency_floor)

        for index, turn in enumerate(self._turns):
            witnessed = (
                self._witnessed_before[index]
                if index < len(self._witnessed_before)
                else []
            )
            parts: list[str] = []
            if witnessed:
                parts.extend(
                    format_witnessed_events(
                        witnessed,
                        f"Before turn {turn.turn_number}, you observed:",
                    )
                )
                parts.append("")
            parts.extend(format_own_turn(turn))
            blocks.append(
                _RenderBlock(
                    order=order,
                    text=join_lines(parts),
                    salience=self._salience_scores[index],
                    in_recency_floor=index >= recency_start,
                )
            )
            order += 1

        if self._pending:
            if self._turns:
                heading = f"Since turn {self._turns[-1].turn_number}, you observed:"
            else:
                heading = "You observed:"
            blocks.append(
                _RenderBlock(
                    order=order,
                    text=join_lines(format_witnessed_events(self._pending, heading)),
                    salience=1,
                    in_recency_floor=True,
                )
            )
        return blocks

    def _select_blocks_for_budget(self, blocks: list[_RenderBlock]) -> list[_RenderBlock]:
        selected: list[_RenderBlock] = []
        used = 0

        def try_add(block: _RenderBlock) -> bool:
            nonlocal used
            extra = 2 if selected else 0  # blank line between blocks
            cost = len(block.text) + extra
            if selected and used + cost > self.char_budget:
                return False
            if not selected and cost > self.char_budget:
                selected.append(block)
                used = cost
                return True
            if used + cost > self.char_budget:
                return False
            selected.append(block)
            used += cost
            return True

        recency = [block for block in blocks if block.in_recency_floor]
        for block in sorted(recency, key=lambda item: item.order, reverse=True):
            try_add(block)

        remaining = [block for block in blocks if block not in selected]
        remaining.sort(key=lambda item: (-item.salience, -item.order))
        for block in remaining:
            try_add(block)

        return selected

    def _evict_storage_if_needed(self) -> None:
        while len(self._turns) > self.storage_window:
            protected = set(
                range(max(0, len(self._turns) - self.recency_floor), len(self._turns))
            )
            evict_index = None
            evict_score = None
            for index in range(len(self._turns)):
                if index in protected:
                    continue
                score = self._salience_scores[index]
                if evict_score is None or score < evict_score:
                    evict_score = score
                    evict_index = index
            if evict_index is None:
                break
            self._turns.pop(evict_index)
            self._witnessed_before.pop(evict_index)
            self._salience_scores.pop(evict_index)

    @property
    def total_turns(self) -> int:
        return self._total_turns

    @property
    def stored_turns(self) -> list[TurnRecord]:
        return list(self._turns)
