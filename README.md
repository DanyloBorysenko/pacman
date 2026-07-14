*This project has been created as part of the 42 curriculum by danborys, sudas.*

# Pac-Man

## Description

This project is a full reimplementation of the classic **Pac-Man** arcade game, built in Python with [pygame-ce](https://pyga.me/) as part of the 42 curriculum "Rank04" track. The goal of the project is to build a complete, playable game from scratch: procedurally generated mazes, ghost AI, scoring, lives, levels, animations, sound, and a persistent highscore board — all wrapped in a small game engine with a clean separation between game rules (backend) and rendering (frontend).

The player controls Pac-Man through a maze, eating pac-gums for points while avoiding four ghosts. Eating a super pac-gum temporarily lets Pac-Man eat the ghosts instead for bonus points. Clearing a maze of all pac-gums advances to the next (harder, faster) level; losing all lives ends the game. Scores can be saved to a persistent, sorted highscore leaderboard.

The game also ships as a browser-playable WebAssembly build (via [pygbag](https://github.com/pygame-web/pygbag)) in [build/web/](build/web/), in addition to running natively as a desktop application.

## Instructions

### Requirements

- Python **>= 3.13**
- [uv](https://docs.astral.sh/uv/) (dependency/venv manager used by this project)

All other dependencies (`pygame-ce`, `pygame-textinput`, `numpy`, the vendored `mazegenerator` package, plus `flake8`/`mypy` for linting) are declared in [pyproject.toml](pyproject.toml) and pinned in [uv.lock](uv.lock); `uv` installs them automatically into a local `.venv/`.

### Build & run

```bash
# install dependencies into a local .venv (uv sync)
make install

# run the game with the default configuration
make run
```

`make run` is equivalent to `uv run python3 main.py config.json` — the game always takes a configuration file as its single argument.

Other Makefile targets:

| Target       | Description                                                              |
|--------------|---------------------------------------------------------------------------|
| `make install` | Syncs the virtual environment from `uv.lock` / `pyproject.toml`.        |
| `make run`     | Launches the game with `config.json`.                                   |
| `make debug`   | Launches the game under `pdb` for debugging.                            |
| `make lint`    | Runs `flake8` and strict `mypy` over `src/`.                            |
| `make clean`   | Removes `__pycache__`, `.mypy_cache`, `.pytest_cache` directories.       |
| `make fclean`  | `clean` + removes the `.venv`.                                          |
| `make re`      | `fclean` followed by `install`.                                         |

### Controls

| Key                | Action                     |
|--------------------|----------------------------|
| Arrow keys / WASD   | Move Pac-Man               |
| Space               | Pause / resume             |
| Escape              | Back to previous menu      |
| Enter               | Confirm menu selection     |

The in-game **Instructions** screen (accessible from the main menu) always displays the live scoring/timing values read from the active `config.json`.

### Web / browser version

A pre-built WebAssembly export lives in [build/web/](build/web/) (`index.html`, `pacman.tar.gz` / `pacman.apk`), generated with `pygbag`. It can be served with any static file server — the whole game (rules + rendering) runs client-side inside a WASM Python 3.12 runtime in the browser, there is no backend server involved. Regenerating it requires running `pygbag` against `main.py` (not itself wired into the Makefile).

## Configuration

The game is configured through a single JSON file passed as the command-line argument (`config.json` by default). Despite the `.json` extension, the parser tolerates comment lines starting with `#` or `//`, which are stripped before parsing.

Default shipped [config.json](config.json):

```json
{
    "high_score_filename": "scoreboard.json",
    "maze_width": 16,
    "maze_height": 12,
    "points_per_pacgum": 10,
    "lives": 3,
    "pacgum": 50,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "ghost_edible_time": 5.0,
    "ghost_reappear_time": 5.0,
    "seed": 42,
    "level_max_time": 90.0,
    "max_level": 10,
    "pacman_speed": 4.0,
    "ghost_speed": 3.5
}
```

| Key                        | Meaning                                                                 |
|-----------------------------|--------------------------------------------------------------------------|
| `high_score_filename`       | Path of the JSON file used to persist the leaderboard.                  |
| `maze_width` / `maze_height`| Dimensions (in cells) of the generated maze.                            |
| `lives`                     | Starting number of lives.                                               |
| `pacgum`                    | Number of regular pac-gums placed per level.                            |
| `points_per_pacgum`         | Points awarded for eating a regular pac-gum.                            |
| `points_per_super_pacgum`   | Points awarded for eating a super pac-gum.                              |
| `points_per_ghost`          | Points awarded for eating a frightened ghost.                           |
| `ghost_edible_time`         | Seconds ghosts stay frightened/edible after a super pac-gum.            |
| `ghost_reappear_time`       | Seconds a ghost stays dead before respawning.                           |
| `seed`                      | Seed used for the very first maze generation.                           |
| `level_max_time`            | Seconds allowed to clear a level before a life is lost.                 |
| `max_level`                 | Number of levels to clear to win the game.                              |
| `pacman_speed` / `ghost_speed` | Base movement speed (cells/second) for Pac-Man and ghosts.           |

**Validation behavior** (implemented in [src/backend/parse_config_files.py](src/backend/parse_config_files.py)):
- If the file is missing, empty, or not valid JSON, a warning is printed and built-in defaults are used instead.
- Unknown keys are ignored with a `[Config Warning]`.
- Known keys are type-checked against the expected type (`int`/`float` are coerced where sensible); a type mismatch prints a `[Config Type Warning]` and falls back to the default for that key.
- The resulting dictionary is unpacked directly into the `GameConfig` dataclass ([src/state.py](src/state.py)) used throughout the game.

## Highscore

Scores are persisted as a flat JSON array in the file named by `high_score_filename` (default: [scoreboard.json](scoreboard.json)), where each entry is `{"name": str, "score": int}`.

We chose a plain sorted JSON file over a database because the leaderboard is small, local, and single-player: no concurrent writers, no queries beyond "give me the top N," and no need for a schema migration story. It also keeps the save file human-readable and trivially portable between the native and web builds.

Handled by [`ScoreBoardHandler`](src/backend/score_board_handler.py):
- **Loading**: reads the JSON file on startup; if the file is missing or corrupted, it starts from an empty list rather than crashing.
- **Reading**: `get_player_list(top_ten=True)` returns only the top 10 entries (shown on the main menu); `top_ten=False` returns the full list (shown on the dedicated, paginated Highscores screen).
- **Adding a score**: at the end of a game, the player is offered to save their score under a name. `add_new_player(name, score)` validates the name — **maximum 10 characters**, and (after stripping spaces) must be alphanumeric only — rejecting anything else with an on-screen error message. Valid entries are appended, the whole list is re-sorted by score (descending), and immediately written back to disk.

## Maze Generation

Mazes are produced by the 42 school-provided **A-Maze-ing** package (`mazegenerator`), vendored in this repository both as a wheel ([mazegenerator-2.0.1-py3-none-any.whl](mazegenerator-2.0.1-py3-none-any.whl)) and as unpacked source ([mazegenerator/mazegenerator.py](mazegenerator/mazegenerator.py)), and pulled in as a local path dependency in [pyproject.toml](pyproject.toml).

`MazeGenerator(size=(width, height), seed=...)` builds a perfect maze using a recursive-backtracker algorithm and exposes each cell as an integer bitmask of open walls (`NORTH=1, EAST=2, SOUTH=4, WEST=8`). The game reuses this same bitmask for gameplay content by OR-ing in extra bits on top of the wall bits (`PACGUM=16`, `SUPER_PACGUM=32`, `CHERRY=64`, see [`BitMaps`](src/state.py)), so a single integer per cell encodes both the walls and what's inside it.

Integration in the game:
- At startup, `main.py` builds one `MazeGenerator(size=(config.maze_width, config.maze_height), seed=42)` and hands it to `GameLogic`.
- [`GameInitializer`](src/backend/game_initializer.py) then populates the raw maze with content: it finds a valid open center cell for Pac-Man's spawn, forces the four maze corners to hold super pac-gums and ghost homes, and randomly scatters the remaining regular pac-gums across the rest of the open cells.
- On every level-up, `GameInitializer.reload_new_level_map` generates a **brand-new, freshly-seeded `MazeGenerator`** and re-runs the same placement pipeline, so each level presents a different layout while still respecting the configured dimensions.

## Implementation

- **Language / runtime**: Python 3.13, using `pygame-ce` for rendering, input, and audio, and `numpy` for the maze's underlying grid storage.
- **Game loop**: driven by [`Controller.run_single_scene`](src/frontend/controller.py), called every frame either directly (native desktop, `pac-man.py`) or from an `asyncio` loop that yields control each iteration (`main.py`), which is required so the WASM/browser build doesn't block the browser's own event loop. Frame timing is capped at 60 FPS via `pygame.time.Clock`.
- **Scene state machine**: the UI is organized as a stack of [`Scene`](src/frontend/scene.py) objects (`MainMenuScene`, `GameScene`, `PauseScene`, `InstructionsScene`, `HighScoresScene`, `FinalScene`), each implementing `handle_event` / `update` / `render`, and requesting transitions via `switch_to(...)`.
- **Backend/frontend decoupling**: gameplay rules live entirely under [src/backend/](src/backend/) and know nothing about pygame; the frontend under [src/frontend/](src/frontend/) only reads `GameState` and draws it. The two communicate through a `GameState.events` queue: backend actions append typed `GameEvent`s (e.g. `GumEatenEvent`, `GhostEatenEvent`, `LevelUpEvent`, `GameOverEvent`), and `GameScene` drains that queue each frame to trigger the matching sound effect and/or animation.
- **Movement**: both Pac-Man and ghosts move continuously between grid cells using `GridMover.advance_towards_target`, a fractional, delta-time-based interpolation that snaps to the destination tile when a frame's step would overshoot it, so movement speed is frame-rate independent and never clips through walls.
- **Ghost AI**: implemented with the Strategy pattern ([`GhostMovementStrategy`](src/backend/ghost_movement_logic.py)). All four ghosts use `PseudoRandomMovement`, which at every junction rolls a per-ghost `chase_probability` to decide between chasing Pac-Man directly (`DirectionalMovement`, minimizing Manhattan distance — or maximizing it to flee when frightened) and moving randomly (`RandomMovement`). Different probabilities per ghost (0.95 / 0.3 / 0.5 / 0.9) give each of the four ghosts a distinct "personality," from aggressive chaser to mostly-random wanderer.
- **Animations**: a small `Animation` ABC and `AnimationManager` (in [src/frontend/scenes/game_scene.py](src/frontend/scenes/game_scene.py)) drive blocking (death, game-over, victory, level-up, countdown) and non-blocking (ghost-eaten score popup) sequences; blocking animations pause the backend simulation update until they finish.
- **Cheats** (for testing/demo purposes, toggled from within a game): invincibility, skip level, extra life, and freeze ghosts — see `GameLogic.activate_cheat_mode`.

## General Software Architecture

The codebase follows a **Model/Backend – View/Frontend split** with an event queue connecting the two:

```
main.py / pac-man.py            (entry points: load config, build MazeGenerator,
                                  GameLogic, Controller, run the async/sync loop)
        │
        ▼
src/backend/                    "Model + rules" — no rendering, no pygame dependency
├── logic.py            → GameLogic            top-level facade: owns MazeGenerator,
│                                               GameConfig, ScoreBoardHandler; builds
│                                               ghosts; exposes update()/update_direction()/
│                                               activate_cheat_mode()
├── game_initializer.py → GameInitializer       populates a maze with pac-gums, super
│                                               pac-gums, ghost homes, Pac-Man spawn
├── game_state_manager.py → GameStateManager    per-frame orchestrator: timers, Pac-Man
│                                               movement, ghost movement, collisions
├── game_actions.py     → GameAction subclasses ConsumeItemsAction, CheckLevelClearAction,
│                                               PlayerDeathAction, GhostEatenAction
├── game_physics.py     → GridMover,             continuous grid movement /
│                         PacmanMovementController, wall-collision resolution
│                         GhostMovementController
├── ghost_life_cycle.py → GhostLifecycleManager  edible/respawn countdown timers
├── ghost_movement_logic.py → GhostMovementStrategy and subclasses (Random,
│                                               Directional, PseudoRandom) — ghost AI
├── parse_config_files.py → parse_game_config()  config.json loading/validation
└── score_board_handler.py → ScoreBoardHandler   highscore persistence & validation
        │
        │   src/state.py — shared data model: GameConfig, Pacman, Ghost, GameState,
        │   GameStats, BitMaps, Direction, GameEvent hierarchy (GumEatenEvent,
        │   GhostEatenEvent, LevelUpEvent, PacmanDiedEvent, GameOverEvent,
        │   VictoryEvent, GameStartEvent, CherryAppearedEvent, CherryEatenEvent)
        │
        ▼  (GameState.events queue, drained once per frame)
src/frontend/                   "View + input Controller" — pygame only, no game rules
├── controller.py  → Controller     owns the pygame window/clock, translates raw
│                                   pygame events into InputEvents, drives the active
│                                   Scene, plays background music
├── event.py       → InputEvent     engine-agnostic input event dataclass
├── scene.py       → Scene (ABC)    handle_event / update / render + switch_to(...)
├── renderer.py    → Renderer       all pygame drawing (maze, sprites, menus, text,
│                                   animations) — no game-rule logic
└── scenes/
    ├── main_menu_scene.py   → MainMenuScene      menu + top-10 mini leaderboard
    ├── game_scene.py        → GameScene,          live gameplay, sound effects,
    │                          Animation subclasses, AnimationManager
    ├── pause_scene.py       → PauseScene          continue / main menu
    ├── instructions_scene.py→ InstructionsScene   rules & controls (from GameConfig)
    ├── highscores_scene.py  → HighScoresScene     full paginated leaderboard
    └── final_scene.py       → FinalScene          victory/defeat + name entry
```

Key relationships:
- `GameLogic` (backend) is constructed once and injected into `Controller`/`GameScene` (frontend); the frontend never mutates game rules directly, only calls `GameLogic.update(...)` / `update_direction(...)` and reads the resulting `GameState`.
- `GameStateManager` composes the physics controllers, lifecycle manager, and actions to advance the simulation by one `dt`; it is the single place per-frame game rules are applied.
- Ghost behavior is pluggable via the `GhostMovementStrategy` interface, letting each ghost carry an independent strategy instance without the collision/lifecycle code needing to know which one.
- `GameScene` is the bridge between the two layers: it calls into the backend each frame, then reacts to whatever `GameEvent`s came out of that call to decide what to render/play next.

## Resources

- [Pygame Community Edition (pygame-ce) documentation](https://pyga.me/docs/) — rendering, event, audio, and sprite APIs used throughout `src/frontend/`.
- [pygbag documentation](https://pygame-web.github.io/) — packaging a pygame application to WebAssembly for the browser build in `build/web/`.
- [uv documentation](https://docs.astral.sh/uv/) — dependency/venv management used by the Makefile.
- Wikipedia — [Pac-Man](https://en.wikipedia.org/wiki/Pac-Man) and [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm) (recursive backtracker, the algorithm underlying the provided `mazegenerator` package) — background on original game rules and maze-generation theory.
- The [Strategy design pattern](https://refactoring.guru/design-patterns/strategy) — reference for the ghost AI implementation (`GhostMovementStrategy` and its subclasses).

**AI usage**: AI assistance (Claude) was used during development to help debug the ghost movement/oscillation logic, review code for lint/type-checking issues (`flake8`/`mypy` compliance), and, at the end of the project, to explore the finished codebase and draft this README from the existing source, configuration, and project-management documentation.
