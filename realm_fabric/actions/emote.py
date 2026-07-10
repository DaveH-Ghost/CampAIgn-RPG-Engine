"""Emote turn action — gesture at an entity or free-text target (V0.4.2)."""

from __future__ import annotations

from realm_fabric.action_outcome import ActionOutcome
from realm_fabric.agent import Agent
from realm_fabric.area import Area
from realm_fabric.emote_phrasing import (
    emote_target_phrase_for_actor,
    emote_target_phrase_neutral,
    format_emote_line,
)


def emote(agent: Agent, area: Area, target: str, action_name: str) -> ActionOutcome:
    """Perform a past-tense emote directed at *target*."""
    verb = action_name.strip()
    target_id = target.strip()
    actor_phrase = emote_target_phrase_for_actor(area, agent, target_id)
    neutral_phrase = emote_target_phrase_neutral(area, target_id)
    return ActionOutcome(
        result=f"You {verb} at {actor_phrase}.",
        passive_result=format_emote_line(agent.name, verb, neutral_phrase),
    )
