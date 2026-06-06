"""
test_multi_agent.py

Tests for V0.1 Section 3 multi-agent support.
"""

from src.agent import Agent
from src.llm.schemas import AgentTurn
from src.memory import Memory
from src.perception import build_passive_vision, perform_look
from src.simulation import next_turn_number_for_agent, step_turn
from src.world import create_initial_world
from src.world_edit import create_agent_from_args, edit_object_from_args


def _make_turn(**kwargs) -> AgentTurn:
    defaults = {
        "reasoning": "test",
        "action": "speak",
        "target": None,
        "content": "Hello.",
    }
    defaults.update(kwargs)
    return AgentTurn(**defaults)


def test_get_agents_returns_copy():
    world = create_initial_world()
    agents = world.get_agents()
    assert len(agents) == 1
    agents.clear()
    assert len(world.agents) == 1


def test_get_agent_by_name_case_insensitive():
    world = create_initial_world()
    assert world.get_agent_by_name("explorer") is world.get_agent()
    assert world.get_agent_by_name("EXPLORER") is world.get_agent()
    assert world.get_agent_by_name("Missing") is None


def test_memory_isolation_between_agents():
    world = create_initial_world()
    explorer = world.get_agent()
    create_agent_from_args(world, 'name "Goblin" desc "A goblin." at 0,3')
    goblin = world.get_agent_by_name("Goblin")

    perform_look(explorer, world, "obj_ball_01")

    assert explorer.memory.has_looked_at("obj_ball_01")
    assert not goblin.memory.has_looked_at("obj_ball_01")
    goblin_vision = build_passive_vision(goblin, world)
    assert "Ceramic Ball (obj_ball_01), (2, 2) - [?]" in goblin_vision


def test_per_agent_turn_numbers_when_alternating():
    world = create_initial_world()
    explorer = world.get_agent()
    create_agent_from_args(world, 'name "Goblin" desc "A goblin." at 0,3')
    goblin = world.get_agent_by_name("Goblin")

    step_turn(
        explorer,
        world,
        _make_turn(content="Explorer speaks."),
        next_turn_number_for_agent(explorer),
    )
    step_turn(
        goblin,
        world,
        _make_turn(content="Goblin speaks."),
        next_turn_number_for_agent(goblin),
    )
    step_turn(
        explorer,
        world,
        _make_turn(content="Explorer again."),
        next_turn_number_for_agent(explorer),
    )

    assert [t.turn_number for t in explorer.memory.turns] == [1, 2]
    assert [t.turn_number for t in goblin.memory.turns] == [1]


def test_cross_agent_invalidation_per_agent():
    world = create_initial_world()
    explorer = world.get_agent()
    create_agent_from_args(world, 'name "Goblin" desc "A goblin." at 0,3')
    goblin = world.get_agent_by_name("Goblin")

    perform_look(explorer, world, "obj_ball_01")
    perform_look(goblin, world, "obj_ball_01")
    edit_object_from_args(world, 'obj_ball_01 desc "A shiny ball."')

    assert "[?] [changed]" in build_passive_vision(explorer, world)
    assert "[?] [changed]" in build_passive_vision(goblin, world)


def test_stepper_switch_changes_active_agent_vision():
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd('create-agent name "Goblin" desc "A goblin." at 0,3')
    goblin = stepper.world.get_agent_by_name("Goblin")

    stepper.onecmd("switch Goblin")
    assert stepper.agent is goblin
    vision = build_passive_vision(stepper.agent, stepper.world)
    assert "You are at (0, 3)." in vision


def test_stepper_switch_unknown_agent(capsys):
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd("switch Nobody")
    out = capsys.readouterr().out
    assert "not found" in out
    assert "agents" in out or "list" in out


def test_stepper_switch_does_not_increment_session_turn():
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd('create-agent name "Goblin" desc "x" at 0,0')
    before = stepper.session_turn
    stepper.onecmd("switch Goblin")
    assert stepper.session_turn == before
    assert stepper.agent.name == "Goblin"


