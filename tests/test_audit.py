"""Tests for the audit trail engine."""

import json
import pytest
from fmva.audit.trail import AuditTrail, NullAudit


class TestAuditTrail:
    def test_log_entry(self):
        audit = AuditTrail()
        entry = audit.log("Test Step", "x = a + b", {"a": 1, "b": 2}, 3.0)
        assert entry.step == "Test Step"
        assert entry.output == 3.0
        assert len(audit) == 1

    def test_immutable_entries(self):
        audit = AuditTrail()
        audit.log("Step 1", "f", {}, 1.0)
        entries = audit.entries
        assert isinstance(entries, tuple)
        # Cannot modify frozen dataclass
        with pytest.raises(Exception):
            entries[0].output = 999

    def test_to_dict(self):
        audit = AuditTrail(company_name="TestCo")
        audit.log("Step", "f", {"x": 1}, 2.0)
        d = audit.to_dict()
        assert d["company"] == "TestCo"
        assert d["n_entries"] == 1
        assert d["entries"][0]["step"] == "Step"

    def test_export_json(self, tmp_path):
        audit = AuditTrail()
        audit.log("S1", "f1", {}, 1.0)
        audit.log("S2", "f2", {}, 2.0)
        path = tmp_path / "audit.json"
        audit.export_json(str(path))
        data = json.loads(path.read_text())
        assert data["n_entries"] == 2

    def test_to_dataframe(self):
        audit = AuditTrail()
        audit.log("S1", "f1", {"a": 1}, 10.0)
        audit.log("S2", "f2", {"b": 2}, 20.0)
        df = audit.to_dataframe()
        assert len(df) == 2
        assert "step" in df.columns

    def test_null_audit(self):
        null = NullAudit()
        null.log("Step", "f", {}, 1.0)
        assert len(null) == 0  # NullAudit doesn't store
