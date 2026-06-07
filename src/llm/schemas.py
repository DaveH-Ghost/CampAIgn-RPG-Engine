"""
LLM structured output schemas — V0.2 compound turns.

Navigation phase: AgentNavigationTurn
Action phase: AgentActionTurn
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional
import re

from src.coordinates import CoordinateParseError, parse_coordinate_target


TurnActionType = Literal["speak", "interact", "none"]

MAX_SPEAK_SENTENCES = 5
MAX_SPEAK_CHARACTERS = 500


def count_speak_sentences(text: str) -> int:
    """Count sentences; ellipsis runs are not sentence boundaries."""
    normalized = re.sub(r"\.{2,}", "\u2026", text.strip())
    parts = [s.strip() for s in re.split(r"[.!?]+\s*", normalized) if s.strip()]
    return len(parts)


def _validate_reasoning(v: str) -> str:
    text = v.strip()
    if len(text) > 400:
        raise ValueError(
            "ERR:REASONING_TOO_LONG: reasoning must be 400 characters or fewer "
            f"(current length: {len(text)})."
        )
    return v


def _validate_short_optional(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if len(v.strip().split()) > 3:
        raise ValueError(
            "ERR:INVALID_CONTENT: confidence and emotion should be short (1-3 words max)."
        )
    return v


def _validate_speak_content(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    text = v.strip()
    if not text:
        return v
    sentence_count = count_speak_sentences(text)
    if sentence_count > MAX_SPEAK_SENTENCES:
        raise ValueError(
            f"ERR:CONTENT_TOO_LONG: speak is limited to a maximum of {MAX_SPEAK_SENTENCES} sentences "
            f"(you used {sentence_count})."
        )
    if len(text) > MAX_SPEAK_CHARACTERS:
        raise ValueError(
            f"ERR:CONTENT_TOO_LONG: speak content is limited to {MAX_SPEAK_CHARACTERS} characters "
            f"(you used {len(text)})."
        )
    return v


class AgentNavigationTurn(BaseModel):
    """Structured output for the navigation phase of a compound agent turn."""

    reasoning: str = Field(
        description="Private thoughts for the navigation decision (max 400 characters)."
    )
    move_target: Optional[str] = Field(
        default=None,
        description='Grid coordinate as "x,y" (e.g. "2,3"), or null to stay in place.',
    )
    confidence: Optional[str] = Field(default=None, description="1-3 words.")
    emotion: Optional[str] = Field(default=None, description="1-3 words.")

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        return _validate_reasoning(v)

    @field_validator("move_target")
    @classmethod
    def validate_move_target(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not str(v).strip():
            return None
        try:
            parse_coordinate_target(v)
        except CoordinateParseError as exc:
            raise ValueError(str(exc)) from exc
        return v

    @field_validator("confidence", "emotion")
    @classmethod
    def validate_short_fields(cls, v: Optional[str]) -> Optional[str]:
        return _validate_short_optional(v)


class AgentActionTurn(BaseModel):
    """Structured output for the action phase of a compound agent turn."""

    reasoning: str = Field(
        description="Private thoughts for look/speak/interact decisions (max 400 characters)."
    )
    look_target: Optional[str] = Field(
        default=None,
        description="Entity id to examine, or null to skip look.",
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
        description="Speak dialogue when turn_action is speak.",
    )
    confidence: Optional[str] = Field(default=None, description="1-3 words.")
    emotion: Optional[str] = Field(default=None, description="1-3 words.")

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        return _validate_reasoning(v)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        return _validate_speak_content(v)

    @field_validator("confidence", "emotion")
    @classmethod
    def validate_short_fields(cls, v: Optional[str]) -> Optional[str]:
        return _validate_short_optional(v)

    @model_validator(mode="after")
    def validate_turn_action_fields(self) -> "AgentActionTurn":
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
