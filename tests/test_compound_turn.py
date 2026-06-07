"""
test_compound_turn.py

V0.2 Section 2: compound agent turns.
"""

import pytest

from src.llm.prompt import build_action_prompt, build_navigation_prompt
from src.llm.schemas import AgentActionTurn, AgentNavigationTurn
from src.perception import build_passive_vision
from src.simulation import (
    execute_action_phase,
    execute_nav_phase,
    next_turn_number_for_agent,
    run_compound_turn,
)
from src.world import create_initial_world
from src.world_edit import create_agent_from_args
from src.compound_stepper import parse_compound_step_arg


def nav(move_target=None, reasoning="nav") -> AgentNavigationTurn:
    return AgentNavigationTurn(reasoning=reasoning, move_target=move_target)


def action(
    *,
    look_target=None,
    turn_action="none",
    content=None,
    reasoning="action",
    confidence=None,
    emotion=None,
) -> AgentActionTurn:
    return AgentActionTurn(
        reasoning=reasoning,
        look_target=look_target,
        turn_action=turn_action,
        content=content,
        confidence=confidence,
        emotion=emotion,
    )


def test_nav_null_action_speak_only():
    world = create_initial_world()
    agent = world.get_agent()
    start = agent.position

    record = run_compound_turn(
        agent,
        world,
        nav(None),
        action(turn_action="speak", content="Hello."),
        turn_number=1,
    )

    assert agent.position == start
    assert len(record.steps) == 1
    assert record.steps[0].kind == "speak"
    assert agent.memory.turn_count == 1


def test_move_look_speak_in_order():
    world = create_initial_world()
    agent = world.get_agent()

    record = run_compound_turn(
        agent,
        world,
        nav("2,3"),
        action(look_target="obj_ball_01", turn_action="speak", content="Hi."),
        turn_number=1,
    )

    assert agent.position == (2, 3)
    kinds = [s.kind for s in record.steps]
    assert kinds == ["move", "look", "speak"]
    assert agent.memory.has_looked_at("obj_ball_01")


def test_post_move_look_on_same_tile_as_object():
    """After moving onto the ball's tile, look succeeds with full detail."""
    world = create_initial_world()
    agent = world.get_agent()

    execute_nav_phase(agent, world, nav("2,2"))
    steps = execute_action_phase(
        agent, world, action(look_target="obj_ball_01", turn_action="none")
    )
    assert steps[0].result.startswith("You looked at")
    assert "scuffs" in steps[0].result


def test_invalid_look_after_valid_move_keeps_move():
    world = create_initial_world()
    agent = world.get_agent()

    record = run_compound_turn(
        agent,
        world,
        nav("2,3"),
        action(look_target="obj_missing_99", turn_action="none"),
        turn_number=1,
    )

    assert agent.position == (2, 3)
    assert record.steps[0].kind == "move"
    assert "don't see" in record.steps[1].result.lower()


def test_partial_turn_when_action_none():
    world = create_initial_world()
    agent = world.get_agent()

    nav_steps = execute_nav_phase(agent, world, nav("2,1"))
    record = run_compound_turn(
        agent, world, nav("2,1"), None, turn_number=1, nav_steps=nav_steps
    )

    assert len(record.steps) == 1
    assert agent.position == (2, 1)
    assert agent.memory.turn_count == 1


def test_turn_record_has_structured_steps():
    world = create_initial_world()
    agent = world.get_agent()

    record = run_compound_turn(
        agent,
        world,
        nav("2,3"),
        action(look_target="obj_ball_01", turn_action="speak", content="Hi."),
        turn_number=1,
    )

    assert record.nav_reasoning == "nav"
    assert record.action_reasoning == "action"
    assert len(record.steps) == 3
    assert "\n" in record.result


def test_passive_result_look_wins_over_move():
    world = create_initial_world()
    agent = world.get_agent()

    run_compound_turn(
        agent,
        world,
        nav("2,2"),
        action(look_target="obj_ball_01", turn_action="none"),
        turn_number=1,
    )

    assert "examines" in agent.passive_result
    assert "moves to" not in agent.passive_result


def test_passive_result_speak_wins_over_move_and_look():
    world = create_initial_world()
    explorer = world.get_agent()
    create_agent_from_args(
        world,
        'name "Goblin" pdesc "A goblin." desc "x" personality "x" at 0,3',
    )
    goblin = world.get_agent_by_name("Goblin")
    goblin.position = (1, 1)

    run_compound_turn(
        goblin,
        world,
        nav("2,3"),
        action(look_target="obj_ball_01", turn_action="speak", content="Hi."),
        next_turn_number_for_agent(goblin),
    )

    vision = build_passive_vision(explorer, world)
    assert "Goblin (agent_goblin_01), (2, 3)" in vision
    assert 'Goblin says: "Hi."' in vision
    assert "moves to" not in vision
    assert "examines" not in vision


def test_step_compound_parser():
    parsed = parse_compound_step_arg('2,3 look obj_ball_01 speak Hello.')
    assert parsed.nav.move_target == "2,3"
    assert parsed.action.look_target == "obj_ball_01"
    assert parsed.action.content == "Hello."
    assert parsed.action.turn_action == "speak"

    stay = parse_compound_step_arg("- look obj_ball_01")
    assert stay.nav.move_target is None

    interact = parse_compound_step_arg("2,3 interact obj_cookie_01 eat")
    assert interact.nav.move_target == "2,3"
    assert interact.action.turn_action == "interact"
    assert interact.action.target == "obj_cookie_01"
    assert interact.action.action_name == "eat"


def test_navigation_and_action_prompts_exist():
    world = create_initial_world()
    agent = world.get_agent()
    nav_p = build_navigation_prompt(agent, world)
    act_p = build_action_prompt(agent, world)
    assert "navigation phase" in nav_p.lower()
    assert "action phase" in act_p.lower()
    assert "move_target" in nav_p
    assert "turn_action" in act_p
    assert "move_target" in nav_p
