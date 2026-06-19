---
description: Strict enforcement rules for implementation plan task execution and tracking
globs:
  - docs/04-implementation-plan/implementation-plan.html
---

# STRICT RULES — Implementation Plan Enforcement

These rules are MANDATORY and must be followed WITHOUT EXCEPTION whenever `docs/implementation-plan.html` is referenced, read, or involved in any task.

---

## Rule 1: Pre-Implementation Dependency Check (BLOCKING)

**Before implementing ANY task from the implementation plan, you MUST:**

1. Read `docs/04-implementation-plan/implementation-plan.html`
2. **Read `docs/02-high-leve-architecure/high-level-architecture.html`** — Cross-check folder structures, naming, data flow, and constants against the architecture. See `.gemini/rules/architecture-backward-check.md` for full details.
3. Identify the current phase and verify that ALL prerequisite tasks from previous phases are completed.

**If ANY dependency is NOT ready:**

- **STOP immediately**
- **Tell the user:** "We're not ready. We need: <clear summary of what's lacking, which plan provides it, and which specific tasks must be completed first>"
- **Do NOT proceed with implementation until the user acknowledges**

### Dependency Chain Reference:

- **Plan 01 (Infrastructure)** → No upstream dependencies. Can always start.
- **Plan 02 (Backend)** → Requires Plan 01 shared types, DB schema, Redis config to be Done.
- **Plan 03 (Frontend)** → Requires Plan 01 shared types + WebSocket event maps to be Done. Requires Plan 02 event bus behavior documentation.
- **Plan 04 (Integration)** → Requires Plan 01 Docker config. Requires Plan 02 + 03 to have core functionality Done for integration/E2E tests.

---

## Rule 2: Post-Implementation Status Update (MANDATORY — ATOMIC)

**After successfully implementing ANY task, you MUST update BOTH files. These updates are ATOMIC — they MUST happen in the SAME tool call using `multi_replace_string_in_file`. You are FORBIDDEN from updating the plan HTML in one call and the dashboard in a separate call. If you cannot fit both in one call, you MUST do the dashboard FIRST (since that's what was skipped before).**

### HARD CONSTRAINT: Use `multi_replace_string_in_file` with replacements array containing:

1. Plan HTML badge update + log link
2. Dashboard task badge update
3. Dashboard progress bar + count update
4. Dashboard summary stat update (Completed count)
5. Dashboard changelog entry

**ALL FIVE in ONE call. No exceptions. No "I'll do the dashboard next." SAME CALL.**

### Step A — Update the specific plan's HTML file:

- Find the task in the plan's HTML (e.g., `docs/04-implementation-plan/02-backend/index.html`)
- Change its status badge from:
  ```html
  <span class="badge badge-not-started">Not Started</span>
  ```
  to:
  ```html
  <span class="badge badge-done">Done</span>
  ```
- If the task is partially done / work in progress, use:
  ```html
  <span class="badge badge-in-progress">In Progress</span>
  ```

### Step B — Update the tracking dashboard (SAME CALL AS STEP A):

- Open `docs/04-implementation-plan/00-tracking-dashboard/index.html`
- Find the same task in the "All Tasks" tab and update its badge identically
- Update the plan card's progress bar width percentage and count text (e.g., "1 / 18 complete" → "2 / 18 complete")
- Update the summary stats at the top (Completed count, In Progress count)

### Step C — MANDATORY VERIFICATION READ-BACK:

**After the multi_replace call, you MUST immediately read BOTH files back to verify:**

1. `grep_search` for the task name in the dashboard → confirm badge shows "Done"
2. `grep_search` for the progress count in the dashboard → confirm numbers are correct
3. If ANYTHING is wrong, fix it immediately before proceeding to the next task

**A task is NOT DONE until the verification read-back passes.**

### Step D — Verify consistency:

- The status in the plan file and the dashboard MUST match exactly
- Progress percentages must be mathematically correct (completed / total × 100)
- Completed stat at the top MUST equal the count of "badge-done" entries for that plan

---

## Rule 3: Implementation Log Creation (MANDATORY)

**After successfully implementing ANY task, you MUST create an implementation log file BEFORE marking the task as Done.**

### Step A — Create the log file:

- Location: `docs/04-implementation-plan/05-implementation-logs/{plan}/`
  - `{plan}` = `01-infrastructure`, `02-backend`, `03-frontend`, or `04-integration`
- Filename convention: `{group-number}-{task-number}-{short-slug}.md`
  - Example: `1-01-room-creation.md`, `2-03-state-persistence.md`
- Use the template at `docs/04-implementation-plan/05-implementation-logs/_TEMPLATE.md`
- Fill ALL sections. For "Pseudo Code Snippets", write key logic as pseudocode — NOT full code dumps.
- The "Blockers & Resolutions" section may say "None" if implementation was smooth.

### Step B — Add log link to the plan HTML:

- In the plan's HTML file, find the task's `<div class="task-detail">` section
- Append a log link at the end of the task-detail div:
  ```html
  <a class="impl-log-link" href="../../05-implementation-logs/{plan}/{filename}.md"
    >📋 Implementation Log</a
  >
  ```
- This link MUST be added as part of the same update that changes the badge to Done

### Step C — Verify log completeness:

- The log file MUST exist on disk before the task badge is changed to Done
- The log MUST have all template sections filled (Summary, Files Changed, Key Decisions at minimum)
- The Backlink section MUST correctly reference the plan and task

### Ordering:

1. Implement the code (Rule 1 dependencies already verified)
2. Create the implementation log file (Rule 3 Step A)
3. **SINGLE `multi_replace_string_in_file` CALL** containing ALL of these:
   - Plan HTML: badge → Done + add log link (Rule 2 Step A + Rule 3 Step B)
   - Dashboard: task badge → Done (Rule 2 Step B)
   - Dashboard: progress bar width + count text updated
   - Dashboard: summary stats (Completed count) updated
   - Dashboard: changelog entry added
4. **VERIFICATION READ-BACK** (Rule 2 Step C): grep both files to confirm updates landed

**If step 3 is split across multiple calls, that is a RULE VIOLATION.**

---

## Enforcement

- These rules apply to ALL agents, sub-agents, and tool invocations touching `docs/04-implementation-plan/`
- There are NO exceptions to Rule 1 (dependency check) — even if the user says "just do it"
- There are NO exceptions to Rule 2 (status update) — forgetting to update tracking is a violation
- There are NO exceptions to Rule 3 (implementation log) — a task is NOT Done without its log
- If you are unsure about a dependency status, READ the files first — never assume
