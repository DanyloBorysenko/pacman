from dataclasses import dataclass
from typing import List
from enum import Enum


class Direction(Enum):
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"
    UP = "up"


class CheatModes(Enum):
    pass


@dataclass
class Pacman:
    # coord for the pacman center
    x: float
    y: float
    direction: Direction | None


@dataclass
class Ghost:
    # coordinate for ghost
    x: float
    y: float
    state: None # chasing or fleeing
    colour: None # colour of the ghost when chasing
    

@dataclass
class GameStats:
    scores: int
    level: int
    lives: int
    time_left: int
    cheat_mode: int


@dataclass
class GameStatus:
    status: int # Running (1) or Pause(0)  


@dataclass
class GameConfig:
    pass


@dataclass
class GameState:
    maze: List[List[int]]
    pacman: Pacman
    # ghost: List[Ghost]
    # live_status: GamePlayInfo
