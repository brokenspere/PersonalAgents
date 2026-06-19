---
description: When requirements change, trace back through all plans to verify correctness and log changes
globs:
  - docs/04-implementation-plan/implementation-plan.html
  - docs/01-raw-requirement/REQUIREMENT.md
---

# STRICT RULES — Requirement Change Traceability

These rules are MANDATORY whenever a requirement is added, modified, or removed from the implementation plan or PRD.

---

## Rule 1: Trace Back on Requirement Change (BLOCKING)

**When ANY requirement or task changes (added, modified, removed, or scope changed), you MUST:**

1. Identify all phases that are affected by the change
2. Read `docs/04-implementation-plan/implementation-plan.html`
3. Check if the change impacts any **already-completed tasks** — if yes, flag them for re-validation
4. Check if the change impacts any **downstream phases** that depend on the changed component
5. Update `docs/04-implementation-plan/implementation-plan.html` to reflect the new state.

**If ANY inconsistency is found:**
- **STOP and tell the user:** "Requirement change detected. The following items need re-validation: <list of affected tasks/plans>"
- **Update all affected files** to reflect the corrected state
- **Do NOT mark something as Done if its upstream requirement changed**

### Trace-Back Checklist:
- [ ] Plan 01 shared types still match what Plan 02/03 expect?
- [ ] Dashboard progress counts still mathematically correct?
- [ ] Contract dependency matrix still accurate?
- [ ] No orphaned tasks (tasks whose parent requirement no longer exists)?
- [ ] No new gaps (new requirement without a corresponding task)?

---

## Rule 2: Changelog Entry (MANDATORY)

**After ANY change to an implementation plan file, you MUST append an entry to the changelog section inside the tracking dashboard.**

### Changelog Location:
- File: `docs/04-implementation-plan/00-tracking-dashboard/index.html`
- Section: Look for the `<!-- CHANGELOG -->` marker. If it doesn't exist, create it at the bottom of the content div.

### Changelog Entry Format:
```html
<tr>
  <td>YYYY-MM-DD</td>
  <td><span class="badge badge-[type]">[Type]</span></td>
  <td>[Plan affected]</td>
  <td>[Brief description of what changed]</td>
</tr>
```

### Change Types:
- `badge-done` → **Added** — new task or requirement added
- `badge-in-progress` → **Modified** — existing task scope or description changed
- `badge-not-started` → **Removed** — task or requirement removed
- `badge-done` → **Completed** — task marked as done
- `badge-in-progress` → **Status Change** — task status updated

---

## Rule 3: Dashboard Must Have Changelog Section

**If the tracking dashboard does NOT already have a changelog section, you MUST add one** with this structure:

```html
<!-- CHANGELOG -->
<div class="tab-panel" id="tab-changelog">
  <h2 class="section-title">Changelog</h2>
  <table class="task-table">
    <thead>
      <tr><th>Date</th><th>Type</th><th>Plan</th><th>Description</th></tr>
    </thead>
    <tbody>
      <!-- Entries go here, newest first -->
    </tbody>
  </table>
</div>
```

And add a corresponding tab button:
```html
<div class="tab" data-tab="changelog">Changelog</div>
```

---

## Enforcement

- These rules apply to ALL modifications to implementation plan files
- A changelog entry is required even for status-only updates (Rule 2 of implementation-plan.md)
- If multiple changes happen in one session, each distinct change gets its own changelog row
- Never skip the trace-back — even for "small" changes
