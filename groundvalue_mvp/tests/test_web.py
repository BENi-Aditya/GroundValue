import unittest,tempfile,json,os
from pathlib import Path
from unittest.mock import patch
from threading import Event
import projects,review,web
from jobs import ResearchJobs
from core import Property

class WebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.patcher=patch.object(projects,'DB',Path(self.tmp.name)/'workspace.sqlite3');self.patcher.start();self.addCleanup(self.patcher.stop)
        self.env=patch.dict(os.environ,{'GROUNDVALUE_ACCESS_TOKEN':''});self.env.start();self.addCleanup(self.env.stop)
        self.client=web.app.test_client()
        self.pid=projects.create('Test property',{'bedrooms':2,'area':1200,'unit':'sq ft','area_basis':'Built-up'})
        self.report={'property':{'bedrooms':2,'area':1200,'unit':'sq ft','area_basis':'Built-up','city':'Bengaluru','locality':'Electronic City'},'mode':'live','method':'test','records':[],'warnings':[],'estimate':None,'jobs':[]}
        projects.record(self.pid,{'id':'run-1','state':'completed','events':[],'sources':{},'report':self.report},self.report['property'])

    def test_shell_and_same_origin_routes(self):
        for url in ('/app','/app/property/test','/?view=app','/assets/app.js','/health'):
            response=self.client.get(url);self.assertEqual(response.status_code,200);response.close()
        response=self.client.get('/');self.assertIn(b'/app?view=app',response.data);response.close()

    def test_archive_restore_keeps_history(self):
        self.assertEqual(self.client.delete('/api/properties/'+self.pid).status_code,200)
        self.assertIsNone(projects.get(self.pid));self.assertEqual(len(projects.runs(self.pid)),1)
        self.assertEqual(self.client.post('/api/properties/'+self.pid+'/restore').status_code,200)
        self.assertEqual(projects.get(self.pid)['name'],'Test property')

    def test_reviews_are_append_only_and_linked_to_run(self):
        for decision in ('request_evidence','refer_valuer'):
            r=self.client.post('/api/properties/'+self.pid+'/review',json={'reviewer':'QA reviewer','reason':'Insufficient source coverage','decision':decision,'run_id':'run-1'})
            self.assertEqual(r.status_code,201)
        events=review.events(self.pid);self.assertEqual(len(events),2)
        self.assertTrue(all(e['run_id']=='run-1' for e in events))
        bad=self.client.post('/api/properties/'+self.pid+'/review',json={'reviewer':'QA','reason':'test','decision':'approve_loan','run_id':'run-1'})
        self.assertEqual(bad.status_code,400)

    def test_edit_details_preserves_historical_inputs(self):
        old=projects.runs(self.pid)[0]['input']
        response=self.client.patch('/api/properties/'+self.pid,json={'name':'Updated property','details':{'area':1500,'bedrooms':3}})
        self.assertEqual(response.status_code,200)
        self.assertEqual(projects.get(self.pid)['details']['area'],1500)
        self.assertEqual(projects.runs(self.pid)[0]['input'],old)
        self.assertEqual(review.events(self.pid)[0]['payload']['previous_details']['area'],1200)

    def test_evidence_does_not_mutate_report(self):
        r=self.client.post('/api/properties/'+self.pid+'/evidence',json={'category':'government','title':'Public register','source_url':'https://example.org/record','observed_at':'2026-01-01','access_basis':'Public citation','notes':'Match needs review'})
        self.assertEqual(r.status_code,201)
        self.assertEqual(projects.runs(self.pid)[0]['snapshot']['report'],self.report)

    def test_exports_have_real_history_and_audit(self):
        for kind in ('html','csv','xlsx','json'):
            r=self.client.get('/api/properties/'+self.pid+'/export/'+kind)
            self.assertEqual(r.status_code,200);self.assertIn('attachment',r.headers['Content-Disposition']);r.close()

    def test_cross_origin_and_access_key(self):
        self.assertEqual(self.client.delete('/api/properties/'+self.pid,headers={'Origin':'https://untrusted.example'}).status_code,403)
        with patch.dict(os.environ,{'GROUNDVALUE_ACCESS_TOKEN':'test-secret'}):
            self.assertEqual(self.client.get('/api/history').status_code,401)
            self.assertEqual(self.client.get('/api/history',headers={'Authorization':'Bearer test-secret'}).status_code,200)

    def test_restart_marks_saved_running_job_interrupted(self):
        projects.record(self.pid,{'id':'running-1','state':'running','sources':{'test':{'run_id':'provider-1'}}},self.report['property'])
        web.recover_interrupted();run=next(r for r in projects.runs(self.pid) if r['id']=='running-1')
        self.assertEqual(run['status'],'interrupted');self.assertEqual(run['snapshot']['sources']['test']['run_id'],'provider-1')

    def test_browser_disconnect_does_not_stop_worker(self):
        started=Event();finish=Event();done=Event()
        def runner(target,names,client,notify,cancel):
            started.set();finish.wait(2);done.set();return self.report
        manager=ResearchJobs(runner=runner,saver=lambda r:r,client_factory=lambda key:None)
        manager.start(Property(),['Housing.com'],'test',project_id=self.pid)
        self.assertTrue(started.wait(1))
        with patch.object(web,'get_manager',return_value=manager):
            first=self.client.get('/api/research/active').json
            # An entirely new HTTP client reconnects to the same server-side job.
            reconnect=web.app.test_client().get('/api/research/active').json
            self.assertEqual(first['id'],reconnect['id']);self.assertEqual(reconnect['state'],'running')
        finish.set();self.assertTrue(done.wait(1))
