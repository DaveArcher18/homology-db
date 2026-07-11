# Homology DB agent instructions

Preserve mathematical provenance and explicit uncertainty. Never turn absent data into a mathematical zero, silently merge models, or overwrite a corrected assertion.

Keep changes small and commit by coherent scope. Treat the UI and CW-complex rendering as deferred unless a current ticket explicitly brings them into scope.

## Continuity

Before doing goal work, read `WORKSTATE.md`, then the active Wayfinder map it names. Follow `docs/agents/resume-protocol.md` for claiming, checkpointing, testing, and recovery after interruption or quota exhaustion.

## Agent skills

### Issue tracker

Issues and Wayfinder maps are tracked as local Markdown under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default Pocock triage roles. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository with a root `CONTEXT.md` and system-wide ADRs under `docs/adr/`. See `docs/agents/domain.md`.
