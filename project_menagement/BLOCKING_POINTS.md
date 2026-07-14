## Summary of Blocking Points & Conflicts

A chronological log of the project's significant blocking points and merge conflicts, each grounded in the git history.

1. **2026-06-24 — First backend/frontend merge conflict.** Early parallel work on the menu scene and on the game initializer collided (`initial`, `conflict fixed` commits on the same day). Resolved by manually reconciling the two branches; this prompted the habit of stashing local work before pulling (*"Save my current work before pulling"*, Jun 25).

2. **2026-06-25 — Game initializer vs. in-progress frontend work.** `add game initializer and test` conflicted with concurrent frontend changes; resolved and recorded as *"merged with test and conflict resolved"*.

3. **2026-06-26 — Ghost movement oscillation / edible-color bug.** Ghosts could flip-flop direction at wall junctions, and the edible (frightened) color state didn't track correctly. This blocked further ghost-AI work for about four days (see [TIMELINE.md](TIMELINE.md)) and was resolved by blocking immediate 180° direction reversal and auditing the ghosts' timer/state attributes (*"fixed ghost movement with opposit move blocking and fix the edible mode and chasing mode"*). Documented as a design mitigation in [RISK_ANALYSIS.md](RISK_ANALYSIS.md).

4. **2026-07-04 — Large frontend/backend integration merge.** The animation-heavy frontend branch and the config/scoreboard/cheat-heavy backend branch had diverged for several days and were merged in one session, visible as a cluster of same-day commits (`before merging`, `Replace contents with origin/test_2`, `delete the content in the branch`, `merge the backend`, `merged conflicts were solved`, `Remove the old merged file`, `error fixed, game runnignwith bugs`). This was the single largest integration effort of the project and briefly left the game in a broken state before being stabilized the same day.

5. **2026-07-10 — Package restructuring ("make sub modules").** Splitting the code into the current `src/backend` / `src/frontend` layout temporarily broke imports across both areas (*"make sub modules, bug fixing needed"*), fixed the same day (*"refactor: done refactoring and every thing is working as before"*). This restructuring is what let the two partners work with materially fewer file-level conflicts for the remainder of the project.

6. **2026-07-12 — Second large integration merge.** A backend refactor branch (`beckend_v0.2_refactor`) was merged into the frontend's sound-integration work (*"latest frontend and the backend is merged and conflict resolved"*, *"merge beckend_v0.2_refactor"*), following the same pattern as #4 but resolved faster thanks to the clearer module boundaries established on Jul 10.

7. **2026-07-14 — Late config file rename.** `config.txt` was renamed to `config.json` on the last day of development (*"change config.txt to config.json"*). Because the rename happened so late, a few error-message strings in `main.py` / `pac-man.py` still refer to `config.txt` — a known, low-priority inconsistency left over from this last-minute change rather than a blocking issue.

**Takeaway:** the recurring theme was that long-lived, independent backend/frontend branches produced large, risky merges (#1, #2, #4, #6). The Jul 10 module split (#5) was a direct response to this and measurably reduced conflict size afterward.
