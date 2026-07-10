"""Pluggable object interaction handlers (V0.6.1)."""
from __future__ import annotations

from realm_fabric.interaction_handlers.base import InteractionHandler
from realm_fabric.interaction_handlers.registry import (
    format_handlers_list,
    get_handler_registration,
    is_handler_registered,
    list_registered_handlers,
    register_interaction_handler,
    run_interaction_handler,
    validate_handler_params,
)

__all__ = [
    "InteractionHandler",
    "format_handlers_list",
    "get_handler_registration",
    "is_handler_registered",
    "list_registered_handlers",
    "register_interaction_handler",
    "run_interaction_handler",
    "validate_handler_params",
]
