#!/usr/bin/env python3
"""Run run_experiments_create.py across multiple argument combinations."""

import argparse
import itertools
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch runner that sweeps run_experiments_create.py parameters."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Optional dataset file passed to run_experiments_create.py.",
    )
    parser.add_argument(
        "--sample-sizes",
        type=int,
        nargs="+",
        default=[1000],
        help="List of sample sizes to evaluate (default: 1000).",
    )
    parser.add_argument(
        "--search-trials",
        type=int,
        nargs="+",
        default=[200],
        help="List of search trial counts to evaluate (default: 200).",
    )
    parser.add_argument(
        "--delete-ratios",
        type=float,
        nargs="+",
        default=[0.2],
        help="List of delete ratios to evaluate (default: 0.2).",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[42],
        help="List of RNG seeds to evaluate (default: 42).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/batch_runs",
        help="Directory under which all metrics.json files will be stored.",
    )
    parser.add_argument(
        "--python",
        type=str,
        default=sys.executable,
        help="Python executable used to invoke run_experiments_create.py.",
    )
    return parser.parse_args()


def format_ratio(value: float) -> str:
    """Return a filesystem-friendly representation for a float."""
    if value.is_integer():
        return f"{int(value)}"
    return str(value).replace(".", "p")


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    combinations = list(
        itertools.product(
            args.sample_sizes, args.search_trials, args.delete_ratios, args.seeds
        )
    )
    if not combinations:
        print("No parameter combinations to run.")
        return 1

    for sample_size, search_trials, delete_ratio, seed in combinations:
        delete_str = format_ratio(delete_ratio)
        metrics_path = (
            output_dir
            / f"metrics_sample{sample_size}_search{search_trials}_delete{delete_str}_seed{seed}.json"
        )

        cmd = [
            args.python,
            "run_experiments_create.py",
            "--sample-size",
            str(sample_size),
            "--search-trials",
            str(search_trials),
            "--delete-ratio",
            str(delete_ratio),
            "--seed",
            str(seed),
            "--output-file",
            str(metrics_path),
        ]
        if args.dataset:
            cmd.extend(["--dataset", args.dataset])

        print("\n=== Running", " ".join(cmd), "===")
        subprocess.run(cmd, check=True)

    print(f"\nCompleted {len(combinations)} experimental runs. Metrics saved in {output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
