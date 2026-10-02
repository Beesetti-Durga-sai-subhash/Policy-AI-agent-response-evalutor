from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .loader import InputError, load_pack
from .report import build_report


def evaluate(data_dir: Path, output: Path) -> int:
    corpus, recordings, expected = load_pack(data_dir)
    report = build_report(corpus, recordings, expected)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary = report["summary"]
    print(f"Evaluated {sum(summary['recordings'].values())} recordings")
    print(
        f"Recording verdicts: "
        f"{summary['recordings'].get('PASS', 0)} PASS, "
        f"{summary['recordings'].get('FAIL', 0)} FAIL"
    )
    print(
        f"Check verdicts: "
        f"{summary['checks'].get('PASS', 0)} PASS, "
        f"{summary['checks'].get('FAIL', 0)} FAIL, "
        f"{summary['checks'].get('NOT_EVALUATED', 0)} NOT_EVALUATED"
    )
    print(f"Report: {output}")
    return 1 if summary["recordings"].get("FAIL", 0) else 0


def build_parser() -> argparse.ArgumentParser:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Evaluate recorded policy-assistant responses")
    subparsers = parser.add_subparsers(dest="command", required=True)
    command = subparsers.add_parser("evaluate", help="Evaluate all supplied recordings")
    command.add_argument("--data-dir", type=Path, default=root / "data")
    command.add_argument(
        "--output", type=Path, default=root / "reports" / "evaluation-report.json"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "evaluate":
            return evaluate(args.data_dir, args.output)
    except InputError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Tool error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
