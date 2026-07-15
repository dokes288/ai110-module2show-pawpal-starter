"""Core PawPal+ classes for pet-care task management.

The design uses four classes:
- Task: a single care activity
- Pet: a pet with its own task list
- Owner: a person who can have multiple pets
- Scheduler: collects and organizes tasks across the owner's pets
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from math import ceil
from pathlib import Path
from typing import Any, List, Optional

# Shared scheduling granularity (minutes per time bucket). All slot/gap/
# load methods default to this single value so their answers stay
# consistent -- e.g. next_available_slot() and find_free_gaps() agree on
# where free time starts. Override per-call if a specific method needs a
# different resolution.
DEFAULT_SLOT_MINUTES = 15

# Allowed task priorities and their sort order (lower rank = scheduled
# earlier). Single source of truth: Task.__post_init__ validates against
# this set, and Scheduler.prioritize_tasks() sorts by it.
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass(frozen=True)
class Task:
    """Represents one pet-care activity."""

    title: str
    description: str = ""
    priority: str = "medium"
    scheduled_time: Optional[time] = None
    frequency: str = "once"
    completed: bool = False
    due_date: Optional[date] = None

    def __post_init__(self) -> None:
        # Validation only (no field reassignment), which is safe on a
        # frozen dataclass. Guards against silent typos like
        # priority="urgent" that would otherwise sort below "low".
        if self.priority.lower() not in PRIORITY_RANK:
            raise ValueError(
                f"priority must be one of {sorted(PRIORITY_RANK)}, got {self.priority!r}"
            )

    def update_task(self, **changes) -> "Task":
        """Return a new Task with updated values."""
        return replace(self, **changes)

    def mark_complete(self) -> "Task":
        """Mark the task as complete."""
        return replace(self, completed=True)

    def reschedule(self, scheduled_time: time) -> "Task":
        """Move the task to a new time."""
        return replace(self, scheduled_time=scheduled_time)

    def is_due_on(self, plan_date: date) -> bool:
        """Return True if the task should appear for the supplied date."""
        if self.frequency == "once":
            return True
        if self.frequency == "daily":
            return True
        if self.frequency == "weekly":
            return True
        return False


@dataclass
class Pet:
    """Represents one pet and its tasks."""

    name: str
    species: str
    age_years: Optional[float] = None
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove a task by title."""
        self.tasks = [task for task in self.tasks if task.title != task_title]

    def get_pending_tasks(self) -> List[Task]:
        """Return incomplete tasks for this pet."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """Represents a pet owner who can manage multiple pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's care list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

    def get_all_tasks(self) -> List[Task]:
        """Collect tasks from all pets owned by this person."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """Organizes and manages tasks across an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieve every task from the owner's pets."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> List[Task]:
        """Return all incomplete tasks for the owner's pets."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def filter_tasks(
        self,
        tasks: Optional[List[Task]] = None,
        *,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by completion status and/or pet name."""
        source = tasks if tasks is not None else self.get_all_tasks()
        filtered_tasks = source

        if completed is not None:
            filtered_tasks = [task for task in filtered_tasks if task.completed is completed]

        if pet_name is not None:
            pet_name_lower = pet_name.lower()
            matching_pets = [pet for pet in self.owner.pets if pet.name.lower() == pet_name_lower]
            if matching_pets:
                filtered_tasks = [
                    task
                    for task in filtered_tasks
                    if any(task in pet.tasks for pet in matching_pets)
                ]
            else:
                filtered_tasks = [task for task in filtered_tasks if pet_name_lower in task.title.lower()]

        return filtered_tasks

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by scheduled time, then by title."""
        source = tasks if tasks is not None else self.get_all_tasks()
        return sorted(
            source,
            key=lambda task: (
                task.scheduled_time is None,
                task.scheduled_time or time(23, 59),
                task.title.lower(),
            ),
        )

    def organize_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Backward-compatible wrapper around sort_by_time."""
        return self.sort_by_time(tasks)

    def prioritize_tasks(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Order tasks by priority first, then scheduled time, then title."""
        source = tasks if tasks is not None else self.get_pending_tasks()

        return sorted(
            source,
            key=lambda task: (
                PRIORITY_RANK.get(task.priority.lower(), len(PRIORITY_RANK)),
                task.scheduled_time is None,
                task.scheduled_time or time(23, 59),
                task.title.lower(),
            ),
        )

    def find_conflicts(self, tasks: Optional[List[Task]] = None) -> List[tuple[Task, Task]]:
        """Return pairs of tasks that are scheduled at the same time.
        Defaults to PENDING tasks only when no explicit list is given --
        this matters now that complete_task() keeps a completed record
        instead of discarding it, since without this a just-completed
        recurring task would spuriously "conflict" with its own freshly
        created next occurrence at the same scheduled_time.
        """
        source = tasks if tasks is not None else self.get_pending_tasks()
        conflicts: List[tuple[Task, Task]] = []
        seen: List[tuple[Task, Task]] = []

        for index, left in enumerate(source):
            for right in source[index + 1 :]:
                if left.scheduled_time is None or right.scheduled_time is None:
                    continue
                if left.scheduled_time == right.scheduled_time:
                    pair = (left, right)
                    if pair not in seen and (right, left) not in seen:
                        seen.append(pair)
                        conflicts.append(pair)

        return conflicts

    def get_conflict_warning(self, tasks: Optional[List[Task]] = None) -> Optional[str]:
        """Return a lightweight warning message when tasks overlap, or None if none are found."""
        conflicts = self.find_conflicts(tasks)
        if not conflicts:
            return None

        lines = ["Warning: scheduling conflict detected."]
        for left, right in conflicts:
            lines.append(f"- {left.title} and {right.title} both start at {left.scheduled_time.strftime('%H:%M')}.")
        return "\n".join(lines)

    def _create_next_occurrence(self, task: Task, plan_date: date) -> Task:
        """Create a follow-up task for the next occurrence of a recurring task.

        For recurring tasks, preserve cadence and always produce a due date
        strictly after the completion date so we do not create immediately
        overdue follow-up tasks.
        """
        if task.frequency not in {"daily", "weekly"}:
            return task

        cadence_days = 1 if task.frequency == "daily" else 7
        anchor_date = task.due_date or plan_date
        next_date = anchor_date + timedelta(days=cadence_days)
        while next_date <= plan_date:
            next_date += timedelta(days=cadence_days)

        next_time = task.scheduled_time or time(0, 0)
        return replace(task, completed=False, scheduled_time=next_time, due_date=next_date)

    def complete_task(self, task: Task, plan_date: date) -> Task:
        """Mark a task complete, keeping the completed record in the pet's
        task list (rather than discarding it), and for daily/weekly tasks
        also append a fresh pending task for the next occurrence.
        """
        completed_task = replace(task, completed=True)

        for pet in self.owner.pets:
            for index, existing in enumerate(pet.tasks):
                if existing is task:
                    pet.tasks[index] = completed_task
                    if task.frequency in {"daily", "weekly"}:
                        next_occurrence = self._create_next_occurrence(task, plan_date)
                        pet.tasks.append(next_occurrence)
                    return completed_task

        return completed_task

    def summarize(self) -> str:
        """Return a simple summary of the owner's upcoming tasks."""
        pending = self.get_pending_tasks()
        if not pending:
            return f"{self.owner.name} has no pending tasks."
        lines = [f"{self.owner.name}'s pending tasks:"]
        for task in self.organize_by_time(pending):
            time_text = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "unscheduled"
            lines.append(f"- {task.title} ({time_text})")
        return "\n".join(lines)

    def next_available_slot(
        self,
        duration_minutes: int,
        *,
        day_start: time = time(6, 0),
        day_end: time = time(22, 0),
        step_minutes: int = DEFAULT_SLOT_MINUTES,
        tasks: Optional[List[Task]] = None,
    ) -> Optional[time]:
        """Find the next open time bucket that can fit the requested duration.

        Since Task does not track duration, each scheduled task is treated as
        occupying one `step_minutes` bucket.
        """
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if step_minutes <= 0:
            raise ValueError("step_minutes must be greater than 0")

        start_minutes = day_start.hour * 60 + day_start.minute
        end_minutes = day_end.hour * 60 + day_end.minute
        if end_minutes <= start_minutes:
            raise ValueError("day_end must be later than day_start")

        source = tasks if tasks is not None else self.get_pending_tasks()
        occupied = {
            task.scheduled_time.hour * 60 + task.scheduled_time.minute
            for task in source
            if task.scheduled_time is not None
        }

        required_slots = ceil(duration_minutes / step_minutes)
        latest_start = end_minutes - (required_slots * step_minutes)

        for candidate in range(start_minutes, latest_start + 1, step_minutes):
            window = range(candidate, candidate + required_slots * step_minutes, step_minutes)
            if all(slot not in occupied for slot in window):
                return time(candidate // 60, candidate % 60)

        return None

    def find_free_gaps(
        self,
        *,
        day_start: time = time(6, 0),
        day_end: time = time(22, 0),
        slot_minutes: int = DEFAULT_SLOT_MINUTES,
        tasks: Optional[List[Task]] = None,
    ) -> List[tuple[time, time]]:
        """Return the open (start, end) windows in the day, treating each
        scheduled task as occupying one `slot_minutes` block.

        Where next_available_slot() answers "where can ONE new task go,"
        this answers "where is ALL the free time today" -- the building
        block for workload analysis and for showing an owner their open
        windows at a glance.
        """
        if slot_minutes <= 0:
            raise ValueError("slot_minutes must be greater than 0")

        start_minutes = day_start.hour * 60 + day_start.minute
        end_minutes = day_end.hour * 60 + day_end.minute
        if end_minutes <= start_minutes:
            raise ValueError("day_end must be later than day_start")

        source = tasks if tasks is not None else self.get_pending_tasks()
        occupied = sorted(
            task.scheduled_time.hour * 60 + task.scheduled_time.minute
            for task in source
            if task.scheduled_time is not None
            and start_minutes <= (task.scheduled_time.hour * 60 + task.scheduled_time.minute) < end_minutes
        )

        gaps: List[tuple[time, time]] = []
        cursor = start_minutes
        for task_start in occupied:
            if task_start > cursor:
                gaps.append((time(cursor // 60, cursor % 60), time(task_start // 60, task_start % 60)))
            cursor = max(cursor, task_start + slot_minutes)
        if cursor < end_minutes:
            gaps.append((time(cursor // 60, cursor % 60), time(end_minutes // 60, end_minutes % 60)))

        return gaps

    def analyze_day_load(
        self,
        *,
        day_start: time = time(6, 0),
        day_end: time = time(22, 0),
        slot_minutes: int = DEFAULT_SLOT_MINUTES,
        tasks: Optional[List[Task]] = None,
    ) -> dict[str, Any]:
        """Summarize how full the day is: total planning minutes, minutes
        committed to tasks, free minutes, a 0-100 load percentage, and the
        single largest open gap.

        This is a genuinely different capability from the sorting/priority
        methods -- rather than reordering the same tasks, it tells an
        owner whether the day is over- or under-booked and where their
        biggest free block is, so they can decide whether to add or move
        tasks at all.
        """
        source = tasks if tasks is not None else self.get_pending_tasks()

        start_minutes = day_start.hour * 60 + day_start.minute
        end_minutes = day_end.hour * 60 + day_end.minute
        if end_minutes <= start_minutes:
            raise ValueError("day_end must be later than day_start")
        total_minutes = end_minutes - start_minutes

        scheduled_count = sum(
            1
            for task in source
            if task.scheduled_time is not None
            and start_minutes <= (task.scheduled_time.hour * 60 + task.scheduled_time.minute) < end_minutes
        )
        committed_minutes = min(scheduled_count * slot_minutes, total_minutes)
        free_minutes = total_minutes - committed_minutes

        gaps = self.find_free_gaps(
            day_start=day_start, day_end=day_end, slot_minutes=slot_minutes, tasks=source
        )
        largest_gap = None
        if gaps:
            largest_gap = max(
                gaps,
                key=lambda gap: (gap[1].hour * 60 + gap[1].minute) - (gap[0].hour * 60 + gap[0].minute),
            )

        load_percent = round((committed_minutes / total_minutes) * 100, 1) if total_minutes else 0.0

        return {
            "total_minutes": total_minutes,
            "committed_minutes": committed_minutes,
            "free_minutes": free_minutes,
            "load_percent": load_percent,
            "scheduled_task_count": scheduled_count,
            "largest_free_gap": largest_gap,
        }

    @staticmethod
    def _task_to_dict(task: Task) -> dict[str, Any]:
        """Convert a Task to a JSON-serializable dictionary."""
        return {
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "scheduled_time": task.scheduled_time.isoformat() if task.scheduled_time else None,
            "frequency": task.frequency,
            "completed": task.completed,
            "due_date": task.due_date.isoformat() if task.due_date else None,
        }

    @staticmethod
    def _task_from_dict(task_data: dict[str, Any]) -> Task:
        """Build a Task from persisted dictionary data."""
        raw_time = task_data.get("scheduled_time")
        raw_due_date = task_data.get("due_date")

        return Task(
            title=task_data["title"],
            description=task_data.get("description", ""),
            priority=task_data.get("priority", "medium"),
            scheduled_time=time.fromisoformat(raw_time) if raw_time else None,
            frequency=task_data.get("frequency", "once"),
            completed=task_data.get("completed", False),
            due_date=date.fromisoformat(raw_due_date) if raw_due_date else None,
        )

    def save_to_json(self, file_path: str = "data.json") -> None:
        """Persist owner, pets, and tasks to a JSON file."""
        payload: dict[str, Any] = {
            "owner": {
                "name": self.owner.name,
                "pets": [
                    {
                        "name": pet.name,
                        "species": pet.species,
                        "age_years": pet.age_years,
                        "notes": pet.notes,
                        "tasks": [self._task_to_dict(task) for task in pet.tasks],
                    }
                    for pet in self.owner.pets
                ],
            }
        }

        target = Path(file_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: str = "data.json") -> "Scheduler":
        """Load owner, pets, and tasks from a JSON file.

        Returns an empty owner model when the file does not exist yet.
        """
        source = Path(file_path)
        if not source.exists():
            return cls(Owner(name="Owner"))

        try:
            raw_data = json.loads(source.read_text(encoding="utf-8"))
            owner_data = raw_data.get("owner", {})

            owner = Owner(name=owner_data.get("name", "Owner"))
            for pet_data in owner_data.get("pets", []):
                pet = Pet(
                    name=pet_data["name"],
                    species=pet_data["species"],
                    age_years=pet_data.get("age_years"),
                    notes=pet_data.get("notes", ""),
                )

                for task_data in pet_data.get("tasks", []):
                    pet.add_task(cls._task_from_dict(task_data))

                owner.add_pet(pet)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError) as error:
            raise ValueError(f"Unable to load scheduler data from {file_path}: {error}") from error

        return cls(owner)
