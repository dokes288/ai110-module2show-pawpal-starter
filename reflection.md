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

The scheduler considers, roughly in order of how "hard" each constraint
is: (1) the owner's available hours minus any blocked periods (e.g. a
9-to-5 workday) — the day's real boundaries; (2) how a task is timed —
pinned to a `fixed_time`, constrained to an `earliest_time`/`latest_time`
window, or left fully flexible; (3) task priority, used to decide who
wins when two things can't both fit; (4) task duration, which decides
how much room a task needs once its priority has earned it a place in
line; (5) recurrence (daily/weekly), so a task isn't even offered on a
day it doesn't apply to; and (6) a soft preference,
`prefer_outdoor_morning`, that nudges outdoor tasks earlier in the day
without ever overriding anything above it.

- How did you decide which constraints mattered most?

I ranked them by what breaks if they're violated. Getting the
available-hours/blocked-periods constraint wrong means telling an owner
to do something during hours they've explicitly said they can't — a
hard failure, so it's enforced before anything else is placed. Priority
comes next, since it's the most direct signal the app has for choosing
which task loses when two can't both fit. Duration isn't really its own
tier — it's priority's partner, deciding how much space a task needs
once priority has already earned it a spot. The outdoor-morning
preference sits last on purpose: a nice-to-have that should only ever
break ties between equally-ranked tasks, never compete with something
structural like an owner's blocked hours.

**b. Tradeoffs**

- One tradeoff in the scheduler is that it currently detects conflicts by checking for exact matching scheduled times, rather than full overlap across task durations.
- This is reasonable for the current prototype because the app is focused on lightweight, easy-to-understand scheduling logic for a pet owner. Exact-time matching is simpler to implement, easier to explain, and avoids overcomplicating the UI with duration-based conflict rules that would require more advanced planning logic.

- A second tradeoff: flexible tasks are placed with a greedy heuristic
  (highest priority first, shortest duration as a tiebreaker) rather
  than a truly optimal interval-scheduling algorithm. An optimal packer
  could occasionally fit one extra low-priority task by rearranging the
  day cleverly, but the result would be much harder to justify in the
  "why was this task skipped" explanation the whole design is built
  around. I chose the version an owner could sanity-check by eye over
  the version that's mathematically optimal but opaque.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI differently in each phase. Early on it was design
brainstorming — going from a scenario description to a UML class
diagram took several rounds of "what should this look like," "compare
this version to that one," and "why is this better or worse," not one
prompt producing a finished design. In the middle it became
implementation: turning class stubs into real scheduling logic, with
the AI writing the code and then actually *running* it to confirm the
behavior, rather than just describing what it should do. Toward the
end it was debugging and refactoring — tracking down a bug where
completing a recurring task silently discarded any record that it had
ever been completed, and reasoning through what else in the codebase
would be affected before making that change.

- What kinds of prompts or questions were most helpful?

Not "build me a scheduler," but comparison and verification prompts:
"compare this diagram to the one you made and say which is better and
why," "does this test file actually test what I think it tests," "run
this and show me the real output." Those forced concrete, checkable
answers instead of confident-sounding descriptions.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

At one point, two separate AI tools (Gemini in VS Code and Cursor)
independently reviewed the same skeleton file and both claimed the
dataclasses were frozen and that this conflicted with update methods
I'd defined. It was a specific, plausible-sounding critique — and it
was wrong. When the actual file was pulled up and read line by line,
none of the classes were frozen at that point, and there were no
conflicting update methods to begin with. Two independent tools
agreeing turned out to be a coincidence of both making the same kind of
guess, not confirmation the claim was true. I only caught it by
checking the real file instead of taking the critique at face value —
which became the standard I held every AI suggestion to afterward: if
it's checkable, check it, no matter how many tools agree on it.

**c. AI Strategy**

- Which AI coding assistant features were most effective for building your scheduler?

