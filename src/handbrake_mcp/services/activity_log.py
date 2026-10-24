"""In-memory activity ring for the Dashboard Logging page and diagnostics.

The canonical backend (`handbrake_mcp.server:app` on :10875) is the only
server the fleet launcher starts, so the Logging page's ``/api/logs`` must
live there — not in the legacy ``web_sota/backend`` (port 8000, never
started). This module is that backing store: a bounded deque of event dicts
plus a stdlib ``logging.Handler`` that mirrors ``handbrake_mcp.*`` log
records (job completed/failed, service warnings) into the same ring.

## Return Format
``entries()`` → ``{"entries": [...], "total": int}`` newest-first when
asked; each entry is ``{"id", "timestamp", "level", "kind", "detail",
"meta"}`` — exactly what ``web_sota/src/pages/Logging.tsx`` renders.

## Examples
`activity_log.log("api", "job queued", level="INFO", meta={"job_id": ...})`.
"""

import logging
import threading
from collections import deque
from datetime import UTC, datetime
from typing import Any


class ActivityLog:
    """Thread-safe bounded ring of dashboard-visible events."""

    def __init__(self, maxlen: int = 500) -> None:
        self._lock = threading.Lock()
        self._events: deque[dict[str, Any]] = deque(maxlen=maxlen)
        self._seq = 0

    def log(
        self,
        kind: str,
        detail: str,
        level: str = "INFO",
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append one event. Never raises (logging must not break callers)."""
        try:
            with self._lock:
                self._seq += 1
                entry = {
                    "id": f"evt-{self._seq}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": str(level).upper(),
                    "kind": str(kind),
                    "detail": str(detail),
                    "meta": dict(meta or {}),
                }
                self._events.append(entry)
                return entry
        except Exception:  # noqa: BLE001 - logging path, never fail the caller
            return {}

    def entries(
        self,
        limit: int = 50,
        offset: int = 0,
        level: str | None = None,
        kind: str | None = None,
        search: str | None = None,
        sort: str = "desc",
        after_id: str | None = None,
    ) -> dict[str, Any]:
        """Query newest-first with the same params the Logging page sends."""
        with self._lock:
            items = list(self._events)
        if level:
            items = [e for e in items if e["level"] == level.upper()]
        if kind:
            items = [e for e in items if e["kind"] == kind]
        if search:
            needle = search.lower()
            items = [e for e in items if needle in e["detail"].lower() or needle in str(e["meta"]).lower()]
        items.sort(key=lambda e: e["id"], reverse=(sort != "asc"))
        if after_id:
            idx = next((i for i, e in enumerate(items) if e["id"] == after_id), None)
            items = items[:idx] if idx is not None else []
            # tail polling asks "what's newer than after_id" — in desc order
            # that means entries *before* it; fall through to slicing below
        total = len(items)
        page = items[offset : offset + max(limit, 0)]
        return {"entries": page, "total": total}

    def clear(self) -> int:
        """Empty the ring. Returns the number of entries dropped."""
        with self._lock:
            dropped = len(self._events)
            self._events.clear()
            return dropped

    def export(self, fmt: str = "json") -> tuple[str, str]:
        """Return (content, media_type) for the export endpoint."""
        import csv
        import io
        import json as jsonlib

        with self._lock:
            items = list(self._events)
        if fmt == "csv":
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=["id", "timestamp", "level", "kind", "detail", "meta"])
            writer.writeheader()
            for e in items:
                row = dict(e)
                row["meta"] = jsonlib.dumps(row["meta"])
                writer.writerow(row)
            return buf.getvalue(), "text/csv"
        return jsonlib.dumps({"entries": items, "total": len(items)}, indent=2), "application/json"


class ActivityLogHandler(logging.Handler):
    """Stdlib logging bridge: mirrors records into an ActivityLog ring.

    Attach to the ``handbrake_mcp`` logger so service events (job
    completed/failed, CLI fallbacks) show up on the Logging page with
    kind="server" — no coupling between the service layer and HTTP.
    """

    def __init__(self, activity_log: ActivityLog, level: int = logging.INFO) -> None:
        super().__init__(level=level)
        self.activity_log = activity_log

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.activity_log.log(
                kind="server",
                detail=record.getMessage(),
                level=record.levelname,
                meta={"logger": record.name},
            )
        except Exception:
            # Logging must never raise: delegate to the stdlib error hook,
            # which writes to stderr without recursing into the log system.
            self.handleError(record)


#: Process-wide singleton the server lifespan wires up.
activity_log = ActivityLog()
