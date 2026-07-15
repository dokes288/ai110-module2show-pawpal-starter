# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

- Implement and verify end-to-end scheduler improvements (sorting, filtering, conflict warnings, recurrence), update Streamlit/CLI outputs, and keep UML + README aligned with final code.
- Add one advanced capability beyond baseline requirements and integrate it into both demo paths.

**What did the agent do?**

- Updated `pawpal_system.py` with scheduler methods for sort/filter/conflict/recurrence plus advanced `next_available_slot`.
- Updated `app.py` to use scheduler-driven display, conflict warnings (`st.warning` + `st.table`), and next-slot recommendations.
- Updated `main.py` to demonstrate sorted output, conflict messaging, and next-slot suggestion.
- Expanded `tests/test_pawpal_system.py` to cover core behaviors and the new advanced capability.
- Updated docs/diagram artifacts: `README.md`, `diagrams/pawpal_plus_class_diagram.mmd`, `diagrams/uml_final.mmd`, `diagrams/uml_final.png`.
- Ran verification commands: `python -m pytest`, `python -m pytest --cov`, `python -m py_compile app.py`.

**What did you have to verify or fix manually?**

- Installed missing environment dependencies: `pytest-cov` for coverage and Mermaid rendering dependencies (including Playwright Chromium) for PNG export.
- Reviewed generated UML/docs to ensure class/method names matched the final `Scheduler`-centric implementation.
- Re-ran full tests after major edits to confirm no regressions before acceptance.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | GitHub Copilot Chat (GPT-5.3-Codex), broad prompt | GitHub Copilot Chat (GPT-5.3-Codex), constrained prompt with explicit acceptance criteria |
| **Prompt / task** | "Improve PawPal+ scheduling and update docs." | "Implement `Task.priority` and priority-first scheduling (priority -> time), add tests, run `python -m pytest`, and update README/CLI examples to match actual output." |
| **Response summary** | Produced useful code ideas and partial edits, but some outputs were generic and not always aligned with final file state. | Produced targeted edits in `pawpal_system.py`, `app.py`, `main.py`, tests, and docs; followed with verification commands and iterative fixes. |
| **What was useful** | Good for brainstorming architecture and identifying possible enhancements quickly. | High implementation accuracy, better traceability, stronger test alignment, and fewer missing requirements. |
| **What was flawed** | Ambiguous scope led to drift (placeholder-style docs and occasional mismatch between prose and actual runtime output). | More verbose prompt design overhead; needed clear constraints to avoid over-editing unrelated sections. |
| **Final decision** | Not selected for final delivery workflow. | Selected as primary workflow for final implementation and validation. |

**Which approach did you use in your final implementation and why?**

I used **Option B** for final implementation. The constrained prompt with explicit acceptance criteria (required files, expected behavior, and verification commands) produced more reliable code changes, cleaner test-driven iteration, and documentation that stayed consistent with real CLI/UI outputs.

---

### Second comparison: Claude vs. Copilot (same tasks, different tools)

The table above compares two *prompts* to the same tool. This second table compares two *tools* — GitHub Copilot (GPT-5.3-Codex) and Claude — across the tasks where both worked on the same code. Unlike the prompt-vs-prompt table, the Claude-side cells below are grounded in verifiable events from the working transcript (specific bugs caught, tests run, corrections made).

| | Copilot (GPT-5.3-Codex) | Claude |
|-|--------------------------|--------|
| **Role in the project** | Primary implementer: built the scheduler enhancements, persistence, priority scheduling, and the first drafts of the docs. | Reviewer / verifier / fixer: audited Copilot's output against the actual code and behavior, then corrected discrepancies. |
| **What was useful** | Fast, broad implementation — produced working features (persistence, `next_available_slot`, priority sorting, `tabulate` formatting) and solid first-draft docs with correct structure. Most of its factual claims checked out on verification. | Caught real defects Copilot's output missed and verified every claim by *running* the code, not just reading it: e.g. a `find_conflicts` ripple bug, an uncaught `AttributeError` in `load_from_json`, missing priority validation (typos sorting below `low`), a granularity mismatch between `next_available_slot` and `find_free_gaps`, and stale/duplicated CLI output in the README. |
| **What was flawed** | Several claims drifted from the real code: a `requirements.txt` that didn't exist, CLI output examples that predated the current `main.py`, an "Agent Workflow" section listing zero actual corrections, and an over-tidy narrative that read smoother than events. | Slower and more conservative; asks more questions and flags scope limits rather than pushing ahead. Not immune to its own errors — e.g. an initial "both rescheduling approaches are identical" claim that its own exhaustive test then disproved (22/60 cases differed), which was corrected before delivery. |
| **Final decision** | Kept as the primary implementation — its code was largely sound and its design choices (e.g. `Scheduler`-centric persistence, separate `prioritize_tasks`) were often better than the reviewer's earlier drafts. | Kept as the verification/correction layer. Every Copilot deliverable was run and checked; discrepancies were fixed and regression-tested (test suite grew from 13 to 21 passing across these sessions). |

**Summary of the Claude-vs-Copilot comparison:** the two tools were complementary rather than competing. Copilot was the stronger *producer* — faster, broader, and correct more often than not — and its architecture decisions were frequently kept over the reviewer's own earlier versions. Claude was the stronger *verifier* — its value was almost entirely in catching the minority of claims and behaviors that were wrong (a non-existent `requirements.txt`, stale CLI output, an uncaught exception path, missing input validation) by executing the code rather than trusting it. The decisive, repeated lesson across both tools: running the code caught essentially every real defect that reading it did not, and that discipline had to be applied to *both* tools' output — including catching one of the reviewer's own overstated claims. Neither tool alone would have produced the final result: Copilot's speed plus Claude's verification is what did.
