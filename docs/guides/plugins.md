# Plugin primitives (1.2.0)

CampAIgn-RPG-Engine exposes a small capability surface for apps and Studio plugins.

## Session extensions

Plugin-owned JSON lives in `session.extensions[plugin_id]` and round-trips in saves (`extensions` field, snapshot v4+).

```python
session.set_extension("my_plugin", {"count": 1})
value = session.get_extension("my_plugin")
```

## Interaction handlers

See [handlers.md](handlers.md). Register at process startup before loading saves that reference handler ids.

## Turn verbs

Register free-target compound actions (`action: "verb"`):

```python
from campaign_rpg_engine import register_turn_verb, ActionOutcome

def wave(session, agent, area, turn):
    return ActionOutcome(result="You wave.", passive_result=f"{agent.name} waves.")

register_turn_verb("wave", wave, description="Wave hello")

# Optional: path toward an agent before running (like interact pathing)
register_turn_verb(
    "handoff",
    handoff,
    description="Hand something to a nearby agent",
    path_range=1,
    path_target_from_turn=lambda turn: (turn.target or "").split()[0] or None,
)
```

The LLM uses `action: "verb"`, `verb: "wave"`, and optional `target`.

## Prompt slots

Register named prompt layout slots:

```python
from campaign_rpg_engine import register_prompt_slot, PromptBlock

register_prompt_slot("my_plugin", lambda session, agent, area, ctx, options: "…")

# Add PromptBlock(type="slot", name="my_plugin") to the session prompt layout.
```

## Events

```python
from campaign_rpg_engine import register_event_listener, emit_session_event

register_event_listener("turn_committed", my_fn, plugin_id="my_plugin")
```

Stable event names (v1):

| Event | When |
|-------|------|
| `turn_committed` | After a compound turn is committed |
| `agent_moved` | After a move (edit or turn) |
| `object_created` / `object_removed` / `object_edited` | World object mutations |
| `agent_created` / `agent_removed` / `agent_edited` | Agent mutations |
| `session_loaded` | App emits after import (Studio) |

Use `unregister_event_listeners(plugin_id)` when disabling a plugin.

## Save rules

- **Code** (handlers, turn verbs, prompt slots) must be registered at process startup.
- **State** lives in `session.extensions` and is stored in the save file.
- Saves store plugin data, not Python source. Memory modules are built-in only
  (``recent_turns``, ``salient_turns``, ``rolling_summary``, ``affinity``).

## Studio

See [CampAIgn-RPG-Studio/plugins](https://github.com/DaveH-Ghost/CampAIgn-RPG-Studio/tree/main/plugins) for the plugin host, upload path, and Plugins tab.
