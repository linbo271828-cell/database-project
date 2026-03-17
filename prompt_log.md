# Prompt Log — Workout Tracker

**AI/tools used:** Claude (via Cursor IDE) for code generation, refactors, and schema changes. All outputs were run locally and edited by me where needed.

---

## 1. Initial project setup and database schema

**Prompt (approximate):**

> I need to build a workout tracker for a database assignment. Use SQLite and Python. Create a database module that defines one table for workout entries: exercise name, workout date, sets, top set weight, top set reps, optional bodyweight, unit (lb or kg), and muscle group. Add a CHECK so muscle_group is one of: chest, back, legs, shoulders, arms, core, full_body. Implement full CRUD (create, read, update, delete) in the DB module. Then build a simple CLI that lets me add an entry, view entries, update by ID, and delete by ID. Use a main menu (1–5) and keep the DB logic in a separate file from the CLI.

**What I got / what I did:**

- `workout_db.py`: `init_db()` creating `workout_entries` with the columns above, plus `is_pr` (integer 0/1). Functions: `create_entry`, `list_entries`, `get_entry_by_id`, `update_entry`, `delete_entry`. Constants: `MUSCLE_GROUPS`, `UNITS`, `COMMON_EXERCISES`.
- `workout_tracker.py`: Menu loop (1 Add, 2 View, 3 Update, 4 Delete, 5 Quit). Add flow: pick exercise (from a short preset list or custom name), then date, sets, top weight, top reps, bodyweight, unit, muscle group, PR. View just listed all entries; update/delete asked for ID then confirmed.
- I ran it, added a few rows, and fixed the column order in the printout so it matched the tuple indices from the SELECT.

---

## 2. View options and input validation

**Prompt (approximate):**

> When I choose "View entries" I want options: (1) show all by newest date first, (2) filter by exercise name (substring search), (3) sort by top weight heaviest first. Also add proper validation: sets and reps must be positive integers, weight and bodyweight non-negative, unit must be lb or kg, muscle group must be one of the allowed list, PR must be y/n. On update, if I leave a field blank keep the current value.

**What I got / what I did:**

- `list_entries(view_mode="all" | "filter" | "top_weight", search="")` with the right ORDER BY and WHERE. CLI view menu: "1. Show all (newest date first)", "2. Filter by exercise name", "3. Sort by top weight (heaviest first)".
- Helper functions in `workout_tracker.py`: `read_positive_int`, `read_non_negative_float`, `read_unit`, `read_muscle_group`, `read_yes_no_pr`, each with optional `allow_blank` for update. Update flow now shows current value in brackets and uses allow_blank so blank keeps existing value.
- I had to fix bodyweight on update (the prompt showed empty for null; I kept the existing logic and made the display consistent).

---

## 3. GUI using the same database

**Prompt (approximate):**

> Add a tkinter GUI for the same workout tracker. It should use the same workout_db module and the same workout_entries table. Include a form for adding/editing an entry (exercise, date, sets, top weight, top reps, bodyweight, unit, muscle group, PR). Have a table or list showing entries with the same columns. Let me filter or sort the list. When I type in the exercise field, show autocomplete suggestions from the common exercises list plus any exercise names already in the database—no API, just local data.

**What I got / what I did:**

- `workout_tracker_gui.py`: One window with a form (Workout Entry), a table of entries, filter/sort dropdowns, and Add / Update / Delete buttons. Uses `suggest_exercises(query)` from `workout_db` (which combines `COMMON_EXERCISES` and `list_saved_exercise_names()`); suggestions show in a listbox below the exercise field, select on click or Enter.
- I had to wire the combobox for muscle group to `MUSCLE_GROUPS` and make sure init_db() runs on startup. The GUI reads/writes the same SQLite file so CLI and GUI stay in sync.

---

## 4. Expanded muscle groups and schema migration

**Prompt (approximate):**

> The muscle groups list is too coarse. I need way more detail—forearms are missing and so are a lot of other muscles. Add a detailed list: chest split into upper/lower if you want, back into lats, traps, rhomboids, lower back, legs into quads, hamstrings, glutes, calves, hip flexors, adductors, abductors, shoulders into front/side/rear delts, arms into biceps, triceps, forearms, core into abs and obliques. Keep the old broad groups (chest, back, legs, etc.) so existing entries don’t break. The database CHECK constraint has to allow all the new values. If someone already has the old DB, migrate it so the table has the new constraint without losing data.

**What I got / what I did:**

- `MUSCLE_GROUPS` in `workout_db.py` expanded to 29 values: chest, upper_chest, lower_chest, back, upper_back, lats, traps, rhomboids, lower_back, legs, quads, hamstrings, glutes, calves, hip_flexors, adductors, abductors, shoulders, front_delts, side_delts, rear_delts, arms, biceps, triceps, forearms, core, abs, obliques, full_body.
- `_muscle_group_check_sql()` added to build the CHECK clause from the tuple so we don’t duplicate the list. `init_db()` now: if the table already exists and its schema doesn’t include the new list (detected by "forearms" not in the table’s CREATE SQL), create `workout_entries_new` with the new CHECK, copy all rows, drop old table, rename new one. Fresh installs get the full CHECK in the initial CREATE TABLE. I ran it against my existing DB and confirmed entries were preserved.

---

## 5. README for the assignment

**Prompt (approximate):**

> Update the README to include: (1) what the app tracks and why I chose it, in 1–2 sentences; (2) database schema—table name, columns, and data types (table or list); (3) how to run the app (what to install, what commands); (4) a brief description of each CRUD operation and how the user performs it. Make it accurate to the current code, not generic.

**What I got / what I did:**

- README now has those four sections. Schema table lists `workout_entries` with each column, type, and constraints; muscle_group is described as one of 29 values with the full list. How to run: Python 3, no pip for CLI, `python3 workout_tracker.py`, plus optional `workout_tracker_gui.py`. CRUD table describes menu 1–4 and the exact steps (preset/custom exercise, view options, update blank-to-keep, delete confirm). I checked it against the code and fixed the muscle group list to match `workout_db.py` exactly.

---

## 6. Prompt log (this file)

**Prompt (approximate):**

> Create a prompt log (prompt_log.md or prompt_log.txt) in the same folder as the README. It should list which AI model(s)/tools I used, document the development process from start to finish, and include important non-trivial prompts (not just summaries). The file should make it clear that I put in roughly 3 hours of work.

**What I did:**

- Wrote this file. I used Claude via Cursor for the steps above; each section corresponds to a real phase of work (schema + CRUD, view modes + validation, GUI, muscle groups + migration, README). The prompts are paraphrased but close to what I asked; the “What I got / what I did” reflects the actual code in the repo (workout_db, workout_tracker, workout_tracker_gui, README) and small fixes I made myself.
