# Realm Fabric

Grid-based LLM agent simulation engine: multi-area worlds, compound turns (move → look → speak → interact/emote), pluggable memory modules, and a stable **`realm_fabric`** library API. Build your own UI and scenarios on the engine; use [Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio) as a full GM reference app.

**License:** [MIT](LICENSE) — open source.

**Current version:** **1.0.0** — library-first package (`realm_fabric` only; no CLI). See [Migration from 0.7](docs/MIGRATION-0.7-to-1.0.md) and the [changelog index](docs/changelog/README.md).

## Quick start

```powershell
cd path\to\Realm-Fabric
uv sync
uv run pytest
```

```python
from realm_fabric import Session, load_profile, AgentCompoundTurn

session = Session.from_profile(load_profile("default_compound"))
session.create_agent(name="Scout", position=(0, 0), personality="Curious.")
session.create_object(name="Chest", position=(2, 1), passive_description="An old chest.")
prompt = session.build_prompt()
result = session.run_compound_turn(
    AgentCompoundTurn(reasoning="look around", action="none"),
)
```

**GM web UI:** clone [Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio) (separate GitHub repo):

```powershell
cd path\to\Realm-Studio
uv sync
copy .env.example .env   # optional; or use Settings gear in the UI
uv run realm-studio
```

On Windows, if Smart App Control blocks `uv run realm-studio`, use `uv run python -m backend.main`. Open [http://127.0.0.1:8765](http://127.0.0.1:8765).

## Environment

Copy [`.env.example`](.env.example) to `.env` and set `OPENROUTER_API_KEY` for LLM turns. Optional `OPENROUTER_MODEL` (default `deepseek/deepseek-v4-flash`). Engine tests mock the LLM — no key required for `uv run pytest`.

Realm-Studio **Settings** (gear icon) can set API key and model **in memory for the current server process only** — nothing is written to disk.

## Custom memory modules

Register `.py` modules at process startup before creating agents or loading saves:

```python
from realm_fabric import register_memory_module_from_path

register_memory_module_from_path("path/to/my_module.py")
session.create_agent(..., memory_module="my_module_id")
```

Saves store `module_id` + state only (no bundled source). Import **fails** if a save references a module that is not loaded. Sample module and upload UI: [Realm-Studio `fixtures/custom_memory/`](https://github.com/DaveH-Ghost/Realm-Studio/tree/main/fixtures/custom_memory).

## Lorebooks

Load SillyTavern-style `.json` lorebooks via `session.load_lorebook_from_path(...)` or Realm-Studio **Lorebooks** tab. Add a `lorebook` prompt block in Prompt layout to inject matched world info. Not included in the default prompt layout.

## Tests

```powershell
uv run pytest
```

Realm-Studio API tests live in the [Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio) repo.

## Documentation

Start at **[docs/README.md](docs/README.md)** — guides, API overview, and changelog index.

| Doc | Topic |
|-----|--------|
| [Building on Realm-Fabric](docs/guides/building-on-realm-fabric.md) | App integration (typed API, hosting) |
| [API reference](docs/guides/api-reference.md) | `realm_fabric` exports and Session methods |
| [Migration 0.7 → 1.0](docs/MIGRATION-0.7-to-1.0.md) | Breaking changes (CLI removed, package layout) |
| [Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio) | Full GM reference UI (GitHub) |
| [Roadmap](docs/ROADMAP.md) | Version plans |
| [Long-term goals](LONG_TERM_GOALS.md) | Aspirational features |

Older version notes: [changelog index](docs/changelog/README.md).
