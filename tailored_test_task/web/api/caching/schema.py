from pydantic import BaseModel


class Payload(BaseModel):
    """Payload schema."""

    list_1: list[str]
    list_2: list[str]


class PayloadOutput(BaseModel):
    """Payload output schema."""

    id: int
    output: str
