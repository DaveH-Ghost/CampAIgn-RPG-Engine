"""
LLM structured output schemas — V0.2.5 single-call compound turns.

One AgentCompoundTurn per agent turn: optional move, then optional look, then turn action.
V0.4.1a: reasoning and speak content are truncated at sentence boundaries.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional

from src.coordinates import CoordinateParseError, parse_coordinate_target
from src.llm.text_truncation import (
    REASONING_MAX_CHARS,
    SPEAK_MAX_CHARS,
    count_sentences,
    truncate_at_sentence_boundary,
)
from src.move_target import validate_move_target_syntax


TurnActionType = Literal["speak", "interact", "none"]

MAX_SPEAK_CHARACTERS = SPEAK_MAX_CHARS
MAX_REASONING_CHARACTERS = REASONING_MAX_CHARS


def count_speak_sentences(text: str) -> int:
    """Count sentences; ellipsis runs are not sentence boundaries."""
    return count_sentences(text)


def _truncate_reasoning(v: str) -> str:
    return truncate_at_sentence_boundary(v, REASONING_MAX_CHARS)


def _validate_short_optional(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v.strip().split()) > 3:
        raise ValueError(
            "ERR:INVALID_CONTENT: confidence and emotion should be short (1-3 words max)."
        )
    return v


def _truncate_speak_content(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    text = v.strip()
    if not text:
        return v
    return truncate_at_sentence_boundary(text, SPEAK_MAX_CHARS)


class AgentCompoundTurn(BaseModel):
    """Structured output for one compound agent turn (move → look → turn action)."""

    reasoning: str = Field(
        description=(
            "Private thoughts for the full turn (aim for ~400 characters; "
            "longer text is trimmed at sentence boundaries)."
        ),
    )
    move_target: Optional[str] = Field(
        default=None,
        description='Grid coordinate "x,y", entity id (obj_* / agent_*), or null to stay.',
    )
    look_target: Optional[str] = Field(
        default=None,
        description="Entity id to examine after moving, or null to skip look.",
    )
    turn_action: TurnActionType = Field(
        description='Turn-ending action: "speak", "interact", or "none".',
    )
    target: Optional[str] = Field(
        default=None,
        description="Object id when turn_action is interact.",
    )
    action_name: Optional[str] = Field(
        default=None,
        description='Named object action when turn_action is interact (e.g. "eat").',
    )
    content: Optional[str] = Field(
        default=None,
        description=(
            "Speak dialogue when turn_action is speak (aim for ~500 characters; "
            "longer text is trimmed at sentence boundaries)."
        ),
    )
    confidence: Optional[str] = Field(default=None, description="1-3 words.")
    emotion: Optional[str] = Field(default=None, description="1-3 words.")

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        return _truncate_reasoning(v)

    @field_validator("move_target")
    @classmethod
    def validate_move_target(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not str(v).strip():
            return None
        try:
            return validate_move_target_syntax(v)
        except CoordinateParseError as exc:
            raise ValueError(str(exc)) from exc

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        return _truncate_speak_content(v)

    @field_validator("confidence", "emotion")
    @classmethod
    def validate_short_fields(cls, v: Optional[str]) -> Optional[str]:
        return _validate_short_optional(v)

    @model_validator(mode="after")
    def validate_turn_action_fields(self) -> "AgentCompoundTurn":
        if self.turn_action == "speak":
            if not self.content or not str(self.content).strip():
                raise ValueError("ERR:INVALID_TARGET: speak requires content")
            if self.target or self.action_name:
                raise ValueError("ERR:INVALID_TARGET: target/action_name must be empty for speak")
        elif self.turn_action == "interact":
            if not self.target or not str(self.target).strip():
                raise ValueError("ERR:INVALID_TARGET: interact requires target object id")
            if not self.action_name or not str(self.action_name).strip():
                raise ValueError("ERR:INVALID_TARGET: interact requires action_name")
            if self.content:
                raise ValueError("ERR:INVALID_TARGET: content must be empty for interact")
        elif self.turn_action == "none":
            if self.content or self.target or self.action_name:
                raise ValueError(
                    "ERR:INVALID_TARGET: content, target, and action_name must be empty for none"
                )
        return self
