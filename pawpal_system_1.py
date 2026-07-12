from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import List, Optional


@dataclass(frozen=True)
class Task:
    """Represents a pet care task with scheduling flexibility."""
    id: str
    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = ""
    fixed_time: Optional[time] = None
    earliest_time: Optional[time] = None
    latest_time: Optional[time] = None
    recurrence: Optional[str] = None
    weekly_day: Optional[int] = None

    def update_task(self) -> None:
        """Update task properties."""
        pass

    def get_priority_value(self) -> int:
        """Return numeric priority value for sorting."""
        pass

    def applies_on(self, target_date: date) -> bool:
        """Check if task applies on a given date based on recurrence."""
        pass

    def is_outdoor(self) -> bool:
        """Check if task is an outdoor activity."""
        pass


@dataclass(frozen=True)
class Pet:
    """Represents a pet being cared for."""
    name: str
    species: str
    breed: str = ""
    age_years: float = 0.0
    notes: Optional[str] = None

    def update_pet_info(self) -> None:
        """Update pet information."""
        pass


@dataclass(frozen=True)
class Owner:
    """Represents the pet owner and their availability."""
    name: str
    available_minutes: int = 480
    preferred_start_hour: int = 8
    preferred_end_hour: int = 20
    prefer_outdoor_morning: bool = True

    def update_profile(self) -> None:
        """Update owner profile information."""
        pass

    def set_available_time(self, minutes: int) -> None:
        """Set available time for pet care in minutes."""
        pass

    def validate(self) -> None:
        """Validate owner configuration."""
        pass


class SchedulePlanner:
    """Plans and schedules pet care tasks for a given day."""

    def __init__(self, owner: Owner, pet: Pet, start_time: str = "08:00") -> None:
        """Initialize the planner with owner, pet, and start time."""
        self.owner = owner
        self.pet = pet
        self.start_time = start_time
        self.scheduled_tasks: List[dict] = []
        self.skipped_tasks: List[dict] = []

    def build_daily_plan(self, tasks: List[Task]) -> List[dict]:
        """Build a daily schedule based on available time and task priorities."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the scheduled plan."""
        pass
