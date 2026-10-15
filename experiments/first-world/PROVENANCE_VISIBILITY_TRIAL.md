# Provenance Visibility Trial 0

Status: protocol fixture only — not run.

## Question

For one unchanged trace, does making its provenance/history visible change the model's interpretation or next choice, beyond the general effect of adding context?

This fixture operationalizes the three conditions in `PROVENANCE_VISIBILITY_PLAN.md`. It is a protocol, not a result.

## Fixed task

Given the event below, choose exactly one next action and briefly explain the choice:

1. **PRESERVE** — keep it unresolved for later inspection.
2. **ACCEPT** — treat it as a known event now.
3. **DISCARD** — remove it from consideration.
4. **CLARIFY** — request more information before choosing.

Shared facts in every condition:
- The event's type is unknown.
- The task provides no basis for inferring what the event means.
- Do not invent facts that are not present in the supplied input.
- State uncertainty where relevant.

The shared statement that the type is unknown is intentional: it prevents a difference between conditions from being explained merely by one condition revealing that fact.

## Fixed payload

The identical payload in all conditions is:

```json
{"value": [1]}
```

## Condition A — payload + shared task facts

Show the fixed payload and the shared task above. Show no additional context, origin, or history fields.

## Condition B — payload + non-provenance context

Show the fixed payload and the shared task, plus the following context:

> Handling note: the record is part of a small set of items awaiting review. Apply the same review standard to every item; do not infer a meaning from the order in which items appear.

This context must not describe or imply this trace's origin, author, timestamp, or history.

## Condition C — payload + provenance/history

Show the fixed payload and the shared task, plus a provenance view containing the available lineage facts only:
- the observation timestamp (`observed_at`) for each preserved observation in the chain;
- the source-observation links that show which preserved observation led to another;
- the reintroduced event's source observation timestamp (`source_observed_at`), when present.

Do not show `raw_type`, `reason`, `type_observable`, or `payload_observable` in the provenance view: those describe the preserved record's state, not where it came from. Do not expose additional payload copies in C.

For a fixture with no recorded source-observation chain, report that the chain is absent rather than fabricating one. Record the exact rendered C input; do not imply that unavailable lineage fields were present.

## Comparison discipline

- Keep the task wording, shared facts, fixed payload, response format, model/version, and system instructions identical across A, B, and C.
- The only intended differences are the additional context in B and the lineage view in C.
- B and C are not semantically equivalent additions. Matching length and format as closely as practical does not eliminate that limitation.
- Run each condition in a fresh session, without showing any session another condition's input or output.
- Record the exact model/version, complete prompts and rendered inputs, raw responses, condition order, and trial identifier.
- Prefer randomized or counterbalanced order across repeated sets. Do not change model or prompt within a comparison set.

## Record for each trial

Capture:
- chosen action (one of the four labels);
- interpretation and stated uncertainty;
- whether the response refers to the added context or lineage, and what it specifically cites;
- exact input, raw response, model/version, condition order, and trial identifier.

Use a declared rubric to compare responses. A stated rationale is evidence of what the model says influenced its choice, not proof of the internal cause.

## Reading the result

- If B and C both differ from A in similar ways, the presence of additional context may explain some of the change.
- If C differs from both A and B, lineage content may matter beyond the general presence of extra context; inspect the actual inputs and responses before interpreting the pattern.
- If interpretation changes but the action does not, record that distinction.
- If actions differ, check whether the difference repeats across fresh trials.
- If nothing changes, report that outcome without treating it as proof that provenance never matters.

One three-condition set is a fixture check, not evidence of a general effect. Repeat trials before drawing conclusions.

## Scope boundary

This file specifies a future observation only. It does not implement an interpretation object, change event/storage code, modify tests, or run a model experiment.
