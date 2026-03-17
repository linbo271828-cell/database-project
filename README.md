# Workout Tracker (SQLite + Python CLI)

This project tracks daily lifts so you can monitor progressive overload over time.
Each entry records one exercise summary for a day with your top set and key context.

## Database Schema

Table: `workout_entries`

- `id INTEGER PRIMARY KEY`
- `exercise_name TEXT NOT NULL`
- `workout_date TEXT NOT NULL` (use `YYYY-MM-DD`)
- `sets INTEGER NOT NULL CHECK(sets > 0)`
- `top_weight REAL NOT NULL CHECK(top_weight >= 0)`
- `top_reps INTEGER NOT NULL CHECK(top_reps > 0)`
- `bodyweight REAL CHECK(bodyweight >= 0)`
- `unit TEXT NOT NULL CHECK(unit IN ('lb', 'kg'))`
- `muscle_group TEXT NOT NULL CHECK(muscle_group IN ('chest','back','legs','shoulders','arms','core','full_body'))`
- `is_pr INTEGER NOT NULL DEFAULT 0 CHECK(is_pr IN (0, 1))`

## How To Run

From this folder:

```bash
python3 workout_tracker.py
```

No extra install is needed (uses Python's built-in `sqlite3` module).
On first run, `workout_tracker.db` is created automatically.

## CRUD Operations

- **Create**: choose `1` in the menu, enter lift details, and save a new entry.
- **Read**: choose `2` to view all entries, filter by exercise name, or sort by top weight.
- **Update**: choose `3`, pick an entry `id`, and edit any fields (blank keeps current value).
- **Delete**: choose `4`, pick an entry `id`, review the record, and confirm with `y`.