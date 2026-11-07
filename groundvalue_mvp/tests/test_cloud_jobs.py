import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
import projects
from core import Property
from cloud_jobs import CloudResearchJobs,Prepared
from tinyfish_client import AgentError
class CloudJobsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  for p in [patch.object(projects,'DB',Path(self.tmp.name)/'cloud.db'),patch('cloud_jobs.checkpoint'),patch('cloud_jobs.load_key',return_value='test')]:
   p.start();self.addCleanup(p.stop)
  self.pid=projects.create('Test',{});self.manager=CloudResearchJobs()
 def start_ready(self):
  self.manager.start(Property(),['NoBroker'],'test',self.pid)
  with patch('cloud_jobs.research',side_effect=Prepared('https://nobroker.in/property/buy/test','goal')):self.manager.snapshot()
 def test_resume_after_process_restart(self):
  self.start_ready()
  with patch('cloud_jobs.TinyFish.request',return_value={'run_id':'external-1'}) as request:
   CloudResearchJobs().snapshot();self.assertEqual(request.call_count,1)
  with patch('cloud_jobs.TinyFish.request',return_value={'status':'COMPLETED','result':{'listings':[]}}) as request:
   result=CloudResearchJobs().snapshot();self.assertEqual(result['state'],'completed');self.assertEqual(request.call_args.args[0],'GET');self.assertIsNotNone(result['report'])
 def test_ambiguous_launch_never_replayed(self):
  self.start_ready()
  with patch('cloud_jobs.TinyFish.request',side_effect=AgentError('Timed out')) as request:
   CloudResearchJobs().snapshot();CloudResearchJobs().snapshot();self.assertEqual(request.call_count,1)
  self.assertEqual(self.manager._load()['state'],'failed')
 def test_interrupted_submission_does_not_launch_again(self):
  self.start_ready();job=self.manager._load();job['sources']['NoBroker']['status']='submitting';self.manager._save(job)
  with patch('cloud_jobs.TinyFish.request') as request:
   result=CloudResearchJobs().snapshot();request.assert_not_called();self.assertEqual(result['state'],'failed')
 def test_poll_error_keeps_remote_job(self):
  self.start_ready()
  with patch('cloud_jobs.TinyFish.request',return_value={'run_id':'external-1'}):self.manager.snapshot()
  with patch('cloud_jobs.TinyFish.request',side_effect=AgentError('Temporary network error')):
   result=CloudResearchJobs().snapshot();self.assertEqual(result['state'],'running');self.assertEqual(result['sources']['NoBroker']['run_id'],'external-1')
