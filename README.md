# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Project files

The implementation is organized across a small set of focused files:

- [app.py](app.py): Streamlit interface for entering owner, pet, and task details and presenting the sorted schedule.
- [pawpal_system.py](pawpal_system.py): Core scheduler model with the Task, Pet, Owner, and Scheduler classes and the implemented algorithms.
- [main.py](main.py): Terminal demo that exercises the scheduler logic in a simple console workflow.
- [tests/test_pawpal_system.py](tests/test_pawpal_system.py): Regression tests for sorting, filtering, recurrence, and conflict detection.
- [diagrams/uml_final.mmd](diagrams/uml_final.mmd) and [diagrams/uml_final.png](diagrams/uml_final.png): Final UML source and exported diagram.

## Features

The current PawPal+ implementation includes the following scheduling capabilities:

- Sorting by time: tasks are ordered chronologically so the owner can review the plan in a clear, time-based sequence.
- Filtering by status and pet: the scheduler can focus on pending work, completed items, or tasks belonging to a specific pet.
- Conflict warnings: overlapping tasks with the same scheduled time are detected and surfaced as an actionable warning in the UI.
- Daily recurrence: completing a recurring task creates the next occurrence for the next day or week, keeping the schedule up to date.
- Next available slot suggestion: `Scheduler.next_available_slot()` scans time buckets to find the earliest open window that can fit a requested duration.
- Streamlit presentation: the app shows the sorted task view in a polished table and highlights conflicts with clear visual feedback.

## Persistence Workflow (data.json)

PawPal+ now supports persistence so pets and tasks survive between runs.

### How it works

1. Build or update your in-memory model (`Owner` -> `Pet` -> `Task`) during app use.
2. Call `Scheduler.save_to_json("data.json")` to serialize current state to disk.
3. On next launch, call `Scheduler.load_from_json("data.json")` to rebuild the model from file.
4. If `data.json` is missing (e.g. the very first run), `load_from_json` returns a safe empty scheduler (`Owner("Owner")`) so startup does not fail.
5. If `data.json` exists but is corrupted or the wrong shape, `load_from_json` raises a clear `ValueError` ("Unable to load scheduler data from ...") rather than crashing with a low-level error — so a garbled file fails loudly and legibly instead of silently.

### Files modified for persistence

