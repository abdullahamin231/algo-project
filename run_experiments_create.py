import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from run_experiments_common import (
    STRUCTURE_CLASSES,
    STRUCTURE_ORDER,
    generate_synthetic_posts,
    load_posts,
    print_results_table,
    run_trial,
)


def main():
    parser = argparse.ArgumentParser(
        description="Run identical workloads on BST and Treap and save the collected metrics."
    )
    parser.add_argument("--dataset", type=str, help="Path to JSON lines dataset (id, created_utc, score).")
    parser.add_argument("--sample-size", type=int, default=1000, help="Number of posts to use from dataset or generator.")
    parser.add_argument("--search-trials", type=int, default=200, help="Number of tree search operations per structure.")
    parser.add_argument("--delete-ratio", type=float, default=0.2, help="Fraction of posts deleted after insertions.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed to keep trials reproducible.")
    parser.add_argument("--output-dir", type=str, default="results", help="Directory for the metrics file.")
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Full path for the metrics JSON file (overrides --output-dir).",
    )
    args = parser.parse_args()

    if args.dataset:
        posts = load_posts(args.dataset, args.sample_size)
    else:
        posts = generate_synthetic_posts(args.sample_size, args.seed)

    results = {}
    for structure in STRUCTURE_ORDER:
        trial_rng = random.Random(args.seed)
        feed_cls = STRUCTURE_CLASSES[structure]
        results[structure] = run_trial(feed_cls, posts, args.search_trials, args.delete_ratio, trial_rng)

    print_results_table(results, STRUCTURE_ORDER)

    metadata: Mapping[str, object] = {
        "dataset": args.dataset or "synthetic",
        "sample_size": args.sample_size,
        "search_trials": args.search_trials,
        "delete_ratio": args.delete_ratio,
        "seed": args.seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    metrics_payload = {"metadata": metadata, "results": results}
    output_dir = Path(args.output_dir)
    if args.output_file:
        metrics_path = Path(args.output_file)
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        metrics_path = output_dir / "metrics.json"

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"\nMetrics saved to {metrics_path}")
    print(f"Plot them with `python3 run_experiments_plot.py --metrics-file {metrics_path}`")


if __name__ == "__main__":
    main()
