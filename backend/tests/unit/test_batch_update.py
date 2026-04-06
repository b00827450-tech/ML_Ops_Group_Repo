import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from backend.app.batch import batch_update


def test_run_batch_update_runs_audit_before_anomaly(monkeypatch, capsys):
    call_order = []

    monkeypatch.setattr(
        batch_update,
        "_run_audit_batch",
        lambda: call_order.append("audit") or 3
    )
    monkeypatch.setattr(
        batch_update,
        "_run_anomaly_batch",
        lambda: call_order.append("anomaly") or 3
    )

    batch_update.run_batch_update()

    output = capsys.readouterr().out

    assert call_order == ["audit", "anomaly"]
    assert "Starting batch update" in output
    assert "Audited 3 properties" in output
    assert "Updated anomalies for 3 properties" in output
