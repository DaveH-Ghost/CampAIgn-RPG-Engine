"""
simulation.py

Core turn execution logic (one action per turn).

This module ties together:
- The parsed AgentTurn (from LLM structured output)
- The action implementations
- Recording the TurnRecord into the agent's memory
- Updating last_action and passive_result for other agents' vision

It does *not* handle prompt construction or the LLM call itself
(those live in the llm/ package and will be wired in main/simulation loop later).

For now this is useful for:
- Manual stepping / debugging without the LLM
- Unit testing action + memory + perception integration
"""

from src.action_outcome import ActionOutcome
from src.actions import do_move, do_speak
from src.perception import perform_look as do_look
from src.agent import Agent
from src.llm.schemas import AgentTurn
from src.memory import TurnRecord
from src.world import World


def execute_action(agent: Agent, world: World, turn: AgentTurn) -> ActionOutcome:
    """
    Dispatch to the correct action implementation based on the AgentTurn.

    Returns first-person result for the actor and optional third-person
    passive_result for other agents' passive vision.
    """
    action = turn.action
    target = turn.target
    content = turn.content

    if action == "move":
        return do_move(agent, world, target or "")
    elif action == "look":
        return do_look(agent, world, target or "")
    elif action == "speak":
        return do_speak(agent, world, content or "")
    else:
        return ActionOutcome(
            result=f"This action wasn't recognized: {action}",
        )


def next_turn_number_for_agent(agent: Agent) -> int:
    """Return the next per-agent sequential turn number for TurnRecord."""
    return agent.memory.turn_count + 1


def _append_passive_mood(passive_result: str, turn: AgentTurn) -> str:
    """Append confidence/emotion from the turn to a third-person passive_result."""
    if not passive_result:
        return passive_result

    parts = []
    if turn.confidence:
        parts.append(f"confidence: {turn.confidence}")
    if turn.emotion:
        parts.append(f"Emotion: {turn.emotion}")
    if not parts:
        return passive_result

    return f"{passive_result} ({', '.join(parts)})"


def step_turn(
    agent: Agent, world: World, turn: AgentTurn, turn_number: int
) -> TurnRecord:
    """
    Execute one complete turn for the agent.

    1. Run the action (side effects on agent/world + get result strings).
    2. Update passive_result when the action succeeds observably.
    3. Create a TurnRecord containing the agent's reasoning + the result.
    4. Add the record to the agent's memory (capped at 10 by Memory).
    5. Update agent's last_action.

    Returns the TurnRecord that was created (useful for logging/tests).
    """
    outcome = execute_action(agent, world, turn)

    if outcome.passive_result:
        agent.passive_result = _append_passive_mood(outcome.passive_result, turn)

    record = TurnRecord(
        turn_number=turn_number,
        action=turn.action,
        target=turn.target,
        content=turn.content,
        reasoning=turn.reasoning,
        result=outcome.result,
    )

    agent.memory.add_turn(record)
    agent.last_action = turn.action

    return record
