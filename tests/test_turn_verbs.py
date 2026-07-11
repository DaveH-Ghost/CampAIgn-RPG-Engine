"""Tests for turn verb registry (1.2.0)."""

from campaign_rpg_engine import (
    AgentCompoundTurn,
    Session,
    clear_turn_verbs_for_tests,
    load_profile,
    register_turn_verb,
    run_compound_turn,
)
from campaign_rpg_engine.action_outcome import ActionOutcome


def test_turn_verb_runs_in_compound_turn():
    clear_turn_verbs_for_tests()

    def wave(session, agent, area, turn):
        del session, agent, area, turn
        return ActionOutcome(
            result="You wave.",
            passive_result="Explorer waves.",
        )

    register_turn_verb("wave", wave, description="Wave hello")
    session = Session.from_profile(load_profile("default_compound"))
    agent = session.get_active_agent()
    area = session.get_area_for_agent(agent)
    turn = AgentCompoundTurn(
        reasoning="Testing.",
        action="verb",
        verb="wave",
    )
    record = run_compound_turn(agent, area, turn, 1, session=session)
    assert record.steps[-1].kind == "verb"
    assert "wave" in record.result.lower()
    clear_turn_verbs_for_tests()


def test_unknown_turn_verb_rejected_by_schema():
    clear_turn_verbs_for_tests()
    try:
        AgentCompoundTurn(reasoning="x", action="verb", verb="missing")
        assert False, "expected validation error"
    except ValueError as exc:
        assert "unknown turn verb" in str(exc).lower()
    clear_turn_verbs_for_tests()
