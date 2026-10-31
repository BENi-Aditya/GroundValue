import unittest
from threading import Event
from jobs import ResearchJobs
from core import Property

class JobTests(unittest.TestCase):
 def test_duplicate_start_and_stop(self):
  entered=Event();ended=Event()
  def runner(target,names,client,notify,cancel):
   entered.set();cancel.wait(2);ended.set();return {'mode':'live'}
  manager=ResearchJobs(runner=runner,saver=lambda r:r,client_factory=lambda key:None)
  job=manager.start(Property(),['Housing.com'],'fake-key');self.assertTrue(entered.wait(1))
  with self.assertRaises(ValueError):manager.start(Property(),['Housing.com'],'fake-key')
  self.assertEqual(manager.snapshot()['id'],job)
  manager.stop();self.assertTrue(ended.wait(1))
 def test_actions_deduplicate_and_snapshots_are_independent(self):
  manager=ResearchJobs();manager._job={'sources':{},'events':[]}
  event={'source':'Housing.com','status':'running','steps':[{'id':'a','action':'Open listing'}]}
  manager._progress(event);manager._progress(event)
  snapshot=manager.snapshot()
  self.assertEqual(len([x for x in snapshot['events'] if x['kind']=='action']),1)
  snapshot['events'].clear();self.assertEqual(len(manager.snapshot()['events']),2)
