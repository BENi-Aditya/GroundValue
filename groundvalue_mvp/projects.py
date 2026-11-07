"""Persistent project/run metadata alongside the existing evidence database."""
import sqlite3,json,uuid,os
from contextvars import ContextVar
from pathlib import Path
from contextlib import contextmanager,closing
from datetime import datetime,timezone
DB=Path(os.environ.get('GROUNDVALUE_DB',str(Path(__file__).parent/'data/reports.sqlite3')))
REQUEST_DB=ContextVar('workspace_db',default=None)
def db_path(): return REQUEST_DB.get() or DB
def now(): return datetime.now(timezone.utc).isoformat()
@contextmanager
def connect():
    path=db_path()
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path,timeout=20)) as db:
        db.row_factory=sqlite3.Row
        db.execute('CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT,details TEXT,created TEXT,updated TEXT,archived INTEGER DEFAULT 0)')
        db.execute('CREATE TABLE IF NOT EXISTS project_runs(id TEXT PRIMARY KEY,project_id TEXT,status TEXT,started TEXT,updated TEXT,input TEXT,snapshot TEXT)')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise

def create(name,details):
    pid=uuid.uuid4().hex;t=now()
    with connect() as db: db.execute('INSERT INTO projects VALUES(?,?,?,?,?,0)',(pid,name,json.dumps(details),t,t))
    return pid

def listing():
    with connect() as db: return [dict(r) for r in db.execute('SELECT * FROM projects WHERE archived=0 ORDER BY updated DESC')]
def get(pid):
    with connect() as db:
        r=db.execute('SELECT * FROM projects WHERE id=? AND archived=0',(pid,)).fetchone()
    if not r:return None
    r=dict(r);r['details']=json.loads(r['details']);return r

def rename(pid,name):
    with connect() as db: db.execute('UPDATE projects SET name=?,updated=? WHERE id=?',(name,now(),pid))
def archive(pid):
    with connect() as db: db.execute('UPDATE projects SET archived=1 WHERE id=?',(pid,))
def runs(pid):
    with connect() as db: return [dict(r, snapshot=json.loads(r['snapshot']),input=json.loads(r['input'])) for r in db.execute('SELECT * FROM project_runs WHERE project_id=? ORDER BY started DESC',(pid,))]
def record(pid,job,inputs):
    t=now();snapshot=json.dumps(job,default=str)
    with connect() as db:
        db.execute('INSERT INTO project_runs VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status,updated=excluded.updated,snapshot=excluded.snapshot',(job['id'],pid,job['state'],t,t,json.dumps(inputs),snapshot))
        db.execute('UPDATE projects SET updated=? WHERE id=?',(t,pid))

def import_legacy():
    """Import only actual live reports; synthetic walkthroughs remain in legacy storage."""
    import hashlib
    with connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS imported_reports(id TEXT PRIMARY KEY)')
        try:rows=db.execute("SELECT id,created,payload FROM reports WHERE mode='live'").fetchall()
        except sqlite3.OperationalError:return
        for row in rows:
            if db.execute('SELECT 1 FROM imported_reports WHERE id=?',(row['id'],)).fetchone():continue
            report=json.loads(row['payload']);details=report['property']
            pid='legacy-'+hashlib.sha256(json.dumps(details,sort_keys=True).encode()).hexdigest()[:24]
            name=f"{details.get('bedrooms','')} BHK · {details.get('locality','Electronic City')}"
            db.execute('INSERT OR IGNORE INTO projects VALUES(?,?,?,?,?,0)',(pid,name,json.dumps(details),row['created'],row['created']))
            status='failed' if report.get('jobs') and all(j.get('status')!='completed' for j in report['jobs']) else 'completed'
            snapshot={'id':row['id'],'state':status,'report':report,'events':[],'sources':{},'error':None}
            db.execute('INSERT OR IGNORE INTO project_runs VALUES(?,?,?,?,?,?,?)',(row['id'],pid,status,row['created'],row['created'],json.dumps(details),json.dumps(snapshot)))
            db.execute('INSERT INTO imported_reports VALUES(?)',(row['id'],))