Actually executing code and showing real output, not just generating
it. Running the scheduler against constructed scenarios and seeing the
literal printed result — rather than trusting a description of what the
code "should" do — is what caught almost every real bug in this
project, including the recurring-task completion issue above. A close
second was inline diagram rendering during the UML phase: comparing
structural choices (dependency direction, class count, how a completed
task should be represented) was immediate and visual instead of
something I had to mentally simulate from plain text.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

Both Gemini and Cursor separately suggested adding a direct `pet: Pet`
reference onto `Owner`, to make "Owner owns Pet" more explicit in code.
I rejected it. Adding that field would have created a second place
(`Owner.pet`, alongside `SchedulePlanner`'s own pet reference) that
could quietly drift out of sync — the same "two sources of truth"
problem I'd just finished removing elsewhere in the design (a duplicate
start-time field, a duplicate available-minutes number). Keeping the
Owner–Pet relationship living only inside `SchedulePlanner` meant there
was exactly one place that link could go stale, not two.

- How did using separate chat sessions for different phases help you stay organized?

I deliberately didn't let one AI tool both build the system and grade
its own work. Design and implementation happened in one ongoing
session, but the resulting skeleton and code got routed through two
other tools (Gemini, Cursor) specifically for independent review,
rather than asking the same session that wrote the code whether the
code was good. That separation is what surfaced real problems — Cursor
caught a genuine mismatch between the skeleton and the actual reference
test file that the building session had no reason to notice. It's also
what exposed the frozen-dataclass hallucination above: because the
claim came from two *separate* contexts agreeing rather than one,
checking whether they were both right (or both wrong) was something I
actually had to do, instead of something I could quietly assume was
already handled.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested input validation (invalid duration, invalid priority, negative
available minutes all correctly raise errors), the frozen/mutable
behavior of the dataclasses (that a frozen class actually blocks
reassignment, and that mutable containers behave as expected), and the
core scheduling behaviors: priority ordering when time is tight,
blocked periods correctly carving unavailable time out of the day,
fixed-time conflicts resolving in favor of the higher-priority task,
weekly recurrence only appearing on the correct day, and the
outdoor-morning preference actually changing task order rather than
sitting unused. Whenever I changed something — like the recurring-task
completion fix — I re-ran the full set of checks afterward, not just
the one for the new behavior, specifically to catch any side effect the
change might have introduced elsewhere.

These mattered because several real bugs in this project were only
visible at the "actually run it" level, not the "read the code" level
— a scheduling system can look completely reasonable in review and
still produce a wrong plan the moment two real constraints interact in
a way nobody traced through by hand.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident in the core placement logic — fixed-time handling,
blocked-period carve-outs, priority ordering, and recurrence filtering
— since each was tested against specific scenarios and re-verified
after later changes touched nearby code. I'm less confident under real
scale and messiness: many pets with many overlapping fixed-time tasks
all competing for the same day, or whether the greedy placement
algorithm ever leaves something unscheduled that a smarter (but harder
to explain) algorithm could have fit. With more time I'd specifically
test: two fixed-time tasks scheduled back-to-back with zero gap, a
blocked period that exactly bisects a task's allowed window, and a
weekly recurring task whose next occurrence rolls across a month or
year boundary.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

How much the design improved through direct comparison. Putting my own
class diagram next to independently-generated alternatives and being
forced to articulate exactly why one detail was better than another —
dependency direction, how a completed task should be represented, how
many classes the design was allowed to have — produced a noticeably
cleaner result than my first draft would have reached on its own.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Two things. First, how recurring tasks handle completion — right now,
marking a daily task done only leaves a trace if the code is careful
about it, rather than the data model making that impossible to lose by
design. Second, conflict detection currently only catches tasks
scheduled at the exact same time, not tasks whose durations overlap
without sharing a start time — a deliberate simplification for this
iteration (see Section 2b), but one I'd remove given another pass.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

An AI tool sounding confident — or two AI tools agreeing with each
other — isn't evidence of correctness. The only thing that reliably
caught real bugs in this project was actually running the code and
checking the output against what should have happened, and that
discipline mattered exactly as much with AI-generated suggestions as it
would have with a first draft I'd written myself.
