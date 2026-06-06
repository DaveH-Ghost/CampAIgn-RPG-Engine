"""
simulation.py

Core turn execution logic for V0.

This module ties together:
- The parsed AgentTurn (from LLM structured output)
- The action implementations
- Recording the TurnRecord into the agent's memory
- Updating last_action

It does *not* handle prompt construction or the LLM call itself
(those live in the llm/ package and will be wired in main/simulation loop later).

For now this is useful for:
- Manual stepping / debugging without the LLM
- Unit testing action + memory + perception integration
"""

from src.actions import do_look, do_move, do_speak
from src.agent import Agent
from src.llm.schemas import AgentTurn
from src.memory import TurnRecord
from src.world import World


def execute_action(agent: Agent, world: World, turn: AgentTurn) -> str:
    """
    Dispatch to the correct action implementation based on the AgentTurn.

    Returns the result string that will be shown to the agent
    (and recorded in the TurnRecord).
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
        # Should never happen if schema validation passed
        return f"This action wasn't recognized: {action}"


def next_turn_number_for_agent(agent: Agent) -> int:
    """Return the next per-agent sequential turn number for TurnRecord."""
    return agent.memory.turn_count + 1


def step_turn(
    agent: Agent, world: World, turn: AgentTurn, turn_number: int
) -> TurnRecord:
    """
    Execute one complete turn for the agent.

    1. Run the action (side effects on agent/world + get result string).
    2. Create a TurnRecord containing the agent's reasoning + the result.
    3. Add the record to the agent's memory (capped at 10 by Memory).
    4. Update agent's last_action.

    Returns the TurnRecord that was created (useful for logging/tests).
    """
    result = execute_action(agent, world, turn)

    record = TurnRecord(
        turn_number=turn_number,
        action=turn.action,
        target=turn.target,
        content=turn.content,
        reasoning=turn.reasoning,
        result=result,
    )

    agent.memory.add_turn(record)
    agent.last_action = turn.action

    return record
