"""Tests for session event registry (1.2.0)."""

from campaign_rpg_engine import (
    Session,
    clear_event_listeners_for_tests,
    emit_session_event,
    load_profile,
    register_event_listener,
    unregister_event_listeners,
)


def test_emit_session_event_invokes_listener():
    clear_event_listeners_for_tests()
    seen: list[str] = []

    def on_loaded(session, **payload):
        del session, payload
        seen.append("loaded")

    register_event_listener("session_loaded", on_loaded, plugin_id="test")
    session = Session.from_profile(load_profile("default_compound"))
    emit_session_event(session, "session_loaded")
    assert seen == ["loaded"]
    clear_event_listeners_for_tests()


def test_unregister_event_listeners_by_plugin_id():
    clear_event_listeners_for_tests()
    seen: list[str] = []

    register_event_listener(
        "turn_committed",
        lambda session, **payload: seen.append("a"),
        plugin_id="plugin_a",
    )
    register_event_listener(
        "turn_committed",
        lambda session, **payload: seen.append("b"),
        plugin_id="plugin_b",
    )
    unregister_event_listeners("plugin_a")
    session = Session.from_profile(load_profile("default_compound"))
    emit_session_event(session, "turn_committed")
    assert seen == ["b"]
    clear_event_listeners_for_tests()
