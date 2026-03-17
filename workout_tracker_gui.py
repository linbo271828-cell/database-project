import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from workout_db import (
    MUSCLE_GROUPS,
    UNITS,
    create_entry,
    delete_entry,
    get_entry_by_id,
    init_db,
    list_entries,
    suggest_exercises,
    update_entry,
)


class WorkoutTrackerGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Workout Tracker")
        self.root.geometry("1150x700")
        self.selected_id: int | None = None

        self.exercise_var = tk.StringVar()
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.sets_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.reps_var = tk.StringVar()
        self.bodyweight_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="lb")
        self.group_var = tk.StringVar(value=MUSCLE_GROUPS[0])
        self.is_pr_var = tk.IntVar(value=0)
        self.filter_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="Date (newest)")
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()
        self.exercise_var.trace_add("write", self._on_exercise_change)
        self.load_entries()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill=tk.X)
        bottom = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        bottom.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(top, text="Workout Entry", padding=10)
        form.pack(fill=tk.X)
        for i in range(6):
            form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Exercise").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.exercise_entry = ttk.Entry(form, textvariable=self.exercise_var)
        self.exercise_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        self.suggestions = tk.Listbox(form, height=6)
        self.suggestions.grid(row=1, column=1, sticky="ew", padx=4)
        self.suggestions.grid_remove()
        self.suggestions.bind("<<ListboxSelect>>", self._select_suggestion)
        self.suggestions.bind("<Return>", self._select_suggestion)

        ttk.Label(form, text="Date").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.date_var).grid(row=0, column=3, sticky="ew", padx=4, pady=4)

        ttk.Label(form, text="Sets").grid(row=0, column=4, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.sets_var).grid(row=0, column=5, sticky="ew", padx=4, pady=4)

        ttk.Label(form, text="Top Weight").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.weight_var).grid(row=2, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(form, text="Top Reps").grid(row=2, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.reps_var).grid(row=2, column=3, sticky="ew", padx=4, pady=4)

        ttk.Label(form, text="Bodyweight").grid(row=2, column=4, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.bodyweight_var).grid(row=2, column=5, sticky="ew", padx=4, pady=4)

        ttk.Label(form, text="Unit").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        ttk.Combobox(form, textvariable=self.unit_var, values=UNITS, state="readonly").grid(
            row=3, column=1, sticky="ew", padx=4, pady=4
        )

        ttk.Label(form, text="Muscle Group").grid(row=3, column=2, sticky="w", padx=4, pady=4)
        ttk.Combobox(form, textvariable=self.group_var, values=MUSCLE_GROUPS, state="readonly").grid(
            row=3, column=3, sticky="ew", padx=4, pady=4
        )

        ttk.Checkbutton(form, text="PR Set", variable=self.is_pr_var).grid(row=3, column=4, sticky="w", padx=4, pady=4)

        action_bar = ttk.Frame(form)
        action_bar.grid(row=4, column=0, columnspan=6, sticky="ew", pady=(8, 0))
        ttk.Button(action_bar, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="Update Selected", command=self.update_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(action_bar, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=4)

        controls = ttk.LabelFrame(bottom, text="Browse Entries", padding=10)
        controls.pack(fill=tk.BOTH, expand=True)

        toolbar = ttk.Frame(controls)
        toolbar.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(toolbar, text="Filter Exercise").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Entry(toolbar, textvariable=self.filter_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(toolbar, text="Sort").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Combobox(toolbar, textvariable=self.sort_var, values=("Date (newest)", "Top Weight (heaviest)"), state="readonly").pack(
            side=tk.LEFT
        )
        ttk.Button(toolbar, text="Apply", command=self.load_entries).pack(side=tk.LEFT, padx=8)
        ttk.Button(toolbar, text="Refresh", command=self.load_entries).pack(side=tk.LEFT)

        columns = ("id", "exercise", "date", "sets", "weight", "reps", "bw", "unit", "group", "pr")
        self.tree = ttk.Treeview(controls, columns=columns, show="headings", height=16)
        headings = {
            "id": "ID",
            "exercise": "Exercise",
            "date": "Date",
            "sets": "Sets",
            "weight": "Top Weight",
            "reps": "Top Reps",
            "bw": "Bodyweight",
            "unit": "Unit",
            "group": "Group",
            "pr": "PR",
        }
        widths = {"id": 50, "exercise": 180, "date": 110, "sets": 60, "weight": 90, "reps": 80, "bw": 90, "unit": 60, "group": 110, "pr": 50}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        ttk.Label(self.root, textvariable=self.status_var, padding=(12, 4)).pack(anchor="w")

    def _on_exercise_change(self, *_args) -> None:
        text = self.exercise_var.get().strip()
        suggestions = suggest_exercises(text)
        if not suggestions:
            self.suggestions.grid_remove()
            return

        self.suggestions.delete(0, tk.END)
        for item in suggestions:
            self.suggestions.insert(tk.END, item)

        if self.exercise_entry.focus_get() == self.exercise_entry:
            self.suggestions.grid()
        else:
            self.suggestions.grid_remove()

    def _select_suggestion(self, _event=None) -> None:
        selected = self.suggestions.curselection()
        if not selected:
            return
        picked = self.suggestions.get(selected[0])
        self.exercise_var.set(picked)
        self.suggestions.grid_remove()
        self.exercise_entry.focus_set()

    def _parse_form(self):
        exercise = self.exercise_var.get().strip()
        if not exercise:
            raise ValueError("Exercise is required.")
        workout_date = self.date_var.get().strip()
        if not workout_date:
            raise ValueError("Date is required (YYYY-MM-DD).")

        try:
            sets = int(self.sets_var.get().strip())
            if sets <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("Sets must be a whole number greater than 0.")

        try:
            top_weight = float(self.weight_var.get().strip())
            if top_weight < 0:
                raise ValueError
        except ValueError:
            raise ValueError("Top weight must be a number greater than or equal to 0.")

        try:
            top_reps = int(self.reps_var.get().strip())
            if top_reps <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("Top reps must be a whole number greater than 0.")

        bw_raw = self.bodyweight_var.get().strip()
        bodyweight = None
        if bw_raw:
            try:
                bodyweight = float(bw_raw)
                if bodyweight < 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Bodyweight must be blank or a number greater than or equal to 0.")

        unit = self.unit_var.get().strip().lower()
        if unit not in UNITS:
            raise ValueError("Unit must be lb or kg.")

        muscle_group = self.group_var.get().strip().lower()
        if muscle_group not in MUSCLE_GROUPS:
            raise ValueError("Pick a valid muscle group from the list.")

        is_pr = 1 if self.is_pr_var.get() else 0
        return exercise, workout_date, sets, top_weight, top_reps, bodyweight, unit, muscle_group, is_pr

    def add_entry(self) -> None:
        try:
            payload = self._parse_form()
            create_entry(*payload)
            self.status_var.set("Entry added.")
            self.load_entries()
            self.clear_form(keep_date=True)
        except Exception as exc:
            messagebox.showerror("Add Entry Error", str(exc))

    def load_entries(self) -> None:
        search = self.filter_var.get().strip()
        sort = self.sort_var.get().strip()
        if search:
            rows = list_entries(view_mode="filter", search=search)
        elif sort == "Top Weight (heaviest)":
            rows = list_entries(view_mode="top_weight")
        else:
            rows = list_entries(view_mode="all")

        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            row_id, ex, wdate, sets, wt, reps, bw, unit, group, is_pr = row
            bw_text = "" if bw is None else f"{bw:.1f}"
            self.tree.insert("", tk.END, values=(row_id, ex, wdate, sets, f"{wt:.1f}", reps, bw_text, unit, group, "Y" if is_pr else "N"))
        self.status_var.set(f"Loaded {len(rows)} entries.")

    def on_tree_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if not values:
            return
        entry_id = int(values[0])
        row = get_entry_by_id(entry_id)
        if row is None:
            return

        self.selected_id = row[0]
        self.exercise_var.set(row[1])
        self.date_var.set(row[2])
        self.sets_var.set(str(row[3]))
        self.weight_var.set(str(row[4]))
        self.reps_var.set(str(row[5]))
        self.bodyweight_var.set("" if row[6] is None else str(row[6]))
        self.unit_var.set(row[7])
        self.group_var.set(row[8])
        self.is_pr_var.set(row[9])
        self.status_var.set(f"Selected entry ID {entry_id}.")

    def update_selected(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select an entry from the table first.")
            return
        try:
            payload = self._parse_form()
            update_entry(self.selected_id, *payload)
            self.status_var.set(f"Updated entry ID {self.selected_id}.")
            self.load_entries()
        except Exception as exc:
            messagebox.showerror("Update Entry Error", str(exc))

    def delete_selected(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("No Selection", "Select an entry from the table first.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete entry ID {self.selected_id}?"):
            return
        try:
            delete_entry(self.selected_id)
            self.status_var.set(f"Deleted entry ID {self.selected_id}.")
            self.selected_id = None
            self.load_entries()
            self.clear_form(keep_date=True)
        except Exception as exc:
            messagebox.showerror("Delete Entry Error", str(exc))

    def clear_form(self, keep_date: bool = False) -> None:
        self.exercise_var.set("")
        if not keep_date:
            self.date_var.set(date.today().isoformat())
        self.sets_var.set("")
        self.weight_var.set("")
        self.reps_var.set("")
        self.bodyweight_var.set("")
        self.unit_var.set("lb")
        self.group_var.set(MUSCLE_GROUPS[0])
        self.is_pr_var.set(0)
        self.suggestions.grid_remove()


def main() -> None:
    init_db()
    root = tk.Tk()
    app = WorkoutTrackerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
