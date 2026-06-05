"""
test_perception.py

Tests for V0.1 generalized passive vision and cross-agent invalidation.
"""

from src.agent import Agent
from src.memory import Memory
from src.perception import build_passive_vision, format_object_vision_desc, perform_look
from src.object import Object
from src.world import create_initial_world


def test_initial_sign_in_ever_looked_after_pre_mark():
    """Pre-marked sign in create_initial_world should be in both looked_at and ever_looked."""
    world = create_initial_world()
    agent = world.get_agent()

    assert agent.memory.has_looked_at("obj_sign_01")
    assert agent.memory.has_ever_looked_at("obj_sign_01")
    assert not agent.memory.has_ever_looked_at("obj_ball_01")


def test_ball_vision_states_never_stale_current():
    """Ball: [?] initially, full description after look, changed after invalidate, restored after re-look."""
    world = create_initial_world()
    agent = world.get_agent()

    vision = build_passive_vision(agent, world)
    assert "Ceramic Ball (obj_ball_01), (2, 2) - [?]" in vision

    perform_look(agent, world, "obj_ball_01")
    vision = build_passive_vision(agent, world)
    assert "scuffs and feels light" in vision

    world.invalidate_object_knowledge("obj_ball_01")
    vision = build_passive_vision(agent, world)
    assert "[?] The Ceramic Ball has changed since you last looked at it." in vision
    assert agent.memory.has_ever_looked_at("obj_ball_01")
    assert not agent.memory.has_looked_at("obj_ball_01")

    perform_look(agent, world, "obj_ball_01")
    vision = build_passive_vision(agent, world)
    assert "scuffs and feels light" in vision


def test_sign_shows_changed_message_after_invalidation():
    """Pre-known sign shows generalized changed notice after invalidate, not plain [?]."""
    world = create_initial_world()
    agent = world.get_agent()

    world.invalidate_object_knowledge("obj_sign_01")
    vision = build_passive_vision(agent, world)

    assert "[?] The Wooden Sign has changed since you last looked at it." in vision
    assert "Ceramic Ball (obj_ball_01), (2, 2) - [?]" in vision


def test_sign_description_update_look_restores_new_text():
    """After sign description changes and invalidation, look returns the new text."""
    world = create_initial_world()
    agent = world.get_agent()
    new_text = "Brand new sign text for testing."

    sign = world.get_object_by_id("obj_sign_01")
    sign.description = new_text
    world.invalidate_object_knowledge("obj_sign_01")

    vision = build_passive_vision(agent, world)
    assert "[?] The Wooden Sign has changed since you last looked at it." in vision

    result = perform_look(agent, world, "obj_sign_01")
    assert new_text in result
    assert agent.memory.has_looked_at("obj_sign_01")

    vision = build_passive_vision(agent, world)
    assert new_text in vision


def test_invalidate_object_knowledge_affects_all_agents_who_looked():
    """Both agents who looked at the ball see changed message after invalidation."""
    world = create_initial_world()
    explorer = world.get_agent()
    goblin = Agent(
        id="agent_goblin_01",
        name="Goblin",
        description="A test goblin.",
        position=(0, 0),
        memory=Memory(),
    )
    world.add_agent(goblin)

    perform_look(explorer, world, "obj_ball_01")
    perform_look(goblin, world, "obj_ball_01")
    world.invalidate_object_knowledge("obj_ball_01")

    changed = "[?] The Ceramic Ball has changed since you last looked at it."
    assert changed in build_passive_vision(explorer, world)
    assert changed in build_passive_vision(goblin, world)


def test_agent_who_never_looked_sees_plain_question_mark():
    """Agent who never looked still sees plain [?] after another agent's knowledge is invalidated."""
    world = create_initial_world()
    explorer = world.get_agent()
    goblin = Agent(
        id="agent_goblin_01",
        name="Goblin",
        description="A test goblin.",
        position=(0, 0),
        memory=Memory(),
    )
    world.add_agent(goblin)

    perform_look(explorer, world, "obj_ball_01")
    world.invalidate_object_knowledge("obj_ball_01")

    goblin_vision = build_passive_vision(goblin, world)
    ball_line = next(
        line for line in goblin_vision.split("\n") if "obj_ball_01" in line
    )
    assert ball_line == "Ceramic Ball (obj_ball_01), (2, 2) - [?]"


def test_reset_looked_at_clears_both_sets():
    """reset_looked_at clears both looked_at and ever_looked."""
    memory = Memory()
    memory.mark_looked_at("obj_ball_01")
    memory.mark_looked_at("obj_sign_01")

    assert memory.has_looked_at("obj_ball_01")
    assert memory.has_ever_looked_at("obj_ball_01")

    memory.reset_looked_at()

    assert not memory.has_looked_at("obj_ball_01")
    assert not memory.has_ever_looked_at("obj_ball_01")
    assert not memory.has_looked_at("obj_sign_01")
    assert not memory.has_ever_looked_at("obj_sign_01")


def test_format_object_vision_desc_three_states():
    """format_object_vision_desc returns correct text for each state."""
    obj = Object(
        id="obj_test_01",
        name="Test Object",
        description="Full description here.",
        position=(0, 0),
    )
    memory = Memory()

    assert format_object_vision_desc(obj, memory) == "[?]"

    memory.mark_looked_at("obj_test_01")
    assert format_object_vision_desc(obj, memory) == "Full description here."

    memory.invalidate_look("obj_test_01")
    assert (
        format_object_vision_desc(obj, memory)
        == "[?] The Test Object has changed since you last looked at it."
    )


def test_invalidate_skips_agents_without_looked_at():
    """invalidate_object_knowledge only affects agents with current knowledge."""
    world = create_initial_world()
    agent = world.get_agent()
    assert not agent.memory.has_looked_at("obj_ball_01")

    world.invalidate_object_knowledge("obj_ball_01")

    assert not agent.memory.has_ever_looked_at("obj_ball_01")
    vision = build_passive_vision(agent, world)
    assert "Ceramic Ball (obj_ball_01), (2, 2) - [?]" in vision
