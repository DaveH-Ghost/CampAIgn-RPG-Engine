"""ManualStepper CLI: intro, help, state, and LLM turn logging."""

import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from src.main import ManualStepper

_EXAMPLE_MODULE = (
    Path(__file__).resolve().parent.parent
    / "examples"
    / "custom_memory"
    / "rolling_summary_custom.py"
)


@pytest.fixture(autouse=True)
def _clear_custom_registry():
    from src.memory_modules import registry

    registry._CUSTOM_REGISTRY.clear()
    registry._CUSTOM_METADATA.clear()
    yield
    registry._CUSTOM_REGISTRY.clear()
    registry._CUSTOM_METADATA.clear()


def test_stepper_intro_documents_key_commands():
    intro = ManualStepper.intro
    assert "step-compound" in intro
    assert "handlers" in intro
    assert "memory-modules" in intro
    assert "add-memory-module" in intro
    assert "run" in intro


def test_help_step_compound_documents_usage(capsys):
    stepper = ManualStepper()
    stepper.onecmd("help step-compound")
    out = capsys.readouterr().out
    assert "step-compound" in out.lower()
    assert "interact" in out.lower()


def test_state_shows_step_breakdown_after_compound_turn(capsys):
    stepper = ManualStepper()
    stepper.onecmd("step-compound 2,3 speak Hello.")
    stepper.onecmd("state")
    out = capsys.readouterr().out
    assert "Last turn" in out
    assert "steps:" in out
    assert "[move]" in out or "move" in out
    assert "Composite result:" in out


def test_stepper_delegates_to_session():
    from src.main import ManualStepper
    from src.session import Session

    stepper = ManualStepper()
    assert isinstance(stepper.session, Session)
    assert stepper.area is stepper.session.area
    assert stepper.agent is stepper.session.get_active_agent()


def test_run_logs_single_compound_phase(monkeypatch):
    from src.llm.types import LLMResponse
    from src.llm.schemas import AgentCompoundTurn

    logged_phases = []

    def fake_log_turn(_turn_number, *, phase=None, **kwargs):
        if phase:
            logged_phases.append(phase)

    def fake_compound(_prompt):
        return LLMResponse(
            parsed=AgentCompoundTurn(
                reasoning="stay and speak",
                move=None,
                action="none",
                say="Hi.",
            ),
            raw_response="{}",
        )

    monkeypatch.setattr("src.main.log_turn", fake_log_turn)
    monkeypatch.setattr("src.llm.client.get_compound_turn", fake_compound)

    stepper = ManualStepper()
    stepper._run_llm_turn_for_agent(stepper.agent)

    assert logged_phases == ["compound"]


def test_add_memory_module_command():
    stepper = ManualStepper()
    buf = io.StringIO()
    with redirect_stdout(buf):
        stepper.do_add_memory_module(str(_EXAMPLE_MODULE))
    assert "rolling_summary_custom" in buf.getvalue()


def test_stepper_export_import(tmp_path: Path):
    stepper = ManualStepper()
    stepper.session.session_turn = 2
    path = tmp_path / "session.json"
    stepper.do_export_session(str(path))
    assert path.is_file()
    stepper.session.session_turn = 99
    stepper.do_import_session(str(path))
    assert stepper.session.session_turn == 2


def test_export_import_with_custom_memory_module(tmp_path: Path):
    from src.memory_modules.registry import register_memory_module_from_path

    stepper = ManualStepper()
    register_memory_module_from_path(_EXAMPLE_MODULE)
    stepper.session.run_command(
        'create-agent name "Archivist" personality "x" '
        "memory rolling_summary_custom at 2,2"
    )
    path = tmp_path / "custom.json"
    stepper.do_export_session(str(path))

    fresh = ManualStepper()
    register_memory_module_from_path(_EXAMPLE_MODULE)
    fresh.do_import_session(str(path))
    assert fresh.session.get_agent("Archivist") is not None


def test_import_session_fails_without_custom_module(tmp_path: Path):
    from src.memory_modules.registry import register_memory_module_from_path

    stepper = ManualStepper()
    register_memory_module_from_path(_EXAMPLE_MODULE)
    stepper.session.run_command(
        'create-agent name "Archivist" personality "x" '
        "memory rolling_summary_custom at 2,2"
    )
    path = tmp_path / "custom.json"
    stepper.do_export_session(str(path))

    from src.memory_modules import registry

    registry._CUSTOM_REGISTRY.clear()
    registry._CUSTOM_METADATA.clear()

    fresh = ManualStepper()
    buf = io.StringIO()
    with redirect_stdout(buf):
        fresh.do_import_session(str(path))
    out = buf.getvalue()
    assert "rolling_summary_custom" in out
    assert "not found" in out.lower()
