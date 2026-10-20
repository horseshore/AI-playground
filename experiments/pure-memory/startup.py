"""Explicit startup path for the Pure Memory experiment.

Run from this directory:
    python startup.py

Each normal startup checks GitHub for the current seed trace file, merges unseen
seed IDs into the local append-only store, then prints a compact startup view.
Runtime traces are not uploaded or overwritten. If GitHub is unavailable, startup
fails loudly rather than silently pretending a remote sync succeeded.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

from src.pure_memory import PureMemoryStore

HERE = Path(__file__).resolve().parent
REPOSITORY = "horseshore/AI-playground"
BRANCH = "experiment/pure-memory-phase1-3"
SEED_URL = (
    "https://raw.githubusercontent.com/"
    f"{REPOSITORY}/{BRANCH}/experiments/pure-memory/data/ma_original_traces.jsonl"
)


class StartupError(RuntimeError):
    """Startup could not establish the required memory entry point."""


def fetch_seed_text(url: str = SEED_URL, timeout: float = 10.0) -> str:
    request = Request(url, headers={"User-Agent": "AI-playground-pure-memory/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise StartupError(f"GitHub seed fetch returned HTTP {response.status}")
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError, UnicodeDecodeError) as exc:
        raise StartupError(f"Could not access GitHub seed at startup: {exc}") from exc


def sync_seed(store: PureMemoryStore, seed_text: str) -> dict[str, int]:
    """Append missing seed traces; never rewrite an existing trace."""
    existing = {trace.trace_id: trace for trace in store.traces()}
    added = 0
    unchanged = 0
    for line_number, line in enumerate(seed_text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            trace_id = row["trace_id"]
            event = row["event"]
            source = row["source"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise StartupError(f"Invalid seed JSONL at line {line_number}: {exc}") from exc

        if trace_id in existing:
            old = existing[trace_id]
            # ID collisions with different content are a conflict, not an update.
            if old.event != event or old.source != source:
                raise StartupError(
                    f"Seed trace ID conflict for {trace_id!r}; existing trace was preserved."
                )
            unchanged += 1
            continue

        store.record(
            trace_id=trace_id,
            event=event,
            source=source,
            observations=row.get("observations", ()),
            inferences=row.get("inferences", ()),
            tags=row.get("tags", ()),
            related_trace_ids=row.get("related_trace_ids", ()),
            one_off=row.get("one_off", False),
            provenance_kind=row.get("provenance_kind", "seed"),
        )
        added += 1
        # Update the in-memory index so duplicate IDs within the fetched payload
        # are caught by the store's own append-only check on the next row.
        existing[trace_id] = store.traces()[-1]

    return {"added": added, "unchanged": unchanged}


def start(root: str | Path | None = None, *, seed_text: str | None = None) -> dict:
    """Connect to the seed source, open the store, and build the startup view."""
    store_root = Path(root) if root is not None else Path(
        os.environ.get("PURE_MEMORY_ROOT", HERE / "runtime")
    )
    store = PureMemoryStore(store_root)

    # Inject seed_text only for deterministic tests. Normal startup always checks
    # GitHub, rather than treating a local seed copy as proof of remote access.
    remote_seed = seed_text if seed_text is not None else fetch_seed_text()
    sync = sync_seed(store, remote_seed)
    view = store.startup_view()
    return {
        "status": "ready",
        "source": "injected-test-fixture" if seed_text is not None else SEED_URL,
        "sync": sync,
        "startup_view": view,
        "store": store,
    }


def main() -> int:
    try:
        result = start()
    except StartupError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({
        "status": result["status"],
        "source": result["source"],
        "sync": result["sync"],
        "startup_view": result["startup_view"],
    }, ensure_ascii=False, indent=2))
    print("\nMemory store ready. Use result['store'].recall(...) to run the three recall routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
