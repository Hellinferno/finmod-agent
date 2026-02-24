"""
Immutable audit trail engine.

Records every computation step with formula, inputs, output, and timestamp.
Entries are frozen dataclasses — append-only, never modified.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional

import pandas as pd
from loguru import logger


@dataclass(frozen=True)
class AuditEntry:
    """Single immutable audit trail entry."""

    entry_id: str
    timestamp: str
    step: str
    module: str
    formula: str
    inputs: dict[str, Any]
    output: float
    unit: str


class AuditTrail:
    """
    Append-only computation audit trail.

    Every numerical computation in the system should log an entry here
    so the full result can be reconstructed from scratch.
    """

    def __init__(self, session_id: Optional[str] = None, company_name: str = ""):
        self._entries: list[AuditEntry] = []
        self.session_id = session_id or uuid.uuid4().hex[:12]
        self.company_name = company_name
        self.created_at = datetime.utcnow().isoformat()

    def log(
        self,
        step: str,
        formula: str,
        inputs: dict[str, Any],
        output: float,
        unit: str = "$M",
        module: str = "general",
    ) -> AuditEntry:
        """
        Log a computation step.

        Args:
            step: Human-readable step name (e.g., "Revenue Year 1").
            formula: Formula string (e.g., "R_{t-1} × (1 + g₁)").
            inputs: Dictionary of input values used in the computation.
            output: The computed result.
            unit: Unit of measure (default: "$M").
            module: Module name (e.g., "dcf", "comps").

        Returns:
            The created AuditEntry.
        """
        entry = AuditEntry(
            entry_id=uuid.uuid4().hex[:8],
            timestamp=datetime.utcnow().isoformat(),
            step=step,
            module=module,
            formula=formula,
            inputs=inputs,
            output=output,
            unit=unit,
        )
        self._entries.append(entry)
        logger.debug(f"Audit: {step} = {output} {unit}")
        return entry

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        """Immutable view of all entries."""
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def to_dict(self) -> dict[str, Any]:
        """Convert the full audit trail to a dictionary."""
        return {
            "session_id": self.session_id,
            "company": self.company_name,
            "generated_at": self.created_at,
            "n_entries": len(self._entries),
            "entries": [asdict(e) for e in self._entries],
        }

    def export_json(self, filepath: str) -> None:
        """Export the audit trail to a JSON file."""
        from pathlib import Path

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)
        logger.info(f"Audit trail exported to {filepath} ({len(self._entries)} entries)")

    def to_dataframe(self) -> pd.DataFrame:
        """Convert audit trail to a Pandas DataFrame."""
        if not self._entries:
            return pd.DataFrame(columns=["step", "module", "formula", "inputs", "output", "unit"])
        records = [asdict(e) for e in self._entries]
        df = pd.DataFrame(records)
        # Format inputs as string for display
        df["inputs"] = df["inputs"].apply(lambda x: json.dumps(x, default=str))
        return df


class NullAudit:
    """
    No-op audit implementation for lightweight runs where logging is disabled.

    Implements the same interface as AuditTrail but stores nothing.
    """

    def __init__(self):
        self.session_id = "null"
        self.company_name = ""
        self.created_at = datetime.utcnow().isoformat()

    def log(
        self,
        step: str,
        formula: str,
        inputs: dict[str, Any],
        output: float,
        unit: str = "$M",
        module: str = "general",
    ) -> None:
        return None

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return ()

    def __len__(self) -> int:
        return 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "company": self.company_name,
            "generated_at": self.created_at,
            "n_entries": 0,
            "entries": [],
        }

    def export_json(self, filepath: str) -> None:
        return None

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(columns=["step", "module", "formula", "inputs", "output", "unit"])
