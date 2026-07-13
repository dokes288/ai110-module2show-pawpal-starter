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
- Streamlit presentation: the app shows the sorted task view in a polished table and highlights conflicts with clear visual feedback.

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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Sample Output:

(.venv) PS C:\Users\dokek\Downloads\New folder (2)\ai110-module2show-pawpal-starter> python main.py
========================================
Today's Schedule
========================================
Daily plan for Nze's pets:
07:00 — Rex: Morning walk (30 min) [priority: high] — priority 'high', fit into open time
08:00 — Rex: Feeding (10 min) [priority: high] — fixed time, priority 'high'
17:30 — Luna: Evening playtime (20 min) [priority: medium] — priority 'medium', fit into open time
18:00 — Luna: Litter box cleaning (10 min) [priority: medium] — fixed time, priority 'medium'
(.venv) PS C:\Users\dokek\Downloads\New folder (2)\ai110-module2show-pawpal-starter>

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

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

| Feature | Method | Notes |
|---------|--------|-------|
| Sorting behavior | `Scheduler.sort_by_time()` | Orders pending tasks by their scheduled time, then by title, so the plan is easy to read in chronological order. |
| Filtering behavior | `Scheduler.filter_tasks()` | Filters tasks by completion status and/or pet name, making it easier to focus on a specific pet or view pending versus completed work. |
| Conflict detection logic | `Scheduler.find_conflicts()` and `Scheduler.get_conflict_warning()` | Detects tasks that share the same scheduled time and returns a warning message instead of crashing the program. |
| Recurring task logic | `Scheduler.complete_task()` and `_create_next_occurrence()` | When a daily or weekly task is completed, the scheduler creates a fresh pending task for the next occurrence using `timedelta`. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
