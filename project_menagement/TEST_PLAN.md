## Feature Acceptance Tests

| Test Case ID | Feature Tested | Expected Behavior | Pass/Fail |
| :--- | :--- | :--- | :--- |
| TC-01 | Wall Collision | Pac-Man hits a wall bit and stops cleanly at tile center. | PASS |
| TC-02 | Super Pacgum | Ghosts turn blue, global timer counts down 5s, resets. | PASS |
| TC-03 | Ghost Eaten | Eaten ghost reverts color, score adds 200, teleports home. | PASS |
| TC-04 | Invincibility Cheat | Pressing 'I' toggles cheat; dangerous ghosts pass through. | PASS |
| TC-05 | Level Timer Runout | Timer hits 0.0, player loses 1 life, game resets. | PASS |
| TC-06 | Config Fallback | Launching with a missing/corrupt `config.json` prints a warning and falls back to built-in defaults instead of crashing. | PASS |
| TC-07 | Highscore Name Validation | Entering a name > 10 characters or containing punctuation shows the inline error and does not save; a valid alphanumeric name saves and appears sorted by score. | PASS |
| TC-08 | Level-Up Maze Regeneration | Clearing all pac-gums on a level generates a new maze layout, resets ghost positions, and increases both Pac-Man's and the ghosts' speed by 10%. | PASS |
| TC-09 | Cherry Bonus Life | Once roughly half a level's pac-gums are eaten, a cherry appears at the start tile; eating it grants +1 life. | PASS |
| TC-10 | Victory / Game Over Flow | Clearing `max_level` triggers the victory animation and `FinalScene`; losing all lives triggers the game-over animation and `FinalScene` instead of continuing gameplay (regression fixed 2026-07-06, previously the game incorrectly advanced to the next level after victory). | PASS |

Bugs found and fixed during testing (see [BLOCKING_POINTS.md](BLOCKING_POINTS.md) and [RISK_ANALYSIS.md](RISK_ANALYSIS.md) for full context):
- Ghost movement oscillation / incorrect edible color at wall junctions (fixed 2026-06-26).
- Invincibility cheat applying inconsistently (fixed 2026-07-01).
- Victory incorrectly auto-advancing to the next level (fixed 2026-07-06).
- Config file parsing rejecting otherwise-valid values (fixed 2026-07-06).
- Pac-Man/ghost speed not resetting on a new game after a previous run (fixed 2026-07-06).
