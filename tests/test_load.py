from __future__ import annotations

from core.models import NormalizedRecord
from extract.resources import CUSTOMERS
from load.supabase_sink import SupabaseRestSink


def test_supabase_sink_batches_and_serializes_rows() -> None:
    class FakeSink(SupabaseRestSink):
        def __init__(self):
            super().__init__("https://example.supabase.co", "fake-secret", batch_size=1)
            self.calls = []

        def _post(self, endpoint, payload, conflict_column):
            self.calls.append((endpoint, payload, conflict_column))

    sink = FakeSink()
    records = [
        NormalizedRecord(CUSTOMERS.name, "1", {"name": "A"}, {"clientes_cadastro": []}),
        NormalizedRecord(CUSTOMERS.name, "2", {"name": "B"}, {"clientes_cadastro": []}),
    ]
    sink.upsert(CUSTOMERS, records)
    assert len(sink.calls) == 2
    assert sink.calls[0][2] == "external_id"
    assert sink.calls[0][1][0]["external_id"] == "1"
