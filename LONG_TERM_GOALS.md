# Long Term Goals

**Purpose:**  
This document exists to capture big, exciting, "someday" dreams for this project without letting them pollute or over-scope the current version we're working on.

These are **aspirational goals**. They are not targets for Version 0, Version 0.1, or even Version 1 unless we explicitly decide to pull one in. They are recorded here so they aren't lost and so we can feel the satisfaction of moving them into the "Achieved" section when the time comes.

Treat this file like a trophy case. Checking something off here should feel like a real milestone.

---

## Dream Goals

These are currently out of scope. They represent the kind of experiences we eventually want to create.

### Foundational / Relatively Easier Goals

These are considered lower-complexity improvements that could be reasonable targets for V0.1 or V0.2.

### More Complex Goals

- [ ] Multiple agents that can observe each other, start conversations, form relationships, and influence one another over time  
  *(V0.1 will add multiple **non-interacting** agents sharing a world — same grid, private memory, no mutual perception. That is a stepping stone, not this goal.)*
- [ ] Objects that have their own behaviors and actions (examples: food that can be eaten and gives a taste description, a puzzle box with interactive mechanisms, a door that can be locked/unlocked, etc.)
- [ ] Rectangular / multi-tile objects (e.g. long walls, large furniture, 2x2 trees with 6x6 shadows) where objects occupy multiple grid tiles using size + bounding box definitions instead of single-tile objects
- [ ] A visual interface similar to Roll20 — a grid with tokens representing agents and objects, plus chat bubbles when agents speak
- [ ] **Roll20 plugin support**  
  Integrate the agent with real Roll20 games (via Mod/API Scripts + chat bridge). Enable the agent to perceive live map state and control tokens representing D&D characters, NPCs, and enemies. The external agent handles reasoning/LLM calls; a companion Roll20 script executes token movement, sheet updates, etc. (Roll20 Pro required for the scripting side; communication constrained by the sandbox model.)
- [ ] Agents that can create or modify objects in the world (with some form of validation or rules)
- [ ] Richer memory systems (beliefs, relationships, long-term goals, emotional state)
- [ ] The ability for agents to develop and pursue their own goals over many turns instead of only reacting to the current situation

---

## Achieved Goals

This section is for goals that have actually been completed. When something moves here, it should feel like a genuine accomplishment.

- [x] **General "object knowledge is stale" notification (V0.1)**  
  When an object's detailed description changes after an agent has examined it, passive vision shows a neutral stale state (e.g. `[?] [changed] A simple wooden sign on the wall.`) so the agent knows to `look` again. Works for any object via `ever_looked` + `World.invalidate_object_knowledge()`, not sign-specific. Shipped in V0.1 Section 1 with passive/detailed descriptions (Section 2 perception extension). See [v0.1-implementation-readiness-checklist.md](docs/v0.1-implementation-readiness-checklist.md).

---

## How to Use This Document

- Add new dream goals whenever they come up during development or daydreaming.
- Do **not** use these goals to justify adding scope to the current version.
- When we decide a dream is worth actively working toward, we should first create a proper design document for it (not just check it off).
- Moving something from "Dream Goals" to "Achieved" should be celebrated.

---

*This file is meant to stay fun and inspiring. It is not a roadmap.*