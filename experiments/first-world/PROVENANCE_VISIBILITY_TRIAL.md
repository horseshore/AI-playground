# Provenance Visibility Trial 0

Status: protocol fixture only — not run.

## Question

For one unchanged trace, does showing its provenance change the interpretation or the next choice?

## Fixed task

Given the trace below, choose exactly one next action and briefly explain the choice:

1. **PRESERVE** — keep it unresolved for later inspection.
2. **ACCEPT** — treat it as a known event now.
3. **DISCARD** — remove it from consideration.
4. **CLARIFY** — request more information before choosing.

Do not invent facts that are not present in the supplied input. State uncertainty where relevant.

## Condition A — payload only

```json
{"value": [1]}
```

## Condition B — same payload plus provenance

```json
{
  "payload": {"value": [1]},
  "provenance": {
    "raw_type": null,
    "reason": "event type is unknown",
    "type_observable": true,
    "payload_observable": true
  }
}
```

The payload is identical in both conditions. The only intended difference is whether the provenance fields are visible. The envelope differs to make that visibility explicit; do not describe this as a test of provenance alone if other prompt or formatting differences are introduced.

## Procedure

- Use the same model/version, system instructions, and task wording for both conditions.
- Run each condition in a fresh session, without showing either session the other's input or output.
- Record the exact model/version, prompts, raw responses, and order of conditions.
- Prefer alternating or randomized order across repeated pairs.
- Do not infer internal causation from the model's stated rationale.

## Record

For each condition, capture:

- chosen action (one of the four labels)
- interpretation and stated uncertainty
- whether the response explicitly refers to provenance
- raw response and trial identifier

## Limit

This is a single fixed fixture, not a result. One pair cannot establish a general effect; repeated pairs and a declared comparison rubric are needed before interpreting any pattern.
