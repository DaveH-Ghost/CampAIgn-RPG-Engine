# Realm Fabric

Grid-based LLM agent simulation engine: multi-area worlds, compound turns (move → look → speak → interact/emote), pluggable memory modules, and a stable `realm_fabric` library API. The `realm` CLI and [realm-studio](examples/web/realm-studio) are reference clients — apps build on the engine with their own UI and scenarios.

**License:** [MIT](LICENSE) — open source.

**Current version:** **V0.7.2** (`0.7.2` in `pyproject.toml`) — Python 3.12 PyPI import fix. See [V0.7.2 changelog](docs/changelog/v0.7.2-changelog.md). **V0.7.1** added movement pathing fix and targeted area events; **V0.7.0** introduced the stable `realm_fabric` API.

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
session.create_agent(name="Scout", position=(0, 0), personality="...")
session.create_object(name="Chest", position=(2, 1), passive_description="...")
prompt = session.build_prompt()
result = session.run_compound_turn(AgentCompoundTurn(...))
save_doc = session.to_save_dict()
restored = Session.from_snapshot(save_doc)
```

See [documentation](docs/README.md) and [minimal-server](examples/minimal-server/).

## Environment

Copy [`.env.example`](.env.example) to `.env` and set `OPENROUTER_API_KEY` for LLM turns. Optional `OPENROUTER_MODEL` (default `deepseek/deepseek-v4-flash`). Manual commands work without a key.

realm-studio **Settings** (gear icon) can set API key and model **in memory for the current server process only** — nothing is written to disk.

## V0.7.2 highlights

- **Python 3.12 PyPI fix** — `from __future__ import annotations` across all `src/` modules so `import realm_fabric` works on 3.11/3.12

## V0.7.1 highlights

- **Straight-line movement** — `move_speed` pathing stays on row/column when moving in a straight line
- **Targeted area events** — `emit_area_event(text, agent_ids=...)` for per-agent GM narration
- **PyPI** — `realm_fabric.__version__` reads installed package metadata correctly

## V0.7.0 highlights

- **Public API** — expanded `realm_fabric` exports (lorebooks, prompt blocks, `ObjectAction`, `WorldMutationResult`, memory registration)
- **Typed world API** — `session.create_object()`, `create_agent()`, `edit_object()`, areas, actions — no CLI strings in app code
- **minimal-server** — thin FastAPI reference at `examples/minimal-server/`
- **Docs** — [docs/README.md](docs/README.md)

## V0.6.1 highlights

- **Pluggable handlers** — `register_interaction_handler()`; `ObjectAction.handler_id` + `handler_params`
- **Reference handlers** — `delete_self`, `random_move_self`, `move_area` in `examples/reference_handlers/` (CLI + realm-studio register at startup)
- **Interacts + triggers** — same handler surface for LLM interacts and path-step triggers
- **Saves** — `snapshot_version: 4` (v1–v3 import supported; `effects` migrates to handlers)
- **Breaking** — CLI `effect` → `handler`; `effects` command → `handlers` (alias kept)

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

Full command list, world editing, blocking, hidden objects, triggers, and compound-turn examples: [docs/guides/cli.md](docs/guides/cli.md).

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

Start at **[docs/README.md](docs/README.md)** — guides, API overview, and changelog index.

| Doc | Topic |
|-----|--------|
| [Building on Realm-Fabric](docs/guides/building-on-realm-fabric.md) | App integration (typed API, hosting) |
| [CLI reference](docs/guides/cli.md) | `realm` stepper commands |
| [V0.7.2 changelog](docs/changelog/v0.7.2-changelog.md) | Python 3.12 import fix |
| [V0.7.1 changelog](docs/changelog/v0.7.1-changelog.md) | Movement fix, targeted events, PyPI version |
| [V0.7.0 changelog](docs/changelog/v0.7.0-changelog.md) | Platform SDK, minimal-server |
| [Roadmap](docs/ROADMAP.md) | Version plans |
| [realm-studio](examples/web/realm-studio/README.md) | Full GM reference UI |
| [Long-term goals](LONG_TERM_GOALS.md) | Aspirational features |

Older version notes: [changelog index](docs/changelog/README.md).
