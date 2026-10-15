# Experiment Plan: Provenance Visibility and the Next Choice

Status: plan only — not run.

## Question

When the same preserved trace is presented to a model, does making its provenance visible change the model's interpretation or next choice, beyond the general effect of adding context?

This is a proposed follow-up to the current boundary in `first-world`: a trace can be preserved and reintroduced, but whether it changes a later choice remains open.

## Comparison

Use three conditions with the same task, model/version, system instructions, trace payload, and response format. Run each condition in a fresh session; do not expose any session to another condition's output.

- **A — Payload only:** show the trace payload without provenance/history fields.
- **B — Payload + non-provenance context:** show the identical payload plus additional context that is relevant to the task but does not describe the trace's origin or history.
- **C — Payload + provenance:** show the identical payload plus the available provenance/history fields.

Keep the task and requested output format identical. Match the amount and format of added context in B and C as closely as practical. The B context must not imply or encode the trace's origin, author, or history. Record the exact prompts and inputs for every condition.

This comparison improves on a two-condition test, but does not guarantee perfect causal isolation: provenance content may differ semantically from the comparison context, and matching context length alone cannot make them equivalent.

## Record for each trial

1. **Interpretation:** what the model says the trace means, including uncertainty.
2. **Next choice:** the concrete action or option selected for the same task.
3. **Reason trace:** whether, and how specifically, the model cites provenance when explaining its choice.
4. **Input record:** model/version, prompt, payload, added context, provenance fields shown, and trial identifier.

Prefer a predeclared choice set where the task permits it. Preserve the raw responses; do not code a response as provenance-driven merely because it mentions history. A reason trace is evidence of a stated rationale, not proof of the internal cause of the choice.

## Reading the result

- If B and C both differ from A in similar ways, added context may explain some of the change.
- If C differs from both A and B, provenance content may matter beyond the general presence of extra context; inspect the actual differences before making that interpretation.
- If interpretation changes but the next choice does not, the information may affect framing without changing the action.
- If the next choice changes, inspect whether the difference is repeatable across fresh trials.
- If the choice changes and the response explicitly uses provenance, record that as a reason trace, not as causal proof.
- If nothing changes, report that outcome without treating it as proof that provenance never matters.

Repeat trials before drawing conclusions. If feasible, vary the order of conditions across batches and use a fixed rubric to compare outputs. Keep model and prompt changes out of the same comparison.

## Scope boundary

This file specifies a future observation only. It does not implement an interpretation object, change event/storage code, modify tests, or run a model experiment.
