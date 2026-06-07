"""
test_v0_2_ship.py

V0.2 Section 4: cross-cutting ship criteria and release integration checks.
"""

import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.llm.client import LLMParseError, get_structured_turn
from src.llm.schemas import AgentActionTurn, AgentNavigationTurn


def test_pyproject_version_is_0_2_0():
    data = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    assert data["project"]["version"] == "0.2.0"


def test_pyproject_declares_realm_console_script():
    data = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    assert data["project"]["scripts"]["realm"] == "src.main:main"
    assert data["tool"]["uv"]["package"] is True
    assert "hatchling" in data["build-system"]["requires"]


def test_stepper_intro_documents_v0_2_commands():
    from src.main import ManualStepper

    intro = ManualStepper.intro
    assert "step-compound" in intro
    assert "effects" in intro
    assert "V0.2" in intro


def test_help_step_compound_documents_usage(capsys):
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd("help step-compound")
    out = capsys.readouterr().out
    assert "step-compound" in out.lower()
    assert "interact" in out.lower()


def test_state_shows_step_breakdown_after_compound_turn(capsys):
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd("step-compound 2,3 speak Hello.")
    stepper.onecmd("state")
    out = capsys.readouterr().out
    assert "Last turn" in out
    assert "steps:" in out
    assert "[move]" in out or "move" in out
    assert "Composite result:" in out


def test_run_logs_nav_and_action_phases(monkeypatch):
    from src.main import ManualStepper
    from src.llm.schemas import AgentActionTurn, AgentNavigationTurn
    from src.llm.types import LLMResponse

    logged_phases = []

    def fake_log_turn(_turn_number, *, phase=None, **kwargs):
        if phase:
            logged_phases.append(phase)

    def fake_nav(_prompt):
        return LLMResponse(
            parsed=AgentNavigationTurn(reasoning="stay", move_target=None),
            raw_response="{}",
        )

    def fake_action(_prompt):
        return LLMResponse(
            parsed=AgentActionTurn(reasoning="speak", turn_action="speak", content="Hi."),
            raw_response="{}",
        )

    monkeypatch.setattr("src.main.log_turn", fake_log_turn)
    monkeypatch.setattr("src.llm.client.get_navigation_turn", fake_nav)
    monkeypatch.setattr("src.llm.client.get_action_turn", fake_action)

    stepper = ManualStepper()
    stepper._run_llm_turn_for_agent(stepper.agent)

    assert logged_phases == ["nav", "action"]


def test_speak_at_400_chars_passes():
    text = "A" * 400
    turn = AgentActionTurn(reasoning="x", turn_action="speak", content=text)
    assert len(turn.content) == 400


def test_speak_at_501_chars_fails_content_too_long():
    with pytest.raises(ValidationError) as exc_info:
        AgentActionTurn(
            reasoning="x",
            turn_action="speak",
            content="A" * 501,
        )
    assert "ERR:CONTENT_TOO_LONG" in str(exc_info.value)


def test_navigation_schema_rejects_cardinal_move_target():
    with pytest.raises(ValidationError) as exc_info:
        AgentNavigationTurn(reasoning="Old.", move_target="north")
    assert "ERR:INVALID_TARGET" in str(exc_info.value)


def test_llm_client_raises_invalid_json_on_bad_output(monkeypatch):
    class FakeMessage:
        content = "not json at all"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]
        usage = None

    class FakeCompletions:
        @staticmethod
        def create(**kwargs):
            return FakeResponse()

    class FakeClient:
        chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("src.llm.client.get_llm_client", lambda: FakeClient())

    with pytest.raises(LLMParseError) as exc_info:
        get_structured_turn("prompt", AgentNavigationTurn)

    assert "ERR:INVALID_JSON" in str(exc_info.value)
