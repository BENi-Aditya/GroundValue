"""Session-independent web workspace. Run with python web.py, no Streamlit required."""
import os,json,secrets
from pathlib import Path
from io import BytesIO
from urllib.parse import urlsplit
from flask import request,jsonify,send_from_directory,send_file,Response
from api import app
import projects,review,model_lab
from jobs import get_manager
from tinyfish_client import load_key
from report import html_report,csv_report
from excel_export import workbook

BASE=Path(__file__).parent
app.config['MAX_CONTENT_LENGTH']=8*1024*1024

@app.before_request
def access():
    if not request.path.startswith('/api/'): return
    if request.method not in ('GET','HEAD','OPTIONS'):
        origin=request.headers.get('Origin')
        if origin and urlsplit(origin).netloc!=request.host:
            return jsonify(error='Cross-origin write rejected'),403
    token=os.environ.get('GROUNDVALUE_ACCESS_TOKEN','')
    if not token and request.host.split(':')[0] not in ('localhost','127.0.0.1','[::1]'):
        return jsonify(error='Local workspace requires a localhost address.'),403
    if token and request.path!='/api/session' and not secrets.compare_digest(request.headers.get('Authorization',''), 'Bearer '+token):
        return jsonify(error='Workspace access key required'),401

if os.environ.get('VERCEL'):
    from cloud_storage import install
    install(app)

@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    if request.path.startswith('/api/'): response.headers['Cache-Control']='no-store'
    return response

@app.errorhandler(413)
def too_large(error): return jsonify(error='Upload must be under 8 MB.'),413

@app.errorhandler(ValueError)
def invalid(error): return jsonify(error=str(error)),400

@app.get('/')
def landing():
    if request.args.get('view')=='app': return send_from_directory(BASE/'webapp','index.html')
    return send_from_directory(BASE/'landing','index.html')

@app.get('/app')
@app.get('/app/<path:route>')
def workspace(route=''): return send_from_directory(BASE/'webapp','index.html')

@app.get('/assets/<path:filename>')
def assets(filename): return send_from_directory(BASE/'webapp',filename)

@app.get('/scene.js')
@app.get('/three.module.js')
def scene(): return send_from_directory(BASE/'landing',request.path.lstrip('/'))

@app.get('/health')
def health(): return jsonify(status='ok',service='groundvalue-web')

@app.get('/api/session')
def session(): return jsonify(access_key_required=bool(os.environ.get('GROUNDVALUE_ACCESS_TOKEN')))

@app.get('/api/settings')
def settings(): return jsonify(provider_configured=bool(load_key()),storage='Private cloud snapshots' if os.environ.get('VERCEL') else 'SQLite on this server',
    engine='Flask on Vercel' if os.environ.get('VERCEL') else 'Flask + Waitress',research_scope='Electronic City, Bengaluru · apartments',
    browser_session_required=False,access_control=bool(os.environ.get('GROUNDVALUE_ACCESS_TOKEN')),
    model_scope='Imported transaction data; evaluated categories only')

def require_project(pid):
    prop=projects.get(pid)
    if not prop: raise ValueError('Property not found or archived.')
    return prop

def body():
    data=request.get_json(silent=True)
    if not isinstance(data,dict): raise ValueError('Send a JSON object.')
    return data

@app.get('/api/workspace/<pid>')
def case(pid):
    prop=require_project(pid);runs=projects.runs(pid)
    for run in runs: run['assessment']=review.assessment(run['snapshot'].get('report'))
    return jsonify(property=prop,runs=runs,events=review.events(pid),
        assessment=review.assessment(runs[0]['snapshot'].get('report') if runs else None))

@app.patch('/api/properties/<pid>')
def edit_property(pid):
    prop=require_project(pid);data=body();name=data.get('name','')
    if not isinstance(name,str) or not 1<=len(name.strip())<=180: raise ValueError('Use a property name of 1–180 characters.')
    details=prop['details']
    if 'details' in data:
        from core import Property
        job=get_manager().snapshot()
        if job and job['state']=='running' and job.get('project_id')==pid: raise ValueError('Wait for or stop research before changing property details.')
        if not isinstance(data['details'],dict): raise ValueError('Property details must be an object.')
        details={**details,**{k:v for k,v in data['details'].items() if k in ('bedrooms','area','unit','area_basis','notes')}}
        Property(**{k:v for k,v in details.items() if k in Property.__dataclass_fields__}).validate()
        if not isinstance(details.get('notes',''),str) or len(details.get('notes',''))>6000: raise ValueError('Keep notes under 6,000 characters.')
    with projects.connect() as db:
        db.execute('UPDATE projects SET name=?,details=?,updated=? WHERE id=?',(name.strip(),json.dumps(details),projects.now(),pid))
    review.append(pid,'property_updated',{'name':name.strip(),'details':details,'previous_details':prop['details']})
    return jsonify(ok=True)

@app.delete('/api/properties/<pid>')
def archive_property(pid):
    require_project(pid);job=get_manager().snapshot()
    if job and job['state']=='running' and job.get('project_id')==pid: raise ValueError('Stop active research before archiving.')
    review.append(pid,'archived',{'reason':'Archived from workspace'});projects.archive(pid)
    return jsonify(ok=True)

