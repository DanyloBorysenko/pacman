## Risk Matrix

1. **Risk:** Floating-point precision causing characters to clip through bitmask walls.
   * **Mitigation:** Implemented target-snapping integer tile junctions. Characters only alter direction arrays when exactly matching a cell coordinate. See "Time Delta (dt) & Target Snapping" in [ARCHITECTURAL_CHOICES.md](ARCHITECTURAL_CHOICES.md).

2. **Risk:** Merge conflicts when combining backend logic with frontend UI rendering.
   * **Mitigation:** Strict separation of files. The peer working on frontend never directly mutates fields inside `GameStateManager`; they only read `GameState` data wrappers. Materialized as an explicit `src/backend` / `src/frontend` package split on 2026-07-10. Despite this, two large integration merges still occurred (2026-07-04, 2026-07-12) — see [BLOCKING_POINTS.md](BLOCKING_POINTS.md).

3. **Risk:** Ghost AI oscillating (rapidly flip-flopping direction) at wall junctions, and incorrect edible/chasing state tracking, making ghosts behave unpredictably or look visually wrong (wrong color while frightened).
   * **Mitigation:** Banned immediate 180° direction reversal except at dead ends, and audited/fixed the ghosts' timer and state attributes driving the edible/chasing transitions (fixed 2026-06-26). This was the project's single largest schedule risk, costing ~4 days (see [TIMELINE.md](TIMELINE.md)).

4. **Risk:** Malformed, missing, or partially-invalid `config.json` (wrong types, unknown keys, missing file) crashing the game at startup.
   * **Mitigation:** `parse_game_config` validates every key individually against typed defaults and falls back to safe defaults with a printed warning instead of raising, rather than trusting a raw `json.load(...)` result. Directly motivated by a real config-parsing bug found and fixed on 2026-07-06.

5. **Risk:** Arbitrary or malicious player names being written to the persistent highscore file (e.g. overly long names, punctuation/control characters corrupting the display or the JSON file).
   * **Mitigation:** `ScoreBoardHandler.add_new_player` enforces a 10-character maximum and an alphanumeric-only check (spaces allowed) before persisting, with an on-screen error message on rejection (added 2026-07-13).

6. **Risk:** Lint/type errors and dead/duplicate code (e.g. `ghost_movement.py` vs. `ghost_movement_logic.py`) accumulating unnoticed across two parallel work streams.
   * **Mitigation:** `flake8` and strict `mypy` wired into a dedicated `make lint` target, run repeatedly throughout the project rather than only at the end, though not enforced automatically (no CI is configured — see the main [README.md](../README.md)).
