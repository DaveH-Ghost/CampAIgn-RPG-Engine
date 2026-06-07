"""
test_simulation.py

Compound turn simulation tests.
"""

import pytest

from src.llm.prompt import build_navigation_prompt
from src.llm.schemas import AgentActionTurn, AgentNavigationTurn
from src.simulation import next_turn_number_for_agent, run_compound_turn
from src.world import create_initial_world


def nav(move_target=None, reasoning="Test reasoning.") -> AgentNavigationTurn:
    return AgentNavigationTurn(reasoning=reasoning, move_target=move_target)


def action(**kwargs) -> AgentActionTurn:
    defaults = {"reasoning": "Test reasoning.", "turn_action": "none"}
    defaults.update(kwargs)
    return AgentActionTurn(**defaults)


def test_compound_turn_creates_and_records_turn_record():
    world = create_initial_world()
    agent = world.get_agent()

    record = run_compound_turn(
        agent,
        world,
        nav(),
        action(look_target="obj_ball_01"),
        turn_number=1,
    )

    assert record.turn_number == 1
    assert record.steps[0].kind == "look"
    assert record.steps[0].target == "obj_ball_01"
    assert "You looked at" in record.result
    assert len(agent.memory.turns) == 1
    assert agent.last_action == "look"


def test_compound_preserves_reasoning():
    world = create_initial_world()
    agent = world.get_agent()

    record = run_compound_turn(
        agent,
        world,
        nav(reasoning="Nav thoughts."),
        action(reasoning="Action thoughts.", look_target="obj_ball_01"),
        turn_number=42,
    )

    assert record.nav_reasoning == "Nav thoughts."
    assert record.action_reasoning == "Action thoughts."


def test_compound_move_success():
    world = create_initial_world()
    agent = world.get_agent()

    record = run_compound_turn(
        agent, world, nav("2,3"), action(), turn_number=1
    )

    assert agent.position == (2, 3)
    assert record.result == "You moved to (2, 3)."
    assert agent.passive_result == "Explorer moves to (2, 3)."


def test_compound_move_failure_off_grid():
    world = create_initial_world()
    agent = world.get_agent()

    record = run_compound_turn(
        agent, world, nav("5,5"), action(), turn_number=1
    )

    assert agent.position == (1, 1)
    assert "outside the room" in record.result.lower()
    assert agent.last_action == "move"


def test_compound_look_marks_object():
    world = create_initial_world()
    agent = world.get_agent()
    assert not agent.memory.has_looked_at("obj_ball_01")

    run_compound_turn(
        agent,
        world,
        nav(),
        action(look_target="obj_ball_01"),
        turn_number=1,
    )

    assert agent.memory.has_looked_at("obj_ball_01")


def test_compound_speak_records_text():
    world = create_initial_world()
    agent = world.get_agent()
    spoken = "This ball feels familiar."

    record = run_compound_turn(
        agent,
        world,
        nav(),
        action(turn_action="speak", content=spoken),
        turn_number=1,
    )

    assert f'You said: "{spoken}"' in record.result
    assert agent.position == (1, 1)


def test_multiple_compound_turns_accumulate():
    world = create_initial_world()
    agent = world.get_agent()

    for i in range(5):
        run_compound_turn(
            agent,
            world,
            nav("2,1"),
            action(),
            turn_number=i + 1,
        )

    assert len(agent.memory.turns) == 5
    assert agent.last_action == "move"


def test_build_navigation_prompt_sections():
    world = create_initial_world()
    agent = world.get_agent()
    prompt = build_navigation_prompt(agent, world, include_examples=True)

    assert "You are Explorer" in prompt
    assert "navigation phase" in prompt.lower()
    assert "move_target" in prompt
    assert "Example 1: Move" in prompt
