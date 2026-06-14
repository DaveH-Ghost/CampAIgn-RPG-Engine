# realm-studio

Example web app for [Realm-Fabric](https://github.com/) — wraps the engine `Session` API over HTTP.

**Location:** `examples/web/realm-studio` in the Realm-Fabric repo.

**Status:** **V0.3.2** complete — tag **`v0.3.2`** on the example milestone. Pannable grid, GM **Emit event…**, token images from `appearance` paths.

## Quick start

```powershell
cd examples\web\realm-studio
uv sync
copy ..\..\..\.env.example .env   # set OPENROUTER_API_KEY for Run turn
uv run realm-studio
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) (opens automatically). Right-click the grid to edit; **Emit event…** for GM narration; **Run turn ▶** for the active agent.

## Prerequisites

- Python ≥3.11
- [uv](https://docs.astral.sh/uv/)
- Realm-Fabric engine at repo root (path dependency on `realm-fabric`)
- **OpenRouter API key** for LLM turns (area edits work without it)

## Run (dev server)

```powershell
uv run realm-studio
```

Use `--no-browser` to skip opening the browser:

```powershell
uv run realm-studio --no-browser
```

Alternative:

```powershell
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8765 --reload
```

## UI

- **Grid** — white pannable map; entities show **token images** when `appearance` is set (else name chips); active agent ★
- **Right-click** — create/edit/delete on tiles and tokens; **Play as** for agents
- **Stacked tiles** — manage menu when multiple entities share a cell
- **Toolbar** — active-agent dropdown; **Emit event…**; **Run turn ▶**
- **Sidebar** — session meta, passive vision, recent GM events, turn log
- **Refresh** — manual re-fetch; edits and turns auto-refresh

**Note:** `realm-studio` and the terminal `realm` CLI use **separate in-memory sessions** — CLI edits do not appear in the browser.

## Token images

Entity `appearance` is an image path (engine field). realm-studio resolves it under `/static/` — e.g. `tokens/explorer.svg` → `/static/tokens/explorer.svg`.

Bundled demo tokens live in `frontend/tokens/`. Add PNG/SVG files there and set the path in create/edit modals or via CLI:

```text
edit-agent agent_01 appearance "tokens/explorer.svg"
create-object name "Crate" appearance "tokens/ball.svg" at 3,3
```

Empty path falls back to a name chip. Broken paths fall back at render time.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Liveness |
| `GET` | `/api/state` | `Session.snapshot()` |
| `POST` | `/api/command` | `{ "line": "create-object ..." }` → `run_command` |
| `POST` | `/api/active-agent` | `{ "name_or_id": "Explorer" }` → `set_active_agent` |
| `POST` | `/api/turn` | LLM compound turn (optional `agent_id`, `include_examples`) |
| `POST` | `/api/event` | `{ "text": "..." }` → `emit_area_event` (no turn consumed) |
| `GET` | `/api/prompt` | Build compound prompt (debug) |

See [v0.3.2-changelog.md](../../../docs/v0.3.2-changelog.md) for the full V0.3.2 release notes.

## Tests

```powershell
uv run pytest
```

19 smoke/integration tests in `tests/test_api.py` via FastAPI `TestClient` (mocked LLM — no API key or running server).

From repo root, engine tests remain separate:

```powershell
cd ..\..\..
uv run pytest
```

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | For **Run turn** | [OpenRouter](https://openrouter.ai/) API key |
| `OPENROUTER_MODEL` | No | Default: `deepseek/deepseek-v4-flash` |

`python-dotenv` loads `.env` from the working directory when the server starts.

## Dev: stacked objects on one tile

```powershell
$env:REALM_STUDIO_DEV_STACK = "1"
uv run realm-studio
```

Adds 10 objects on tile **(3, 3)** to test scrollbars. Omit for the normal demo room.

## What's next

**V0.4** — multi-area sessions — see [ROADMAP.md](../../../docs/ROADMAP.md).
