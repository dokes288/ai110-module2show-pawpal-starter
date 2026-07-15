from datetime import date, time

from pawpal_system import Owner, Pet, Scheduler, Task


def test_sorting_correctness_returns_tasks_in_chronological_order() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="Late task", scheduled_time=time(18, 0)),
        Task(title="Early task", scheduled_time=time(8, 0)),
        Task(title="Unscheduled task", scheduled_time=None),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [task.title for task in ordered] == ["Early task", "Late task", "Unscheduled task"]


def test_priority_based_scheduling_orders_high_then_time_then_title() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="Medium task", priority="medium", scheduled_time=time(7, 30)),
        Task(title="Low task", priority="low", scheduled_time=time(7, 0)),
        Task(title="High later", priority="high", scheduled_time=time(8, 0)),
        Task(title="High earlier", priority="high", scheduled_time=time(7, 0)),
    ]

    ordered = scheduler.prioritize_tasks(tasks)

    assert [task.title for task in ordered] == ["High earlier", "High later", "Medium task", "Low task"]


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


def test_recurrence_logic_marks_daily_task_complete_and_creates_next_day_task() -> None:
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


def test_weekly_recurrence_preserves_anchor_cadence() -> None:
    owner = Owner(name="Nze")
    pet = Pet(name="Rex", species="Dog")
    owner.add_pet(pet)

    task = Task(
        title="Weekly grooming",
        scheduled_time=time(9, 0),
        frequency="weekly",
        due_date=date(2026, 7, 13),
    )
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.complete_task(task, plan_date=date(2026, 7, 13))

    pending_tasks = pet.get_pending_tasks()
    assert len(pending_tasks) == 1
    assert pending_tasks[0].title == "Weekly grooming"
    assert pending_tasks[0].due_date == date(2026, 7, 20)


def test_weekly_recurrence_skips_past_due_windows_when_completed_late() -> None:
    owner = Owner(name="Nze")
    pet = Pet(name="Rex", species="Dog")
    owner.add_pet(pet)

    task = Task(
        title="Weekly training",
        scheduled_time=time(10, 0),
        frequency="weekly",
        due_date=date(2026, 7, 1),
    )
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.complete_task(task, plan_date=date(2026, 7, 14))

    pending_tasks = pet.get_pending_tasks()
    assert len(pending_tasks) == 1
    assert pending_tasks[0].title == "Weekly training"
    assert pending_tasks[0].due_date == date(2026, 7, 15)


def test_conflict_detection_flags_duplicate_times() -> None:
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


def test_next_available_slot_skips_occupied_buckets() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="Walk", scheduled_time=time(8, 0)),
        Task(title="Feed", scheduled_time=time(8, 15)),
    ]

    slot = scheduler.next_available_slot(
        duration_minutes=15,
        day_start=time(8, 0),
        day_end=time(10, 0),
        tasks=tasks,
    )

    assert slot == time(8, 30)


def test_next_available_slot_requires_consecutive_open_buckets() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="Walk", scheduled_time=time(8, 15)),
    ]

    slot = scheduler.next_available_slot(
        duration_minutes=30,
        day_start=time(8, 0),
        day_end=time(9, 0),
        tasks=tasks,
    )

    assert slot == time(8, 30)


def test_next_available_slot_returns_none_when_day_is_fully_booked() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="Block 1", scheduled_time=time(8, 0)),
        Task(title="Block 2", scheduled_time=time(8, 15)),
        Task(title="Block 3", scheduled_time=time(8, 30)),
        Task(title="Block 4", scheduled_time=time(8, 45)),
    ]

    slot = scheduler.next_available_slot(
        duration_minutes=15,
        day_start=time(8, 0),
        day_end=time(9, 0),
        tasks=tasks,
    )

    assert slot is None


def test_save_and_load_json_round_trip_preserves_owner_pets_and_tasks(tmp_path) -> None:
    owner = Owner(name="Nze")
    rex = Pet(name="Rex", species="Dog", notes="Needs calm mornings")
    rex.add_task(
        Task(
            title="Morning feed",
            description="Dry food",
            priority="high",
            scheduled_time=time(8, 0),
            frequency="daily",
            completed=False,
            due_date=date(2026, 7, 14),
        )
    )
    owner.add_pet(rex)

    scheduler = Scheduler(owner)
    data_file = tmp_path / "data.json"

    scheduler.save_to_json(str(data_file))
    loaded_scheduler = Scheduler.load_from_json(str(data_file))

    assert loaded_scheduler.owner.name == "Nze"
    assert len(loaded_scheduler.owner.pets) == 1
    loaded_pet = loaded_scheduler.owner.pets[0]
    assert loaded_pet.name == "Rex"
    assert loaded_pet.species == "Dog"
    assert loaded_pet.notes == "Needs calm mornings"
    assert len(loaded_pet.tasks) == 1
    loaded_task = loaded_pet.tasks[0]
    assert loaded_task.title == "Morning feed"
    assert loaded_task.description == "Dry food"
    assert loaded_task.priority == "high"
    assert loaded_task.scheduled_time == time(8, 0)
    assert loaded_task.frequency == "daily"
    assert loaded_task.completed is False
    assert loaded_task.due_date == date(2026, 7, 14)


