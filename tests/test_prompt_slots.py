"""Tests for plugin prompt slot registry (1.2.0)."""

from campaign_rpg_engine import (
    PromptBlock,
    Session,
    build_prompt_context,
    clear_prompt_slots_for_tests,
    load_profile,
    register_prompt_slot,
    validate_prompt_blocks,
)
from campaign_rpg_engine.prompt_blocks import render_prompt_blocks


def test_registered_prompt_slot_renders():
    clear_prompt_slots_for_tests()

    def render_slot(session, agent, area, ctx, options):
        del session, agent, area, ctx, options
        return "PLUGIN_SLOT_TEXT"

    register_prompt_slot("hello_plugin", render_slot, description="Hello")
    blocks = [PromptBlock(type="slot", name="hello_plugin")]
    err = validate_prompt_blocks(blocks)
    assert err is None

    plugin_blocks = [PromptBlock(type="plugin_slot", name="hello_plugin")]
    assert validate_prompt_blocks(plugin_blocks) is None

    session = Session.from_profile(load_profile("default_compound"))
    agent = session.get_active_agent()
    area = session.get_area_for_agent(agent)
    ctx = build_prompt_context(agent, area)
    text = render_prompt_blocks(
        blocks,
        ctx,
        agent=agent,
        area=area,
        session=session,
    )
    assert "PLUGIN_SLOT_TEXT" in text
    clear_prompt_slots_for_tests()
