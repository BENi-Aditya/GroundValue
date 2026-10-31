"""Bounded asynchronous TinyFish client. Never logs credentials or raw errors."""
import json, time, os
from urllib.parse import quote
from pathlib import Path
import requests
from core import safe_url

BASE='https://agent.tinyfish.ai'
FIELDS=['title','project','city','locality','property_type','transaction_type','price_raw','area_raw','area_basis','source_url','listed_at']
SCHEMA={'type':'object','properties':{'listings':{'type':'array','maxItems':10,'items':{'type':'object','properties':{
 **{k:{'type':'string','nullable':True} for k in FIELDS},'bedrooms':{'type':'integer','nullable':True}},'required':FIELDS+['bedrooms']}}},'required':['listings']}
SCHEMA['properties']['notes']={'type':'string'}

class AgentError(RuntimeError):pass
class ResearchCancelled(AgentError):pass

def load_key():
    value=os.environ.get('TINYFISH_API_KEY','').strip()
    if value:return value
    path=Path(__file__).parent/'.env'
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith('TINYFISH_API_KEY='):return line.split('=',1)[1].strip().strip('"\'')
    return ''

class TinyFish:
    def __init__(self,key,session=None):
        if not key:raise AgentError('TinyFish API key is not configured.')
        self.session=session or requests.Session()
        self.session.headers.update({'X-API-Key':key,'Content-Type':'application/json'})

    def request(self,method,path,payload=None,timeout=20):
        try:
            r=self.session.request(method,BASE+path,json=payload,timeout=timeout,allow_redirects=False)
            if r.status_code>=300:raise AgentError(f'TinyFish returned HTTP {r.status_code}. Check account access, credits and request configuration.')
            d=r.json()
            if not isinstance(d,dict):raise AgentError('TinyFish returned an unexpected response format.')
            return d
        except (requests.RequestException,ValueError) as exc:
            raise AgentError('TinyFish request failed or timed out. The provider may still have accepted the job; no automatic resubmission was made.') from None

    def search(self,query,domain):
        try:
            r=self.session.get('https://api.search.tinyfish.ai',params={
                'query':query,'include_domains':domain,'location':'IN','language':'en'},
                timeout=25,allow_redirects=False)
            if r.status_code!=200:raise AgentError(f'TinyFish search returned HTTP {r.status_code}.')
            data=r.json()
            if not isinstance(data,dict) or not isinstance(data.get('results'),list):
                raise AgentError('TinyFish search returned an unexpected result.')
            return [dict(x,url=safe_url(x.get('url'),[domain])) for x in data['results']
                    if isinstance(x,dict) and safe_url(x.get('url'),[domain])]
        except (requests.RequestException,ValueError):
            raise AgentError('TinyFish search could not finish. No browsing job was started.') from None

    def run(self,url,goal,schema=SCHEMA,seconds=420,on_progress=None,cancel=None):
        progress=on_progress or (lambda _:None)
        started=time.monotonic();deadline=started+seconds
        if cancel and cancel.is_set():raise ResearchCancelled('Research stopped before starting.')
        queued=self.request('POST','/v1/automation/run-async',{'url':url,'goal':goal,'output_schema':schema,'agent_config':{'max_duration_seconds':seconds}},timeout=min(20,seconds))
        run_id=queued.get('run_id')
        if not run_id or queued.get('error'):raise AgentError('TinyFish did not confirm a run ID. Check the provider dashboard before retrying.')
        path='/v1/runs/'+quote(str(run_id),safe='')
        progress({'run_id':str(run_id),'status':'queued'})
        terminal=False
        try:
            while time.monotonic()<deadline:
                if cancel and cancel.is_set():raise ResearchCancelled('Research stopped at your request.')
                remaining=deadline-time.monotonic()
                if remaining<=0:break
                result=self.request('GET',path,timeout=max(.1,min(15,remaining)))
                status=str(result.get('status','')).upper()
                steps=[{'id':str(s.get('id','')), 'action':str(s.get('action',''))[:2000],
                        'timestamp':str(s.get('timestamp',''))} for s in result.get('steps',[]) or []
                       if isinstance(s,dict) and s.get('action')][-150:]
                progress({'run_id':str(run_id),'status':status.lower() or 'unknown',
                          'elapsed_seconds':round(time.monotonic()-started), 'steps':steps,
                          'streaming_url':result.get('streaming_url')})
                if status in ('COMPLETED','FAILED','CANCELLED'):
                    terminal=True
                    if status!='COMPLETED':
                        error=result.get('error') or {}
                        code=error.get('code','') if isinstance(error,dict) else ''
                        raise AgentError(f'TinyFish job {status.lower()}'+(f' ({code})' if code else '')+'. No evidence was accepted.')
                    value=result.get('result')
                    if not isinstance(value,dict):raise AgentError('Completed TinyFish job has no structured result.')
                    return {'run_id':str(run_id),'result':value,'steps':result.get('num_of_steps') or len(steps)}
                pause=min(2,max(0,deadline-time.monotonic()))
                if cancel:cancel.wait(pause)
                else:time.sleep(pause)
            raise AgentError('Research exceeded its time limit.')
        finally:
            if not terminal:
                try:
                    cancelled=self.request('POST',path+'/cancel',{},timeout=10)
                    state=cancelled.get('status','').upper()
                    note='cancellation confirmed' if state=='CANCELLED' else ('run already '+state.lower() if state in ('COMPLETED','FAILED') else 'cancellation requested; confirmation pending')
                    progress({'run_id':str(run_id),'status':note})
                except AgentError:
                    progress({'run_id':str(run_id),'status':'remote cancellation unconfirmed; check provider dashboard'})
