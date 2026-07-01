## Risk Matrix

1. **Risk:** Floating-point precision causing characters to clip through bitmask walls.
   * **Mitigation:** Implemented target-snapping integer tile junctions. Characters only alter direction arrays when exactly matching a cell coordinate.
2. **Risk:** Merge conflicts when combining backend logic with frontend UI rendering.
   * **Mitigation:** Strict separation of files. Peer working on frontend never directly mutates fields inside `GameStateManager`; they only read `GameState` data wrappers.