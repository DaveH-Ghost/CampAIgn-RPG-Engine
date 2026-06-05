"""
main.py

Entry point for manual stepping in V0.1 (per readiness checklist).

Supports:
- step                  : advance one turn. For now you (the human) supply
                          the AgentTurn fields to simulate what the LLM would
                          have output. This lets us test the full loop
                          (action -> memory -> vision) without the LLM.
- list / objects / agents : list world entities (read-only, no turn)
- create-object / edit-object / delete-object : edit objects at runtime
- create-agent / edit-agent / delete-agent   : edit agents at runtime
- quit / exit           : leave the simulation.
- vision / state        : print current passive vision or agent/world state.

Typing an agent's name (e.g. "Explorer") will automatically build a prompt
using the current world state and call the LLM to decide the next action.
This design makes it easy to support multiple agents later.

Future: real autonomous runs, better logging, etc.

Run with (from the project root):

    # Easiest way (few-shots OFF by default for token efficiency)
    uv run python src/main.py

    # To include the four few-shot examples:
    uv run python src/main.py --with-fewshots

    # After `uv sync`, you can also do:
    # uv run realm
    # (if the entry point was picked up)

    # To use real LLM calls, copy .env.example to .env and add your OPENROUTER_API_KEY

    # Inside, use 'fewshots off' to toggle at runtime too.

"""

import argparse
import os
import string
import sys

# Ensure 'src' package is importable no matter how this script is launched
# (uv run, python src/main.py, double-click, etc.)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import cmd

from src.log_utils import close_file_logging, log_error, log_turn, setup_file_logging
from src.world import create_initial_world
from src.simulation import step_turn
from src.llm.schemas import AgentTurn
from src.llm.prompt import build_prompt
from src.perception import build_passive_vision
from src.world_edit import (
    create_agent_from_args,
    create_object_from_args,
    delete_agent_by_id,
    delete_object_by_id,
    edit_agent_from_args,
    edit_object_from_args,
    format_agents_list,
    format_full_list,
    format_objects_list,
)

# Lazy import for the client so you can run the manual stepper
# without an OPENROUTER_API_KEY
_get_next_action = None

def _get_llm_function():
    global _get_next_action
    if _get_next_action is None:
        from src.llm.client import get_next_action as _gn
        _get_next_action = _gn
    return _get_next_action


