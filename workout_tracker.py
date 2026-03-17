from datetime import date

from workout_db import (
    COMMON_EXERCISES,
    MUSCLE_GROUPS,
    UNITS,
    create_entry,
    delete_entry as db_delete_entry,
    get_entry_by_id,
    init_db,
    list_entries,
    update_entry as db_update_entry,
)

PRESET_EXERCISES = COMMON_EXERCISES[:6]


def read_non_empty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Value cannot be empty. Please try again.")


def read_positive_int(prompt_text: str, allow_blank: bool = False):
    while True:
        raw = input(prompt_text).strip()
        if allow_blank and raw == "":
            return None
        try:
            value = int(raw)
            if value > 0:
                return value
        except ValueError:
            pass
        print("Enter a whole number greater than 0.")


def read_non_negative_float(prompt_text: str, allow_blank: bool = False):
    while True:
        raw = input(prompt_text).strip()
        if allow_blank and raw == "":
            return None
        try:
            value = float(raw)
            if value >= 0:
                return value
        except ValueError:
            pass
        print("Enter a number greater than or equal to 0.")


def read_unit(prompt_text: str, allow_blank: bool = False):
    while True:
        unit = input(prompt_text).strip().lower()
        if allow_blank and unit == "":
            return None
        if unit in UNITS:
            return unit
        print("Unit must be 'lb' or 'kg'.")


def read_muscle_group(prompt_text: str, allow_blank: bool = False):
    while True:
        group = input(prompt_text).strip().lower()
        if allow_blank and group == "":
            return None
        if group in MUSCLE_GROUPS:
            return group
        print(f"Muscle group must be one of: {', '.join(MUSCLE_GROUPS)}")


def read_yes_no_pr(prompt_text: str, allow_blank: bool = False):
    while True:
        raw = input(prompt_text).strip().lower()
        if allow_blank and raw == "":
            return None
        if raw in {"y", "yes"}:
            return 1
        if raw in {"n", "no"}:
            return 0
        print("Please type y or n.")


def choose_exercise_name() -> str:
    print("Choose an exercise:")
    for i, exercise in enumerate(PRESET_EXERCISES, start=1):
        print(f"{i}. {exercise}")
    custom_option = len(PRESET_EXERCISES) + 1
    print(f"{custom_option}. Custom exercise name")
    while True:
        choice_raw = input("Choose option: ").strip()
        try:
            choice = int(choice_raw)
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= choice <= len(PRESET_EXERCISES):
            return PRESET_EXERCISES[choice - 1]
        if choice == custom_option:
            return read_non_empty("Enter custom exercise name: ")
        print("Invalid option. Try again.")


def add_entry() -> None:
    print("\n--- Add Workout Entry ---")
    exercise_name = choose_exercise_name()
    default_date = date.today().isoformat()
    workout_date = input(f"Workout date (YYYY-MM-DD) [{default_date}]: ").strip() or default_date
    sets = read_positive_int("Number of sets: ")
    top_weight = read_non_negative_float("Top set weight: ")
    top_reps = read_positive_int("Top set reps: ")
    bodyweight = read_non_negative_float("Bodyweight (blank to skip): ", allow_blank=True)
    unit = read_unit("Unit (lb/kg): ")
    print(f"Muscle group options: {', '.join(MUSCLE_GROUPS)}")
    muscle_group = read_muscle_group("Muscle group: ")
    is_pr = read_yes_no_pr("Was this a PR set? (y/n): ")

    create_entry(exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr)
    print("Entry added.\n")


def print_rows(rows) -> None:
    if not rows:
        print("No entries found.\n")
        return

    print("\nID | Date       | Exercise       | Group      | Sets | Top Wt x Reps | BW      | Unit | PR")
    print("-" * 95)
    for row in rows:
        bodyweight = "" if row[6] is None else f"{row[6]:.1f}"
        pr = "Y" if row[9] == 1 else "N"
        print(
            f"{row[0]:<2} | {row[2]:<10} | {row[1]:<14} | {row[8]:<10} | {row[3]:<4} | "
            f"{row[4]:>6.1f} x {row[5]:<4} | {bodyweight:<7} | {row[7]:<4} | {pr}"
        )
    print()


