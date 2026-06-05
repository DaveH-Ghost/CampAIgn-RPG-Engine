from dataclasses import dataclass


@dataclass
class Object:
    """
    Represents a simple, single-tile object in the world.

    Objects occupy one grid tile and carry two optional description layers (V0.1):
    - passive_description: visible at a glance (no look required)
    - description: detailed text revealed by the `look` action

    Objects do not have behavior or interactions yet (out of scope for V0).
    """

    id: str
    """Stable unique identifier for the object (e.g. 'obj_ball_01', 'obj_sign_01')."""

    name: str
    """Short, human-readable name shown in passive vision (e.g. 'Ceramic Ball')."""

    description: str
    """
    Detailed description revealed when the agent uses `look`.

    When non-empty and not yet examined, passive vision shows [?] (optionally
    with passive_description). Empty detailed description means no [?] tag.
    """

    position: tuple[int, int]
    """The grid coordinates of the object as (x, y)."""

    passive_description: str = ""
    """
    Glance-level description visible without looking.

    Shown in passive vision even when the agent has not used `look`. When both
    passive and detailed descriptions exist, never-examined objects show
    "[?] {passive_description}"; stale knowledge shows "[?] [changed] {passive}".
    """
