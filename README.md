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
