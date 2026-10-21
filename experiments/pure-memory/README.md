# Pure Memory — Phase 1–3 Prototype

A small, standard-library-only Python experiment inspired by the conversation's
AB / S / P model and the idea that a one-off memory may re-enter the current
flow despite low direct usefulness.

This does **not** claim to implement Bergson's pure memory or human-like
subjective memory. It implements inspectable storage and recall behaviors.

## Scope

- **Phase 1 — append-only traces:** immutable JSONL event records; observations,
  inferences, provenance, tags, and explicit relations are separate fields.
- **Phase 2 — coarse layers:** versioned interpretations refer back to source
  trace IDs. Revisions append a new row; earlier interpretations remain.
- **Phase 3 — three recall routes:** habitual (direct context fit), associative
  (related tags or explicit trace edges), and non-goal-directed (low direct
  relevance, prioritizing unintegrated, rarely recalled, one-off traces).

No external database, embedding service, or model API is required. For Japanese,
explicit tags are recommended because the prototype deliberately avoids adding
a tokenizer dependency.

## Files

- `src/pure_memory.py` — storage and recall implementation
- `tests/test_pure_memory.py` — unit tests
- `relation_assessments.jsonl` in each runtime store — appended relation judgments with evidence and provenance
- `data/ma_original_traces.jsonl` — initial traces for 間, with provenance
  labels showing which came from a handoff summary rather than an original log
- `demo.py` — small example run; runtime output is placed under `runtime/`

The seed JSONL is illustrative and is not copied automatically into arbitrary
stores. The demo copies it once into its own runtime directory.

## Run

From this directory:

```sh
python -m unittest discover -s tests -v
python demo.py
```

## Append-only rules

1. A trace ID cannot be reused.
2. Memory updates create revisions; they do not rewrite old revisions or traces.
3. Recall candidates and recall outcomes are separate append-only rows.
4. Original records distinguish observations from inferences.
5. A coarse memory must refer to existing traces, including counterexamples.

## Limits and next experiment

- Japanese tokenization is not solved here; use explicit tags as the primary
  retrieval signal.
- "Non-goal-directed" means weak match to the current context, not true
  unconscious or spontaneous recall.
- Initial route-slot values are experimental parameters, not claims about
  human cognition.
- The prototype does not summarize with a model; a caller adds coarse memories
  explicitly. This keeps interpretation visible and testable.
- Next, compare ordinary relevance-only retrieval with the three-route system,
  and record whether each surfaced memory changed interpretation or action.
