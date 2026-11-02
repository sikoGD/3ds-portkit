"""Stable, non-sensitive evidence records used by CLI and MCP reports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def evidence_id(kind: str, subject: Path | str) -> str:
    """Create a repeatable identifier without returning source contents."""
    path = Path(subject).resolve()
    payload = f"{kind}:{path}".encode("utf-8", "surrogateescape")
    return f"ev-{kind}-{hashlib.sha256(payload).hexdigest()[:12]}"


def evidence_report(kind: str, subject: Path | str, result: dict, command: str) -> dict:
    path = Path(subject).resolve()
    return {"evidence_id": evidence_id(kind, path), "kind": kind,
            "subject": str(path), "reproducible_command": command,
            "limits": {"source_contents_returned": False, "automated_reverse_engineering": False},
            "result": result}


def json_schema() -> dict:
    return {"evidence_id": "stable non-content identifier", "reproducible_command": "local command",
            "limits": {"source_contents_returned": False, "automated_reverse_engineering": False}}
