from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScenarioParseRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
        description="Natural-language financial what-if scenario",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class LLMScenarioExtraction(BaseModel):
    """Raw structured result expected from the LLM provider."""

    scenario: dict[str, Any]
    missing_fields: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    requires_clarification: bool = False

    model_config = ConfigDict(extra="forbid")


class ScenarioParseResponse(BaseModel):
    query: str
    scenario: dict[str, Any]
    missing_fields: list[str]
    clarification_questions: list[str]
    assumptions: list[str]
    requires_clarification: bool

    model_config = ConfigDict(extra="forbid")
