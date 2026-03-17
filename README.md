# Workout Tracker

## What the app tracks and why

The app tracks **strength-training entries**: for each exercise on a given day it stores your top set (weight × reps), number of sets, optional bodyweight, unit (lb/kg), muscle group, and whether it was a PR. I chose this because tracking top sets and PRs over time is a simple way to measure progressive overload without logging every single set.

---

## Database schema

There is one table: **`workout_entries`**.

| Column          | Type    | Constraints |
|----------------|---------|-------------|
| `id`           | INTEGER | PRIMARY KEY |
| `exercise_name`| TEXT    | NOT NULL |
| `workout_date` | TEXT    | NOT NULL (YYYY-MM-DD) |
| `sets`         | INTEGER | NOT NULL, > 0 |
| `top_weight`   | REAL    | NOT NULL, ≥ 0 |
| `top_reps`     | INTEGER | NOT NULL, > 0 |
| `bodyweight`   | REAL    | nullable, ≥ 0 |
| `unit`         | TEXT    | NOT NULL, IN ('lb', 'kg') |
| `muscle_group` | TEXT    | NOT NULL, one of 29 allowed values (see below) |
| `is_pr`        | INTEGER | NOT NULL, 0 or 1, default 0 |

**Allowed `muscle_group` values:** chest, upper_chest, lower_chest, back, upper_back, lats, traps, rhomboids, lower_back, legs, quads, hamstrings, glutes, calves, hip_flexors, adductors, abductors, shoulders, front_delts, side_delts, rear_delts, arms, biceps, triceps, forearms, core, abs, obliques, full_body.

---

## How to run the app

**Requirements:** Python 3. No pip install needed for the CLI; it uses the built-in `sqlite3` module.

From the project folder:

```bash
python3 workout_tracker.py
```

On first run, `workout_tracker.db` is created in the same folder (and migrated automatically if you had an older schema).

**GUI (optional):**

```bash
python3 workout_tracker_gui.py
```

The GUI may require a supported tkinter install (usually included with Python on macOS/Windows).

---

## CRUD operations

| Operation | How the user does it |
|-----------|----------------------|
| **Create** | Menu **1** (Add workout entry). Pick an exercise (preset from a short list or type a custom name), then enter workout date (default today), sets, top set weight, top set reps, optional bodyweight, unit (lb/kg), muscle group (must match one of the 29 options), and whether it was a PR (y/n). The app inserts one row into `workout_entries`. |
| **Read**   | Menu **2** (View entries). Choose: (1) show all by newest date, (2) filter by exercise name (substring match), or (3) sort by top weight heaviest first. The app queries the table and prints the list (ID, date, exercise, muscle group, sets, top weight×reps, bodyweight, unit, PR). |
| **Update** | Menu **3** (Update entry). View entries first, then enter the **ID** of the row to change. Re-enter any field to change it; leave a prompt blank to keep the current value. The app updates that row. |
| **Delete** | Menu **4** (Delete entry). View entries, enter the **ID** to remove, confirm with **y**. The app deletes that row. |