@app.get('/api/archive')
def archived():
    with projects.connect() as db:
        rows=[dict(r,details=json.loads(r['details'])) for r in db.execute('SELECT * FROM projects WHERE archived=1 ORDER BY updated DESC')]
    return jsonify(rows)

@app.post('/api/properties/<pid>/restore')
def restore(pid):
    with projects.connect() as db:
        changed=db.execute('UPDATE projects SET archived=0,updated=? WHERE id=? AND archived=1',(projects.now(),pid)).rowcount
    if not changed: raise ValueError('Archived property not found.')
    review.append(pid,'restored',{});return jsonify(ok=True)

@app.get('/api/history')
def history():
    with projects.connect() as db:
        rows=[dict(r) for r in db.execute('SELECT r.id,r.project_id,r.status,r.started,r.updated,p.name FROM project_runs r JOIN projects p ON p.id=r.project_id WHERE p.archived=0 ORDER BY r.started DESC')]
    return jsonify(rows)

@app.get('/api/research/active')
def active(): return jsonify(get_manager().snapshot())

@app.post('/api/research/<job_id>/stop')
def stop(job_id):
    manager=get_manager();job=manager.snapshot()
    if not job or job['id']!=job_id or job['state']!='running': raise ValueError('This run is not active.')
    manager.stop();return jsonify(ok=True)

@app.post('/api/properties/<pid>/review')
def add_review(pid): require_project(pid);return jsonify(review.decision(pid,body())),201

@app.post('/api/properties/<pid>/evidence')
def add_evidence(pid): require_project(pid);return jsonify(review.evidence(pid,body())),201

@app.get('/api/properties/<pid>/export/<kind>')
def export(pid,kind):
    prop=require_project(pid);runs=projects.runs(pid)
    if kind=='xlsx':
        return send_file(BytesIO(workbook(prop,runs)),as_attachment=True,download_name='groundvalue-'+pid[:8]+'.xlsx',mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if kind=='json':
        payload={'property':prop,'runs':runs,'audit_trail':review.events(pid)}
        return Response(json.dumps(payload,indent=2),mimetype='application/json',headers={'Content-Disposition':'attachment; filename=groundvalue-audit.json'})
    selected=request.args.get('run')
    run=next((r for r in runs if r['id']==selected),None) if selected else next((r for r in runs if r['snapshot'].get('report')),None)
    report=run['snapshot'].get('report') if run else None
    if not report: raise ValueError('This run has no report to export yet.')
    if kind not in ('html','csv'): raise ValueError('Unknown export format.')
    return Response(html_report(report) if kind=='html' else csv_report(report),
        mimetype='text/html' if kind=='html' else 'text/csv',headers={'Content-Disposition':f'attachment; filename=groundvalue-report.{kind}'})

@app.get('/api/models')
def models(): return jsonify(model_lab.listing())

@app.get('/api/datasets/template')
def dataset_template(): return Response(model_lab.template(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=transactions-template.csv'})

@app.post('/api/datasets')
def dataset_upload():
    file=request.files.get('file')
    if not file: raise ValueError('Select a transaction CSV.')
    try: content=file.read().decode('utf-8-sig')
    except UnicodeDecodeError: raise ValueError('Use a UTF-8 CSV file.')
    return jsonify(model_lab.ingest(content,request.form.get('source',''),request.form.get('access_basis',''))),201

@app.post('/api/models/train')
def model_train(): return jsonify(model_lab.train(body().get('dataset_id'))),201

@app.post('/api/properties/<pid>/predict')
def model_predict(pid):
    require_project(pid);data=body()
    if not isinstance(data.get('features'),dict): raise ValueError('Property features are required.')
    result=model_lab.predict(data.get('model_id'),data['features'])
    return jsonify(review.append(pid,'model_prediction',result)),201

def recover_interrupted():
    """Never silently resubmit paid provider calls after a server restart."""
    with projects.connect() as db:
        rows=db.execute("SELECT id,snapshot FROM project_runs WHERE status='running'").fetchall()
        for row in rows:
            snapshot=json.loads(row['snapshot']);snapshot.update(state='interrupted',error='Server restarted. Check the saved provider run before retrying; no automatic resubmission was made.')
            db.execute('UPDATE project_runs SET status=?,snapshot=?,updated=? WHERE id=?',('interrupted',json.dumps(snapshot),projects.now(),row['id']))

if __name__=='__main__':
    from waitress import serve
    host=os.environ.get('HOST','127.0.0.1');port=int(os.environ.get('PORT','8080'))
    if host not in ('127.0.0.1','localhost','::1') and not os.environ.get('GROUNDVALUE_ACCESS_TOKEN'):
        raise SystemExit('Set GROUNDVALUE_ACCESS_TOKEN before binding the workspace to an external interface.')
    recover_interrupted()
    print(f'GroundValue: http://{host}:{port}/app',flush=True)
    serve(app,host=host,port=port,threads=8)
