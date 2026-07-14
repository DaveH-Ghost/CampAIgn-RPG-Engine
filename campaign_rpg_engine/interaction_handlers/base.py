"""Interaction handler protocol (V0.6.1 / 1.4.1)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from campaign_rpg_engine.action_outcome import ActionOutcome
    from campaign_rpg_engine.agent import Agent
    from campaign_rpg_engine.area import Area
    from campaign_rpg_engine.object import Object
    from campaign_rpg_engine.object_action import ObjectAction
    from campaign_rpg_engine.session import Session


class InteractionHandler(Protocol):
    """App-registered world-change behavior for object interacts and triggers."""

    def __call__(
        self,
        session: Session | None,
        area: Area,
        agent: Agent,
        obj: Object,
        action: ObjectAction,
    ) -> ActionOutcome | str | None:
        """
        Return value meaning (1.4.1):

        - ``None`` — success; interact uses ``action.result`` / ``action.passive_result``
        - ``str`` — abort; actor-only error, empty passive
        - ``ActionOutcome`` — final interact outcome (skips success templates)
        """
        ...
