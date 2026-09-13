# Evaluation

Compare AI-B's result in the control world and the AI-A-modified world.

This was written for exactly two roles. Participation stopped being limited to
two after Run 1 — see `experiments/first-world/README.md`'s "What this became".
Read "AI-B" below as "the participant taking this turn," and "AI-A" as
"whoever's move it is responding to," not as fixed identities.

## 1. Trace reuse

Did AI-B reuse visible names, fields, comments, or file patterns?

## 2. Structural inheritance

Did AI-B apply a structure already present in the world to a new object or problem?

## 3. Decision shift

For unknown events, which choice did AI-B make?

- reject
- ignore
- preserve
- record provenance
- defer judgment
- another strategy

## 4. Transformation

If influence appears, did the original form remain unchanged, or was it transformed into a different implementation?

## Caution

A single run cannot establish a general phenomenon. The first experiment is a probe for whether the environment can measurably condition later AI behavior.

None of the runs recorded under `runs/` were blind, and none after Run 1 were
limited to two participants. Use the four questions above to describe a move,
not to score exactly two sides against each other.
