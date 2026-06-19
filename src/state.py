from dataclasses import dataclass
from typing import List
from enum import Enum


class Direction(Enum):
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"
    UP = "up"


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
