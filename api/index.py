"""Explicit Vercel Python function entrypoint."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'groundvalue_mvp'))
from web import app
