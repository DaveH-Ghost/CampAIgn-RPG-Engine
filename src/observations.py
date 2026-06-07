"""Broadcast observable agent actions to other agents' memory modules."""

from src.agent import Agent
from src.memory_modules.base import WitnessedEvent
from src.perception import get_visible_look_target_ids
from src.world import World


def can_observe_agent(observer: Agent, actor: Agent, world: World) -> bool:
    """Return True if the actor appears in the observer's passive vision."""
    if observer.id == actor.id:
        return False
    return actor.id in get_visible_look_target_ids(observer, world)


def broadcast_actor_turn(
    world: World,
    actor: Agent,
    *,
    session_turn: int,
) -> None:
    """
    Record the actor's passive_result in each observing agent's memory module.

    Call after the actor's passive_result is set for the turn.
    """
    if not actor.passive_result:
        return

    event = WitnessedEvent(
        session_turn=session_turn,
        actor_id=actor.id,
        actor_name=actor.name,
        text=actor.passive_result,
        actor_position=actor.position,
    )

    for observer in world.agents:
        if not can_observe_agent(observer, actor, world):
            continue
        observer.memory.record_observation(event, observer_id=observer.id)
