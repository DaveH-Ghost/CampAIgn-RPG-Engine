"""Broadcast observable agent actions to other agents' memory modules."""

from __future__ import annotations

from src.agent import Agent
from src.area import Area
from src.area_event import AREA_EVENT_ACTOR_ID, AREA_EVENT_ACTOR_NAME
from src.emote_phrasing import emote_target_phrase_for_witness, format_emote_line
from src.memory_modules.base import WitnessedEvent
from src.perception import get_visible_look_target_ids
from src.turn_record import TurnStep


def can_observe_agent(observer: Agent, actor: Agent, area: Area) -> bool:
    """Return True if the actor appears in the observer's passive vision."""
    if observer.id == actor.id:
        return False
    return actor.id in get_visible_look_target_ids(observer, area)


def _witness_text_for_emote(
    actor: Agent,
    area: Area,
    emote_step: TurnStep,
    observer: Agent,
) -> str:
    action_name = (emote_step.content or "").strip()
    target = (emote_step.target or "").strip()
    phrase = emote_target_phrase_for_witness(area, target, observer)
    return format_emote_line(actor.name, action_name, phrase)


def broadcast_actor_turn(
    area: Area,
    actor: Agent,
    *,
    session_turn: int,
    emote_step: TurnStep | None = None,
) -> None:
    """
    Record the actor's observable action in each observing agent's memory module.

    Call after the actor's passive_result is set for the turn.
    Emote steps use per-observer target phrasing (``you`` for the emote target).
    """
    if not actor.passive_result and emote_step is None:
        return

    for observer in area.agents:
        if not can_observe_agent(observer, actor, area):
            continue
        if emote_step is not None:
            text = _witness_text_for_emote(actor, area, emote_step, observer)
        else:
            text = actor.passive_result
        if not text:
            continue
        event = WitnessedEvent(
            session_turn=session_turn,
            actor_id=actor.id,
            actor_name=actor.name,
            text=text,
            actor_position=actor.position,
        )
        observer.memory.record_observation(event, observer_id=observer.id)


def broadcast_area_event(
    area: Area,
    *,
    session_turn: int,
    text: str,
) -> None:
    """
    Record a room-wide event in every agent's memory module.

    Uses a pseudo-actor so area events are distinct from agent passive_result.
    """
    event = WitnessedEvent(
        session_turn=session_turn,
        actor_id=AREA_EVENT_ACTOR_ID,
        actor_name=AREA_EVENT_ACTOR_NAME,
        text=text,
        actor_position=(-1, -1),
    )
    for agent in area.agents:
        agent.memory.record_observation(event, observer_id=agent.id)
