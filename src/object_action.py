"""Declarative object interaction definitions for V0.2."""

from dataclasses import dataclass, field

from src.effect_spec import EffectSpec


@dataclass
class ObjectAction:
    """One named interaction an agent can perform on an object."""

    name: str
    range: int
    result: str
    passive_result: str
    effects: list[EffectSpec] = field(default_factory=list)
