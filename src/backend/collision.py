import math

def check_entity_collisions(self) -> None:
    """Iterates through all active ghosts to verify if they collide with Pac-Man."""
    pacman = self.game_state.pacman
    
    for ghost in self.game_state.ghosts:
        # 1. Calculate straight-line distance
        distance = math.sqrt((pacman.x - ghost.x)**2 + (pacman.y - ghost.y)**2)
        
        # 2. Check if they overlap (closer than half a tile distance)
        if distance < 0.5:
            # Handle cheat mode: if invincibility is active, skip punishing the player
            if getattr(self.game_state, "cheat_invincibility", False):
                continue
                
            if ghost.is_edible:
                # Scenario A: Pac-Man eats the ghost
                self.game_state.score += self.game_state.config.points_per_ghost
                
                # Reset the ghost back to its home corner location
                ghost.reset_to_home_corner()
                ghost.is_edible = False
                # Add a cooldown timer for respawning if required by your layout rules
            else:
                # Scenario B: Ghost kills Pac-Man
                self._handle_player_death()
                return  # Stop checking other ghosts for this frame