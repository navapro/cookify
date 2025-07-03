#!/usr/bin/env sh
set -euo pipefail

# Paths to your Python scripts (adjust as needed)
PY1="reset_and_create_tables.py"
PY2="sample_data_hydrate-db.py"
PY3="hydrate-db.py"

echo "Running ${PY1}..."
python3 "${PY1}"

echo "Running ${PY2}..."
python3 "${PY2}"

echo "Running ${PY3}..."
python3 "${PY3}"

echo "All scripts completed successfully."
