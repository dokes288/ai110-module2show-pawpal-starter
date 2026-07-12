"""Core PawPal+ classes for pet-care task management.

The design uses four classes:
- Task: a single care activity
- Pet: a pet with its own task list
- Owner: a person who can have multiple pets
- Scheduler: collects and organizes tasks across the owner's pets
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time
from typing import List, Optional


@dataclass(frozen=True)
class Task:
    """Represents one pet-care activity."""

    title: str
    description: str = ""
    scheduled_time: Optional[time] = None
    frequency: str = "once"
    completed: bool = False

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

    def organize_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
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
