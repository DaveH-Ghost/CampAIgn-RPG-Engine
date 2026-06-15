"""
interact.py

Declarative object interactions for V0.2 Section 3.

Result/passive templates support placeholders documented in
``src.interact_templates`` (e.g. ``{actor}``, ``{object}``, ``{object_start}``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.action_outcome import ActionOutcome
from src.agent import Agent
from src.grid import chebyshev_distance
from src.interact_templates import InteractTemplateContext, format_interact_template
from src.object import Object
from src.object_action import ObjectAction
from src.object_effects import EffectContext, apply_effects
from src.perception import is_object_in_passive_vision
from src.area import Area

if TYPE_CHECKING:
    from src.session import Session


def _resolve_agent_area(
    session: Session | None,
    agent_id: str,
    fallback: str | None,
) -> str:
    if session is not None:
        return session.agent_area.get(agent_id) or fallback or ""
    return fallback or ""


def interact(
    agent: Agent,
    area: Area,
    target_id: str,
    action_name: str,
    *,
    session: Session | None = None,
    source_area_id: str | None = None,
) -> ActionOutcome:
    """Execute an object interaction from the action phase."""
    obj = area.get_object_by_id(target_id)
    if obj is None:
        return ActionOutcome(result="That object does not exist.")

    action = obj.actions.get(action_name)
    if action is None:
        return ActionOutcome(
            result=(
                f"'{action_name}' is not an action you can perform on {obj.name}."
            ),
        )

    if not is_object_in_passive_vision(agent, area, target_id):
        return ActionOutcome(
            result=f"You can't reach {obj.name} from here.",
        )

    if not _in_range(agent, obj, action):
        return ActionOutcome(
            result=(
                f"Unfortunately you are too far from {obj.name} to {action_name}."
            ),
        )

    object_area = source_area_id or ""
    actor_start_area = _resolve_agent_area(session, agent.id, source_area_id)
    object_start = obj.position
    actor_start = agent.position

    if action.effects:
        ctx = EffectContext(
            area=area,
            session=session,
            source_area_id=source_area_id,
        )
        effect_err = apply_effects(ctx, agent, obj, list(action.effects))
        if effect_err:
            return ActionOutcome(result=effect_err)

    template_ctx = InteractTemplateContext(
        actor=agent.name,
        object_name=obj.name,
        object_start=object_start,
        object_end=obj.position,
        actor_start=actor_start,
        actor_end=agent.position,
        object_start_area=object_area,
        object_end_area=object_area,
        actor_start_area=actor_start_area,
        actor_end_area=_resolve_agent_area(session, agent.id, source_area_id),
    )
    return ActionOutcome(
        result=format_interact_template(action.result, template_ctx),
        passive_result=format_interact_template(action.passive_result, template_ctx),
    )


def _in_range(agent: Agent, obj: Object, action: ObjectAction) -> bool:
    return chebyshev_distance(agent.position, obj.position) <= action.range
