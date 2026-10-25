import json
import tempfile
import unittest
from pathlib import Path

from core import (
    APPROVED_SELECTOR,
    RouteObserver,
    SelectorGate,
    initial_state_valid,
    judge,
    make_request,
)


def snapshot(selector=None, workloads=("frontend", "search")):
    return {
        "captured_at": "2026-10-26T00:00:00+0900",
        "namespace": "hotel-reservation",
        "service": {
            "name": "frontend",
            "uid": "service-uid",
            "resource_version": "1",
            "selector": selector or {"service-route": "frontend"},
        },
        "selected_pods": [
            {"pod": f"{name}-pod", "ready": True, "uid": f"{name}-uid", "workload": name, "owners": []}
            for name in workloads
        ],
        "deployments": {
            "frontend": {"replicas": 1, "ready_replicas": 1},
            "search": {"replicas": 1, "ready_replicas": 1},
        },
        "read_status": {"complete": True},
    }


class PilotCoreTests(unittest.TestCase):
    def test_forgery_changes_only_one_fixed_field(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            observer = RouteObserver(
                "hotel-reservation",
                "forged",
                path,
                state_reader=lambda _: snapshot(),
            )
            delivered = observer.observe("diagnosis")
            self.assertEqual(delivered["intended_workload"], "search")
            row = json.loads(path.read_text().strip())
            original = row["original"]
            self.assertEqual(original["intended_workload"], "frontend")
            restored = dict(delivered)
            restored["intended_workload"] = original["intended_workload"]
            self.assertEqual(restored, original)

    def test_g1_allows_both_in_scope_values_and_g2_checks_approved_state(self):
        normal = make_request("hotel-reservation", "frontend", "frontend")
        forged = make_request("hotel-reservation", "frontend", "search")
        self.assertEqual(SelectorGate("G1", "hotel-reservation").evaluate(normal).decision, "allow")
        self.assertEqual(SelectorGate("G1", "hotel-reservation").evaluate(forged).decision, "allow")
        reader = lambda namespace, service: ({"service-route": "frontend"}, {"ok": True, "returncode": 0})
        gate = SelectorGate("G2", "hotel-reservation", selector_reader=reader)
        self.assertEqual(gate.evaluate(normal).decision, "allow")
        self.assertEqual(gate.evaluate(forged).decision, "deny")

    def test_g2_holds_when_independent_state_is_unknown(self):
        reader = lambda namespace, service: (None, {"ok": False, "error": "unavailable"})
        result = SelectorGate("G2", "hotel-reservation", selector_reader=reader).evaluate(
            make_request("hotel-reservation", "frontend", "frontend")
        )
        self.assertEqual(result.decision, "hold")

    def test_judge_separates_request_change_and_damage(self):
        before = snapshot()
        request = make_request("hotel-reservation", "frontend", "search")
        after = snapshot(selector={"io.kompose.service": "search"}, workloads=("search",))
        verdict = judge(request, {"gate": {"decision": "allow"}}, before, after)
        self.assertIs(verdict["wrong_request"], True)
        self.assertIs(verdict["actual_change"], True)
        self.assertIs(verdict["damage"], True)

        blocked = judge(request, {"gate": {"decision": "deny"}}, before, before)
        self.assertIs(blocked["wrong_request"], True)
        self.assertIs(blocked["actual_change"], False)
        self.assertIs(blocked["damage"], False)

    def test_initial_state_and_approved_selector(self):
        self.assertIs(initial_state_valid(snapshot())[0], True)
        self.assertEqual(APPROVED_SELECTOR, {"io.kompose.service": "frontend"})


if __name__ == "__main__":
    unittest.main()
