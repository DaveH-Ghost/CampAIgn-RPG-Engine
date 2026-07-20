"""Interact pathing vs explicit compound move (V0.6.0b / positioning fix)."""

from campaign_rpg_engine.area import create_initial_area
from campaign_rpg_engine.llm.schemas import AgentCompoundTurn
from campaign_rpg_engine.session import Session
from campaign_rpg_engine.simulation import execute_nav_phase


def test_nav_phase_skips_move_when_interact_out_of_range():
    """Explicit move that would not reach interact range is ignored (interact paths)."""
    area = create_initial_area()
    agent = area.get_agent()
    agent.position = (0, 0)
    agent.move_speed = 2

    steps = execute_nav_phase(
        agent,
        area,
        AgentCompoundTurn(
            reasoning="kick",
            move="0,1",
            action="interact",
            target="obj_ball_01",
            verb="kick",
        ),
    )

    assert steps == []
    assert agent.position == (0, 0)


def test_nav_phase_honors_move_when_interact_would_reach():
    """Explicit move that lands in interact range runs as the nav step."""
    area = create_initial_area()
    agent = area.get_agent()
    agent.position = (0, 0)
    agent.move_speed = 4

    steps = execute_nav_phase(
        agent,
        area,
        AgentCompoundTurn(
            reasoning="approach from the east",
            move="3,2",
            action="interact",
            target="obj_ball_01",
            verb="kick",
        ),
    )

    assert len(steps) == 1
    assert steps[0].kind == "move"
    assert agent.position == (3, 2)


def test_interact_paths_then_kicks_ball():
    session = Session.from_default()
    agent = session.get_active_agent()
    agent.position = (0, 0)
    agent.move_speed = 3

    record = session.run_compound_turn(
        AgentCompoundTurn(
            reasoning="kick from afar",
            move="0,0",
            action="interact",
            target="obj_ball_01",
            verb="kick",
        ),
    )

    assert record.ok
    assert agent.position == (1, 1)
    move_steps = [step for step in record.record.steps if step.kind == "move"]
    interact_steps = [step for step in record.record.steps if step.kind == "interact"]
    assert len(move_steps) == 1
    assert len(interact_steps) == 1
    assert "Ceramic Ball" in move_steps[0].result
    assert move_steps[0].passive_result
    assert "kick" in record.message.lower() or "ball" in record.message.lower()
    assert "Ceramic Ball" in record.record.result


def test_interact_honors_positioning_move_then_kicks():
    """When move already reaches range, keep that tile instead of nearest-path overwrite."""
    session = Session.from_default()
    agent = session.get_active_agent()
    agent.position = (0, 0)
    agent.move_speed = 4

    record = session.run_compound_turn(
        AgentCompoundTurn(
            reasoning="stand east of the ball then kick",
            move="3,2",
            action="interact",
            target="obj_ball_01",
            verb="kick",
        ),
    )

    assert record.ok
    assert agent.position == (3, 2)
    move_steps = [step for step in record.record.steps if step.kind == "move"]
    interact_steps = [step for step in record.record.steps if step.kind == "interact"]
    assert len(move_steps) == 1
    assert len(interact_steps) == 1
    assert "(3, 2)" in move_steps[0].result or "3,2" in move_steps[0].result.replace(" ", "")
    assert "kick" in interact_steps[0].result.lower() or "ball" in interact_steps[0].result.lower()
