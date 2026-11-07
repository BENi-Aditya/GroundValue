"""Provider-owned research runs, resumed in bounded HTTP requests.

No daemon thread or open browser session is required for a submitted provider run.
Polling records results and advances to the next selected source. An ambiguous
submission is never retried automatically.
"""
import json,time,uuid
from dataclasses import asdict
from urllib.parse import quote
import projects
from core import Property,analyse,safe_url
from research import research,SOURCES,SOURCE_SECONDS
from tinyfish_client import TinyFish,AgentError,SCHEMA,load_key
from cloud_storage import checkpoint

class Prepared(BaseException):
    def __init__(self,url,goal):self.url=url;self.goal=goal
class PreparingClient(TinyFish):
    def run(self,url,goal,**kwargs):raise Prepared(url,goal)

class CloudResearchJobs:
    def _load(self):
        with projects.connect() as db:
            row=db.execute('SELECT snapshot FROM project_runs ORDER BY started DESC LIMIT 1').fetchone()
        return json.loads(row[0]) if row else None
    def _save(self,job):
        projects.record(job['project_id'],job,job['input']);checkpoint()
    def _event(self,job,name,status,message):
        job['events'].append({'source':name,'kind':'status','message':message,'at':projects.now()})
        job['events']=job['events'][-200:]
    def start(self,target,names,key,project_id=None):
        target.validate();previous=self._load()
        if previous and previous['state']=='running':raise ValueError('Research is already running. Watch or stop it first.')
        job={'id':uuid.uuid4().hex,'state':'running','started':time.time(),'events':[],
             'sources':{n:{'status':'queued'} for n in names},'names':names,'observations':[],
             'report':None,'error':None,'stop_requested':False,'project_id':project_id,'input':asdict(target)}
        self._event(job,'GroundValue','queued','Research queued. Progress is saved between requests.')
        self._save(job);return job['id']
    def snapshot(self):
        job=self._load()
        if job and job['state']=='running':self._advance(job)
        if job:
            # Keep internal launch goals and raw observations off the public response.
            result=json.loads(json.dumps(job));result.pop('observations',None)
            for source in result['sources'].values():source.pop('launch',None)
            return result
        return None
    def _advance(self,job):
        target=Property(**{k:v for k,v in job['input'].items() if k in Property.__dataclass_fields__})
        client=TinyFish(load_key())
        names=job.get('names',list(job['sources']))
        for name in names:
            source=job['sources'][name];status=source['status'];domain=SOURCES[name][1]
            if status in ('completed','failed','cancelled'):continue
            try:
                if status=='queued':
                    try:
                        report=research(target,[name],PreparingClient(load_key()))
                        source.update(status='failed',error=next((j.get('error') for j in report.get('jobs',[]) if j.get('error')),'No starting page found.'))
                    except Prepared as prepared:
                        source.update(status='ready',launch={'url':prepared.url,'goal':prepared.goal,'output_schema':SCHEMA,'agent_config':{'max_duration_seconds':SOURCE_SECONDS}})
                        self._event(job,name,'ready','Source page discovered. Browser job is ready to start.')
                elif status=='ready':
                    source['status']='submitting';self._save(job)
                    result=client.request('POST','/v1/automation/run-async',source['launch'],timeout=20)
                    if not result.get('run_id'):raise AgentError('Provider did not confirm a run ID. Check its dashboard before retrying.')
                    source.update(status='running',run_id=str(result['run_id']),submitted=time.time());source.pop('launch',None)
                    self._event(job,name,'running','Live browser research started. You can leave and return to this workspace.')
                elif status=='submitting':
                    source.update(status='failed',error='Submission was interrupted. Check the provider dashboard before retrying. No automatic resubmission occurred.')
                else:
                    result=client.request('GET','/v1/runs/'+quote(source['run_id'],safe=''),timeout=15)
                    state=str(result.get('status','')).upper()
                    source['streaming_url']=result.get('streaming_url')
                    source['elapsed_seconds']=int(time.time()-source.get('submitted',time.time()))
                    steps=[x for x in (result.get('steps') or []) if isinstance(x,dict) and x.get('action')][-150:]
                    previous=set(source.get('seen_steps',[]))
                    for step in steps:
                        ident=str(step.get('id') or str(step.get('timestamp',''))+step['action'])
                        if ident not in previous:self._event(job,name,'action',str(step['action'])[:2000]);previous.add(ident)
                    source['seen_steps']=list(previous)[-200:]
                    if state=='COMPLETED':
                        payload=result.get('result') or {};listings=payload.get('listings')
                        if not isinstance(listings,list) or len(listings)>10:raise AgentError('Provider returned an invalid listings result.')
                        for row in listings:
                            if isinstance(row,dict):job['observations'].append(dict(row,source_url=safe_url(row.get('source_url'),[domain]),retrieved_at=projects.now(),job_source=name))
                        source.update(status='completed',count=len(listings),notes=str(payload.get('notes',''))[:4000])
                        self._event(job,name,'completed',f'Received {len(listings)} records. Checking comparability.')
                    elif state in ('FAILED','CANCELLED'):
                        source.update(status=state.lower(),error='Provider run '+state.lower()+'. No evidence accepted.')
                    elif source['elapsed_seconds']>SOURCE_SECONDS+180:
                        try:client.request('POST','/v1/runs/'+quote(source['run_id'],safe='')+'/cancel',{},timeout=10)
                        except AgentError:pass
                        source.update(status='failed',error='Provider time limit exceeded. Check its dashboard for final status.')
            except AgentError as error:
                # A transient status read can be retried safely. A POST submission cannot.
                if status in ('queued','ready','submitting'):source.update(status='failed',error=str(error))
                else:source['last_poll_error']=str(error)
                self._event(job,name,'error',str(error))
            self._finish_if_ready(job,target,names)
            job['elapsed_seconds']=int(time.time()-job['started']);self._save(job);return
        self._finish_if_ready(job,target,names);self._save(job)
    def _finish_if_ready(self,job,target,names):
        if not all(s['status'] in ('completed','failed','cancelled') for s in job['sources'].values()):return
        jobs=[dict(s,source=n) for n,s in job['sources'].items()]
        job['report']=analyse(target,job['observations'],'live',jobs,domains=[SOURCES[n][1] for n in names])
        job['report'].update(report_id=uuid.uuid4().hex,created_at=projects.now())
        job['state']='completed' if any(s['status']=='completed' for s in jobs) else 'failed'
    def stop(self):
        job=self._load()
        if not job or job['state']!='running':return
        client=TinyFish(load_key())
        for name,source in job['sources'].items():
            if source['status'] in ('completed','failed','cancelled'):continue
            if source.get('run_id'):
                try:client.request('POST','/v1/runs/'+quote(source['run_id'],safe='')+'/cancel',{},timeout=10)
                except AgentError:source['error']='Remote cancellation unconfirmed. Check the provider dashboard.'
            source['status']='cancelled'
        job.update(state='stopped',stop_requested=True);self._event(job,'GroundValue','stopped','Stop requested. Saved research remains available.');self._save(job)
