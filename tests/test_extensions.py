"""Tests for session.extensions (1.2.0)."""

from campaign_rpg_engine import Session, load_profile


def test_extensions_round_trip_in_save():
    session = Session.from_profile(load_profile("default_compound"))
    session.set_extension("my_plugin", {"items": [1, 2]})
    data = session.to_save_dict()
    assert data["extensions"]["my_plugin"] == {"items": [1, 2]}

    restored = Session.from_snapshot(data)
    assert restored.get_extension("my_plugin") == {"items": [1, 2]}


def test_extensions_default_empty_on_old_save_without_field():
    session = Session.from_profile(load_profile("default_compound"))
    data = session.to_save_dict()
    del data["extensions"]
    restored = Session.from_snapshot(data)
    assert restored.extensions == {}
