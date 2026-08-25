#!/bin/bash
# Run (or resume) the Opus extension tier matrix.
# Safe to re-run: --skip-existing skips completed episodes.
# Run from repo root: bash harness/resume_opus_ext.sh
cd "$(dirname "$0")/.." || exit 1
for cond in B E FILE SHARD; do
    n=$(ls runs/opus_ext/$cond/rep1/*.json 2>/dev/null | wc -l | tr -d ' ')
    echo "===== OPUS-EXT COND $cond ($n/88 done) $(date +%H:%M) ====="
    .venv/bin/python harness/run_opus_ext.py --condition $cond --skip-existing
done
echo "===== OPUS-EXT MATRIX COMPLETE ====="
