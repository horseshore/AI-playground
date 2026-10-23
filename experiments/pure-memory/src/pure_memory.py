"""Minimal, append-only memory layers for the Pure Memory experiment.

This is a storage and recall prototype, not an implementation of Bergson's
pure memory. Original traces are immutable records; coarse memories are
separate, versioned interpretations; recall outcomes are appended separately.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Iterable
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"Expected a JSON object at {path}:{line_number}")
            rows.append(value)
    return rows


def _append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def _tag_set(values: Iterable[str]) -> set[str]:
    return {str(value).strip().casefold() for value in values if str(value).strip()}


def _tokens(text: str) -> set[str]:
    # This intentionally uses only the standard library. Japanese segmentation
    # is not attempted; explicit tags are the reliable path for Japanese input.
    return {
        part.casefold()
        for part in re.findall(r"[A-Za-z0-9_]+|[一-龯ぁ-んァ-ヴー]{2,}", text)
        if len(part) > 1
    }


@dataclass(frozen=True)
class Trace:
    trace_id: str
    event: str
    source: str
    observed_at: str = field(default_factory=utc_now)
    observations: tuple[str, ...] = ()
    inferences: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    related_trace_ids: tuple[str, ...] = ()
    # Legacy annotation only. None means unassessed; True/False are not inferred from record count.
    one_off: bool | None = None
    # Keep the distinction between a direct record and a handoff/summary visible.
    provenance_kind: str = "direct_record"
    one_off_assessment_source: str | None = None


@dataclass(frozen=True)
class MemoryRevision:
    memory_id: str
    revision: int
    summary: str
    source_trace_ids: tuple[str, ...]
    counterexample_trace_ids: tuple[str, ...] = ()
    confidence: str = "tentative"
    created_at: str = field(default_factory=utc_now)
    supersedes_revision: int | None = None


@dataclass(frozen=True)
class RecallEvent:
    recall_id: str
    status: str
    trace_id: str
    route: str
    context: str
    context_tags: tuple[str, ...]
    reason: str
    created_at: str = field(default_factory=utc_now)
    adopted: bool | None = None
    interpretation_changed: bool | None = None
    action_changed: bool | None = None
    outcome_note: str | None = None
    caller_state: str = "unknown"
    goal_supplied: bool | None = None


@dataclass(frozen=True)
class RelationAssessment:
    relation_id: str
    source_trace_id: str
    target_trace_id: str
    relation_kind: str
    proposed_by: str
    evidence: str
    status: str = "candidate"
    created_at: str = field(default_factory=utc_now)


class PureMemoryStore:
    """JSONL-backed append-only traces, memory revisions, and recall events."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.trace_path = self.root / "traces.jsonl"
        self.memory_path = self.root / "memory_revisions.jsonl"
        self.recall_path = self.root / "recall_events.jsonl"
        self.relation_path = self.root / "relation_assessments.jsonl"

    def traces(self) -> list[Trace]:
        return [
            Trace(
                **{
                    **row,
                    "observations": tuple(row.get("observations", ())),
                    "inferences": tuple(row.get("inferences", ())),
                    "tags": tuple(row.get("tags", ())),
                    "related_trace_ids": tuple(row.get("related_trace_ids", ())),
                }
            )
            for row in _read_jsonl(self.trace_path)
        ]

    def memory_revisions(self) -> list[MemoryRevision]:
        return [
            MemoryRevision(
                **{
                    **row,
                    "source_trace_ids": tuple(row.get("source_trace_ids", ())),
                    "counterexample_trace_ids": tuple(row.get("counterexample_trace_ids", ())),
                }
            )
            for row in _read_jsonl(self.memory_path)
        ]

    def current_memories(self) -> list[MemoryRevision]:
        latest: dict[str, MemoryRevision] = {}
        for memory in self.memory_revisions():
            if memory.memory_id not in latest or memory.revision > latest[memory.memory_id].revision:
                latest[memory.memory_id] = memory
        return sorted(latest.values(), key=lambda item: (item.created_at, item.memory_id))

    def recall_events(self) -> list[RecallEvent]:
        return [RecallEvent(**row) for row in _read_jsonl(self.recall_path)]

    def relation_assessments(self) -> list[RelationAssessment]:
        return [RelationAssessment(**row) for row in _read_jsonl(self.relation_path)]

    def assess_relation(
        self, *, source_trace_id: str, target_trace_id: str,
        relation_kind: str, proposed_by: str, evidence: str,
        status: str = "candidate", relation_id: str | None = None,
    ) -> RelationAssessment:
        """Append a sourced relation assessment; a relation never asserts identity by itself."""
        known = {trace.trace_id for trace in self.traces()}
        missing = {source_trace_id, target_trace_id} - known
        if missing:
            raise ValueError(f"Relation refers to unknown traces: {sorted(missing)}")
        if source_trace_id == target_trace_id:
            raise ValueError("A relation assessment must connect two distinct trace IDs")
        if not relation_kind.strip() or not proposed_by.strip() or not evidence.strip():
            raise ValueError("relation_kind, proposed_by, and evidence must not be empty")
        allowed = {"candidate", "accepted", "rejected", "superseded"}
        if status not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        row = RelationAssessment(
            relation_id=relation_id or f"relation-{uuid4().hex}",
            source_trace_id=source_trace_id, target_trace_id=target_trace_id,
            relation_kind=relation_kind, proposed_by=proposed_by, evidence=evidence,
            status=status,
        )
        if any(old.relation_id == row.relation_id for old in self.relation_assessments()):
            raise ValueError(f"relation_id already exists: {row.relation_id}")
        _append_jsonl(self.relation_path, asdict(row))
        return row

    def append_trace(self, trace: Trace) -> Trace:
        if not trace.trace_id.strip():
            raise ValueError("trace_id must not be empty")
        if not trace.event.strip():
            raise ValueError("event must not be empty")
        if any(old.trace_id == trace.trace_id for old in self.traces()):
            raise ValueError(f"trace_id already exists: {trace.trace_id}")
        _append_jsonl(self.trace_path, asdict(trace))
        return trace

    def record(
        self,
        *,
        event: str,
        source: str,
        trace_id: str | None = None,
        observations: Iterable[str] = (),
        inferences: Iterable[str] = (),
        tags: Iterable[str] = (),
        related_trace_ids: Iterable[str] = (),
        one_off: bool | None = None,
        provenance_kind: str = "direct_record",
        one_off_assessment_source: str | None = None,
    ) -> Trace:
        trace = Trace(
            trace_id=trace_id or f"trace-{uuid4().hex}",
            event=event,
            source=source,
            observations=tuple(observations),
            inferences=tuple(inferences),
            tags=tuple(tags),
            related_trace_ids=tuple(related_trace_ids),
            one_off=one_off,
            provenance_kind=provenance_kind,
            one_off_assessment_source=one_off_assessment_source,
        )
        return self.append_trace(trace)

    def add_memory(
        self,
        *,
        memory_id: str,
        summary: str,
        source_trace_ids: Iterable[str],
        counterexample_trace_ids: Iterable[str] = (),
        confidence: str = "tentative",
    ) -> MemoryRevision:
        known_trace_ids = {trace.trace_id for trace in self.traces()}
        sources = tuple(dict.fromkeys(source_trace_ids))
        counterexamples = tuple(dict.fromkeys(counterexample_trace_ids))
        unknown = (set(sources) | set(counterexamples)) - known_trace_ids
        if unknown:
            raise ValueError(f"Memory refers to unknown traces: {sorted(unknown)}")
        if not memory_id.strip() or not summary.strip():
            raise ValueError("memory_id and summary must not be empty")

        previous = [
            revision for revision in self.memory_revisions()
            if revision.memory_id == memory_id
        ]
        previous_revision = max((item.revision for item in previous), default=0)
        revision = MemoryRevision(
            memory_id=memory_id,
            revision=previous_revision + 1,
            summary=summary,
            source_trace_ids=sources,
            counterexample_trace_ids=counterexamples,
            confidence=confidence,
            supersedes_revision=previous_revision or None,
        )
        _append_jsonl(self.memory_path, asdict(revision))
        return revision

    def recall(
        self,
        *,
        context: str,
        tags: Iterable[str] = (),
        related_trace_ids: Iterable[str] = (),
        limit: int = 6,
        associative_slots: int = 1,
        non_goal_slots: int = 1,
        caller_state: str = "task_focused",
        goal_supplied: bool | None = None,
    ) -> list[RecallEvent]:
        """Generate candidates through habitual, associative, and non-goal routes.

        Selection is deterministic and inspectable. No embedding model or
        language model is hidden inside this first-phase prototype.
        """
        if limit < 0 or associative_slots < 0 or non_goal_slots < 0:
            raise ValueError("slot counts and limit must be non-negative")
        allowed_states = {"task_focused", "waiting", "resting", "pre_sleep", "unknown"}
        if caller_state not in allowed_states:
            raise ValueError(f"caller_state must be one of {sorted(allowed_states)}")
        if goal_supplied is None:
            goal_supplied = caller_state == "task_focused" and bool(context.strip())
        traces = self.traces()
        if limit == 0 or not traces:
            return []

        context_tags = _tag_set(tags)
        context_tokens = _tokens(context)
        related_ids = set(related_trace_ids)
        trace_by_id = {trace.trace_id: trace for trace in traces}
        usage: dict[str, int] = {}
        for event in self.recall_events():
            if event.status == "candidate":
                usage[event.trace_id] = usage.get(event.trace_id, 0) + 1
        integrated_ids = {
            trace_id
            for memory in self.memory_revisions()
            for trace_id in memory.source_trace_ids
        }

        def overlap(trace: Trace) -> int:
            tag_overlap = len(context_tags & _tag_set(trace.tags))
            token_overlap = len(context_tokens & _tokens(trace.event))
            return tag_overlap * 3 + token_overlap

        ranked = sorted(traces, key=lambda trace: (-overlap(trace), trace.observed_at, trace.trace_id))
        non_goal_n = min(non_goal_slots, limit)
        associative_n = min(associative_slots, max(0, limit - non_goal_n))
        habitual_n = max(0, limit - non_goal_n - associative_n)
        chosen: list[tuple[Trace, str, str]] = []
        chosen_ids: set[str] = set()

        # Route 1: direct fit to the active context.
        for trace in ranked:
            if len([item for item in chosen if item[1] == "habitual"]) >= habitual_n:
                break
            if overlap(trace) <= 0 or trace.trace_id in chosen_ids:
                continue
            chosen.append((trace, "habitual", f"direct context overlap={overlap(trace)}"))
            chosen_ids.add(trace.trace_id)

        # Route 2: related by an explicit trace edge or by tags with the
        # habitual candidates. It is not required to match the active context.
        seed_tags: set[str] = set()
        for trace, route, _ in chosen:
            if route == "habitual":
                seed_tags.update(_tag_set(trace.tags))
        associative_candidates = []
        for trace in traces:
            if trace.trace_id in chosen_ids:
                continue
            edge_match = bool(set(trace.related_trace_ids) & (related_ids | chosen_ids))
            tag_match = bool(_tag_set(trace.tags) & seed_tags) if seed_tags else False
            if edge_match or tag_match:
                associative_candidates.append(
                    (trace, 2 if edge_match else 1, edge_match, tag_match)
                )
        associative_candidates.sort(
            key=lambda item: (-item[1], usage.get(item[0].trace_id, 0), item[0].observed_at)
        )
        for trace, _, edge_match, tag_match in associative_candidates[:associative_n]:
            why = "explicit trace relation" if edge_match else "shares tags with a habitual candidate"
            chosen.append((trace, "associative", why))
            chosen_ids.add(trace.trace_id)

        # Route 3: allow an unintegrated, one-off or rarely recalled trace to
        # enter even when it has no direct relevance to the active context.
        non_goal_candidates = [trace for trace in traces if trace.trace_id not in chosen_ids]
        non_goal_candidates.sort(
            key=lambda trace: (
                trace.trace_id in integrated_ids,
                usage.get(trace.trace_id, 0),
                trace.one_off is not True,
                overlap(trace),
                trace.observed_at,
                trace.trace_id,
            )
        )
        for trace in non_goal_candidates[:non_goal_n]:
            chosen.append(
                (
                    trace,
                    "non_goal_directed",
                    "kept eligible despite weak direct relevance; ranked by integration, prior recall, and one-off status",
                )
            )
            chosen_ids.add(trace.trace_id)

        # Fill any unfilled slots from the overall ranking without claiming
        # that this fallback is non-goal-directed.
        for trace in ranked:
            if len(chosen) >= limit:
                break
            if trace.trace_id not in chosen_ids:
                chosen.append((trace, "associative", "fallback candidate; route distinction is provisional"))
                chosen_ids.add(trace.trace_id)

        result: list[RecallEvent] = []
        for trace, route, reason in chosen[:limit]:
            event = RecallEvent(
                recall_id=f"recall-{uuid4().hex}",
                status="candidate",
                trace_id=trace.trace_id,
                route=route,
                context=context,
                context_tags=tuple(sorted(context_tags)),
                reason=reason,
                caller_state=caller_state,
                goal_supplied=goal_supplied,
            )
            _append_jsonl(self.recall_path, asdict(event))
            result.append(event)
        return result

    def record_outcome(
        self,
        recall_id: str,
        *,
        adopted: bool,
        interpretation_changed: bool = False,
        action_changed: bool = False,
        note: str | None = None,
    ) -> RecallEvent:
        """Append an outcome row; never modify the original candidate row."""
        candidates = [
            event for event in self.recall_events()
            if event.recall_id == recall_id and event.status == "candidate"
        ]
        if not candidates:
            raise ValueError(f"Unknown recall candidate: {recall_id}")
        candidate = candidates[-1]
        outcome = RecallEvent(
            recall_id=recall_id,
            status="outcome",
            trace_id=candidate.trace_id,
            route=candidate.route,
            context=candidate.context,
            context_tags=candidate.context_tags,
            reason=candidate.reason,
            adopted=adopted,
            interpretation_changed=interpretation_changed,
            action_changed=action_changed,
            outcome_note=note,
        )
        _append_jsonl(self.recall_path, asdict(outcome))
        return outcome

    def startup_view(self, max_memories: int = 8) -> dict[str, Any]:
        """Small restart surface: current coarse memories plus unresolved traces."""
        memories = self.current_memories()[-max_memories:]
        referenced = {trace_id for memory in memories for trace_id in memory.source_trace_ids}
        unresolved = [
            trace for trace in self.traces()
            if trace.trace_id not in referenced
        ]
        return {
            "current_memories": [
                {"memory_id": item.memory_id, "revision": item.revision, "summary": item.summary}
                for item in memories
            ],
            "unintegrated_trace_ids": [item.trace_id for item in unresolved],
            "note": "This view is a compact entry point, not a replacement for original traces.",
        }
