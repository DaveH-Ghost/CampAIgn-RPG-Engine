"""
prompt.py

Prompt construction for V0 / V0.1.

This module builds the full text prompt sent to the LLM (DeepSeek via OpenRouter).

It follows the exact structure and rules agreed in the readiness checklist (Section 7).

The prompt includes:
- Character description
- System rules
- Room description
- Current passive vision (from perception)
- Available actions this turn (computed from world state)
- Recent history (from agent's memory)
- Turn-specific reminders
- Output format reminder
- 4 few-shot examples (optional; off by default for token efficiency)

This is kept separate from the LLM client so it can be tested and iterated independently.
"""

from src.agent import Agent
from src.memory import TurnRecord
from src.perception import build_passive_vision
from src.world import World


# =============================================================================
# Few-shot examples (copied verbatim from the readiness checklist)
# =============================================================================

FEW_SHOT_EXAMPLES = """
Example 1: Correct use of `speak` (pure dialogue only)

Context:
You are at (1, 1).
Ceramic Ball (obj_ball_01), (2, 2) - [?]
Wooden Sign (obj_sign_01), (2, 4) - [?] A simple wooden sign on the wall.
You are at (1, 1).
You may move to any coordinate (x, y) where x and y are integers from 0 to 4.
You can look at any object or other agent listed in Passive Vision (including [?] and [?] [changed] entries).

Output:
{
  "reasoning": "I notice the ball has a [?] tag. I should comment on that and consider looking at it soon.",
  "action": "speak",
  "target": null,
  "content": "That ball has a question mark next to it. I wonder what happens if I look at it.",
  "confidence": "curious",
  "emotion": "intrigued"
}

Example 2: Using `look` when seeing `[?]` 

Context:
You are at (2, 3).
Ceramic Ball (obj_ball_01), (2, 2) - A slightly worn ceramic ball. It has a few scuffs and feels light.
Wooden Sign (obj_sign_01), (2, 4) - [?] A simple wooden sign on the wall.
You are at (2, 3).
You may move to any coordinate (x, y) where x and y are integers from 0 to 4.
You can look at any object or other agent listed in Passive Vision (including [?] and [?] [changed] entries).

Output:
{
  "reasoning": "The wooden sign shows [?] with only a glance description. I haven't read it properly yet. I should look at it to get the full text.",
  "action": "look",
  "target": "obj_sign_01",
  "content": null,
  "confidence": "decided",
  "emotion": "curious"
}

Example 3: Choosing a valid coordinate `move`

Context:
You are at (2, 2).
Ceramic Ball (obj_ball_01), (2, 2) - A slightly worn ceramic ball. It has a few scuffs and feels light.
Wooden Sign (obj_sign_01), (2, 4) - It reads: "..."
You are at (2, 2).
You may move to any coordinate (x, y) where x and y are integers from 0 to 4.

Output:
{
  "reasoning": "I want to get closer to the sign so I can examine it more easily. Moving to (2, 4) puts me on the sign's tile.",
  "action": "move",
  "target": "2,4",
  "content": null,
  "confidence": "certain",
  "emotion": "focused"
}

Example 4: Responding to an object that has changed

Context:
You are at (1, 1).
Ceramic Ball (obj_ball_01), (2, 2) - [?] [changed]
Wooden Sign (obj_sign_01), (2, 4) - [?] A simple wooden sign on the wall.
You are at (1, 1).
You may move to any coordinate (x, y) where x and y are integers from 0 to 4.
You can look at any object or other agent listed in Passive Vision (including [?] and [?] [changed] entries).

Output:
{
  "reasoning": "The ceramic ball shows [?] [changed], which means my examined knowledge is out of date. I should look at it again to see the current description.",
  "action": "look",
  "target": "obj_ball_01",
  "content": null,
  "confidence": "curious",
  "emotion": "alert"
}
""".strip()


# =============================================================================
# Prompt sections
# =============================================================================

