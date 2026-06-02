from dataclasses import dataclass
from typing import Optional

from src.agent import Agent
from src.memory import Memory
from src.object import Object


class World:
    """
    Represents the entire simulation world for Version 0.

    The World holds all the state:
    - The single agent
    - All objects in the environment
    - Grid rules and boundaries

    In V0 the world is very small and simple:
    - 5x5 grid (coordinates 0-4 in both x and y)
    - (0, 0) is the southwest corner. Y increases northward.
    - Only one agent.
    - Only two objects (a ceramic ball and a wooden sign).
    - No blocking objects. The agent can occupy the same tile as the ball.
    - Room boundaries are not represented as objects. They are described
      to the agent via a static room description string in the prompt.

    This class is currently a regular class (not a dataclass) because it
    will likely grow methods for querying and updating state.
    """

    # Grid constants (as defined in the V0 readiness checklist)
    WIDTH: int = 5
    HEIGHT: int = 5
    MIN_COORD: int = 0
    MAX_COORD: int = 4

    def __init__(self):
        self.agents: list[Agent] = []
        self.objects: list[Object] = []

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the world."""
        self.agents.append(agent)

    def add_object(self, obj: Object) -> None:
        """Add an object to the world."""
        self.objects.append(obj)

    def get_agent(self) -> Optional[Agent]:
        """
        Return the single agent in the world.

        In V0 there is only ever one agent. Returns None if no agent exists.
        """
        if not self.agents:
            return None
        return self.agents[0]

    def get_object_at(self, position: tuple[int, int]) -> Optional[Object]:
        """Return the object at a given position, if any."""
        for obj in self.objects:
            if obj.position == position:
                return obj
        return None

    def get_object_by_id(self, object_id: str) -> Optional[Object]:
        """Return the object with the given ID, if it exists in the world."""
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None

    def get_objects(self) -> list[Object]:
        """Return all objects currently in the world."""
        return self.objects

    def is_valid_position(self, position: tuple[int, int]) -> bool:
        """Check whether a position is inside the playable grid."""
        x, y = position
        return (
            self.MIN_COORD <= x <= self.MAX_COORD
            and self.MIN_COORD <= y <= self.MAX_COORD
        )

    def get_room_description(self) -> str:
        """
        Return the static room description shown to the agent every turn.

        In V0, walls and room boundaries are conveyed through this text
        rather than being modeled as objects.
        """
        return (
            "You are in a small room with a hardwood floor and four wooden walls."
        )


# =============================================================================
# Initial World State (as defined in the V0 readiness checklist)
# =============================================================================

def create_initial_world() -> World:
    """
    Create and return the starting world state for Version 0.

    This function centralizes the initial configuration so it is easy to
    inspect and modify during development and experimentation.

    Starting state:
    - Agent at (1, 1)
    - Ceramic Ball at (2, 2)
    - Wooden Sign at (2, 4)
    """
    world = World()

    # Create the agent
    agent = Agent(
        id="agent_01",
        name="Explorer",
        description=(
            "You are a curious explorer placed in a small, controlled room. "
            "Your goal is to understand your environment through careful "
            "observation and deliberate action."
        ),
        position=(1, 1),
        memory=Memory(),
        last_action=None,
    )
    world.add_agent(agent)

    # Create the ceramic ball
    ball = Object(
        id="obj_ball_01",
        name="Ceramic Ball",
        description="A slightly worn ceramic ball. It has a few scuffs and feels light.",
        position=(2, 2),
    )
    world.add_object(ball)

    # Create the wooden sign
    sign = Object(
        id="obj_sign_01",
        name="Wooden Sign",
        description=(
            'A simple wooden sign. It reads: "This is a controlled environment. '
            'You are the only one here. This sign may occasionally be updated '
            'with new information. When it changes, you will be notified."'
        ),
        position=(2, 4),
    )
    world.add_object(sign)

    # Pre-mark the sign as "looked at" in initial state so it shows its
    # description in passive vision (ball starts as [?]). This matches
    # several examples in the readiness checklist. When the sign is later
    # updated via debug command, we will invalidate it.
    agent.memory.mark_looked_at(sign.id)

    return world
