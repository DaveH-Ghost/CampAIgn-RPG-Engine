# realm-studio

Example web app for [Realm-Fabric](https://github.com/) — wraps the engine `Session` API over HTTP.

**Location:** `examples/web/realm-studio` in the Realm-Fabric repo.

**Status:** **0.3.1d** — grid UI, right-click editing, and LLM **Run turn**.

## Prerequisites

- Python ≥3.11
- [uv](https://docs.astral.sh/uv/)
- Realm-Fabric engine at repo root (this example uses a path dependency on `realm-fabric`)
- **OpenRouter API key** for LLM turns (see [Environment](#environment))

## Setup

From this directory:

```powershell
cd examples\web\realm-studio
uv sync
```

Copy the repo root `.env.example` to `.env` (or create `.env` here) and set your key:

```powershell
copy ..\..\..\.env.example .env
# Edit .env — set OPENROUTER_API_KEY=sk-or-...
```

## Run (dev server)

```powershell
uv run realm-studio
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) — opens automatically in your default browser (5×5 grid with Explorer, ball, sign). Use `--no-browser` to skip:

```powershell
uv run realm-studio --no-browser
```

Alternative:

```powershell
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8765 --reload
```

## UI (0.3.1b–d)

- **Grid** — agents (green) and objects (purple) at snapshot positions; active agent marked with ★
- **Right-click** empty tile → create object or agent; right-click chip → edit, delete, or **Play as** (agents)
- **Stacked tiles** — manage menu lists entities on the cell
- **Toolbar** — active-agent dropdown; **Run turn ▶** calls the LLM for the active agent
- **Refresh** — manual re-fetch; successful edits and turns auto-refresh

**Note:** `realm-studio` and the terminal `realm` CLI use separate in-memory sessions — CLI edits do not appear in the browser.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | `{ "ok": true }` |
| `GET` | `/api/state` | Engine `Session.snapshot()` |
| `POST` | `/api/command` | `{ "line": "create-object ..." }` → `run_command` |
| `POST` | `/api/active-agent` | `{ "name_or_id": "Explorer" }` → `set_active_agent` |
| `POST` | `/api/turn` | LLM compound turn for active (or optional `agent_id`) agent |

### `POST /api/turn` body

```json
{}
```

Optional fields:

- `agent_id` — run for a specific agent instead of the active one
- `include_examples` — include few-shot examples in the prompt (default: off)

Response on success:

```json
{
  "ok": true,
  "message": "Composite result text…",
  "snapshot": { "...": "..." },
  "steps": [{ "kind": "speak", "result": "…", "...": "…" }]
}
```

## Tests

```powershell
uv run pytest
```

Uses FastAPI `TestClient` with a mocked LLM — no API key or running server required.

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | For **Run turn** | OpenRouter API key ([get one](https://openrouter.ai/)) |
| `OPENROUTER_MODEL` | No | Model override (default: `deepseek/deepseek-v4-flash`) |

`python-dotenv` loads `.env` from the working directory when the server starts. Place `.env` in this folder or the repo root.

Area edits (`POST /api/command`) do not call the LLM.

## Dev: test stacked objects (temporary)

To verify tile scrollbars, start the server with 10 extra objects on tile **(3, 3)**:

```powershell
$env:REALM_STUDIO_DEV_STACK = "1"
uv run realm-studio
```

Unset the variable (or omit it) for the normal demo room.
