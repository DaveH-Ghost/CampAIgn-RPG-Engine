# Custom memory modules (V0.4.6)

Example and contract for **runtime-loaded** memory modules.

## Contract

Each custom module is a single `.py` file that defines:

| Symbol | Required | Purpose |
|--------|----------|---------|
| `MODULE_ID` | Yes | Unique id (must not match built-in: `recent_turns`, `salient_turns`, `rolling_summary`) |
| `create_module(**config)` | Yes | Factory returning a `MemoryModule` |
| `MODULE_LABEL` | No | Display name in realm-studio |
| `MODULE_DESCRIPTION` | No | Short description |
| `CREATE_AGENT_OPTIONS` | No | List of `{flag, label, default, min, max?}` for create-agent UI |

The module must implement `export_state()` / `restore_state()` for session save/load (inherit from a built-in or implement on the protocol).

Imports from `src.*` are allowed when the Realm-Fabric engine is installed.

## Example

[`rolling_summary_custom.py`](rolling_summary_custom.py) — same behavior as built-in `rolling_summary`, id `rolling_summary_custom`.

## CLI

```text
add-memory-module path/to/rolling_summary_custom.py
create-agent name "Archivist" personality "..." memory rolling_summary_custom at 1,1
```

## realm-studio

1. Open **Settings** (gear) → **Add memory module** → upload `.py`
2. Create agent — memory dropdown lists only **loaded** modules (built-ins + uploaded)
3. Re-uploading the same `MODULE_ID` **overwrites** the registered module (dev-friendly)

## Save / load

Session saves reference `module_id` only (no bundled source). Before **import-session** or **Load session**, every custom `module_id` in the save must already be loaded; otherwise import fails with:

`Memory module '…' is not found. Load the module before loading this save.`
