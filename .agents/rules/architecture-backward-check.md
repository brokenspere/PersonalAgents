---
description: MANDATORY backward-check against high-level architecture before any implementation
globs:
  - 'workers/**'
  - 'scheduler/**'
  - 'shared/**'
---

# STRICT RULES — Architecture Backward-Check (BLOCKING)

These rules are MANDATORY before implementing ANY code in `workers/`, `scheduler/`, or `shared/`. They exist because the high-level architecture document is the SINGLE SOURCE OF TRUTH for structural decisions.

---

## Rule 1: Pre-Implementation Architecture Cross-Check (BLOCKING)

**Before writing ANY code, you MUST:**

1. Read `docs/02-high-leve-architecure/high-level-architecture.html` and `docs/03-logic/logic.html`
2. Find the section relevant to what you're implementing (System Overview, Component Logic, Data Flow)
3. Verify your planned implementation matches:
   - **Folder structure** — Architecture prescribes exact directory layouts (e.g., Docker build context usage). Follow them.
   - **Naming conventions** — Component names (Workers) and file paths must match.
   - **Data flow patterns** — Events, Message Broker queues, and the Extraction Payload model must match.
   - **Technology choices** — Use the prescribed libraries (BeautifulSoup, Celery, Redis).
4. If there is ANY discrepancy between the implementation plan task description and the architecture, **STOP and flag it to the user** before proceeding.

---

## Rule 2: Specific Cross-Check Points by Area

### packages/shared/

- Architecture prescribes subdirectories: `types/`, `constants/`, `validators/`
- All TypeScript interfaces, game constants, and validation schemas must be organized per this structure
- Verify exported types match what the architecture's System Overview describes

### apps/server/

- Must use modular structure: `src/modules/{room, game, dice, tile, economy, timer, leaderboard}/`
- Event bus lives at `src/events/`
- Config lives at `src/config/`
- Must match the component responsibilities listed under "Application Layer — Game Server"

### apps/web/

- Must use route structure: `src/app/{player, display, admin}/`
- Hooks at `src/hooks/` (useSocket, useGameState, useTimer)
- Components at `src/components/`
- Must match "Client Layer" responsibilities

### docker/

- Must match infrastructure decisions (Nginx, PM2, Redis config as described)

---

## Rule 3: Formula & Constant Validation

**When implementing game constants or economy formulas:**

1. Cross-check EVERY numeric value against the architecture's Economy Engine section
2. Cross-check timer durations against the Game State Machine section
3. Cross-check game parameters against the Round Progression table
4. If a value in the implementation plan CONFLICTS with the architecture, flag it — do NOT silently pick one

**Known reference values from architecture:**

- Starting budget: 1,000,000 THB
- Starting carbon: 60,000 tCO2e
- Turn time: 60 seconds per player (configurable before game start)
- Turn model: Sequential (one player at a time)
- Timeout behavior: Skip turn (no action occurs)
- Rounds: 5 (2 rolls each = 10 total rotations)
- Max players: 5
- Name max: 10 chars
- Rejoin window: 30 seconds
- START bonus: +150,000
- Greenwash penalty: -40,000/round
- KBANK threshold: carbon < 5,000 → +40,000
- Chance outcomes: +50k/-75k or +120k/-90k
- dMRV: 80% carbon tax discount, greenwash immunity

---

## Rule 4: Conflict Resolution Protocol

If the architecture and the implementation plan task disagree:

1. **STOP implementation**
2. **State the conflict clearly**: "Architecture says X, but implementation plan says Y"
3. **Recommend**: Which source is likely correct based on game logic consistency
4. **Wait for user decision** before proceeding

The architecture is the higher-authority document. Implementation plan tasks are derived from it. If they conflict, the architecture is more likely correct.

---

## Enforcement

- These rules apply to ALL implementation work — no exceptions
- Skipping the backward-check is a VIOLATION even for "obvious" or "simple" tasks
- The cross-check MUST be documented in the implementation log under "Key Decisions" if any architectural alignment was verified
- If you already read the architecture in the current session, you may reference it from memory — but must re-read if unsure
