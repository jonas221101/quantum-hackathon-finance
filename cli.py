from __future__ import annotations

import argparse
from pathlib import Path

from src.analysis import export_analysis, run_analysis
from src.data import DEFAULT_DATA_PATH
from src.report import write_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum finance allocation analysis")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--classical-only", action="store_true")
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--starts", type=int, default=2)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    result = run_analysis(
        args.data,
        include_quantum=not args.classical_only,
        qaoa_reps=args.reps,
        qaoa_starts=args.starts,
        shots=args.shots,
    )
    export_analysis(result, args.output)
    if args.report:
        write_markdown_report(result, args.output / "analysis_report.md")
    print("Classical winners:")
    for mandate, portfolio in result["classical_winners"].items():
        print(f"  {mandate}: {portfolio}")
    if result["quantum"]:
        print(f"Quantum backend: {result['quantum']['backend']}")
    print(f"Exports written to {args.output.resolve()}")


if __name__ == "__main__":
    main()
