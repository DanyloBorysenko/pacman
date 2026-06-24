from typing import Tuple
from ..state import GameState, Direction, BitMaps

PACMAN_SPEED = 40
GHOST_SPEED = 40


class GameStateManager:
	def __init__(self, game_state: GameState):
		self.game_state = game_state

	def request_move(self, direction: Tuple[int, int]) -> None:
		curr_x = int(self.game_state.pacman.x)
		curr_y = int(self.game_state.pacman.y)
		curr_tile = self.game_state.maze[curr_y, curr_x]
		self.game_state.pacman.direction = direction
		if not self._is_move_allowed(curr_tile, direction):
			return
		else:
			self.move(direction)
	
	def _is_move_allowed(self, curr_tile: int, direction: Tuple[int, int]) -> bool:
		if direction == Direction.RIGHT and (curr_tile & BitMaps.EAST):
			return False
		elif direction == Direction.LEFT and (curr_tile & BitMaps.WEST):
			return False
		elif direction == Direction.UP and (curr_tile & BitMaps.NORTH):
			return False
		elif direction == Direction.DOWN and (curr_tile & BitMaps.SOUTH):
			return False
		return True
	
	def move(self, direction: Tuple[int, int]) -> None:
		self.game_state.pacman.x += direction[0] + self.game_state.pacman.x
		self.game_state.pacman.y += direction[0] + self.game_state.pacman.y
		new_x = self.game_state.pacman.x
		new_y = self.game_state.pacman.y
		new_tile = self.game_state[new_y, new_x]

		if (new_tile & BitMaps.PACGUM):
			self.game_state.live_status.current_score += self.game_state.config.points_per_pacgum
			self.game_state.maze[new_y, new_x] &= ~BitMaps.PACGUM
		elif (new_tile & BitMaps.SUPER_PACGUM):
			self.game_state.live_status.current_score += self.game_state.config.points_per_super_pacgum
			self.game_state.maze[new_y, new_x] &= ~BitMaps.SUPER_PACGUM
			pass
	



