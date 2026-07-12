from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


def _parse_time(time_string: str) -> int:
    time_string = (time_string or "00:00").strip()
    hours, minutes = [int(part) for part in time_string.split(":")]
    return hours * 60 + minutes


def _format_time(minutes_since_midnight: int) -> str:
    hours = minutes_since_midnight // 60
    minutes = minutes_since_midnight % 60
    return f"{hours:02d}:{minutes:02d}"


@dataclass(frozen=True)
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    notes: Optional[str] = None
    preferred_time: Optional[str] = None
    pet_name: Optional[str] = None
    status: str = "pending"
    is_recurring: bool = False

    def __post_init__(self) -> None:
        if self.duration_minutes <= 0:
            raise ValueError("Task duration_minutes must be greater than 0")
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"Priority must be one of {list(PRIORITY_RANK)}")

        normalized_status = (self.status or "pending").strip().lower()
        if not normalized_status:
            normalized_status = "pending"
        object.__setattr__(self, "status", normalized_status)

        if self.pet_name is not None:
            object.__setattr__(self, "pet_name", self.pet_name.strip() or None)

    @property
    def priority_value(self) -> int:
        return PRIORITY_RANK[self.priority]


@dataclass(frozen=True)
class Pet:
    name: str
    species: str


@dataclass(frozen=True)
class Owner:
    name: str
    available_minutes: int = 480

    def __post_init__(self) -> None:
        if self.available_minutes < 0:
            raise ValueError("Owner available_minutes cannot be negative")


@dataclass(frozen=True)
class ScheduledTask:
    task: Task
    start_time: str
    end_time: str
    reason: str


class SchedulePlanner:
    def __init__(self, owner: Owner, pet: Pet, start_time: str = "08:00") -> None:
        self.owner = owner
        self.pet = pet
        self.start_time = start_time
        self.scheduled_tasks: List[ScheduledTask] = []
        self.skipped_tasks: List[Task] = []

    def _task_is_candidate(self, task: Task) -> bool:
        if task.is_recurring:
            return True

        if task.status == "done":
            return False

        if task.pet_name is not None and task.pet_name.lower() != self.pet.name.lower():
            return False

        return True

    def _has_conflict(self, task: Task, current_time: int) -> bool:
        if task.preferred_time is None:
            return False

        preferred_time_value = _parse_time(task.preferred_time)
        if preferred_time_value < current_time:
            return True

        for scheduled in self.scheduled_tasks:
            start_value = _parse_time(scheduled.start_time)
            end_value = _parse_time(scheduled.end_time)
            if start_value <= preferred_time_value < end_value:
                return True

        return False

    def build_daily_plan(self, tasks: List[Task]) -> List[ScheduledTask]:
        self.scheduled_tasks = []
        self.skipped_tasks = []

        candidate_tasks = [task for task in tasks if self._task_is_candidate(task)]
        sorted_tasks = sorted(
            candidate_tasks,
            key=lambda task: (
                -task.priority_value,
                _parse_time(task.preferred_time) if task.preferred_time else 24 * 60,
                task.duration_minutes,
                task.title.lower(),
            ),
        )

        remaining_minutes = self.owner.available_minutes
        current_time = _parse_time(self.start_time)

        for task in sorted_tasks:
            if task.duration_minutes > remaining_minutes:
                self.skipped_tasks.append(task)
                continue

            if self._has_conflict(task, current_time):
                self.skipped_tasks.append(task)
                continue

            start_time_text = _format_time(current_time)
            end_time_text = _format_time(current_time + task.duration_minutes)
            reason = (
                f"Selected because it is priority '{task.priority}' and fits in the available time."
            )
            self.scheduled_tasks.append(
                ScheduledTask(task=task, start_time=start_time_text, end_time=end_time_text, reason=reason)
            )
            current_time += task.duration_minutes
            remaining_minutes -= task.duration_minutes

        return self.scheduled_tasks

    def explain_plan(self) -> str:
        if not self.scheduled_tasks:
            if not self.skipped_tasks:
                return "No tasks were provided to build a plan."
            return (
                "No tasks could be scheduled within the available time. "
                "Try increasing the available minutes or reducing task durations."
            )

        lines = [
            f"Daily plan for {self.pet.name} ({self.pet.species}):",
        ]
        for scheduled in self.scheduled_tasks:
            lines.append(
                f"{scheduled.start_time} — {scheduled.task.title} "
                f"({scheduled.task.duration_minutes} min) [priority: {scheduled.task.priority}]"
            )
        if self.skipped_tasks:
            lines.append("")
            skipped_titles = ", ".join(task.title for task in self.skipped_tasks)
            lines.append(
                "Skipped lower-priority tasks due to time constraints: "
                f"{skipped_titles}."
            )
        return "\n".join(lines)