class ManualStepper(cmd.Cmd):
    # Allow hyphenated commands (create-object, edit-agent, etc.)
    identchars = string.ascii_letters + string.digits + "_-"

    intro = (
        "Realm-Fabric V0.1 Manual Stepper\n"
        "Type 'help' or '?' for commands.\n"
        "- 'step <action> ...'   : manually simulate a turn (for testing)\n"
        "- Type an agent's name (e.g. 'Explorer') : let the LLM decide its action\n"
        "- 'list' / 'objects' / 'agents' : list world entities (no turn)\n"
        "- 'create-object' / 'edit-object' / 'delete-object' : edit objects\n"
        "- 'create-agent' / 'edit-agent' / 'delete-agent' : edit agents\n"
        "- 'prompt' : show the full prompt that would be sent to the LLM\n"
        "- 'fewshots on/off' : toggle few-shot examples in prompts (off by default)\n"
        "Sign updates: edit-object obj_sign_01 desc \"new text\" (pdesc for glance text)\n"
        "CLI flags: --log , --with-fewshots\n"
        "Example: Explorer\n"
        "Example: step look obj_ball_01\n"
        "Example: list\n"
        "Example: edit-object obj_sign_01 desc \"Updated sign text.\"\n"
    )
    prompt = "(realm) "

    def __init__(self, include_examples: bool = False):
        super().__init__()
        self.world = create_initial_world()
        # Support multiple agents by name (case-insensitive lookup)
        self.agents: dict[str, "Agent"] = {
            a.name.lower(): a for a in self.world.agents
        }
        self.agent = self.world.get_agent()  # current active agent
        self.turn_number = 0
        self.include_examples = include_examples  # for prompt builder, toggleable for experiments

    def do_vision(self, arg):
        """Show current passive vision."""
        print(build_passive_vision(self.agent, self.world))

    def do_prompt(self, arg):
        """Show the full prompt that would be sent to the LLM right now."""
        prompt = build_prompt(self.agent, self.world, include_examples=self.include_examples)
        print(f"[Full prompt - {len(prompt)} characters] (fewshots={'on' if self.include_examples else 'off'})\n")
        print(prompt)

    def do_state(self, arg):
        """Print basic agent and world state (for the currently active agent)."""
        print(f"Turn: {self.turn_number}")
        print(f"Active agent: {self.agent.name} at {self.agent.position}")
        print(f"Memory turns: {self.agent.memory.turn_count}")
        print(f"Looked at (current): {sorted(self.agent.memory.looked_at)}")
        print(f"Ever looked at: {sorted(self.agent.memory.ever_looked)}")
        print(f"Few-shots in prompts: {'on' if self.include_examples else 'off'}")
        objs = [(o.name, o.id, o.position) for o in self.world.get_objects()]
        print(f"Objects: {objs}")

    def do_objects(self, arg):
        """List all objects in the world (id, name, position). Does not consume a turn."""
        print(format_objects_list(self.world))

    def do_agents(self, arg):
        """List all agents in the world (id, name, position, active marker). Does not consume a turn."""
        print(format_agents_list(self.world, self.agent))

    def do_list(self, arg):
        """List all agents and objects (same as running agents then objects). Does not consume a turn."""
        print(format_full_list(self.world, self.agent))

    def do_create_object(self, arg):
        """
        Create a new object in the world.

        Usage:
            create-object name "Ceramic Ball" pdesc "A ball on the floor." desc "A worn ball." at 2,2
        """
        obj, message = create_object_from_args(self.world, arg)
        print(message)

    def do_edit_object(self, arg):
        """
        Edit an existing object by id.

        Usage:
            edit-object obj_ball_01 pdesc "A ball." desc "New description."
            edit-object obj_ball_01 name "Old Ball" pos 3,3
        """
        print(edit_object_from_args(self.world, arg))

    def do_delete_object(self, arg):
        """
        Delete an object by id.

        Usage:
            delete-object obj_ball_01
        """
        print(delete_object_by_id(self.world, arg))

    def do_create_agent(self, arg):
        """
        Create a new agent in the world. Does not change the active agent.

        Usage:
            create-agent name "Goblin" desc "A grumpy goblin." at 0,3
        """
        agent, message = create_agent_from_args(self.world, arg)
        if agent is not None:
            self.agents[agent.name.lower()] = agent
        print(message)

    def do_edit_agent(self, arg):
        """
        Edit an existing agent by id.

        Usage:
            edit-agent agent_01 desc "Updated personality."
            edit-agent agent_01 name "Scout" pos 2,1
        """
        result = edit_agent_from_args(self.world, arg)
        if result.ok and result.agent is not None:
            if result.old_name_lower and result.old_name_lower in self.agents:
                del self.agents[result.old_name_lower]
            self.agents[result.agent.name.lower()] = result.agent
        print(result.message)

    def do_delete_agent(self, arg):
        """
        Delete an agent by id. Cannot delete the last agent.

        Usage:
            delete-agent agent_goblin_01
        """
        result = delete_agent_by_id(self.world, arg.strip())
        if result.ok and result.deleted_agent is not None:
            name_lower = result.deleted_agent.name.lower()
            if name_lower in self.agents:
                del self.agents[name_lower]
            if self.agent.id == result.deleted_agent.id:
                self.agent = self.world.agents[0]
        print(result.message)

    def do_fewshots(self, arg):
        """
        Toggle or show the few-shot examples setting for prompts.
        (Default is now OFF for token efficiency.)

        Usage:
            fewshots          # show current state
            fewshots on       # enable (adds the 4 examples)
            fewshots off      # disable
        """
        arg = arg.strip().lower()
        if arg in ("on", "yes", "true", "1", "enable"):
            self.include_examples = True
            print("Few-shot examples: ENABLED (included in prompts)")
        elif arg in ("off", "no", "false", "0", "disable"):
            self.include_examples = False
            print("Few-shot examples: DISABLED (removed from prompts to save tokens)")
        else:
            status = "ENABLED" if self.include_examples else "DISABLED"
            print(f"Few-shot examples are currently {status}.")
            print("Use 'fewshots on' or 'fewshots off' to change.")

    def do_step(self, arg):
        """
        Manually simulate one turn for the currently active agent.
        Use this for testing specific behaviors without calling the LLM.

        Usage:
            step move north
            step look obj_ball_01
            step speak This is what I say.
        """
        if not arg:
            print("Usage: step <move|look|speak> [target_or_content...]")
            return

        parts = arg.split(maxsplit=1)
        action = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        target = None
        content = None

        if action == "move":
            target = rest.strip() or None
        elif action == "look":
            target = rest.strip() or None
        elif action == "speak":
            content = rest.strip() or None
        else:
            print(f"Unknown action '{action}'. Use move, look, or speak.")
            return

        try:
            turn = AgentTurn(
                reasoning="[manual step - no real reasoning]",
                action=action,
                target=target,
                content=content,
            )
        except Exception as e:
            log_error("Invalid manual turn data", e)
            print(f"Invalid turn data: {e}")
            return

        self.turn_number += 1

        full_prompt = build_prompt(self.agent, self.world, include_examples=self.include_examples)

        record = step_turn(self.agent, self.world, turn, self.turn_number)

        # Rich log for manual step (no raw LLM output since it was manual)
        log_turn(
            self.turn_number,
            prompt=full_prompt,
            result=f"Action: {record.action} target={record.target} content={record.content}\n"
                   f"Reasoning: {record.reasoning}\nResult: {record.result}",
            always_to_file=False,
        )

    def onecmd(self, line):
        """Support hyphenated commands like create-object and edit-agent."""
        line = self.precmd(line)
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.postcmd(self.emptyline(), line)
        if not cmd:
            return self.postcmd(self.default(line), line)
        self.lastcmd = line
        func = getattr(self, "do_" + cmd.replace("-", "_"), None)
        if func is None:
            return self.postcmd(self.default(line), line)
        return self.postcmd(func(arg), line)

    def do_help(self, arg):
        """Show help; supports hyphenated command names."""
        if arg:
            arg = arg.replace("-", "_")
        return super().do_help(arg)

    def do_quit(self, arg):
        """Exit the simulator."""
        print("Goodbye.")
        return True

    def do_exit(self, arg):
        """Exit the simulator."""
        return self.do_quit(arg)

    def do_EOF(self, arg):
        """Ctrl-D to exit."""
        print()
        return self.do_quit(arg)

    # ------------------------------------------------------------------
    # LLM-driven turns by typing agent name (supports future multi-agent)
    # ------------------------------------------------------------------

    def default(self, line: str):
        """
        If the user types an agent's name (instead of a built-in command),
        run that agent using the LLM to decide its action.
        This is the main way to let agents "think" autonomously.
        """
        line = line.strip()
        if not line:
            return

        name_lower = line.lower()
        if name_lower in self.agents:
            self._run_llm_turn_for_agent(self.agents[name_lower])
            return

        # Not an agent name — let cmd.Cmd handle it (unknown command)
        super().default(line)

    def _run_llm_turn_for_agent(self, agent: "Agent"):
        """Build prompt, call LLM, execute the resulting turn."""
        print(f"\n=== Running LLM for {agent.name} ===")

        try:
            prompt = build_prompt(agent, self.world, include_examples=self.include_examples)
            print(f"Prompt length: {len(prompt)} chars (fewshots={'on' if self.include_examples else 'off'}, type 'prompt' to view full)")

            print("Calling LLM...")
            get_next_action = _get_llm_function()
            llm_response = get_next_action(prompt)
            turn = llm_response.turn

            # === Rich logging using the logging module (per readiness checklist) ===
            # This will go to console (rich) and to file if --log or error
            log_turn(
                self.turn_number + 1,
                prompt=prompt,
                raw_output=llm_response.raw_response,
                parsed_turn={
                    "action": turn.action,
                    "target": turn.target,
                    "content": turn.content,
                    "reasoning": turn.reasoning,
                    "confidence": turn.confidence,
                    "emotion": turn.emotion,
                },
                tokens={
                    "prompt": llm_response.prompt_tokens,
                    "completion": llm_response.completion_tokens,
                    "total": llm_response.total_tokens,
                } if llm_response.total_tokens is not None else None,
                always_to_file=False,
            )

            self.turn_number += 1
            record = step_turn(agent, self.world, turn, self.turn_number)

            print(f"\n--- Turn {self.turn_number} result ---")
            print(f"Action: {record.action}")
            print(f"Result: {record.result}")
            print()

            # Make this agent the active one for subsequent vision/state commands
            self.agent = agent

        except Exception as e:
            log_error(f"LLM call failed for {agent.name}", e)
            import traceback
            traceback.print_exc()


def main():
    """Entry point for the manual stepper (used by `uv run realm`)."""
    parser = argparse.ArgumentParser(description="Realm-Fabric V0 Manual Stepper")
    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable full logging of every turn to a timestamped file in logs/",
    )
    parser.add_argument(
        "--with-fewshots",
        action="store_true",
        help="Include the four few-shot examples in prompts (off by default for token efficiency; current models perform well without them)",
    )
    args = parser.parse_args()

    log_path = None
    if args.log:
        log_path = setup_file_logging()

    try:
        stepper = ManualStepper(include_examples=args.with_fewshots)
        stepper.cmdloop()
    finally:
        if log_path:
            close_file_logging()
            print(f"\nFull log written to: {log_path}")


if __name__ == "__main__":
    main()
