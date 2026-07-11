# Issue tracker: Local Markdown

Issues and specs (also known as PRDs) for this repo live as Markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says “publish to the issue tracker”

Create a new file under `.scratch/<feature-slug>/`, creating the directory if needed.

## When a skill says “fetch the relevant ticket”

Read the file at the referenced path. The user will normally pass the path or issue number directly.

## Wayfinding operations

- **Map:** `.scratch/<effort>/map.md`
- **Child ticket:** `.scratch/<effort>/issues/NN-<slug>.md`
- **Type:** a `Type:` line records `research`, `prototype`, `grilling`, or `task`
- **Status:** a `Status:` line records `open`, `claimed`, or `resolved`
- **Claim owner:** `Claimed by:` identifies the session or automation; `Claimed at:` records the UTC timestamp
- **Blocking:** a `Blocked by: NN, NN` line lists blocking ticket numbers; an empty value means unblocked
- **Frontier:** scan issue files for open, unblocked, unclaimed tickets; first by number wins
- **Claim:** set `Status: claimed` and save before work
- **Resolve:** append the answer under `## Answer`, set `Status: resolved`, then add a one-line context pointer to the map’s Decisions-so-far section

Local Markdown has no native assignment field, so `Status: claimed` plus `Claimed by:` is the concurrency claim. A resumed run continues the claimed ticket named in `WORKSTATE.md`; it does not open a duplicate. Blocking is the explicit fallback body convention.
