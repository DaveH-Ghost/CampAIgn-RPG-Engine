# Realm Fabric

A grid-based agent simulation framework designed around structured output and narrative roleplay.

**Current Status:** V0 complete and validated (100+ LLM turns, reliable structured output). V0.1 Sections 1–2 implemented (generalized perception + world editing commands). Section 3 (multi-agent polish) not yet implemented.

**Documentation:**

- [V0.1 implementation checklist](docs/v0.1-implementation-readiness-checklist.md) — agreed design for the next version
- [Roadmap](docs/ROADMAP.md) — version plans (V0.1, V0.2, V0.3)
- [Long-term goals](LONG_TERM_GOALS.md) — aspirational features
- [V0 implementation checklist](docs/v0-implementation-readiness-checklist.md) — V0 design reference

## Running / Testing (without LLM)

1. Install [uv](https://docs.astral.sh/uv/) if you don't have it (Windows PowerShell):
  ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
2. In the project folder:
  ```powershell
   cd C:\Users\david\desktop\Projects\Git_Projects\Realm-Fabric
   uv sync
  ```
3. Run the interactive manual tester:
  ```powershell
   uv run python src/main.py
  ```
   Few-shot examples are disabled by default for token efficiency (saves ~50% tokens). Use `--with-fewshots` if you want the 4 examples included.
   Inside the `(realm)` prompt you can:
  - `list` — overview of all agents and objects (no turn consumed)
  - `objects` — list all objects with ids (for `edit-object` / `delete-object`)
  - `agents` — list all agents with ids and active marker
  - `state` — active agent context (memory, turn count, few-shots)
  - `vision` — see what the active agent currently perceives
  - `prompt` — see the full prompt the LLM would receive
  - `step look obj_ball_01` — manually drive the agent (great for testing)
  - `Explorer` — (type the agent's name) to let the **LLM** decide the next action (requires OPENROUTER_API_KEY). Few-shot examples are OFF by default (saves ~50% tokens; current models perform well without them). Use `--with-fewshots` or `fewshots on` to enable.
  - `quit`

### World editing (V0.1)

Listing and editing commands do **not** consume a turn. Use `list`, `objects`, or `agents` to look up entity ids before editing.

```
list
objects
agents
create-object name "Crate" pdesc "A crate." desc "A wooden crate." at 0,0
edit-object obj_sign_01 pdesc "A sign on the wall." desc "Updated sign text."
edit-object obj_ball_01 pos 3,3
delete-object obj_crate_01
create-agent name "Goblin" desc "A grumpy goblin." at 0,3
edit-agent agent_01 name "Scout"
delete-agent agent_goblin_01
```

The old V0 `sign` command is removed. Update the sign with:

```
edit-object obj_sign_01 pdesc "A sign on the wall." desc "This is new text."
```

Objects support two description layers: **`pdesc`** (passive glance, visible without looking) and **`desc`** (detailed, hidden behind `[?]` until examined). Stale examined knowledge shows as `[?] [changed] {pdesc}`.

### Planned for V0.1 Section 3 (not yet implemented)

- **Multi-agent:** `switch <name>` to change active agent without a turn; per-agent turn numbers

## Environment Variables & .env Files (Beginner Guide)

This project uses **environment variables** for things like API keys. We manage them with a library called `python-dotenv`.

### What are .env files?

A `.env` file is just a plain text file that looks like this:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
```

Each line is `KEY=VALUE`. These become available to your program as if you had set them in the operating system environment.

### Why use .env files?

- You don't want to hard-code secrets (API keys, passwords) into your source code.
- Different people/machines can have different values.
- You can have different settings for development vs production.

### How to set one up in this project

1. Copy the template that is safe to commit:
  ```powershell
   copy .env.example .env
  ```
2. Open the new `.env` file in a text editor and fill in the values.
3. Save it. The program will automatically pick it up.

**Important**: The file `.env` is listed in `.gitignore`, so Git will never commit your real keys.

### How this program loads .env files

When you trigger anything that needs the LLM (e.g. typing the agent's name in the stepper), the code in `src/llm/client.py` automatically runs:

```python
load_dotenv()                    # loads .env
load_dotenv(".env.local", override=True)   # then loads .env.local (if it exists)
```

This means:

- Values in `.env.local` will override values in `.env`
- You only need a `.env` file for basic use

### Can I have multiple .env files?

**Yes.** This is very common. Here are typical patterns:


| File               | Purpose                          | Commit to Git?                | Example use                                                  |
| ------------------ | -------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| `.env`             | Base settings for the project    | No (use .env.example instead) | Shared team defaults                                         |
| `.env.local`       | Your personal overrides          | **Never**                     | Your own API keys, local database URL                        |
| `.env.development` | Development-specific settings    | Sometimes                     | Debug flags, local services                                  |
| `.env.production`  | Production settings              | Sometimes                     | Real production keys (usually managed by the server instead) |
| `.env.example`     | Template with placeholder values | **Yes**                       | Shows teammates what keys are needed                         |


You can load any of them explicitly like this (advanced):

```python
from dotenv import load_dotenv
load_dotenv(".env.development", override=True)
```

### Quick commands

```powershell
# Create your local file from the template
copy .env.example .env

# Edit it (add your real OPENROUTER_API_KEY)

# Then run the program - it will automatically read the .env file
uv run python src/main.py
```

### Without any .env file

You can still use almost everything:

- All the manual commands (`step ...`, `vision`, `state`, etc.) work perfectly.
- The only thing that requires an `OPENROUTER_API_KEY` is when you type an agent's name (e.g. `Explorer`) to let the LLM actually decide what to do.

This design is intentional so you can explore and test the system without needing any paid services.

### Where the code actually reads the variables

Look at `src/llm/client.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()                    # loads .env + .env.local
api_key = os.getenv("OPENROUTER_API_KEY")
model   = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
```

`os.getenv("SOME_KEY")` looks for an environment variable. `load_dotenv()` populates those variables from the .env file(s) before the rest of the program runs.

That's the whole magic.

## Running tests

Tests use [pytest](https://docs.pytest.org/) and run **without** an API key or network access. They cover world setup, the `AgentTurn` schema, simulation turns, and passive vision / invalidation logic.

### Run all tests

From the project folder:

```powershell
uv run pytest
```

By default this runs quietly (`-q` is set in `pyproject.toml`). You should see a final `passed` summary when everything is green.

### Useful variants

```powershell
# Verbose — shows each test name as it runs
uv run pytest -v

# Single file
uv run pytest tests/test_perception.py -v

# Single test by name
uv run pytest tests/test_perception.py::test_ball_vision_states_never_stale_current -v

# Stop on first failure (helpful while debugging)
uv run pytest -x
```

### What each test file covers

| File | Focus |
|------|--------|
| `tests/test_schema.py` | `AgentTurn` Pydantic validation (valid/invalid move, look, speak) |
| `tests/test_world.py` | Initial world state, grid rules, passive vision baseline |
| `tests/test_simulation.py` | `step_turn`, actions, memory side effects, prompt builder |
| `tests/test_perception.py` | V0.1 generalized "has changed" vision and cross-agent invalidation |
| `tests/test_world_edit.py` | V0.1 world editing commands (create/edit/delete, listings, id generation) |

### First-time setup

`uv sync` installs pytest via the `dev` dependency group. If pytest is missing:

```powershell
uv sync
uv run pytest -v
```

