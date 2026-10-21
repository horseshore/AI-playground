# Pure Memory design note: relations, uncertainty, and waiting

Status: design proposal, not yet implemented or validated.
Branch: `experiment/pure-memory-recall-state`
Context: discussion with 造 about the seven seed traces and the third recall route.

## 1. Do not classify a trace as one-off by default

The existing seed records currently use `one_off: true` throughout. This records the design intention ("do not discard one-time traces") as if it were a verified property of each event. It does not establish that each event is genuinely unique.

Do not rewrite the append-only seed traces to make the schema look cleaner. Treat their `one_off` values as legacy annotations whose evidential basis may be insufficient. A future reader should be able to distinguish:
- an explicitly supported assessment,
- an unassessed / unknown status,
- the provenance and evidence for the assessment.

Do not infer event uniqueness from the fact that only one record currently exists.

## 2. Keep events apart from relations between records

Avoid treating `occurrence_count` as a primary fact. Counting presupposes a decision about which observations count as the same event.

Instead, append relation assessments one at a time. Each relation should minimally record:
- relation ID;
- source trace ID and target trace ID;
- relation kind (for example: resembles, may-repeat-pattern, contrasts-with, possible-same-event);
- who or what proposed the relation;
- evidence / rationale;
- when it was proposed;
- status (candidate, accepted, rejected, superseded), without deleting earlier assessments.

A relation is not identity. Even multiple shared features should not automatically promote two traces to "the same event." Counts, if later useful, can be derived from a stated set of relation assessments and must remain a view, not an immutable property of the traces.

## 3. Separate event repetition from recall repetition

The occurrence of an event and the later retrieval of a trace are different things. Recall history should record each encounter with a trace, including:
- recall event ID and trace ID;
- timestamp;
- caller state / recall mode;
- whether a goal or question was supplied;
- what was surfaced and why, if a reason is available;
- later outcome, if known: no change, interpretation changed, action changed, or unknown.

Do not count repeated recalls as repeated occurrences of the original event. Keep the candidate record and any later outcome as separate append-only entries.

## 4. Reframe the third route as caller-state-based, not a low-score route

The current route is called `non_goal_directed`, but its implementation prioritizes low direct relevance, unintegrated traces, rare recalls, and one-off traces. That is a heuristic for escaping ordinary relevance ranking; it is not evidence of spontaneous or unconscious recall.

Proposed experiment: allow a caller to enter a no-question / waiting state, instead of assigning traces a "lack of relevance" score. Record that state explicitly. Possible states include:
- `task_focused`: a question or action goal is present;
- `waiting`: no new retrieval question is supplied for this interval;
- `resting`: the caller explicitly marks a pause;
- `pre_sleep`: only if the environment can actually represent this state;
- `unknown`: caller state was not recorded.

Do not claim that a waiting state itself causes spontaneous recall. First test whether retrieval initiated during such a state surfaces different traces than task-focused retrieval. Record empty outcomes too; a pause that surfaces nothing is not a failed memory.

For the island simulation, "sitting by the fire," "waiting at the frog pond," and "before sleep" are candidate environmental states only when the hand log or environment confirms them. Do not invent these states from silence in the log.

## 5. Keep observations, interpretations, and unknowns distinct

- Original traces remain append-only.
- Relation assessments are a separate layer.
- Interpretations remain versioned and refer to trace IDs.
- Recall events describe a later encounter, not a modification of the source trace.
- Unknown is a legitimate state; missing evidence must not be silently converted into a negative or positive classification.

The "first rhyme" problem remains open: explicit tags and token matching may fail to surface a pattern that exists in the sequence or shape of a whole visit. This note does not solve that retrieval limitation.

## 6. Minimal implementation sequence

1. Add a relation-assessment JSONL layer and tests for append-only history, unknown trace IDs, and non-identity relation types.
2. Replace the boolean-only one-off API for new records with an explicit unknown / assessed status plus provenance. Preserve legacy input when reading old records.
3. Add caller-state to recall events and a waiting-state experiment that does not require a context relevance score.
4. Compare task-focused retrieval with waiting-state retrieval over the same trace store; report what surfaced and what changed. Do not describe the result as "pure memory" without further evidence.

No implementation or test results are implied by this design note.
