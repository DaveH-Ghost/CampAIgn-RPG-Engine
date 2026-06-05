# Realm-Fabric Roadmap

This document outlines concrete plans for versions after V0.

See also [LONG_TERM_GOALS.md](../LONG_TERM_GOALS.md) for larger aspirational / dream goals that are not yet tied to specific versions.

These plans are subject to change as we learn and discuss.

## V0.1

**Focus:** Make the world dynamic and support multiple agents, with general editing tools and improved perception for changes. Everything remains fully manual (human decides which agent acts when by typing its name). The initial world state remains unchanged (still starts with a single "Explorer" agent).

### 1. Generalize the "has changed" notification
- Remove all sign-specific special cases.
- Any change to an object's description (via editing commands) will invalidate the "looked at" knowledge for **all agents** that have previously looked at that object.
- Agents that had looked at the object will see a generalized "[?] The <Object Name> has changed since you last looked at it." notification in their passive vision (instead of plain "[?]").
- The `invalidate_look` mechanism in `Memory` will be used (and extended if needed) to support this across multiple agents.
- The special `sign "new text"` command will be removed (see editing commands below).

### 2. Multi-agent support
- The world, stepper, perception, memory, simulation, and prompt builder will treat multiple agents as first-class.
- Each agent has its own independent `Memory` (own turn history, own `looked_at` set, own position).
- Typing an agent's name in the ManualStepper (e.g. `Explorer` or `Goblin`) gives *that agent* a turn:
  - Builds a prompt specific to that agent.
  - Lets the LLM decide its action (if using LLM mode).
  - Executes the turn for that agent only.
  - Updates only that agent's state and memory.
- The currently "active" agent (last one given a turn, or switched to) is used for commands like `vision`, `state`, `prompt`, manual `step`, etc.
- Agents share the same world grid and objects but do not yet observe or interact with each other (no perception of other agents, no conversations, etc.).
- `do_agents` command (and related listing) will be enhanced to clearly show multiple agents.
- Initial world (`create_initial_world`) stays exactly as in V0 (one agent). Additional agents are introduced via the new editing commands during a session.

### 3. General editing commands (objects + agents)
- Replace the special `sign` command with a set of general commands in the ManualStepper for creating, editing, and deleting both **objects** and **agents**.
- Objects and agents may have the same `name`, but must have unique `id` values.
- New commands will support:
  - Creating new objects/agents at specific positions.
  - Editing name, description, position (and other fields as appropriate).
  - Deleting objects/agents.
- Editing an object's description will trigger the generalized "has changed" invalidation for all relevant agents (per item 1).
- Editing agents will update their description/position/etc. live. (Agent memory is private and not directly edited this way.)
- Commands will be designed for easy use during manual testing sessions.
- The world starts identical to V0; all changes happen at runtime via these commands.
- Keep the experience fully manual (no automatic sequencing of agent turns).

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
- Each version should stay focused. We will create a small readiness checklist or plan doc before starting implementation on a version (similar to the V0 checklist).
- When a version is complete, we can move relevant items to "Achieved" in LONG_TERM_GOALS.md and update this roadmap.
- This document is meant to be living — edit it as plans evolve.