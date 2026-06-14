"""
test_schema.py

Pydantic validation for V0.2.5 compound turn schema.
"""

import pytest
from pydantic import ValidationError

from src.llm.schemas import (
    AgentCompoundTurn,
    MAX_SPEAK_CHARACTERS,
    count_speak_sentences,
)


def test_valid_compound_stay_and_speak():
    turn = AgentCompoundTurn(
        reasoning="Staying put.",
        move_target=None,
        turn_action="speak",
        content="Hello.",
    )
    assert turn.move_target is None
    assert turn.turn_action == "speak"


def test_valid_compound_move():
    turn = AgentCompoundTurn(
        reasoning="Going.",
        move_target="2,4",
        turn_action="none",
    )
    assert turn.move_target == "2,4"


def test_valid_compound_move_to_entity_id():
    turn = AgentCompoundTurn(
        reasoning="To the ball.",
        move_target="obj_ball_01",
        turn_action="none",
    )
    assert turn.move_target == "obj_ball_01"


def test_invalid_compound_cardinal_move():
    with pytest.raises(ValidationError) as exc_info:
        AgentCompoundTurn(
            reasoning="Old.",
            move_target="north",
            turn_action="none",
        )
    assert "ERR:INVALID_TARGET" in str(exc_info.value)


def test_valid_compound_speak():
    turn = AgentCompoundTurn(
        reasoning="Speaking.",
        turn_action="speak",
        content="Hello there.",
    )
    assert turn.turn_action == "speak"


def test_valid_compound_look_only():
    turn = AgentCompoundTurn(
        reasoning="Looking.",
        look_target="obj_ball_01",
        turn_action="none",
    )
    assert turn.look_target == "obj_ball_01"


def test_compound_speak_requires_content():
    with pytest.raises(ValidationError):
        AgentCompoundTurn(reasoning="x", turn_action="speak")


def test_compound_interact_requires_fields():
    with pytest.raises(ValidationError):
        AgentCompoundTurn(reasoning="x", turn_action="interact", target="obj_x")


def test_count_speak_sentences_ellipsis():
    assert count_speak_sentences("Hi! Wait... really?") == 2


def test_speak_500_chars_allowed():
    text = "A" * 400
    turn = AgentCompoundTurn(reasoning="x", turn_action="speak", content=text)
    assert len(turn.content) == 400


def test_speak_over_500_chars_rejected():
    with pytest.raises(ValidationError) as exc_info:
        AgentCompoundTurn(
            reasoning="x",
            turn_action="speak",
            content="A" * 501,
        )
    assert "CONTENT_TOO_LONG" in str(exc_info.value)
    assert str(MAX_SPEAK_CHARACTERS) in str(exc_info.value)


def test_reasoning_too_long():
    with pytest.raises(ValidationError) as exc_info:
        AgentCompoundTurn(reasoning="x" * 401, turn_action="none")
    assert "REASONING_TOO_LONG" in str(exc_info.value)
