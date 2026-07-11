# Resume protocol

The repository, not conversation memory, is the authority for long-running work.

## Entry sequence

1. Read `AGENTS.md`, `CONTEXT.md`, and `WORKSTATE.md`.
2. Read only the active Wayfinder map and current ticket named by `WORKSTATE.md`.
3. Inspect `git status --short --branch` and recent scoped commits before editing.
4. If the current ticket is claimed and `WORKSTATE.md` identifies it, resume that ticket from its checkpoint.
5. Otherwise claim the first open, unblocked, unclaimed frontier ticket before work.

## Checkpoints

At every meaningful boundary and before a risky or long-running action:

- update `WORKSTATE.md` with the current ticket, last completed action, exact next action, verification state, and important paths;
- append executed checks to `TESTLOG.md` when it exists;
- leave the worktree coherent;
- prefer a small verified commit over a large uncommitted batch.

If a command or computation can be resumed, store its input manifest, output location, and checkpoint identifier. Never rely on terminal scrollback as the only record.

## Interruption and quota exhaustion

When usage or a process ends unexpectedly, the next scheduled run:

- preserves existing uncommitted changes;
- resumes the named claimed ticket instead of claiming another;
- reruns the smallest relevant verification before trusting partial output;
- records repeated external failures rather than deleting evidence;
- exits cleanly with an updated checkpoint if capacity is still unavailable.

Recurring wakeups cannot bypass a hard quota. Their purpose is to retry after capacity returns.

If `WORKSTATE.md` says `Status: BLOCKED`, a recurring wakeup exits without
project mutation. Only new user input or the named external-state change resumes
the goal; that resumed run starts a fresh blocked audit.

## Concurrency

- Treat the `Active run lease` in `WORKSTATE.md` as authoritative. A scheduled
  run exits without mutation while the lease is fresh, even when the lease and
  ticket are owned by the same agent name. A stale lease may be replaced so a
  dead run cannot block recovery.
- Refresh the lease heartbeat at meaningful checkpoints during a long run and
  remove the lease when yielding at a committed boundary.
- Do not work a ticket claimed by another live run.
- Parallel agents receive bounded subtasks and do not edit the same files unless explicitly coordinated.
- Agents report evidence to the primary run; the primary run integrates and commits.
- If two branches explore genuinely different reasonable directions, keep both until the deciding ticket compares them.

## Completion

Set `WORKSTATE.md` to `COMPLETE` only after the objective-level completion audit passes. The recurring resume automation must exit without mutation when it sees that state.
