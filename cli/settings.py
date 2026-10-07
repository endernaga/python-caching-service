from pathlib import Path
from typing import Self

from pydantic import Field, HttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CLISettings(BaseSettings):
    """CLI options for exercising the caching service."""

    host: HttpUrl = Field(
        default=HttpUrl("http://localhost:8000"),
        description="URL of the caching service",
    )
    repeat: int = Field(
        default=1,
        description="Number of create/read iterations",
    )
    input: Path | None = Field(
        default=None,
        description='Input file path, or "-" for stdin',
    )
    # alias keeps the public flag as --json without shadowing BaseSettings.json
    json_payload: str | None = Field(
        default=None,
        alias="json",
        description="Inline JSON payload (properly escaped)",
    )
    output: Path | None = Field(
        default=None,
        description='Output file path, or "-" for stdout',
    )

    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_prog_name="cache-cli",
        cli_ignore_unknown_args=False,
        populate_by_name=True,
        # -h is reserved for --help by argparse; task doc lists -h for both.
        cli_shortcuts={
            "repeat": "r",
            "input": "i",
            "json_payload": "j",
            "output": "o",
        },
    )

    @field_validator("repeat")
    @classmethod
    def validate_repeat(cls, value: int) -> int:
        """Reject non-positive iteration counts."""
        if value < 1:
            raise ValueError("--repeat must be greater than 0")
        return value

    @model_validator(mode="after")
    def require_input_source(self) -> Self:
        """Exactly one of --json or --input must be provided."""
        if self.json_payload is None and self.input is None:
            raise ValueError("Either --json or --input must be provided")
        if self.json_payload is not None and self.input is not None:
            raise ValueError("Provide only one of --json or --input")
        return self
