#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

DIR="results/batch_runs"
OUTDIR="results"

if [ ! -d "$DIR" ]; then
    echo "Directory $DIR not found" >&2
    exit 1
fi

for f in "$DIR"/*.json; do
    [ -e "$f" ] || continue
    fname=$(basename "$f")
    outname="${fname%.json}.png"
    echo "Processing: $f -> $OUTDIR/$outname"
    python3 run_experiments_plot.py --metrics-file "$f" --output-file "$OUTDIR/$outname"
done