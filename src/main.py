"""
main.py

Entry point for manual stepping in V0 (per readiness checklist).

Supports:
- step                  : advance one turn. For now you (the human) supply
                          the AgentTurn fields to simulate what the LLM would
                          have output. This lets us test the full loop
                          (action -> memory -> vision) without the LLM.
- sign "new text"       : debug command to update the wooden sign's description
                          and invalidate the agent's memory of it (triggers the
                          special "has changed" notification).
- quit / exit           : leave the simulation.
- vision / state        : print current passive vision or agent/world state.

Future: this will be replaced by real LLM-driven turns once we wire the
llm/ package.

Run with:
    uv run python -m src.main
    # or from project root (with PYTHONPATH):
    uv run python -c "
import sys
sys.path.insert(0, '.')
from src.main import ManualStepper
ManualStepper().cmdloop()
"
"""

import cmd
from src.world import create_initial_world
from src.simulation import step_turn
from src.llm.schemas import AgentTurn
from src.llm.prompt import build_prompt
from src.perception import build_passive_vision


class ManualStepper(cmd.Cmd):
    intro = (
        "Realm-Fabric V0 Manual Stepper\n"
        "Type 'help' or '?' for commands.\n"
        "Use 'step <action> [target] [content]' to simulate an agent turn.\n"
        "Use 'prompt' to see the exact text that would be sent to the LLM.\n"
        "Example: step look obj_ball_01\n"
        "Example: step move north\n"
        "Example: step speak Hello there.\n"
    )
    prompt = "(realm) "

    def __init__(self):
        super().__init__()
        self.world = create_initial_world()
        self.agent = self.world.get_agent()
        self.turn_number = 0

    def do_vision(self, arg):
        """Show current passive vision."""
        print(build_passive_vision(self.agent, self.world))

    def do_prompt(self, arg):
        """Show the full prompt that would be sent to the LLM right now."""
        prompt = build_prompt(self.agent, self.world)
        print(f"[Full prompt - {len(prompt)} characters]\n")
        print(prompt)

    def do_state(self, arg):
        """Print basic agent and world state."""
        print(f"Turn: {self.turn_number}")
        print(f"Agent pos: {self.agent.position}")
        print(f"Memory turns: {self.agent.memory.turn_count}")
        print(f"Looked at: {sorted(self.agent.memory.looked_at)}")
        objs = [(o.name, o.position) for o in self.world.get_objects()]
        print(f"Objects: {objs}")

    def do_step(self, arg):
        """
        Simulate one agent turn.

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
            print(f"Invalid turn data: {e}")
            return

        self.turn_number += 1

        # Build and show the prompt that would be sent to the model
        full_prompt = build_prompt(self.agent, self.world)
        print(f"\n[PROMPT that would be sent to LLM - {len(full_prompt)} chars]")
        print(full_prompt[:800] + "\n... [truncated for display] ...\n")

        record = step_turn(self.agent, self.world, turn, self.turn_number)

        print(f"--- Turn {self.turn_number} ---")
        print(f"Action: {record.action} target={record.target} content={record.content}")
        print(f"Reasoning: {record.reasoning}")
        print(f"Result: {record.result}")
        print()

    def do_sign(self, arg):
        """
        Debug command: update the wooden sign's description.

        Usage:
            sign This is the new text on the sign.
        """
        if not arg:
            print("Usage: sign <new description text>")
            return

        sign = self.world.get_object_by_id("obj_sign_01")
        if sign is None:
            print("Sign not found!")
            return

        old = sign.description
        sign.description = arg
        self.agent.memory.invalidate_look("obj_sign_01")

        print("Sign updated.")
        print(f"Old: {old[:60]}...")
        print(f"New: {arg[:60]}...")
        print("The agent's memory of the sign has been invalidated.")

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


if __name__ == "__main__":
    ManualStepper().cmdloop()
