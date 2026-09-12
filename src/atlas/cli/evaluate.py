"""Run the offline evaluation suite."""

from __future__ import annotations

from atlas.evaluation.runner import run_evaluation


def main() -> None:
    report = run_evaluation()
    print(report.summary())
