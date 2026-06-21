from dataclasses import dataclass
from typing import List
from enum import Enum


class Direction(Enum):
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    UP = (0, -1)


@dataclass
class Pacman:
    # coord for the pacman center
    x: float
    y: float
    direction: Direction | None


@dataclass
class GameState:
    maze: List[List[int]]
    pacman: Pacman
