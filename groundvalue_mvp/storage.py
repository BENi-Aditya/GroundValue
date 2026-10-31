import sqlite3,json,uuid,os,tempfile
from contextlib import closing
from datetime import datetime,timezone
from pathlib import Path

def save(report, path=None):
    if path is None:
        if os.environ.get('STREAMLIT_SHARING_MODE') or not os.access(Path(__file__).parent, os.W_OK):
            path = Path(tempfile.gettempdir()) / 'groundvalue_reports.sqlite3'
        else:
            path = Path(__file__).parent / 'data' / 'reports.sqlite3'
    else:
        path = Path(path)
    print(f"[DEBUG storage.save] Saving report to: {path}")
    path.parent.mkdir(parents=True,exist_ok=True)
    report=dict(report,report_id=uuid.uuid4().hex,created_at=datetime.now(timezone.utc).isoformat())
    print(f"[DEBUG storage.save] Report ID: {report['report_id']}, Mode: {report.get('mode')}")
    print(f"[DEBUG storage.save] Report has {len(report.get('comparisons', []))} comparisons")
    with closing(sqlite3.connect(path)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS reports (id TEXT PRIMARY KEY, created TEXT NOT NULL, mode TEXT NOT NULL, payload TEXT NOT NULL)')
        db.execute('INSERT INTO reports VALUES (?,?,?,?)',(report['report_id'],report['created_at'],report['mode'],json.dumps(report,allow_nan=False)))
        db.commit()
    print(f"[DEBUG storage.save] Report saved successfully to database")
    return report

def latest_live(path=None):
    if path is None:
        if os.environ.get('STREAMLIT_SHARING_MODE') or not os.access(Path(__file__).parent, os.W_OK):
            path = Path(tempfile.gettempdir()) / 'groundvalue_reports.sqlite3'
        else:
            path = Path(__file__).parent / 'data' / 'reports.sqlite3'
    else:
        path = Path(path)
    if not path.exists():return None
    with closing(sqlite3.connect(path)) as db:
        try:
            row=db.execute("SELECT payload FROM reports WHERE mode='live' ORDER BY created DESC LIMIT 1").fetchone()
        except sqlite3.OperationalError:return None
    return json.loads(row[0]) if row else None
