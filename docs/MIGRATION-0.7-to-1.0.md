# Migration: 0.7.x → 1.0.0

Realm-Fabric **1.0.0** is a **library-first** release. The engine ships as a single `realm_fabric` package on PyPI. The bundled `realm` CLI and `Session.run_command()` string layer are removed.

**Realm-Studio** (GM web app) lives in a [separate GitHub repository](https://github.com/DaveH-Ghost/Realm-Studio) and is not published to PyPI.

---

## Install

```powershell
uv add "realm-fabric>=1.0.0"
```

Pre-1.0 archive: branch `archive/0.7.x` on GitHub (tag `v0.7.2`).

---

## Breaking changes

### Package layout

| 0.7.x | 1.0.0 |
|-------|-------|
| `src/` tree + thin `realm_fabric` facade | Single `realm_fabric/` package at repo root |
| `from src.session import Session` (tests/CLI) | `from realm_fabric import Session` |
| `import realm_fabric` re-exported from `src/` | Import only `realm_fabric` in apps |

### CLI removed

| 0.7.x | 1.0.0 |
|-------|-------|
| `uv run realm` stepper | **Removed** — use Realm-Studio or your own UI |
| `docs/guides/cli.md` | **Removed** — see [API reference](guides/api-reference.md) |
| `[project.scripts] realm = ...` | **Removed** from `pyproject.toml` |

### `Session.run_command()` removed

| 0.7.x | 1.0.0 |
|-------|-------|
| `session.run_command("create-object ...")` | `session.create_object(name=..., position=..., ...)` |
| `session.run_command("create-agent ...")` | `session.create_agent(name=..., position=..., ...)` |
| `session.run_command("edit-agent ...")` | `session.edit_agent(agent_id, ...)` |
| `session.run_command("emit-event ...")` | `session.emit_area_event(text)` |
| `session.run_command("list")` | `session.snapshot()` |
| `CommandResult` | **Removed** — use `WorldMutationResult`, `SessionResult`, `TurnResult` |

See [Building on Realm-Fabric](guides/building-on-realm-fabric.md) for the full typed API table.

### Public exports trimmed

Removed from `realm_fabric.__all__` (import submodules if you own GM string dispatch):

- `CommandResult`
- `create_area_from_args`, `edit_area_from_args` (moved to `realm_fabric.area_edit`)
- `edit_agent_for_session`, `edit_object_for_session`
- `parse_area_event_arg` (use `session.emit_area_event` or `realm_fabric.area_event`)

### Realm-Studio location

| 0.7.x | 1.0.0 |
|-------|-------|
| `examples/web/realm-studio/` in monorepo | [github.com/DaveH-Ghost/Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio) |

Studio depends on `realm-fabric` from PyPI (or local editable during co-dev). It keeps stepper-style GM commands in **`backend/command_dispatch.py`**, which imports `realm_fabric.area_edit` helpers — not `Session.run_command()`.

### Examples removed in 1.0

| 0.7.x | 1.0.0 |
|-------|-------|
| `examples/minimal-server/` | **Removed** — use [Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio) `backend/` as HTTP reference |
| `examples/reference_handlers/` | **Removed** — canonical copy in [Realm-Studio/reference_handlers](https://github.com/DaveH-Ghost/Realm-Studio/tree/main/reference_handlers) |
| `examples/custom_memory/` | **Removed** — sample + upload UI in [Realm-Studio/fixtures/custom_memory](https://github.com/DaveH-Ghost/Realm-Studio/tree/main/fixtures/custom_memory) |

Use typed `Session` methods in your HTTP handlers. See [Building on Realm-Fabric](guides/building-on-realm-fabric.md).

---

## Migration checklist

1. **Bump dependency:** `realm-fabric>=1.0.0`
2. **Fix imports:** replace all `src.*` with `realm_fabric`
3. **Replace `run_command`:** map each command to typed `Session` methods (table above)
4. **Remove CLI assumptions:** no `uv run realm` in docs or CI
5. **Re-test saves:** `snapshot_version` 4 unchanged; `Session.from_snapshot()` API stable
6. **Studio:** use external repo; verify against 1.0 wheel (`uv build` + install `.whl`)

---

## Unchanged (stable)

- `AgentCompoundTurn` schema and compound-turn simulation
- `Session.run_compound_turn()`, `build_prompt()`, `snapshot()`, `to_save_dict()`
- Interaction handler registration API
- Memory modules and lorebooks
- `snapshot_version: 4` save format (v1–v3 import still supported)

---

## Related

- [API reference](guides/api-reference.md)
- [Building on Realm-Fabric](guides/building-on-realm-fabric.md)
- [Changelog index](changelog/README.md)
