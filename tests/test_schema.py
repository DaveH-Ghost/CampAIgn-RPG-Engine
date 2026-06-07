"""
test_schema.py

Pydantic validation for V0.2 compound turn schemas.
"""

import pytest
from pydantic import ValidationError

from src.llm.schemas import (
    AgentActionTurn,
    AgentNavigationTurn,
    MAX_SPEAK_CHARACTERS,
    count_speak_sentences,
)


def test_valid_navigation_stay():
    turn = AgentNavigationTurn(reasoning="Staying put.", move_target=None)
    assert turn.move_target is None


def test_valid_navigation_move():
    turn = AgentNavigationTurn(reasoning="Going.", move_target="2,4")
    assert turn.move_target == "2,4"


def test_invalid_navigation_cardinal():
    with pytest.raises(ValidationError) as exc_info:
        AgentNavigationTurn(reasoning="Old.", move_target="north")
    assert "ERR:INVALID_TARGET" in str(exc_info.value)


def test_valid_action_speak():
    turn = AgentActionTurn(
        reasoning="Speaking.",
        turn_action="speak",
        content="Hello there.",
    )
    assert turn.turn_action == "speak"


def test_valid_action_look_only():
    turn = AgentActionTurn(
        reasoning="Looking.",
        look_target="obj_ball_01",
        turn_action="none",
    )
    assert turn.look_target == "obj_ball_01"


def test_action_speak_requires_content():
    with pytest.raises(ValidationError):
        AgentActionTurn(reasoning="x", turn_action="speak")


def test_action_interact_requires_fields():
    with pytest.raises(ValidationError):
        AgentActionTurn(reasoning="x", turn_action="interact", target="obj_x")


def test_count_speak_sentences_ellipsis():
    assert count_speak_sentences("Hi! Wait... really?") == 2


def test_speak_500_chars_allowed():
    text = "A" * 400
    turn = AgentActionTurn(reasoning="x", turn_action="speak", content=text)
    assert len(turn.content) == 400


def test_speak_over_500_chars_rejected():
    with pytest.raises(ValidationError) as exc_info:
        AgentActionTurn(
            reasoning="x",
            turn_action="speak",
            content="A" * 501,
        )
    assert "CONTENT_TOO_LONG" in str(exc_info.value)
    assert str(MAX_SPEAK_CHARACTERS) in str(exc_info.value)


def test_reasoning_too_long():
    with pytest.raises(ValidationError) as exc_info:
        AgentNavigationTurn(reasoning="x" * 401, move_target=None)
    assert "REASONING_TOO_LONG" in str(exc_info.value)
