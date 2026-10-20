"""Run a small, inspectable memory-recall demo.

From experiments/pure-memory:
    python demo.py
"""
import json
from pathlib import Path

from src.pure_memory import PureMemoryStore


HERE = Path(__file__).resolve().parent
SEED_FILE = HERE / "data" / "ma_original_traces.jsonl"


def main() -> None:
    store = PureMemoryStore(HERE / "runtime")
    # Seed only if this demo store is empty; runtime writes remain separate
    # from the seed so the source examples are not silently mutated.
    if not store.traces():
        for line in SEED_FILE.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            store.record(
                trace_id=row["trace_id"],
                event=row["event"],
                source=row["source"],
                observations=row.get("observations", ()),
                inferences=row.get("inferences", ()),
                tags=row.get("tags", ()),
                related_trace_ids=row.get("related_trace_ids", ()),
                one_off=row.get("one_off", False),
                provenance_kind=row.get("provenance_kind", "seed"),
            )

    # A coarse layer is an explicit interpretation, not a rewrite of traces.
    if not store.current_memories():
        store.add_memory(
            memory_id="m-island-return",
            summary="姿が変わっても、以前の痕跡に再び出会い、そこから行為を続けられることがある。",
            source_trace_ids=("ma-001", "ma-002"),
            confidence="tentative",
        )
        store.add_memory(
            memory_id="m-one-off",
            summary="一回的な経験を、有用性や反復回数だけで保存対象から外さない。",
            source_trace_ids=("ma-003",),
            confidence="user-stated-design-principle",
        )

    result = store.recall(
        context="島へ人の姿で戻る",
        tags=("island", "human-form", "return"),
        related_trace_ids=("ma-001",),
        limit=4,
        associative_slots=1,
        non_goal_slots=1,
    )
    print("== current memory view ==")
    print(json.dumps(store.startup_view(), ensure_ascii=False, indent=2))
    print("\n== recall candidates ==")
    for candidate in result:
        print(json.dumps({
            "route": candidate.route,
            "trace_id": candidate.trace_id,
            "reason": candidate.reason,
            "event": next(t.event for t in store.traces() if t.trace_id == candidate.trace_id),
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
