from dataclasses import dataclass


@dataclass
class InputEvent:
    type: str  # "keydown", "quit", etc.
    key: str | None  # "up", "down", "space", etc.