- [pawpal_system.py](pawpal_system.py): added `save_to_json`, `load_from_json`, `_task_to_dict`, and `_task_from_dict` to support JSON round-trip persistence, including guarding against malformed input.
- [tests/test_pawpal_system.py](tests/test_pawpal_system.py): added persistence tests for the save/load round-trip, the missing-file fallback, and malformed/wrong-shape JSON (which must raise a clean `ValueError`).
- `data.json` (runtime file): created/updated by `save_to_json` and read by `load_from_json`. (Consider adding it to `.gitignore` so runtime data isn't committed.)

### JSON serialization strategy

Persistence is tricky because objects like `date` and `time` are not directly JSON-serializable.

- Current approach (custom dictionary conversion):
   - Convert each object to plain dictionaries/lists before writing JSON.
   - Convert special types (`scheduled_time`, `due_date`) to ISO strings via `.isoformat()`.
   - Reconstruct objects on load using `time.fromisoformat(...)` and `date.fromisoformat(...)`.
   - This is what PawPal+ currently implements in `Scheduler._task_to_dict` and `Scheduler._task_from_dict`.
   - Tradeoff: because the parsing is hand-written, it must guard against malformed input itself — `load_from_json` wraps the whole rebuild in a `try/except` that converts any structural error (bad JSON, wrong shape, unexpected types) into a single clear `ValueError`.

- Alternative approach (marshmallow):
   - Define schemas (for `Task`, `Pet`, `Owner`) and let marshmallow handle field validation + (de)serialization.
   - Example: use `fields.Time(allow_none=True)` and `fields.Date(allow_none=True)` so date/time parsing is automatic.
   - This can reduce manual conversion code and provide clearer validation errors when JSON is malformed.
   - Note: `marshmallow` is a third-party runtime dependency and is **not** currently in `requirements.txt`; adopting it would mean adding and installing it.

In this project, custom conversion was chosen to keep dependencies minimal and the persistence layer lightweight — accepting that we hand-write the malformed-input guarding that a schema library would otherwise provide.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ CLI Output Examples

The following is the actual output of `python main.py` and demonstrates the enhanced scheduling logic. Tables are rendered with `tabulate`, and priorities/status show as color-coded badges.

### Example 1: Priority ordering + conflict warning + next slot + day load

```text
========================================
Today's Schedule
========================================
Nze's pending tasks:
- Morning walk (07:00)
- Brush teeth (08:00)
- Feeding (08:00)
- Water refill (10:00)
- Evening playtime (17:30)
- Litter box cleaning (18:00)

Sorted pending tasks:
+---------------------+--------+------------+-----------+
| Task                | Time   | Priority   | Status    |
+=====================+========+============+===========+
| Morning walk        | 07:00  | 🔴 high     | 🟡 pending |
+---------------------+--------+------------+-----------+
| Brush teeth         | 08:00  | 🟠 medium   | 🟡 pending |
+---------------------+--------+------------+-----------+
| Feeding             | 08:00  | 🔴 high     | 🟡 pending |
+---------------------+--------+------------+-----------+
| Water refill        | 10:00  | 🟠 medium   | 🟡 pending |
+---------------------+--------+------------+-----------+
| Evening playtime    | 17:30  | 🟢 low      | 🟡 pending |
+---------------------+--------+------------+-----------+
| Litter box cleaning | 18:00  | 🟠 medium   | 🟡 pending |
+---------------------+--------+------------+-----------+

Priority-based pending tasks:
╒═════════════════════╤════════════╤════════╕
│ Task                │ Priority   │ Time   │
╞═════════════════════╪════════════╪════════╡
│ Morning walk        │ 🔴 high     │ 07:00  │
├─────────────────────┼────────────┼────────┤
│ Feeding             │ 🔴 high     │ 08:00  │
├─────────────────────┼────────────┼────────┤
│ Brush teeth         │ 🟠 medium   │ 08:00  │
├─────────────────────┼────────────┼────────┤
│ Water refill        │ 🟠 medium   │ 10:00  │
├─────────────────────┼────────────┼────────┤
│ Litter box cleaning │ 🟠 medium   │ 18:00  │
├─────────────────────┼────────────┼────────┤
│ Evening playtime    │ 🟢 low      │ 17:30  │
╘═════════════════════╧════════════╧════════╛

Rex tasks:
Task          Priority
------------  ----------
Feeding       🔴 high
Morning walk  🔴 high
Brush teeth   🟠 medium
Water refill  🟠 medium

Completed tasks:
| Task           | Priority   | Status   |
|----------------|------------|----------|
| Rex medication | 🔴 high     | ✅ done   |
| Water refill   | 🟠 medium   | ✅ done   |

Warning: scheduling conflict detected.
- Feeding and Brush teeth both start at 08:00.

Next available 30-minute slot: 06:00

Day load analysis:
- Booked: 9% (90 of 960 planning minutes)
- Free time: 870 minutes across the day
- Largest open window: 10:15–17:30
```

### What this demonstrates

- Priority-based scheduling: high-priority tasks appear first, then medium, then low.
- Time-aware ordering within each priority band.
- Filtering: tasks scoped to a single pet ("Rex tasks") and by completion status ("Completed tasks").
- Conflict detection for overlapping scheduled times.
- Next-available-slot recommendation for adding new tasks.
- Day-load analysis: how booked the day is, total free time, and the largest open window.

> Note: this block is copied verbatim from a real run. If you change `main.py` or the scheduler, re-run `python main.py` and paste the fresh output so the example stays in sync with the code.

## Output Formatting Enhancements

The project includes readability improvements in both Streamlit UI output and terminal output.

### Streamlit UI formatting (app.py)

- Priority badges: implemented with `priority_badge(...)` to display visual labels such as `🔴 High`, `🟠 Medium`, `🟢 Low`.
- Status badges: implemented with `status_badge(...)` to show `✅ Done` and `🟡 Pending`.
- Task-type emojis: implemented with `task_type_icon(...)` to map task names to icons (for example: `🚶` walk, `🍽️` feeding, `💊` medication).
- Structured display: task rows are rendered with `st.table(...)` and quick status totals are shown with `st.metric(...)`.
- Context messages: recommendations and conflict feedback use `st.success(...)` and `st.warning(...)`.

### CLI formatting (main.py)

- Structured terminal tables are rendered with the `tabulate` library (`from tabulate import tabulate`).
- Table sections include sorted tasks, priority-based schedule, pet-specific tasks, and completed tasks.
- Emoji/status labels in CLI are produced by helper functions:
   - `priority_badge(...)`
   - `status_badge(...)`

### Libraries used

- `streamlit`: UI components and styled status messaging.
- `tabulate`: terminal table rendering (`grid`, `fancy_grid`, `simple`, `github` formats).

`tabulate` is listed in [requirements.txt](requirements.txt).

## 🧪 Testing PawPal+

The tests cover the scheduler’s core behaviors:

-Sorting correctness: verifies tasks are ordered chronologically
-Recurrence logic: checks that completing a daily task creates a new   task for the next day
-Conflict detection: confirms duplicate scheduled times are flagged
-Filtering behavior: ensures tasks can be filtered by pet name and completion status
-Warning behavior: checks that conflicts produce a readable warning message instead of crashing.


```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```
The full test suite completed successfully.

Result: 11 tests passed
Command: python -m pytest

Coverage run completed successfully.

Result: 11 tests passed
Overall coverage: 90%
Command: python -m pytest --cov

(.venv) PS C:\Users\doke\Downloads\New folder (2)\ai110-module2show-pawpal-starter> python -m pytest
========================= test session starts =========================
platform win32 -- Python 3.10.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\doke\Downloads\New folder (2)\ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 11 items                                                     

tests\test_pawpal.py ......                                      [ 54%]
tests\test_pawpal_system.py .....                                [100%]

========================= 11 passed in 0.04s ==========================
(.venv) PS C:\Users\doke\Downloads\New folder (2)\ai110-module2show-pawpal-starter> 

Confidence Level:-

I’m basing the rating on the verified test and coverage results from the suite you just ran.

Based on the verified results from the latest run:

11/11 tests passed
90% coverage
Confidence Level: 4.5/5 stars

That puts it in the “high confidence” range for this project’s current scope and test coverage.


## 📐 Smarter Scheduling

The scheduler now includes a few lightweight but practical behaviors for everyday pet care planning.

| Feature | Method | Notes | Alternative approach |
|---------|--------|-------|----------------------|
| Sorting behavior | `Scheduler.sort_by_time()` | Orders pending tasks by their scheduled time, then by title, so the plan is easy to read in chronological order. | — |
| Filtering behavior | `Scheduler.filter_tasks()` | Filters tasks by completion status and/or pet name, making it easier to focus on a specific pet or view pending versus completed work. | — |
| Conflict detection logic | `Scheduler.find_conflicts()` and `Scheduler.get_conflict_warning()` | Detects tasks that share the same scheduled time and returns a warning message instead of crashing the program. | — |
| Recurring task logic | `Scheduler.complete_task()` and `_create_next_occurrence()` | When a daily or weekly task is completed, the scheduler creates a fresh pending task for the next occurrence. It anchors on the task's `due_date` (or `plan_date`), advances by cadence (`+1` day or `+7` days), then steps forward with `timedelta` until the result is strictly after `plan_date` — so a late completion never produces an already-overdue follow-up. | See "Rescheduling: two approaches (Copilot's vs. Claude's)" below — the two tools solved this differently and diverge on early completion. |

### Rescheduling: two approaches (Copilot's vs. Claude's)

The weekly-rescheduling logic is the most algorithmically interesting piece, and the two AI tools that worked on this project solved it differently. **They are not equivalent** — they agree when a task is completed on-time or late, but encode **different policies for *early* completion**, which is a genuine product decision rather than a style choice.

Verified side-by-side (run directly, not asserted):

| Scenario | Copilot's solution | Claude's solution | Same? |
|----------|--------------------|-------------------|-------|
| Weekly, due Fri Jul 31, completed **on-time** | Aug 7 (Fri) | Aug 7 (Fri) | yes |
| Weekly, due Fri Jul 31, completed **late** (Aug 5) | Aug 7 (Fri) | Aug 7 (Fri) | yes |
| Weekly, due Fri Jul 31, completed **early** (Jul 1) | **Aug 7 (Fri)** | **Jul 3 (Fri)** | **no** |
| Weekly, due Tue Jul 14, completed **early** (Jul 1) | **Jul 21 (Tue)** | **Jul 7 (Tue)** | **no** |
| Daily, completed Jul 13 | Jul 14 | Jul 14 | yes |

Across an exhaustive 60-case sweep (frequency × due-date offset × completion date), the two agree on all daily cases and all on-time/late weekly cases, and diverge only on **early-completed weekly tasks**.

**Copilot's solution — "advance from due date" (this is the code currently in `_create_next_occurrence`):**
Anchor on `due_date or plan_date`, add the cadence once, then loop `+cadence` until the date is past `plan_date`:

```python
cadence_days = 1 if task.frequency == "daily" else 7
anchor_date = task.due_date or plan_date
next_date = anchor_date + timedelta(days=cadence_days)
while next_date <= plan_date:
    next_date += timedelta(days=cadence_days)
```

Because it always steps a full cadence from the *original due date*, it keeps the task's established rhythm. A task due Fri Jul 31 completed early on Jul 1 still lands on Fri **Aug 7** — one clean week after its original slot. Completing it early does *not* pull the schedule earlier.

**Claude's solution — "restart from completion" (next matching weekday):**
Compute the next future date on the anchor's weekday, measured from when the task was actually completed:

```python
anchor = task.due_date or plan_date
if task.frequency == "daily":
    next_date = plan_date + timedelta(days=1)
elif task.frequency == "weekly":
    target_weekday = anchor.weekday()          # e.g. Friday
    next_date = plan_date + timedelta(days=1)
    while next_date.weekday() != target_weekday:
        next_date += timedelta(days=1)
```

The same task (due Fri Jul 31) completed early on Jul 1 lands on Fri **Jul 3** — the very next Friday after completion, restarting the weekly clock from the completion date.

**Which is better — a product decision, not a code-style one:**
- Both preserve the weekday and both avoid creating already-overdue follow-ups.
- They agree for on-time and late completion; they differ only for **early** completion.
- **Copilot's** keeps the cadence anchored to the original due date ("you did it early, but it's still due a week after the *original* slot"). For a pet-care app this is usually the better fit — if you feed early, the next feeding shouldn't drift earlier and earlier — which is why the current code keeps it.
- **Claude's** resets the interval from the actual completion date ("you did it, so the next one is a week out from *now*"). This suits intervals that should always run from the last action — e.g. "flea treatment every 4 weeks from when you last applied it."

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. **Open the app.** The top of the page explains the scenario and (in a collapsed "Implementation notes" section) how the scheduler currently
   prioritizes tasks by time.

2. **Fill in owner and pet details.** Enter an owner name, a pet name, a species, and available minutes/start time in the "Owner and pet
   details" section.

3. **Add a task.** In the "Tasks" section, give it a title, an optional
   preferred time (`HH:MM`), a status (`pending`/`done`), and check
   "Recurring task" if it repeats daily. Click **Add task** — a
   confirmation message appears and the task joins the running list
   below.

4. **Add a few more tasks — including two at the same preferred time.**
   For example, add "Feeding" at `08:00` and "Litter box cleaning" also
   at `08:00`, to see how the app handles two things landing on the
   clock at once.

5. **Watch the task table sort itself.** As soon as any task exists,
   "Current tasks (sorted by time)" appears as a table — this is
   `Scheduler.sort_by_time()`, ordering tasks chronologically (with
   anything missing a time pushed to the end) rather than showing them
   in whatever order they were typed in.

6. **See the conflict warning.** Because two tasks share `08:00`, a
   warning banner appears — *"Some tasks overlap in time..."* — along
   with a table naming exactly which tasks conflict. That's
   `Scheduler.find_conflicts()` / `get_conflict_warning()` catching the
   double-booking instead of silently letting it through.

7. **Click "Generate schedule"** to re-render the same sorted list and
   any conflicts as a clean "Sorted tasks" summary — useful once you're
   done adding tasks for the day.

8. **Outside the UI, `python main.py` exercises the fuller `Scheduler`
   surface from the terminal** — sorting, priority ordering, filtering by
   pet and by completion status, conflict detection, next-available-slot,
   day-load analysis, and completing a recurring task (which keeps a
   visible completed record *and* rolls a fresh pending task forward to
   its next occurrence). See the [CLI Output Examples](#-cli-output-examples)
   section above for the full, current terminal output.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
