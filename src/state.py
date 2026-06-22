from dataclasses import dataclass
from typing import List
from enum import Enum


class Direction(Enum):
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"
    UP = "up"


class GameConfig(Enum):
	high_score_filename = None
	lives = 3
	pacgum = 42
	points_per_pacgum : 10
	points_per_super_pacgum : 50
	points_per_ghost : 200
	seed : 42
	level_max_time : 90


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
    current_score: int
    current_level: int
    lives_remain: int
    time_left: int
    cheat_mode: int


@dataclass
class GameStatus:
	status: int # Running (1) or Pause(0)  


@dataclass
class GameState:
    maze: List[List[int]]
    pacman: Pacman
    ghosts: List[Ghost]
    live_status: GameState
    config: GameConfig

