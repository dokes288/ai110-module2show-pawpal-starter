from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def test_sort_by_time_orders_tasks_by_time_value() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="Late task", scheduled_time=time(18, 0)),
        Task(title="Early task", scheduled_time=time(8, 0)),
        Task(title="Unscheduled task", scheduled_time=None),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [task.title for task in ordered] == ["Early task", "Late task", "Unscheduled task"]


def test_filter_tasks_supports_status_and_pet_name_filters() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="Rex morning walk", completed=False),
        Task(title="Luna evening play", completed=False),
        Task(title="Rex feeding", completed=True),
    ]

    filtered = scheduler.filter_tasks(tasks, completed=False, pet_name="Rex")

    assert [task.title for task in filtered] == ["Rex morning walk"]


def test_completed_daily_task_creates_next_occurrence() -> None:
    owner = Owner(name="Nze")
    pet = Pet(name="Rex", species="Dog")
    owner.add_pet(pet)

    task = Task(title="Morning feed", scheduled_time=time(8, 0), frequency="daily")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.complete_task(task, plan_date=date(2026, 7, 12))

    pending_tasks = pet.get_pending_tasks()
    assert len(pending_tasks) == 1
    assert pending_tasks[0].title == "Morning feed"
    assert pending_tasks[0].completed is False
    assert pending_tasks[0].frequency == "daily"
    assert pending_tasks[0].due_date == date(2026, 7, 13)


def test_find_conflicts_detects_same_time_tasks() -> None:
    owner = Owner(name="Nze")
    rex = Pet(name="Rex", species="Dog")
    luna = Pet(name="Luna", species="Cat")
    owner.add_pet(rex)
    owner.add_pet(luna)

    rex.add_task(Task(title="Morning walk", scheduled_time=time(8, 0)))
    rex.add_task(Task(title="Check collar", scheduled_time=time(8, 0)))
    luna.add_task(Task(title="Playtime", scheduled_time=time(8, 0)))

    scheduler = Scheduler(owner)
    conflicts = scheduler.find_conflicts()

    assert len(conflicts) == 3
    assert any(conflict[0].title == "Morning walk" and conflict[1].title == "Check collar" for conflict in conflicts)
    assert any(conflict[0].title == "Morning walk" and conflict[1].title == "Playtime" for conflict in conflicts)


def test_get_conflict_warning_returns_readable_message() -> None:
    owner = Owner(name="Nze")
    rex = Pet(name="Rex", species="Dog")
    owner.add_pet(rex)

    rex.add_task(Task(title="Morning walk", scheduled_time=time(8, 0)))
    rex.add_task(Task(title="Check collar", scheduled_time=time(8, 0)))

    scheduler = Scheduler(owner)
    warning = scheduler.get_conflict_warning()

    assert warning is not None
    assert "Warning: scheduling conflict detected." in warning
    assert "Morning walk" in warning
    assert "Check collar" in warning
