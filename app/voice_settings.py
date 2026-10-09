import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VoiceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: Literal["qwen-1.7b", "qwen-0.6b", "qwen-0.6b-eco"] = "qwen-1.7b"
    speed: float = Field(default=1.0, ge=0.85, le=3.0)
    speed_method: Literal["rubberband", "atempo"] = "rubberband"
    stability: int = Field(default=50, ge=0, le=100)
    similarity: Literal["timbre", "reference"] = "reference"
    style: int = Field(default=0, ge=0, le=100)
    language_override: bool = False
    language: Literal["Auto", "Spanish", "English"] = "Spanish"
    audio_effects: bool = False


def settings_from_json(value: str | None) -> VoiceSettings:
    return VoiceSettings.model_validate(json.loads(value or "{}"))
