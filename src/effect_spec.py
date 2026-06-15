"""Parameterized object interaction effects (V0.4.0d+)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EffectSpec:
    """One registered effect invocation with optional keyword params."""

    name: str
    params: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_name(cls, name: str) -> EffectSpec:
        return cls(name=name)