def _get_system_instructions() -> str:
    """Core rules of the simulation (compiled from the V0 spec)."""
    return """You exist inside a small, controlled 5x5 grid room. Your coordinates range from (0,0) in the southwest corner to (4,4) in the northeast. Y increases northward.

You may only perform ONE action per turn. The allowed actions are:
- move: Move to any in-bounds grid coordinate (x, y). Use target "x,y" (e.g. "2,3"). You cannot move outside the grid.
- look: Examine an object or another agent that appears in your passive vision (including entries marked with [?]). You will receive its detailed description if one exists.
- speak: Say something out loud. Limited to a maximum of five sentences. Prefer pure verbal dialogue; avoid emotes (*smiles*), action markers (_waves_), or stage-direction asides.

Important rules:
- Only entities listed in your current passive vision can be looked at (objects and other agents; you do not see yourself).
- Objects and other agents may show a passive glance line without looking. Hidden detailed description is marked with "[?]" (optionally alongside the passive line). Stale examined knowledge appears as "[?] [changed]" with the passive line.
- Other agents also show their most recent observable action (e.g. speech or movement) appended to their passive vision line, including confidence and Emotion when provided (e.g. '(confidence: curious, Emotion: intrigued)').
- Your words when speaking have no direct mechanical effect on the world, however other agents can hear and react to them.
- Always respond with a single, valid JSON object. Do not add any text before or after the JSON."""


def _get_available_actions(agent: Agent, world: World) -> str:
    """Build the exact 'Available Actions This Turn' block per the V0.2 spec."""
    x, y = agent.position
    lines = [
        f"You are at ({x}, {y}).",
        "You may move to any coordinate (x, y) where x and y are integers from 0 to 4.",
        "",
        "You can look at any object or other agent listed in Passive Vision "
        "(including [?] and [?] [changed] entries).",
    ]
    return "\n".join(lines)


def _format_history(turns: list[TurnRecord]) -> str:
    """Format the recent history exactly as specified in the checklist."""
    if not turns:
        return "No previous turns yet."

    lines = []
    for t in turns:  # oldest first
        lines.append(f"Turn {t.turn_number}:")
        lines.append(f"Action: {t.action}")
        if t.target is not None:
            lines.append(f"Target: {t.target}")
        lines.append(f"Reasoning: {t.reasoning}")
        lines.append(f"Result: {t.result}")
        lines.append("")  # blank line between turns

    return "\n".join(lines).rstrip()


def build_prompt(agent: Agent, world: World, include_examples: bool = False) -> str:
    """
    Assemble the complete prompt for the current turn.

    This follows the canonical high-level order from the V0 spec:
    Character Description, System Instructions, Room Description,
    Current Passive Vision, Available Actions, Recent History,
    Current Instructions, Output Format.

    The four few-shot examples from the checklist are included only when
    include_examples=True (off by default for token efficiency; current
    models perform well without them).

    Args:
        include_examples: Whether to include the four few-shot examples.
            Default is False.
    """
    parts = []

    # 1. Character Description
    parts.append(f"You are {agent.name}.")
    parts.append(f"Your personality: {agent.personality}")
    parts.append("")
    parts.append(f"Your detailed description: {agent.description}")
    parts.append("")

    # 2. System Instructions / Rules
    parts.append(_get_system_instructions())
    parts.append("")

    # 3. Room Description
    parts.append(world.get_room_description())
    parts.append("")

    # 4. Current Passive Vision
    parts.append("Current situation:")
    parts.append(build_passive_vision(agent, world))
    parts.append("")

    # 5. Available Actions This Turn
    parts.append(_get_available_actions(agent, world))
    parts.append("")

    # 6. Recent History
    history_text = _format_history(agent.memory.get_recent_turns(10))
    parts.append("Recent history:")
    parts.append(history_text)
    parts.append("")

    # 7. Current Instructions / Reminders
    parts.append("You may only speak up to five sentences this turn. Spoken text should be things you say out loud.")
    parts.append("")

    # 8. Output Format
    parts.append(
        "Respond with ONLY a valid JSON object matching this exact structure (no extra text, no markdown):\n"
        "{\n"
        '  "reasoning": "Your private thoughts (max 400 characters).",\n'
        '  "action": "move" | "look" | "speak",\n'
        '  "target": "2,3" | "obj_ball_01" | null,\n'
        '  "content": "spoken text or null",\n'
        '  "confidence": "curious" | "certain" | ... (1-3 words),\n'
        '  "emotion": "focused" | "intrigued" | ... (1-3 words)\n'
        "}"
    )
    parts.append("")

    # Few-shot examples (optional for token savings / future chat format)
    if include_examples:
        parts.append("Here are some examples of correct behavior:")
        parts.append(FEW_SHOT_EXAMPLES)

    return "\n".join(parts).strip()
