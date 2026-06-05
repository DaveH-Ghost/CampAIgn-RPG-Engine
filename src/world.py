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

    def remove_object(self, object_id: str) -> bool:
        """Remove an object by ID. Returns True if removed, False if not found."""
        for i, obj in enumerate(self.objects):
            if obj.id == object_id:
                self.objects.pop(i)
                return True
        return False

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent by ID. Returns True if removed, False if not found."""
        for i, agent in enumerate(self.agents):
            if agent.id == agent_id:
                self.agents.pop(i)
                return True
        return False

    def get_agent(self) -> Optional[Agent]:
        """
        Return the first agent in the world.

        In V0 there is only ever one agent at startup. Returns None if no agent exists.
        """
        if not self.agents:
            return None
        return self.agents[0]

    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Return the agent with the given ID, if it exists in the world."""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None

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

    def invalidate_object_knowledge(self, object_id: str) -> None:
        """
        Remove up-to-date look knowledge for an object across all agents.

        Call this whenever an object's description changes (e.g. edit-object).
        Do not call agent.memory.invalidate_look directly.

        Agents who had looked at the object will see the generalized changed
        notification; agents who never looked still see plain [?].
        """
        for agent in self.agents:
            if agent.memory.has_looked_at(object_id):
                agent.memory.invalidate_look(object_id)

    def clear_object_examination_history(self, object_id: str) -> None:
        """
        Clear looked_at and ever_looked for an object across all agents.

        Used when detailed description is removed so agents are not stuck in
        a stale state they cannot clear via look.
        """
        for agent in self.agents:
            agent.memory.clear_examination(object_id)


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

    sign = Object(
        id="obj_sign_01",
        name="Wooden Sign",
        passive_description="A simple wooden sign on the wall.",
        description=(
            'It reads: "This is a controlled environment. '
            'You are the only one here. This sign may occasionally be updated '
            'with new information. When it changes, you will be notified."'
        ),
        position=(2, 4),
    )
    world.add_object(sign)

    return world
