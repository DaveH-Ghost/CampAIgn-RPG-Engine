"""
test_schema.py

Pydantic validation for V0.2.5 compound turn schema.
"""

import pytest
from pydantic import ValidationError

from src.llm.schemas import (
    AgentCompoundTurn,
    count_speak_sentences,
)


def test_valid_compound_stay_and_speak():
    turn = AgentCompoundTurn(
        reasoning="Staying put.",
        move_target=None,
        turn_action="none",
        content="Hello.",
    )
    assert turn.move_target is None
    assert turn.content == "Hello."


def test_valid_compound_speak_and_interact():
    turn = AgentCompoundTurn(
        reasoning="Talk and act.",
        content="Hello.",
        turn_action="interact",
        target="obj_cookie_01",
        action_name="eat",
    )
    assert turn.content == "Hello."
    assert turn.turn_action == "interact"


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
        turn_action="none",
        content="Hello there.",
    )
    assert turn.content == "Hello there."


def test_compound_rejects_legacy_speak_turn_action():
    with pytest.raises(ValidationError):
        AgentCompoundTurn(reasoning="x", turn_action="speak", content="Hi")


def test_valid_compound_look_only():
    turn = AgentCompoundTurn(
        reasoning="Looking.",
        look_target="obj_ball_01",
        turn_action="none",
    )
    assert turn.look_target == "obj_ball_01"


def test_compound_interact_requires_fields():
    with pytest.raises(ValidationError):
        AgentCompoundTurn(reasoning="x", turn_action="interact", target="obj_x")


def test_count_speak_sentences_ellipsis():
    assert count_speak_sentences("Hi! Wait... really?") == 2


def test_speak_truncated_when_later_sentence_starts_after_budget():
    first = "A" * 498 + ". "
    second = "B" * 50
    turn = AgentCompoundTurn(
        reasoning="x",
        turn_action="none",
        content=first + second,
    )
    assert turn.content == "A" * 498 + "."
    assert "B" not in turn.content


def test_speak_single_long_sentence_not_cut_mid_sentence():
    text = "A" * 501
    turn = AgentCompoundTurn(reasoning="x", turn_action="none", content=text)
    assert len(turn.content) == 501


def test_reasoning_truncated_drops_late_sentences():
    first = "a" * 398 + ". "
    second = "b" * 100
    turn = AgentCompoundTurn(reasoning=first + second, turn_action="none")
    assert turn.reasoning == "a" * 398 + "."
