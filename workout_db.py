import sqlite3
from typing import Optional


DB_PATH = "workout_tracker.db"
MUSCLE_GROUPS = ("chest", "back", "legs", "shoulders", "arms", "core", "full_body")
UNITS = ("lb", "kg")
COMMON_EXERCISES = (
    "Bench Press",
    "Incline Bench Press",
    "Dumbbell Bench Press",
    "Squat",
    "Front Squat",
    "Deadlift",
    "Romanian Deadlift",
    "Overhead Press",
    "Barbell Row",
    "Pull-up",
    "Lat Pulldown",
    "Leg Press",
    "Lunge",
    "Bicep Curl",
    "Tricep Pushdown",
)


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_connection() as con:
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_entries (
                id INTEGER PRIMARY KEY,
                exercise_name TEXT NOT NULL,
                workout_date TEXT NOT NULL,
                sets INTEGER NOT NULL CHECK(sets > 0),
                top_weight REAL NOT NULL CHECK(top_weight >= 0),
                top_reps INTEGER NOT NULL CHECK(top_reps > 0),
                bodyweight REAL CHECK(bodyweight >= 0),
                unit TEXT NOT NULL CHECK(unit IN ('lb', 'kg')),
                muscle_group TEXT NOT NULL CHECK(
                    muscle_group IN ('chest', 'back', 'legs', 'shoulders', 'arms', 'core', 'full_body')
                ),
                is_pr INTEGER NOT NULL DEFAULT 0 CHECK(is_pr IN (0, 1))
            )
            """
        )
        con.commit()


def create_entry(
    exercise_name: str,
    workout_date: str,
    sets: int,
    top_weight: float,
    top_reps: int,
    bodyweight: Optional[float],
    unit: str,
    muscle_group: str,
    is_pr: int,
) -> None:
    with get_connection() as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO workout_entries (
                exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr),
        )
        con.commit()


def list_entries(view_mode: str = "all", search: str = "") -> list[tuple]:
    with get_connection() as con:
        cur = con.cursor()
        if view_mode == "filter":
            cur.execute(
                """
                SELECT id, exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr
                FROM workout_entries
                WHERE LOWER(exercise_name) LIKE LOWER(?)
                ORDER BY workout_date DESC, id DESC
                """,
                (f"%{search}%",),
            )
        elif view_mode == "top_weight":
            cur.execute(
                """
                SELECT id, exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr
                FROM workout_entries
                ORDER BY top_weight DESC, top_reps DESC, id DESC
                """
            )
        else:
            cur.execute(
                """
                SELECT id, exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr
                FROM workout_entries
                ORDER BY workout_date DESC, id DESC
                """
            )
        return cur.fetchall()


def get_entry_by_id(entry_id: int) -> Optional[tuple]:
    with get_connection() as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT id, exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr
            FROM workout_entries
            WHERE id = ?
            """,
            (entry_id,),
        )
        return cur.fetchone()


def update_entry(
    entry_id: int,
    exercise_name: str,
    workout_date: str,
    sets: int,
    top_weight: float,
    top_reps: int,
    bodyweight: Optional[float],
    unit: str,
    muscle_group: str,
    is_pr: int,
) -> None:
    with get_connection() as con:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE workout_entries
            SET exercise_name = ?, workout_date = ?, sets = ?, top_weight = ?, top_reps = ?,
                bodyweight = ?, unit = ?, muscle_group = ?, is_pr = ?
            WHERE id = ?
            """,
            (exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr, entry_id),
        )
        con.commit()


def delete_entry(entry_id: int) -> None:
    with get_connection() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM workout_entries WHERE id = ?", (entry_id,))
        con.commit()


def list_saved_exercise_names() -> list[str]:
    with get_connection() as con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT DISTINCT exercise_name
            FROM workout_entries
            ORDER BY exercise_name COLLATE NOCASE ASC
            """
        )
        return [row[0] for row in cur.fetchall() if row[0]]


def suggest_exercises(query: str) -> list[str]:
    query_clean = query.strip().lower()
    combined = list(dict.fromkeys((*COMMON_EXERCISES, *list_saved_exercise_names())))
    if not query_clean:
        return combined[:8]

    starts = [name for name in combined if name.lower().startswith(query_clean)]
    contains = [name for name in combined if query_clean in name.lower() and name not in starts]
    return (starts + contains)[:8]
