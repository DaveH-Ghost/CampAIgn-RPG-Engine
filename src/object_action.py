"""Declarative object interaction definitions for V0.2."""

from dataclasses import dataclass, field
from typing import Literal

from src.effect_spec import EffectSpec

ActionKind = Literal["interact", "trigger"]


@dataclass
class ObjectAction:
    """One named interaction or trigger on an object."""

    name: str
    range: int
    result: str
    passive_result: str
    effects: list[EffectSpec] = field(default_factory=list)
    kind: ActionKind = "interact"
    """``interact`` — LLM compound-turn action; ``trigger`` — engine path step."""

    halt_movement: bool = False
    """When ``kind`` is ``trigger``, stop the mover on the firing tile."""

    delete_after_trigger: bool = True
    """When ``kind`` is ``trigger``, remove the object after it fires."""

    trigger_exceptions: list[str] = field(default_factory=list)
    """Agent ids that do not fire this trigger."""
