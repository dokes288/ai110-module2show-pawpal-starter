import streamlit as st
from datetime import time

from pawpal import Owner, Pet, SchedulePlanner, Task

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
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Generate schedule")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(name=owner_name or "Owner", available_minutes=available_minutes)
        pet = Pet(name=pet_name or "Pet", species=species)
        planner = SchedulePlanner(owner=owner, pet=pet, start_time=start_time.strftime("%H:%M"))

        task_objects = [
            Task(
                title=task["title"],
                duration_minutes=task["duration_minutes"],
                priority=task["priority"],
                preferred_time=task.get("preferred_time"),
                pet_name=task.get("pet_name"),
                status=task.get("status", "pending"),
                is_recurring=task.get("is_recurring", False),
            )
            for task in st.session_state.tasks
        ]

        schedule = planner.build_daily_plan(task_objects)

        if schedule:
            st.success("Schedule generated successfully.")
            st.markdown("### Daily plan")
            schedule_data = [
                {
                    "Start": item.start_time,
                    "End": item.end_time,
                    "Task": item.task.title,
                    "Duration": f"{item.task.duration_minutes} min",
                    "Priority": item.task.priority,
                    "Reason": item.reason,
                }
                for item in schedule
            ]
            st.table(schedule_data)
            st.markdown("### Plan explanation")
            st.code(planner.explain_plan())
        else:
            st.info("No tasks could be scheduled within the available time.")
            st.markdown(planner.explain_plan())

        if planner.skipped_tasks:
            st.markdown("### Skipped tasks")
            st.write(
                [
                    {"Title": task.title, "Duration": task.duration_minutes, "Priority": task.priority}
                    for task in planner.skipped_tasks
                ]
            )
