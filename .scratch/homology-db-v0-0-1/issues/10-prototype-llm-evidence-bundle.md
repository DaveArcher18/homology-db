Type: prototype
Status: open
Claimed by:
Claimed at:
Blocked by: 05, 06

# Prototype the LLM lookup evidence bundle

## Question

What structured request, result, match explanation, completeness warning, provenance expansion, and compact context bundle let an LLM tool request mathematical examples safely without building natural-language interpretation yet?

## Comments

### 2026-07-11 bounded-QA scope clarification

This ticket still prototypes the structured evidence bundle; it does not add a bespoke natural-language parser or a general-purpose agent. The release's separate bounded QA client may use model-native tool calling as its only interpretation layer, with access limited to `resolve_subject`, `read_homology`, `query_examples`, and `expand_evidence`. The evidence contract produced here is an input to that acceptance run.
