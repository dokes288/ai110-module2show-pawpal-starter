"""Core PawPal+ classes for pet-care task management.

The design uses four classes:
- Task: a single care activity
- Pet: a pet with its own task list
- Owner: a person who can have multiple pets
- Scheduler: collects and organizes tasks across the owner's pets
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta
from typing import List, Optional


@dataclass(frozen=True)
class Task:
    """Represents one pet-care activity."""

    title: str
    description: str = ""
    scheduled_time: Optional[time] = None
    frequency: str = "once"
    completed: bool = False
    due_date: Optional[date] = None

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
        """Create a follow-up task for the next occurrence of a recurring task."""
        if task.frequency not in {"daily", "weekly"}:
            return task

        if task.frequency == "daily":
            next_date = plan_date + timedelta(days=1)
        else:
            next_date = plan_date + timedelta(weeks=1)

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
