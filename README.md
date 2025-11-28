# Treap vs BST Experiment Runner

The workload is split into two scripts so you can create the experimental metrics
independently from the visualization step.

## Generate metrics

```bash
python3 run_experiments_create.py \
    --dataset path/to/posts.jsonl \
    --sample-size 2000 \
    --search-trials 500 \
    --delete-ratio 0.25 \
    --output-dir results
```

Arguments:
- `--dataset`: Optional JSON lines dataset (each line needs `id`, `created_utc`, `score`). If omitted, a synthetic dataset is generated.
- `--sample-size`: Number of posts to load/use (default: 1000).
- `--search-trials`: Number of tree searches executed per structure (default: 200).
- `--delete-ratio`: Fraction of posts deleted after all insertions (default: 0.2).
- `--seed`: Random seed to keep trials reproducible (default: 42).
- `--output-dir`: Directory under which the metrics JSON file is written (default: `results`).
- `--output-file`: Optional override for the metrics file path (default: `results/metrics.json`).

The script prints a metric table and writes a JSON payload that captures the metadata
and per-structure metrics.

## Plot the results

```bash
python3 run_experiments_plot.py --metrics-file results/metrics.json --output-dir results
```

Arguments:
- `--metrics-file`: Path to the JSON file produced by `run_experiments_create.py`.
- `--output-dir`: Directory where the visualization image `treap_vs_bst_metrics.png` will be saved (default: `results`).

The plotting script reloads the metrics file, echoes the metadata and the same metric
table, and saves a grouped-bar PNG that compares average operation times along with
tree height and balance factor for both structures.
