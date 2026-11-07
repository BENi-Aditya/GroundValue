"""Append-only analyst decisions and external evidence, stored beside research."""
import json
import uuid
from datetime import datetime, timezone
import projects
from core import safe_url

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS case_events(id TEXT PRIMARY KEY,project_id TEXT,run_id TEXT,kind TEXT,created TEXT,payload TEXT)')

def append(pid, kind, payload, run_id=None):
    event = dict(id=uuid.uuid4().hex, project_id=pid, run_id=run_id, kind=kind,
                 created=projects.now(), payload=payload)
    with projects.connect() as db:
        initialize(db)
        db.execute('INSERT INTO case_events VALUES(?,?,?,?,?,?)',
                   (event['id'],pid,run_id,kind,event['created'],json.dumps(payload,allow_nan=False)))
    return event

def events(pid):
    with projects.connect() as db:
        initialize(db)
        return [dict(r,payload=json.loads(r['payload'])) for r in db.execute(
            'SELECT * FROM case_events WHERE project_id=? ORDER BY created DESC',(pid,))]

def assessment(report):
    report=report or {}
    records=report.get('records',[])
    accepted=[r for r in records if r.get('included')]
    flags=['Asking-price evidence is not a verified collateral valuation.']
    if not report.get('estimate'): flags.append('Too few usable comparisons to calculate an asking-price estimate.')
    if len({r.get('source_domain') for r in accepted})<2: flags.append('Fewer than two independent listing sources.')
    if any(not r.get('listed_at') for r in accepted): flags.append('Some listing dates are unknown.')
    if any(j.get('status')!='completed' for j in report.get('jobs',[])): flags.append('One or more research sources did not finish.')
    if report.get('mode')=='sample': flags.append('Synthetic sample: not eligible as lending evidence.')
    return {'outcome':'refer','label':'Independent valuation required','flags':flags,
            'accepted':len(accepted),'excluded':len(records)-len(accepted),
            'confidence':'Not calibrated','policy_version':'research-review-v1',
            'next_step':'Review source evidence and request an independent valuation before a collateral decision.'}

def decision(pid, data):
    if data.get('decision') not in ('request_evidence','refer_valuer','research_reviewed'):
        raise ValueError('Choose a supported review decision.')
    for key in ('reviewer','reason'):
        if not isinstance(data.get(key),str) or not 2<=len(data[key].strip())<=2000:
            raise ValueError('Reviewer and a clear reason are required.')
    run=next((r for r in projects.runs(pid) if r['id']==data.get('run_id')),None)
    if not run: raise ValueError('Select a saved research run to review.')
    return append(pid,'review',{'reviewer':data['reviewer'].strip(),'reason':data['reason'].strip(),
        'decision':data['decision'],'assessment':assessment(run['snapshot'].get('report')),
        'notice':'Reviewer name is self-declared in this single-workspace prototype; this is not a credit approval.'},run['id'])

def evidence(pid,data):
    if data.get('category') not in ('transaction','government','geospatial','infrastructure','imagery','market','property'):
        raise ValueError('Unsupported evidence category.')
    url=safe_url(data.get('source_url'))
    if not url: raise ValueError('Provide a valid HTTPS source citation.')
    for key in ('title','notes','access_basis'):
        if not isinstance(data.get(key),str) or not 2<=len(data[key].strip())<=6000:
            raise ValueError('Title, findings and access basis are required.')
    try:
        observed=datetime.fromisoformat(data['observed_at']).date()
        if observed>datetime.now(timezone.utc).date(): raise ValueError()
    except (KeyError,ValueError,TypeError): raise ValueError('Provide a valid observation date, not in the future.')
    return append(pid,'evidence',{**{k:data[k].strip() for k in ('category','title','notes','access_basis')},
        'source_url':url,'observed_at':str(observed),'verification':'Analyst supplied; not independently verified',
        'usage':'Context only. Not automatically merged into the asking-price estimate.'})
