# Realm-Fabric documentation

**Realm-Fabric** is a grid-based LLM agent simulation engine with a stable **`realm_fabric`** library API. The reference GM app is **[Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio)** (GitHub only).

**Current release:** **1.0.0** — library-first; no bundled CLI or HTTP examples. See [MIGRATION-0.7-to-1.0.md](MIGRATION-0.7-to-1.0.md).

---

## New here?

1. [Overview](guides/overview.md) — mental model (Session, areas, compound turns)
2. [Building on Realm-Fabric](guides/building-on-realm-fabric.md) — install, typed API, hosting
3. [Realm-Studio](https://github.com/DaveH-Ghost/Realm-Studio) — runnable reference app (grid, lorebooks, handlers, memory upload)

---

## Guides

| Guide | Description |
|-------|-------------|
| [Overview](guides/overview.md) | Architecture and core concepts |
| [Building on Realm-Fabric](guides/building-on-realm-fabric.md) | App integration entry point |
| [Compound turns](guides/turns.md) | `AgentCompoundTurn`, LLM vs player agents |
| [Interaction handlers](guides/handlers.md) | Pluggable object behavior |
| [Persistence & snapshots](guides/persistence.md) | `to_save_dict()` vs `snapshot()` |
| [Memory & lorebooks](guides/memory-and-lorebooks.md) | Modules, lore injection, prompt blocks |
| [API reference](guides/api-reference.md) | `realm_fabric` exports and Session methods |
| [LLM turn schemas](schemas/README.md) | `AgentCompoundTurn` JSON shape |

---

## Planning & history

| Doc | Description |
|-----|-------------|
| [Migration 0.7 → 1.0](MIGRATION-0.7-to-1.0.md) | Breaking changes for library-only 1.0 |
| [Roadmap](ROADMAP.md) | Version plans |
| [Changelog index](changelog/README.md) | Per-version release notes |
| [Long-term goals](../LONG_TERM_GOALS.md) | Aspirational / out-of-scope items |

---

## Examples in this repo

| Path | Role |
|------|------|
| [examples/README.md](../examples/README.md) | Points to Realm-Studio for runnable apps |
| [examples/lorebook/](../examples/lorebook/) | Sample SillyTavern lorebook JSON |

Engine tests use [`tests/fixtures/`](../tests/fixtures/) (not published in the PyPI wheel).

---

## Stability

- Import from **`realm_fabric`** in application code (`realm_fabric.__all__` is semver-guaranteed).
- Submodules such as `realm_fabric.area_edit` are for tests and app-owned command dispatch — not top-level exports.
- Save format version: **`snapshot_version`** in save JSON (currently **4**).
