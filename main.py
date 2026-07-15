"""Small demo script for PawPal+.

Creates an owner with two pets, gives each pet a few tasks at different
times, builds today's plan, and prints it to the terminal.

Run with:  python main.py
"""
from datetime import date, time
from tabulate import tabulate

from pawpal_system import Owner, Pet, Task, Scheduler


def priority_badge(priority: str) -> str:
    badges = {"high": "🔴 high", "medium": "🟠 medium", "low": "🟢 low"}
    return badges.get(priority.lower(), f"⚪ {priority}")


def status_badge(completed: bool) -> str:
    return "✅ done" if completed else "🟡 pending"


def main() -> None:
    # --- Owner -----------------------------------------------------------
    owner = Owner(name="Nze")

    # --- Pets --------------------------------------------------------------
    rex = Pet(name="Rex", species="Dog")
    luna = Pet(name="Luna", species="Cat")

    owner.add_pet(rex)
    owner.add_pet(luna)

    # --- Tasks (added out of order to show the new sorting logic) --------
    luna.add_task(
        Task(
            title="Litter box cleaning",
            priority="medium",
            scheduled_time=time(18, 0),
        )
    )
    rex.add_task(
        Task(
            title="Feeding",
            priority="high",
            scheduled_time=time(8, 0),
        )
    )
    luna.add_task(
        Task(
            title="Evening playtime",
            priority="low",
            scheduled_time=time(17, 30),
        )
    )
    rex.add_task(
        Task(
            title="Morning walk",
            priority="high",
            scheduled_time=time(7, 0),
        )
    )
    rex.add_task(
        Task(
            title="Rex medication",
            priority="high",
            scheduled_time=time(9, 0),
            completed=True,
        )
    )
    rex.add_task(
        Task(
            title="Water refill",
            priority="medium",
            scheduled_time=time(10, 0),
            frequency="daily",
        )
    )
    rex.add_task(
        Task(
            title="Brush teeth",
            priority="medium",
            scheduled_time=time(8, 0),
        )
    )

    # --- Build and print today's plan --------------------------------------
    scheduler = Scheduler(owner)
    recurring_task = next(task for task in rex.tasks if task.title == "Water refill")
    scheduler.complete_task(recurring_task, date.today())

    print("=" * 40)
    print("Today's Schedule")
    print("=" * 40)
    print(scheduler.summarize())

    print("\nSorted pending tasks:")
    sorted_rows = []
    for task in scheduler.sort_by_time(scheduler.get_pending_tasks()):
        time_text = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "unscheduled"
        sorted_rows.append([task.title, time_text, priority_badge(task.priority), status_badge(task.completed)])
    print(tabulate(sorted_rows, headers=["Task", "Time", "Priority", "Status"], tablefmt="grid"))

    print("\nPriority-based pending tasks:")
    priority_rows = []
    for task in scheduler.prioritize_tasks(scheduler.get_pending_tasks()):
        time_text = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "unscheduled"
        priority_rows.append([task.title, priority_badge(task.priority), time_text])
    print(tabulate(priority_rows, headers=["Task", "Priority", "Time"], tablefmt="fancy_grid"))

    print("\nRex tasks:")
    rex_rows = [[task.title, priority_badge(task.priority)] for task in scheduler.filter_tasks(scheduler.get_pending_tasks(), pet_name="Rex")]
    print(tabulate(rex_rows, headers=["Task", "Priority"], tablefmt="simple"))

    print("\nCompleted tasks:")
    completed_rows = []
    for task in scheduler.filter_tasks(scheduler.get_all_tasks(), completed=True):
        completed_rows.append([task.title, priority_badge(task.priority), status_badge(task.completed)])
    print(tabulate(completed_rows, headers=["Task", "Priority", "Status"], tablefmt="github"))

    warning = scheduler.get_conflict_warning()
    if warning:
        print("\n" + warning)

    suggested_slot = scheduler.next_available_slot(duration_minutes=30)
    if suggested_slot:
        print(f"\nNext available 30-minute slot: {suggested_slot.strftime('%H:%M')}")
    else:
        print("\nNo 30-minute slot is available in the default planning window.")

    day_load = scheduler.analyze_day_load()
    print("\nDay load analysis:")
    print(f"- Booked: {day_load['load_percent']:.0f}% "
          f"({day_load['committed_minutes']} of {day_load['total_minutes']} planning minutes)")
    print(f"- Free time: {day_load['free_minutes']} minutes across the day")
    largest = day_load["largest_free_gap"]
    if largest:
        print(f"- Largest open window: {largest[0].strftime('%H:%M')}–{largest[1].strftime('%H:%M')}")


if __name__ == "__main__":
    main()
