from dataclasses import dataclass


@dataclass
class InputEvent:
    """Normalized input event passed from the Controller to the
    active Scene, decoupling scenes from raw pygame events."""

    type: str  # "keydown", "quit", etc.
    key: str | None  # "up", "down", "space", etc.
