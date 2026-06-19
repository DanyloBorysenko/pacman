from dataclasses import dataclass
from typing import List


@dataclass
class Position:
    row: int
    col: int


@dataclass
class GameState:
    maze: List[List[int]]
    pacman: Position
