#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/groundvalue_mvp"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
if ! .venv/bin/python -c 'import flask, waitress, requests, numpy' 2>/dev/null; then
  .venv/bin/python -m pip install -r requirements-web.txt
fi
exec .venv/bin/python web.py
