"""Interaction handler protocol (V0.6.1)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from realm_fabric.agent import Agent
    from realm_fabric.area import Area
    from realm_fabric.object import Object
    from realm_fabric.object_action import ObjectAction
    from realm_fabric.session import Session


class InteractionHandler(Protocol):
    """App-registered world-change behavior for object interacts and triggers."""

    def __call__(
        self,
        session: Session | None,
        area: Area,
        agent: Agent,
        obj: Object,
        action: ObjectAction,
    ) -> str | None:
        """Return ``None`` on success, or an in-world error string."""
        ...
