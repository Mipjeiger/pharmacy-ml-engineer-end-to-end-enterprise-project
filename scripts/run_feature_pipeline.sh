#!/bin/bash
set -e

echo "==============================="
echo "START PHARMACY FEATURE PIPELINE"
echo "==============================="

python3 scripts/run_offline_features.py

feast apply

feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")

python3 scripts/slack_notify.py --message "✅ Feature pipeline completed successfully."

echo "=================================="
echo " PIPELINE FINISHED SUCCESSFULLY "
echo "=================================="