def test_stepper_manual_step_uses_per_agent_turn_number():
    from src.main import ManualStepper

    stepper = ManualStepper()
    explorer = stepper.agent
    stepper.onecmd('create-agent name "Goblin" desc "x" at 0,0')
    stepper.onecmd("switch Explorer")
    stepper.onecmd("step speak Hi from Explorer.")
    stepper.onecmd("switch Goblin")
    stepper.onecmd("step speak Hi from Goblin.")
    stepper.onecmd("switch Explorer")
    stepper.onecmd("step speak Explorer turn two.")

    assert [t.turn_number for t in explorer.memory.turns] == [1, 2]
    assert [t.turn_number for t in stepper.world.get_agent_by_name("Goblin").memory.turns] == [1]


def test_create_agent_reserved_command_name_rejected():
    world = create_initial_world()
    agent, msg = create_agent_from_args(world, 'name "vision" desc "x" at 0,0')
    assert agent is None
    assert "conflicts with a stepper command" in msg


def test_create_agent_reserved_hyphen_command_rejected():
    world = create_initial_world()
    agent, msg = create_agent_from_args(
        world, 'name "create-object" desc "x" at 0,0'
    )
    assert agent is None
    assert "conflicts" in msg


def test_edit_agent_rename_to_reserved_name_rejected():
    from src.world_edit import edit_agent_from_args

    world = create_initial_world()
    result = edit_agent_from_args(world, 'agent_01 name "switch"')
    assert not result.ok
    assert "conflicts" in result.message


def test_run_command_uses_active_agent(monkeypatch):
    from src.main import ManualStepper

    stepper = ManualStepper()
    called = []

    def fake_run(agent):
        called.append(agent)

    monkeypatch.setattr(stepper, "_run_llm_turn_for_agent", fake_run)
    stepper.onecmd("run")
    assert len(called) == 1
    assert called[0] is stepper.agent


def test_run_after_switch_uses_switched_agent(monkeypatch):
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd('create-agent name "Goblin" desc "x" at 0,0')
    goblin = stepper.world.get_agent_by_name("Goblin")
    stepper.onecmd("switch Goblin")
    called = []

    def fake_run(agent):
        called.append(agent)

    monkeypatch.setattr(stepper, "_run_llm_turn_for_agent", fake_run)
    stepper.onecmd("run")
    assert called == [goblin]


def test_stepper_commands_case_insensitive(monkeypatch):
    from src.main import ManualStepper

    stepper = ManualStepper()
    called = []

    def fake_run(agent):
        called.append(agent)

    monkeypatch.setattr(stepper, "_run_llm_turn_for_agent", fake_run)
    stepper.onecmd("Run")
    assert len(called) == 1


def test_reserved_commands_include_run_and_hyphenated():
    from src.main import ManualStepper
    from src.stepper_commands import collect_reserved_command_names, get_reserved_stepper_commands

    derived = collect_reserved_command_names(ManualStepper)
    cached = get_reserved_stepper_commands()
    assert derived == cached
    assert "run" in cached
    assert "create-agent" in cached
    assert "?" in cached


def test_llm_failure_still_sets_active_agent(monkeypatch):
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd('create-agent name "Goblin" desc "x" at 0,0')
    goblin = stepper.world.get_agent_by_name("Goblin")
    assert stepper.agent.name == "Explorer"

    def failing_get():
        def fail(_prompt):
            raise RuntimeError("LLM unavailable")

        return fail

    monkeypatch.setattr("src.main._get_llm_function", failing_get)
    stepper.default("Goblin")
    assert stepper.agent is goblin


def test_stepper_delete_active_agent_fallback(capsys):
    from src.main import ManualStepper

    stepper = ManualStepper()
    stepper.onecmd('create-agent name "Goblin" desc "x" at 0,0')
    goblin = stepper.world.get_agent_by_name("Goblin")
    stepper.agent = goblin
    stepper.onecmd("delete-agent agent_goblin_01")
    assert stepper.agent.id == "agent_01"
    assert stepper.agent.name == "Explorer"
    out = capsys.readouterr().out
    assert "Active agent: Explorer (agent_01)" in out