def view_entries() -> None:
    print("\n--- View Entries ---")
    print("1. Show all (newest date first)")
    print("2. Filter by exercise name")
    print("3. Sort by top weight (heaviest first)")
    choice = input("Choose an option: ").strip()

    if choice == "2":
        search = read_non_empty("Exercise name contains: ")
        rows = list_entries(view_mode="filter", search=search)
    elif choice == "3":
        rows = list_entries(view_mode="top_weight")
    else:
        rows = list_entries(view_mode="all")
    print_rows(rows)


def fetch_entry_by_id(entry_id: int):
    return get_entry_by_id(entry_id)


def update_entry() -> None:
    print("\n--- Update Entry ---")
    view_entries()
    entry_id = read_positive_int("Enter ID to update: ")
    row = fetch_entry_by_id(entry_id)
    if row is None:
        print("Entry not found.\n")
        return

    print("Leave blank to keep current value.")
    exercise_name = input(f"Exercise name [{row[1]}]: ").strip() or row[1]
    workout_date = input(f"Workout date [{row[2]}]: ").strip() or row[2]
    sets_input = read_positive_int(f"Sets [{row[3]}]: ", allow_blank=True)
    sets = row[3] if sets_input is None else sets_input
    top_weight_input = read_non_negative_float(f"Top weight [{row[4]}]: ", allow_blank=True)
    top_weight = row[4] if top_weight_input is None else top_weight_input
    top_reps_input = read_positive_int(f"Top reps [{row[5]}]: ", allow_blank=True)
    top_reps = row[5] if top_reps_input is None else top_reps_input

    current_bodyweight = "" if row[6] is None else str(row[6])
    bodyweight_raw = input(f"Bodyweight [{current_bodyweight}] (blank keeps): ").strip()
    if bodyweight_raw == "":
        bodyweight = row[6]
    else:
        try:
            parsed = float(bodyweight_raw)
            if parsed < 0:
                raise ValueError
            bodyweight = parsed
        except ValueError:
            print("Invalid bodyweight. Keeping previous value.")
            bodyweight = row[6]

    unit_input = read_unit(f"Unit [{row[7]}] (lb/kg): ", allow_blank=True)
    unit = row[7] if unit_input is None else unit_input

    print(f"Muscle group options: {', '.join(MUSCLE_GROUPS)}")
    muscle_group_input = read_muscle_group(f"Muscle group [{row[8]}]: ", allow_blank=True)
    muscle_group = row[8] if muscle_group_input is None else muscle_group_input

    is_pr_input = read_yes_no_pr(f"PR [{('y' if row[9] == 1 else 'n')}] (y/n): ", allow_blank=True)
    is_pr = row[9] if is_pr_input is None else is_pr_input

    db_update_entry(entry_id, exercise_name, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr)
    print("Entry updated.\n")


def delete_entry() -> None:
    print("\n--- Delete Entry ---")
    view_entries()
    entry_id = read_positive_int("Enter ID to delete: ")
    row = fetch_entry_by_id(entry_id)
    if row is None:
        print("Entry not found.\n")
        return

    print(
        f"Selected: ID {row[0]} | {row[2]} | {row[1]} | "
        f"{row[4]:.1f}{row[7]} x {row[5]} | {row[8]} | PR={'Y' if row[9] else 'N'}"
    )
    confirm = input("Are you sure you want to delete this entry? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.\n")
        return

    db_delete_entry(entry_id)
    print("Entry deleted.\n")


def menu_loop() -> None:
    while True:
        print("--- Workout Tracker ---")
        print("1. Add workout entry")
        print("2. View entries")
        print("3. Update entry")
        print("4. Delete entry")
        print("5. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_entry()
        elif choice == "2":
            view_entries()
        elif choice == "3":
            update_entry()
        elif choice == "4":
            delete_entry()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Try again.\n")


if __name__ == "__main__":
    init_db()
    menu_loop()
