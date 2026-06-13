# realm-studio

Example web app for [Realm-Fabric](https://github.com/) — wraps the engine `Session` API over HTTP.

**Location:** `examples/web/realm-studio` in the Realm-Fabric repo.

**Status:** **0.3.1a** — FastAPI backend + `GET /api/state` snapshot; minimal JSON viewer page. Grid UI and right-click editing come in later slices ([v0.3.1-changelog](../../../docs/v0.3.1-changelog.md)).

## Prerequisites

- Python ≥3.11
- [uv](https://docs.astral.sh/uv/)
- Realm-Fabric engine at repo root (this example uses a path dependency on `realm-fabric`)

## Setup

From this directory:

```powershell
cd examples\web\realm-studio
uv sync
```

## Run (dev server)

```powershell
uv run realm-studio
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765) — opens automatically in your default browser. Use `--no-browser` to skip:

```powershell
uv run realm-studio --no-browser
```

Alternative:

```powershell
uv run uvicorn backend.app:app --host 127.0.0.1 --port 8765 --reload
```

## API (0.3.1a)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | `{ "ok": true }` |
| `GET` | `/api/state` | Engine `Session.snapshot()` — grid, agents, objects, passive vision |

LLM turns and area-edit commands arrive in **0.3.1c** / **0.3.1d**.

## Tests

```powershell
uv run pytest
```

Uses FastAPI `TestClient` — no API key or running server required.

## Environment

**0.3.1a** does not call the LLM. For future slices, copy `.env` with `OPENROUTER_API_KEY` to the repo root or this folder as documented in 0.3.1d.