def test_load_from_json_returns_empty_scheduler_when_file_missing(tmp_path) -> None:
    missing_file = tmp_path / "data.json"

    scheduler = Scheduler.load_from_json(str(missing_file))

    assert scheduler.owner.name == "Owner"
    assert scheduler.owner.pets == []


def test_find_free_gaps_reports_open_windows_between_tasks() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="A", scheduled_time=time(8, 0)),
        Task(title="B", scheduled_time=time(9, 0)),
    ]

    gaps = scheduler.find_free_gaps(
        day_start=time(8, 0), day_end=time(10, 0), slot_minutes=30, tasks=tasks
    )

    assert gaps == [(time(8, 30), time(9, 0)), (time(9, 30), time(10, 0))]


def test_find_free_gaps_empty_day_is_one_full_window() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    gaps = scheduler.find_free_gaps(
        day_start=time(8, 0), day_end=time(10, 0), slot_minutes=30, tasks=[]
    )

    assert gaps == [(time(8, 0), time(10, 0))]


def test_analyze_day_load_computes_load_and_largest_gap() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="A", scheduled_time=time(8, 0)),
        Task(title="B", scheduled_time=time(9, 0)),
    ]

    load = scheduler.analyze_day_load(
        day_start=time(8, 0), day_end=time(10, 0), slot_minutes=30, tasks=tasks
    )

    assert load["total_minutes"] == 120
    assert load["committed_minutes"] == 60
    assert load["free_minutes"] == 60
    assert load["load_percent"] == 50.0
    assert load["scheduled_task_count"] == 2
    assert load["largest_free_gap"] in {
        (time(8, 30), time(9, 0)),
        (time(9, 30), time(10, 0)),
    }


def test_analyze_day_load_fully_booked_is_100_percent() -> None:
    owner = Owner(name="Nze")
    scheduler = Scheduler(owner)

    tasks = [
        Task(title="A", scheduled_time=time(8, 0)),
        Task(title="B", scheduled_time=time(8, 30)),
    ]

    load = scheduler.analyze_day_load(
        day_start=time(8, 0), day_end=time(9, 0), slot_minutes=30, tasks=tasks
    )

    assert load["load_percent"] == 100.0
    assert load["free_minutes"] == 0
    assert load["largest_free_gap"] is None


def test_slot_and_gap_methods_agree_at_default_granularity() -> None:
    """Regression guard: next_available_slot() and find_free_gaps() must
    use the same default granularity, so a suggested slot always falls
    within a reported free gap. If someone changes one default without
    the other, this fails loudly.
    """
    owner = Owner(name="Nze")
    rex = Pet(name="Rex", species="Dog")
    owner.add_pet(rex)
    rex.add_task(Task(title="A", scheduled_time=time(8, 0)))
    rex.add_task(Task(title="B", scheduled_time=time(8, 30)))

    scheduler = Scheduler(owner)
    slot = scheduler.next_available_slot(
        duration_minutes=30, day_start=time(8, 0), day_end=time(11, 0)
    )
    gaps = scheduler.find_free_gaps(day_start=time(8, 0), day_end=time(11, 0))

    assert slot is not None
    assert any(start <= slot < end for start, end in gaps)


def test_load_from_json_raises_clean_error_on_malformed_structure(tmp_path) -> None:
    """A syntactically valid JSON file with the wrong shape (e.g. a bare
    list, or an owner that isn't a dict) should raise a clean ValueError,
    not leak a low-level AttributeError/TypeError.
    """
    import pytest

    bad_list = tmp_path / "bad_list.json"
    bad_list.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ValueError):
        Scheduler.load_from_json(str(bad_list))

    bad_owner = tmp_path / "bad_owner.json"
    bad_owner.write_text('{"owner": "not a dict"}', encoding="utf-8")
    with pytest.raises(ValueError):
        Scheduler.load_from_json(str(bad_owner))


def test_task_rejects_invalid_priority() -> None:
    """A typo'd or unsupported priority must raise at construction rather
    than being silently accepted and sorted below 'low'.
    """
    import pytest

    with pytest.raises(ValueError):
        Task(title="Typo priority", priority="urgent")


def test_task_accepts_valid_priorities_case_insensitively() -> None:
    for value in ["low", "Medium", "HIGH"]:
        task = Task(title="ok", priority=value)
        assert task.priority == value  # stored as-given; compared case-insensitively when sorting
