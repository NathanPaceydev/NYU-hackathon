#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
"$PYTHON_BIN" src/run.py
"$PYTHON_BIN" src/validate.py
"$PYTHON_BIN" src/practical_comparisons.py
"$PYTHON_BIN" src/report.py
"$PYTHON_BIN" src/presentation_data.py
"$PYTHON_BIN" src/build_html.py
"$PYTHON_BIN" src/figure_gallery.py
