import pytest

from pawpal import Owner, Pet, SchedulePlanner, Task


def test_task_priority_ordering_and_schedule_generation():
    tasks = [
        Task(title="Morning walk", duration_minutes=30, priority="high"),
        Task(title="Evening enrichment", duration_minutes=20, priority="medium"),
        Task(title="Grooming", duration_minutes=15, priority="low"),
    ]
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    planner = SchedulePlanner(owner=owner, pet=pet, start_time="08:00")

    schedule = planner.build_daily_plan(tasks)

    assert [item.task.title for item in schedule] == ["Morning walk", "Evening enrichment"]
    assert schedule[0].start_time == "08:00"
    assert schedule[0].end_time == "08:30"
    assert schedule[1].start_time == "08:30"
    assert schedule[1].end_time == "08:50"
    assert planner.skipped_tasks[0].title == "Grooming"


def test_explain_plan_mentions_skipped_tasks():
    tasks = [
        Task(title="Medication", duration_minutes=40, priority="high"),
        Task(title="Training", duration_minutes=30, priority="medium"),
    ]
    owner = Owner(name="Alex", available_minutes=40)
    pet = Pet(name="Oliver", species="cat")
    planner = SchedulePlanner(owner=owner, pet=pet)

    planner.build_daily_plan(tasks)
    explanation = planner.explain_plan()

    assert "Medication" in explanation
    assert "Training" in explanation
    assert "Skipped lower-priority tasks" in explanation


def test_invalid_task_raises_value_error():
    with pytest.raises(ValueError):
        Task(title="Bad task", duration_minutes=0, priority="high")

    with pytest.raises(ValueError):
        Task(title="Bad priority", duration_minutes=10, priority="urgent")


def test_owner_negative_available_minutes_raises():
    with pytest.raises(ValueError):
        Owner(name="Sam", available_minutes=-10)


def test_tasks_are_sorted_by_preferred_time_and_conflicts_are_detected():
    tasks = [
        Task(title="Morning walk", duration_minutes=30, priority="high", preferred_time="08:00"),
        Task(title="Medication", duration_minutes=15, priority="high", preferred_time="08:15"),
        Task(title="Evening play", duration_minutes=20, priority="medium", preferred_time="18:00"),
    ]
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog")
    planner = SchedulePlanner(owner=owner, pet=pet, start_time="08:00")

    schedule = planner.build_daily_plan(tasks)

    assert [item.task.title for item in schedule] == ["Morning walk", "Evening play"]
    assert any(task.title == "Medication" for task in planner.skipped_tasks)


def test_pending_tasks_for_the_current_pet_are_selected_and_recurring_tasks_are_kept():
    tasks = [
        Task(title="Feed Mochi", duration_minutes=10, priority="high", pet_name="Mochi", status="pending"),
        Task(title="Feed Luna", duration_minutes=10, priority="high", pet_name="Luna", status="pending"),
        Task(title="Brush coat", duration_minutes=20, priority="medium", pet_name="Mochi", status="done"),
        Task(title="Water refill", duration_minutes=5, priority="medium", pet_name="Mochi", is_recurring=True),
    ]
    owner = Owner(name="Jordan", available_minutes=40)
    pet = Pet(name="Mochi", species="dog")
    planner = SchedulePlanner(owner=owner, pet=pet, start_time="08:00")

    schedule = planner.build_daily_plan(tasks)

    assert [item.task.title for item in schedule] == ["Feed Mochi", "Water refill"]
    assert all(item.task.pet_name in (None, "Mochi") for item in schedule)
