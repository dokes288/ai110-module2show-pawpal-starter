# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
Initial UML Design — Summary

Four main classes:

-Owner: Profile and availability constraints
-Pet: Pet details and metadata
-Task: Care activity with flexible scheduling attributes (priority, duration, timing windows, recurrence)
-SchedulePlanner: Builds daily schedule by selecting and ordering tasks based on owner/pet constraints
SchedulePlanner uses Owner and Pet to constrain task selection, then produces a ranked schedule and explanation. Data classes represent entities; SchedulePlanner implements the scheduling logic.

- What classes did you include, and what responsibilities did you assign to each?

Classes and Responsibilities:

Owner

Responsibilities: Store owner profile (name, available minutes, preferred hours, outdoor preference). Validate owner configuration.
Pet

Responsibilities: Store pet information (name, species, breed, age, notes). Update pet details.
Task

Responsibilities: Represent a care activity with all scheduling metadata (title, duration, priority, category, timing constraints, recurrence). Determine priority value for sorting, check if task applies on a given date, and identify outdoor activities.
SchedulePlanner

Responsibilities: Orchestrate scheduling by taking Owner and Pet constraints, building a daily plan from a task list, tracking scheduled vs. skipped tasks, and explaining the plan logic to the user.
Responsibility Division:

Data classes (Owner, Pet, Task) encapsulate domain entities and basic query methods.
SchedulePlanner implements the core algorithm: constraint enforcement, task selection, ordering, and reasoning.

**b. Design changes**

- Did your design change during implementation?

Yes.

- If yes, describe at least one change and why you made it.

1. Owner, Pet, and Task are now @dataclass(frozen=True), matching
   pawpal.py's proven pattern. Their update_*() stubs now return a NEW
   instance (via dataclasses.replace) rather than mutate in place --
   the only way to "update" a frozen dataclass. They currently raise
   NotImplementedError since no field-editing UI/logic exists yet; wire
   them up with dataclasses.replace(self, **changes) when it does.

2. Task and Owner validate via __post_init__ (like pawpal.py), and ALSO
   expose an explicit validate() method that __post_init__ calls --
   this keeps the UML's explicit validate() method meaningful while
   still validating automatically at construction time.

3. PRIORITY_RANK is a module-level table (ported from pawpal.py) backing
   Task.get_priority_value() -- previously that method had nothing to
   compute from.

4. Scheduled/skipped entries use TypedDict (ScheduledEntry, SkippedEntry)
   instead of a 5th ScheduledTask class or bare dicts -- keeps the class
   count at 4 while still giving typed field names.

5. Owner.blocked_periods is restored (dropped somewhere during UML
   iteration, but present in an earlier working version of this
   project) so a workday can be carved out of the middle of the day.

6. Two "dual source of truth" bugs are resolved by deletion, not by
   picking a winner:
   - SchedulePlanner no longer takes its own start_time -- the day's
     start/end come from Owner.preferred_start_hour/preferred_end_hour
     only.
   - Owner no longer has a separate available_minutes -- available time
     is derived from preferred_start_hour/preferred_end_hour minus
     blocked_periods, so there's one number, not two that can disagree.

7. Task.is_outdoor() is derived from category, and
   Owner.prefer_outdoor_morning is now actually wired into scheduling:
   outdoor tasks get a placement boost so they land earlier in the
   (time-ordered) free windows when the owner has that preference set.

8. build_daily_plan() now takes plan_date and calls task.applies_on(),
   closing the previously-missing recurrence pipeline. It also calls
   owner.validate() up front (Cursor's suggestion).

NOT changed, on purpose -- a deliberate call, not an oversight:
  Owner and Pet still don't reference each other directly (no
  `pet: Pet` field on Owner), even though both external reviews
  suggested adding one. Only SchedulePlanner holds both. Adding a
  second reference on Owner would recreate the exact "two places can
  disagree" problem just fixed in #6 above -- SchedulePlanner's pet and
  Owner's pet could drift apart. If you want Owner to formally "own" a
  Pet outside of a SchedulePlanner context, that's worth a real decision
  (e.g. Owner holds the canonical Pet and SchedulePlanner reads
  owner.pet instead of taking its own), not a bolt-on field.

  Three Core Actions: -

1. Set up owner and pet profile
Enter who they are and who they're caring for — owner name, available time today, preferred hours, and pet details (name, species, breed, age). This gives the scheduler the constraints it needs.

2. Manage care tasks
Add, edit, and remove tasks such as walks, feeding, meds, enrichment, and grooming. Each task should include at least duration and priority, plus optional details like category, recurrence, and preferred time of day.

3. Generate and review today's plan
Produce a daily schedule from their tasks and constraints, then view it as a clear timeline — what happens when, what was skipped, and why the app chose that plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- One tradeoff in the scheduler is that it currently detects conflicts by checking for exact matching scheduled times, rather than full overlap across task durations.
- This is reasonable for the current prototype because the app is focused on lightweight, easy-to-understand scheduling logic for a pet owner. Exact-time matching is simpler to implement, easier to explain, and avoids overcomplicating the UI with duration-based conflict rules that would require more advanced planning logic.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
