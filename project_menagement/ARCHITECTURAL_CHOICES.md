Decoupled Architecture: "We separated the game loop logic (GameStateManager) entirely from the display layer (Renderer) so that backend simulations remain independent of graphics rendering."

Strategy Pattern: "Ghost movements utilize an abstract base class (GhostMovementStrategy) allowing polymorphic behavior swaps (Random, Directional, Frightened) seamlessly at runtime."

Time Delta (dt): "We chose float coordinates tracking along with target snapping (step_size >= distance_to_target) to ensure accurate speed pacing across any user hardware frame rate limits."