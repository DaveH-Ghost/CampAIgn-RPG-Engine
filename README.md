# Realm Fabric

Grid-based LLM agent simulation engine: multi-area worlds, compound turns (move → look → speak → interact/emote), pluggable memory modules, and a stable `realm_fabric` library API. The `realm` CLI and [realm-studio](examples/web/realm-studio) are reference clients — apps build on the engine with their own UI and scenarios.

**Current version:** **V0.6.0** (`0.6.0` in `pyproject.toml`) — tactical grid simulation: movement blocking, pathfinding, interact pathing, multi-tile footprints, hidden objects, and path-step triggers.

## Quick start

```powershell
# Engine + CLI
cd path\to\Realm-Fabric
uv sync
uv run realm

# Example web UI
cd examples\web\realm-studio
uv sync
copy ..\..\..\.env.example .env   # optional; or use Settings gear in the UI
uv run realm-studio
```

On Windows, if Smart App Control blocks `uv run realm-studio`, use:

```powershell
uv run python -m backend.main
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). See [realm-studio README](examples/web/realm-studio/README.md).

## Library API

```python
from realm_fabric import Session, load_profile, AgentCompoundTurn

session = Session.from_profile(load_profile("default_compound"))
prompt = session.build_prompt()
result = session.run_compound_turn(AgentCompoundTurn(...))
save_doc = session.to_save_dict()
restored = Session.from_snapshot(save_doc)
```

## Environment

Copy [`.env.example`](.env.example) to `.env` and set `OPENROUTER_API_KEY` for LLM turns. Optional `OPENROUTER_MODEL` (default `deepseek/deepseek-v4-flash`). Manual commands work without a key.

realm-studio **Settings** (gear icon) can set API key and model **in memory for the current server process only** — nothing is written to disk.

## V0.6.0 highlights

- **Movement blocking** — objects block tiles by default; BFS pathfinding when `move_speed` is set
- **Interact pathing** — compound `interact` paths toward the object (replaces explicit `move` that turn)
- **Passive vision** — look guidance and in-range interactions merged into one prompt slot
- **Multi-tile objects** — `width` / `height` footprints; range uses nearest footprint tile
- **Hidden objects + triggers** — GM-only placements; engine-fired triggers on path steps (`Session.emit_area_event`)
- **Saves** — `snapshot_version: 3` (v1–v2 import still supported)
- **realm-studio** — footprint overlay, hidden-trigger wizard, collapsible create/edit modals, `private_data` for custom apps

## Custom memory modules (V0.4.6)

Load `.py` modules at runtime before create-agent or session import:

```text
add-memory-module path\to\my_module.py
```

Saves store `module_id` + state only (no bundled source). Import **fails** if a save references a module that is not loaded. Example: [examples/custom_memory/](examples/custom_memory/).

## Lorebooks (V0.5.0)

Load SillyTavern-style `.json` lorebooks into the session (CLI `load-lorebook` or realm-studio **Lorebooks** tab). Add a `lorebook` prompt block (per book) in Prompt layout to inject matched world info. Not included in the default prompt layout.

## CLI reference

Full command list, world editing, blocking, hidden objects, triggers, and compound-turn examples: [docs/cli.md](docs/cli.md).

## Tests

```powershell
# Engine (repo root)
uv run pytest

# realm-studio
cd examples\web\realm-studio
uv run pytest
```

No API key or network required — LLM calls are mocked in tests.

## Documentation

| Doc | Topic |
|-----|--------|
| [V0.6.0 changelog](docs/v0.6.0-changelog.md) | Grid simulation, triggers, snapshot v3 |
| [V0.5.0 changelog](docs/v0.5.0-changelog.md) | Lorebooks, prompt slot, Lorebooks tab |
| [V0.4.6 changelog](docs/v0.4.6-changelog.md) | Custom memory modules, settings |
| [V0.4.5 changelog](docs/v0.4.5-changelog.md) | Session save/load |
| [Roadmap](docs/ROADMAP.md) | Version plans (next: V0.6.1 handlers) |
| [realm-studio](examples/web/realm-studio/README.md) | Web UI, API, settings |
| [Long-term goals](LONG_TERM_GOALS.md) | Aspirational features |
| [CLI reference](docs/cli.md) | `realm` stepper commands |

Older changelogs: [v0.4.4](docs/v0.4.4-changelog.md), [v0.4.3](docs/v0.4.3-changelog.md), [v0.4.2](docs/v0.4.2-changelog.md), [v0.4.1](docs/v0.4.1-changelog.md), [v0.4.0](docs/v0.4.0-changelog.md).
