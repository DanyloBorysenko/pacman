import numpy as np
import enum
from random import random
from typing import List, Tuple
from ..state import GameState


GUM_PROBABILITY = 0.8
WALL_MASK = 15
PACGUM = 16
SUPER_PACGUM = 32


class GameBoardGenerator:
	def __init__(self, game_state: GameState):
		self.game_state = game_state
		if not isinstance(game_state.maze, np.ndarray):
			self.game_state.maze = np.array(game_state.maze)

	def _place_pacgums(self) -> None:
		random_matrix = np.random.rand(self.game_state.maze.shape)
		is_corridors = self.maze < WALL_MASK
		gum_mask = is_corridors & (random_matrix < 0.8)
		self.maze[gum_mask] |= PACGUM
	
	def _place_super_pacgums(self) -> None:
		corners = [
			(0, 0),
			(0, self.game_state.maze.shape[1] - 1),
			(self.game_state.maze.shape[0] - 1, 0),
			(self.game_state.maze.shape[0] - 1, self.game_state.maze.shape[1] - 1),
			]
		
		for y, x in corners:
			self.game_state.maze[y, x] &= ~PACGUM
			self.game_state.maze[y, x] |= SUPER_PACGUM

