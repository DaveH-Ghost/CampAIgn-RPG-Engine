"""Registered prompt slot renderers for plugins (1.2.0)."""

from __future__ import annotations

from campaign_rpg_engine.prompt_slots.registry import (
    clear_prompt_slots_for_tests,
    is_prompt_slot_registered,
    list_registered_prompt_slots,
    register_prompt_slot,
    render_registered_prompt_slot,
)

__all__ = [
    "clear_prompt_slots_for_tests",
    "is_prompt_slot_registered",
    "list_registered_prompt_slots",
    "register_prompt_slot",
    "render_registered_prompt_slot",
]
