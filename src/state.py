from dataclasses import dataclass
from typing import List


@dataclass
class GameState:
    maze: List[List[int]]
