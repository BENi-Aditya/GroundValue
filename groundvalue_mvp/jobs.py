"""One local research worker, independent of Streamlit reruns and reconnects."""
from copy import deepcopy
from datetime import datetime,timezone
from threading import Event, Lock, Thread
import time,os
import uuid
from functools import lru_cache
from research import research
from storage import save
from tinyfish_client import TinyFish

@lru_cache(maxsize=1)
def get_manager():
    if os.environ.get('VERCEL'):
        from cloud_jobs import CloudResearchJobs
        return CloudResearchJobs()
    return ResearchJobs()

class ResearchJobs:
    def __init__(self, runner=research, saver=save, client_factory=TinyFish):
        self._runner=runner;self._saver=saver;self._client_factory=client_factory
        self._lock=Lock();self._job=None;self._cancel=Event()

    def snapshot(self):
        with self._lock:return deepcopy(self._job)

    def start(self,target,names,key,project_id=None):
        target.validate()
        with self._lock:
            if self._job and self._job['state']=='running':
                raise ValueError('Research is already running. Watch or stop the existing job.')
            self._cancel=Event()
            self._job={'id':uuid.uuid4().hex,'state':'running','started':time.time(),
                       'events':[],'sources':{},'report':None,'error':None,'stop_requested':False}
            self._job['project_id']=project_id
            from dataclasses import asdict
            self._job['input']=asdict(target)
            self._persist()
            job_id=self._job['id']
        Thread(target=self._work,args=(target,list(names),key),daemon=True,name='groundvalue-research').start()
        return job_id

    def _persist(self):
        if self._job.get('project_id'):
            from projects import record
            record(self._job['project_id'],self._job,self._job['input'])

    def stop(self):
        with self._lock:
            if self._job and self._job['state']=='running':
                self._job['stop_requested']=True;self._cancel.set()

    def _progress(self,event):
        with self._lock:
            source=event.get('source','TinyFish')
            previous=self._job['sources'].setdefault(source,{'seen_steps':[]})
            status=event.get('status','unknown')
            def append(message,kind):
                self._job['events'].append({'source':source,'message':str(message)[:2000],
                    'kind':kind,'at':datetime.now(timezone.utc).isoformat()})
            if status!=previous.get('status'):
                append(event.get('message') or status.replace('_',' ').capitalize(),'status')
            for step in event.get('steps',[]):
                identity=step.get('id') or (step.get('timestamp','')+step.get('action',''))
                if identity not in previous['seen_steps']:
                    previous['seen_steps'].append(identity);append(step['action'],'action')
            previous.update({k:v for k,v in event.items() if k not in ('steps','source')})
            self._job['events']=self._job['events'][-200:]
            self._persist()

    def _work(self,target,names,key):
        try:
            result=self._runner(target,names,self._client_factory(key),notify=self._progress,cancel=self._cancel)
            report=self._saver(result)
            with self._lock:
                failed=bool(result.get('jobs')) and all(j.get('status')!='completed' for j in result['jobs'])
                self._job.update(state='stopped' if self._cancel.is_set() else ('failed' if failed else 'completed'),
                                 report=report,elapsed_seconds=int(time.time()-self._job['started']))
                self._persist()
        except Exception:
            # Do not echo request objects, credentials or raw provider responses.
            with self._lock:
                self._job.update(state='failed',error='Research could not finish. Check the activity log and provider run before retrying.',
                                 elapsed_seconds=int(time.time()-self._job['started']))
                self._persist()
