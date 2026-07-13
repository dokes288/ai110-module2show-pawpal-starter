import streamlit as st
from datetime import datetime, time
from typing import Optional

from pawpal_system import Owner, Pet, Scheduler, Task


def build_scheduler_view(task_inputs: list[dict]) -> tuple[list[dict], list[dict], Optional[str]]:
    """Convert UI task entries into scheduler-friendly tasks and return sorted rows, conflicts, and warnings."""
    owner = Owner(name="Owner")
    pet = Pet(name="Pet", species="other")
    owner.add_pet(pet)

    scheduler_tasks: list[Task] = []
    for task in task_inputs:
        preferred_time = task.get("preferred_time")
        scheduled_time = None
        if preferred_time:
            try:
                scheduled_time = datetime.strptime(preferred_time, "%H:%M").time()
            except ValueError:
                scheduled_time = None

        scheduler_task = Task(
            title=task["title"],
            description=task.get("description", ""),
            scheduled_time=scheduled_time,
            frequency="daily" if task.get("is_recurring") else "once",
            completed=task.get("status") == "done",
        )
        scheduler_tasks.append(scheduler_task)
        pet.add_task(scheduler_task)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(scheduler_tasks)
    display_rows = [
        {
            "Title": task.title,
            "Time": task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "Unscheduled",
            "Frequency": task.frequency,
            "Status": "done" if task.completed else "pending",
        }
        for task in sorted_tasks
    ]

    conflict_rows: list[dict] = []
    for left, right in scheduler.find_conflicts(sorted_tasks):
        conflict_rows.append(
            {
                "Task": left.title,
                "Time": left.scheduled_time.strftime("%H:%M") if left.scheduled_time else "Unscheduled",
                "Conflicts with": right.title,
            }
        )

    warning = None
    if conflict_rows:
        warning = (
            "Some tasks overlap in time. This may make it harder to care for your pet smoothly. "
            "Try moving one task to a different time."
        )

    return display_rows, conflict_rows, warning


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps a pet owner plan daily care tasks using task priority, duration, and available time.
Use the inputs below to add tasks, set availability, and generate a daily schedule.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet based on constraints like time, priority, and available minutes.
"""
    )

with st.expander("Implementation notes", expanded=False):
    st.markdown(
        """
The scheduler selects tasks by priority first, then by shorter duration. It stops once the owner's
available minutes are exhausted and reports skipped tasks.
"""
    )

st.divider()

st.subheader("Owner and pet details")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_minutes = st.slider("Available minutes today", min_value=0, max_value=720, value=480)
start_time = st.time_input("Schedule start time", value=time(hour=8, minute=0))

st.divider()

st.subheader("Tasks")
st.caption("Add tasks with duration and priority. The scheduler will choose the highest-priority tasks that fit.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns([4, 2, 2])
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns([2, 2, 2])
with col4:
    preferred_time = st.text_input("Preferred time (HH:MM)", value="")
with col5:
    task_pet_name = st.text_input("Pet name (optional)", value="")
with col6:
    task_status = st.selectbox("Status", ["pending", "done"], index=0)

recurring_task = st.checkbox("Recurring task")

if st.button("Add task"):
    if task_title.strip() == "":
        st.error("Enter a task title before adding a task.")
    else:
        st.session_state.tasks.append(
            {
                "title": task_title.strip(),
                "duration_minutes": int(duration),
                "priority": priority,
                "preferred_time": preferred_time.strip() or None,
                "pet_name": task_pet_name.strip() or None,
                "status": task_status,
                "is_recurring": recurring_task,
            }
        )
        st.success(f"Added task: {task_title.strip()}")

if st.session_state.tasks:
    display_rows, conflict_rows, warning = build_scheduler_view(st.session_state.tasks)
    st.write("Current tasks (sorted by time):")
    st.table(display_rows)
    if warning:
        st.warning(warning)
        st.caption("Conflicting items")
        st.table(conflict_rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Generate schedule")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        display_rows, conflict_rows, warning = build_scheduler_view(st.session_state.tasks)
        st.success("Schedule generated successfully.")
        st.markdown("### Sorted tasks")
        st.table(display_rows)
        if warning:
            st.warning(warning)
            st.caption("Conflicting items")
            st.table(conflict_rows)
