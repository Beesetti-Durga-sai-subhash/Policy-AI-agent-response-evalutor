from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone

from .assertions import FAIL, evaluate_recording


def build_report(corpus: dict, recordings: list[dict], expected_data: dict) -> dict:
    results = []
    for recording in recordings:
        recording_id = recording["recording_id"]
        checks = evaluate_recording(
            recording,
            corpus,
            expected_data["recordings"][recording_id],
            expected_data["global_prohibited_claims"],
        )
        results.append(
            {
                "recording_id": recording_id,
                "verdict": FAIL if any(item["verdict"] == FAIL for item in checks) else "PASS",
                "checks": checks,
            }
        )

    check_counts = Counter(
        item["verdict"] for result in results for item in result["checks"]
    )
    recording_counts = Counter(item["verdict"] for item in results)
    by_risk: dict[str, Counter] = defaultdict(Counter)
    for result in results:
        for item in result["checks"]:
            by_risk[item["risk_area"]][item["verdict"]] += 1

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Offline evaluation of the 12 supplied recordings",
        "summary": {
            "recordings": dict(recording_counts),
            "checks": dict(check_counts),
            "risk_areas": {key: dict(value) for key, value in sorted(by_risk.items())},
        },
        "results": results,
        "limitations": [
            "Recordings do not establish current live-system behavior.",
            "No live latency, load, production availability, or retry timing was measured.",
            "The supplied cases are hand-picked and do not represent a response distribution.",
            "Passing evaluator self-tests proves evaluator behavior, not product correctness.",
        ],
    }
