# Realm-Fabric Roadmap

This document outlines concrete plans for versions after V0.

See also [LONG_TERM_GOALS.md](../LONG_TERM_GOALS.md) for larger aspirational / dream goals that are not yet tied to specific versions.

These plans are subject to change as we learn and discuss.

## V0.1

**Status:** Sections 1–2 **implemented** (generalized perception, editing commands, passive/detailed descriptions). Section 3 (multi-agent polish: `switch`, per-agent turn numbers) — design complete, not yet implemented. See [v0.1-implementation-readiness-checklist.md](v0.1-implementation-readiness-checklist.md).

**Focus:** Make the world dynamic with general editing tools and improved perception for changes, then add multi-agent support. Everything remains fully manual (human decides which agent acts when by typing its name, or uses `switch` to inspect another agent without a turn). The initial world still starts with a single "Explorer" agent, ball, and sign.

**Implementation order:** (1) generalized stale perception → (2) editing commands + perception extension → (3) multi-agent support.

### 1. Generalize the "has changed" notification — ✅ Implemented
- Removed all sign-specific special cases in `perception.py`.
- Added `ever_looked` tracking on `Memory` to distinguish never examined from stale examined knowledge.
- Stale vision: **`[?] [changed] {passive}`** (or `[?] [changed]` if no passive line). Never-examined with hidden detail: `[?]` or `[?] {passive}`.
- Any change to an object's **detailed** description (`desc`) calls `World.invalidate_object_knowledge(id)` on all agents with current knowledge.
- Name, position, or **passive** (`pdesc`) edits do **not** invalidate look knowledge.
- Few-shot examples and system rules updated in `prompt.py`.
- The `sign` command removed; use `edit-object obj_sign_01 desc "..."` (and optional `pdesc`).

### 2. General editing commands (objects + agents) — ✅ Implemented
- Keyword-style stepper commands (`create-object`, `edit-object`, `delete-object`, `create-agent`, `edit-agent`, `delete-agent`), parsed with `shlex.split`.
- Objects support **`pdesc`** (passive glance) and **`desc`** (detailed, hidden behind `[?]` until examined).
- **Listing commands** (read-only, no turn consumed): `list` (everything), `objects` (all objects), `agents` (all agents with ids and active marker). Primary way to look up ids for edit/delete without running a turn or viewing a prompt.
- **ID rules:** auto-generated per category (`obj_{slug}_01`, `agent_{slug}_01`); immutable after creation. Object display names may duplicate; agent display names must be unique among agents (case-insensitive). Objects and agents may share a display name with each other.
- **Edit/delete** commands take entity **id**, not display name.
- Editing an object's description triggers generalized "has changed" invalidation (per item 1).
- Agent edits affect name/description/position only — private memory is untouched.
- `create-agent` does not change the active agent.
- The world starts identical to V0; all changes happen at runtime via these commands.
- Keep the experience fully manual (no automatic sequencing of agent turns).

### 3. Multi-agent support — design complete, not yet implemented
- Each agent has its own independent `Memory` (own turn history, own `looked_at` / `ever_looked`, own position).
- Typing an agent's name (e.g. `Explorer` or `Goblin`) gives *that agent* an **LLM turn** — build prompt, execute action, update only that agent, set as active.
- **`switch <name>`** changes the active agent without a turn or LLM call (for `vision`, `state`, `prompt`, manual `step`).
- `vision`, `state`, `prompt`, manual `step`, etc. operate on the active agent.
- **Per-agent turn numbers** in `TurnRecord` (no gaps when agents alternate).
- Add `World.get_agents()`, `get_agent_by_id()`, `get_agent_by_name()`; keep `get_agent()` as first agent for backward compatibility.
- Agents share the same world grid and objects but do not observe or interact with each other (no other agents in passive vision).
- Initial world (`create_initial_world`) stays exactly as in V0. Additional agents are introduced via editing commands from item 2.

These changes improve experimentation while keeping the core "one structured action per LLM call per agent" model that was validated in V0.

## V0.2

**Status:** Undecided.

We will discuss and define V0.2 after completing V0.1.

## V0.3

**Focus:** Basic graphical user interface for visualization and direct interaction. Prepares the data model for visual rendering.

- **GUI**:
  - A clickable grid view of the world.
  - Clicking on a tile opens a context menu.
  - The menu allows running commands on that tile/location (e.g. create object/agent here, edit nearby entities, inspect, delete, move things, etc.).
  - The GUI will coexist with (or augment) the existing ManualStepper for LLM/agent turns and logging.

- **Image / rendering support**:
  - `Object` and `Agent` dataclasses will gain a new field (e.g. `image: Optional[str] = None` or similar) to specify an image, sprite path, or asset identifier.
  - This field will be used by the GUI to draw the entity on its tile.
  - Core logic (perception, actions, memory, prompts) will ignore the image field for now (it is purely for visualization).
  - Initial world and editing commands will support setting the image field.

Larger items (richer agent interactions, object behaviors, full D&D-style systems, Roll20 integration, lorebooks, etc.) remain in LONG_TERM_GOALS.md and can be pulled into specific versions when we decide they are ready.

---

**Notes**
- Each version should stay focused. Create a readiness checklist before implementation (as with V0 and V0.1).
- When a version is **implemented**, move relevant items to "Achieved" in LONG_TERM_GOALS.md and update this roadmap.
- This document is meant to be living — edit it as plans evolve.
