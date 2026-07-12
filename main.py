"""Small demo script for PawPal+.

Creates an owner with two pets, gives each pet a few tasks at different
times, builds today's plan, and prints it to the terminal.

Run with:  python main.py
"""
from datetime import date, time

from pawpal_system import Owner, Pet, Task, Scheduler


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
            scheduled_time=time(18, 0),
        )
    )
    rex.add_task(
        Task(
            title="Feeding",
            scheduled_time=time(8, 0),
        )
    )
    luna.add_task(
        Task(
            title="Evening playtime",
            scheduled_time=time(17, 30),
        )
    )
    rex.add_task(
        Task(
            title="Morning walk",
            scheduled_time=time(7, 0),
        )
    )
    rex.add_task(
        Task(
            title="Rex medication",
            scheduled_time=time(9, 0),
            completed=True,
        )
    )
    rex.add_task(
        Task(
            title="Water refill",
            scheduled_time=time(10, 0),
            frequency="daily",
        )
    )
    rex.add_task(
        Task(
            title="Brush teeth",
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
    for task in scheduler.sort_by_time(scheduler.get_pending_tasks()):
        time_text = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "unscheduled"
        print(f"- {task.title} ({time_text})")

    print("\nRex tasks:")
    for task in scheduler.filter_tasks(scheduler.get_pending_tasks(), pet_name="Rex"):
        print(f"- {task.title}")

    print("\nCompleted tasks:")
    for task in scheduler.filter_tasks(scheduler.get_all_tasks(), completed=True):
        print(f"- {task.title}")

    warning = scheduler.get_conflict_warning()
    if warning:
        print("\n" + warning)


if __name__ == "__main__":
    main()
