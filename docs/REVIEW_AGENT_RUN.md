# Database-connected review agent run

This run is prepared so the reviewer only has to read one Codex task. The
review agent must not modify the repository, consult the internet, or answer
from memory when the local database cannot support a claim.

## Agent procedure

1. Read `AGENTS.md`, `docs/TEST_DRIVE.md`, and
   `qa/review/questions-v1.json`.
2. Run the public-seam tests and `python3 -m homology_db demo` as a preflight.
3. Answer every question in manifest order by invoking only these database
   operations through `python3 -m homology_db tool ...`:
   `resolve_subject`, `read_homology`, `query_examples`, and
   `expand_evidence`.
4. Use exactly one generated `snapshot_id` for the entire report. If a call
   returns another Snapshot, stop and report an integrity failure.
5. Every stated Homology group must name the returned assertion ID and
   evidence ID. Expand the supporting evidence for every subject used in a
   lookup or comparison.
6. Preserve typed failures. Unsupported coefficients, unresolved names,
   absent data, and uncomputed capabilities are never mathematical zero.
7. Do not infer homeomorphism, homotopy equivalence, or identity merely from
   equal Homology.
8. Do not edit files or create commits. The only deliverable is the final task
   response for human review.

## Final response format

Begin with a compact preflight block containing:

- test result;
- subject count;
- Snapshot ID;
- supported coefficient systems; and
- any integrity or capability warnings.

Then provide one numbered section per `R01` through `R12` containing:

- the question in one line;
- the direct answer in readable mathematical notation;
- the exact database operations used;
- assertion IDs and evidence IDs for every group claim; and
- a visible caveat whenever the database did not support the requested claim.

Finish with a reviewer checklist covering mathematical correctness, clarity,
grounding, and whether any answer crossed a preview limitation. Do not mark
your own answers approved; approval belongs to the human reviewer.

## Scope statement

This is a review demonstration of the 60-subject local preview, not the frozen
100-prompt release gate and not evidence that the planned 1,159 Models have
been ingested or qualified.
