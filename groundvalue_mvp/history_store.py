import sqlite3,json
from contextlib import closing
from pathlib import Path

def recent_reports(limit=6, path=None):
    """Read recent reports for the workspace without changing saved history."""
    path=Path(path or Path(__file__).parent/'data'/'reports.sqlite3')
    if not path.exists(): return []
    with closing(sqlite3.connect(path)) as db:
        try:
            rows=db.execute('SELECT payload FROM reports ORDER BY created DESC LIMIT ?', (limit,)).fetchall()
        except sqlite3.OperationalError: return []
    return [json.loads(row[0]) for row in rows]
