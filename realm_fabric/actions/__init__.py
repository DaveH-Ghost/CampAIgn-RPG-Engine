"""
Actions package.

Contains move, speak, and interact implementations. Look is implemented in
perception.py (perform_look) because it shares vision/memory logic.
"""
from __future__ import annotations

from realm_fabric.actions.emote import emote as do_emote
from realm_fabric.actions.interact import interact as do_interact
from realm_fabric.actions.interact import interact_phases as do_interact_phases
from realm_fabric.actions.move import move as do_move
from realm_fabric.actions.speak import speak as do_speak

__all__ = ["do_emote", "do_interact", "do_interact_phases", "do_move", "do_speak"]
