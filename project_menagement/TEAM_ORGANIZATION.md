## Structure

Two partners, split along the same backend/frontend boundary the codebase itself is organized around:

- **Danylo Borysenko** — Frontend Engine Core: pygame view/scenes, the input `Controller`, the `Renderer` (maze/sprite/UI drawing), and the animation system (`AnimationManager`, death/victory/level-up animations). Representative commits: *"simple controller and renderer were implemented"* (Jun 19), *"scenes abstraction was created; controller now can switch scenes"* (Jun 23), *"AnimationManager and Animation classes were created"* (Jun 29), *"ghost's blinking was added; final scene shows scores now"* (Jul 8).
- **Sukanta Das** — Backend Simulation Layer: `GameState`/game rules, grid movement and collisions, ghost AI tuning, config parsing, the score board, cheat modes, audio wiring, and the web (WASM) build. Representative commits: *"add ghost movement and pacman tracking"* (Jun 25), *"add config file parsing, managing score board and 2 cheat mode"* (Jul 1), *"alphanumeric checks were added to score_board_handler"* (Jul 13), *"created web version, the version is in on the build"* (Jul 14).

In practice the split was not absolute — both partners touched shared files (`src/state.py`, `main.py`) and each occasionally patched the other's area (e.g. Sukanta fixed the ghost oscillation bug inside the movement/AI code on Jun 26); the roles above describe primary ownership, not a hard wall.

## Decision Making

Daily syncs before coding. Technical impasses were resolved by prototyping options locally and proceeding with the approach that required the fewest changes to existing modules. The decision to keep a strict `src/backend` / `src/frontend` package split (formalized during the "make sub modules" refactor on 2026-07-10) was itself one of these decisions — it let both partners keep working in parallel with fewer file-level conflicts.

## How Issues Were Handled

Bugs were generally fixed by whichever partner owned the affected area, with the other partner looped in when the bug crossed the backend/frontend boundary (e.g. the ghost oscillation/edible-color bug, which touched both the movement logic and how the renderer displayed ghost state). Integration issues — merge conflicts between the two long-running work streams — were resolved through dedicated merge sessions rather than small incremental merges; see [BLOCKING_POINTS.md](BLOCKING_POINTS.md) for a concrete log of these with dates and evidence.

## Blocking Points

The main recurring blocking point was discussing and fixing the ghost oscillation loop and the edible-color bug, solved by auditing the ghosts' tracking/state attributes together. A full list of blocking points and conflicts, with the commits that evidence them, is kept separately in [BLOCKING_POINTS.md](BLOCKING_POINTS.md).
