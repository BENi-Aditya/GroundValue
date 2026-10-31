import unittest
from unittest.mock import patch
from tinyfish_client import TinyFish,AgentError
from research import research
from core import Property

class ClientTests(unittest.TestCase):
 def test_provider_schema_uses_supported_keywords(self):
  from tinyfish_client import SCHEMA
  allowed={'anyOf','enum','format','items','maxItems','maximum','minItems','minimum','nullable','properties','propertyOrdering','required','type'}
  def check(node):
   self.assertTrue(set(node)<=allowed)
   for child in node.get('properties',{}).values():check(child)
   if 'items' in node:check(node['items'])
  check(SCHEMA)
 def setUp(self):
  self.search=patch.object(TinyFish,'search',return_value=[{'url':'https://housing.com/in/buy/bengaluru/electronic-city-gid/2bhk-fid/','title':'2 BHK sale'}])
  self.search.start();self.addCleanup(self.search.stop)
 def test_completed_contract(self):
  c=TinyFish('fake-key')
  with patch.object(c,'request',side_effect=[{'run_id':'abc'},{'status':'COMPLETED','result':{'listings':[]}}]) as req:
   r=c.run('https://housing.com/','goal',seconds=1)
   self.assertEqual(r['result'],{'listings':[]});self.assertEqual(req.call_count,2)
 def test_failure_not_accepted(self):
  c=TinyFish('fake-key')
  with patch.object(c,'request',side_effect=[{'run_id':'abc'},{'status':'FAILED','result':{'listings':[{}]}}]):
   with self.assertRaises(AgentError):c.run('https://housing.com/','goal',seconds=1)
 def test_no_resubmission_on_unknown_start(self):
  c=TinyFish('fake-key')
  with patch.object(c,'request',side_effect=AgentError('unknown outcome')) as req:
   with self.assertRaises(AgentError):c.run('https://housing.com/','goal',seconds=1)
   self.assertEqual(req.call_count,1)
 def test_read_failure_requests_remote_cancel(self):
  c=TinyFish('fake-key');events=[]
  with patch.object(c,'request',side_effect=[{'run_id':'abc'},AgentError('network failed'),{}]) as req:
   with self.assertRaises(AgentError):c.run('https://housing.com/','goal',seconds=1,on_progress=events.append)
   self.assertEqual(req.call_args.args[:2],('POST','/v1/runs/abc/cancel'))
   self.assertIn('confirmation pending',events[-1]['status'])
 def test_live_failure_does_not_use_samples(self):
  c=TinyFish('fake-key')
  with patch.object(c,'run',side_effect=AgentError('source blocked')):
   r=research(Property(),['Housing.com'],c)
   self.assertIsNone(r['estimate']);self.assertEqual(r['records'],[]);self.assertEqual(r['mode'],'live')
   self.assertEqual(r['jobs'][0]['status'],'failed')
 def test_bad_result_contract(self):
  c=TinyFish('fake-key')
  with patch.object(c,'run',return_value={'run_id':'x','result':{'listings':'bad'}}):
   r=research(Property(),['Housing.com'],c);self.assertIsNone(r['estimate'])
 def test_cancellation_is_retained_in_report(self):
  c=TinyFish('fake-key')
  with patch.object(c,'request',side_effect=[{'run_id':'abc'},AgentError('network failed'),{}]):
   r=research(Property(),['Housing.com'],c)
  self.assertEqual(r['jobs'][0]['run_id'],'abc')
  self.assertIn('confirmation pending',r['jobs'][0]['cancellation'])
  self.assertIsNone(r['estimate'])
 def test_auth_no_redirects(self):
  from unittest.mock import Mock
  session=Mock();session.headers={};response=Mock(status_code=302);session.request.return_value=response
  c=TinyFish('fake-key',session)
  with self.assertRaises(AgentError):c.request('GET','/v1/runs/test')
  self.assertFalse(session.request.call_args.kwargs['allow_redirects'])
 def test_live_steps_and_preview_are_forwarded(self):
  c=TinyFish('fake-key');events=[]
  response={'status':'COMPLETED','result':{'listings':[]},'steps':[{'id':'step-1','action':'Open listing','timestamp':'now'}],
            'streaming_url':'https://tf-test.fra0-tinyfish.unikraft.app/stream/0'}
  with patch.object(c,'request',side_effect=[{'run_id':'abc'},response]):
   result=c.run('https://housing.com/','goal',on_progress=events.append)
  self.assertEqual(events[-1]['steps'][0]['action'],'Open listing')
  self.assertTrue(events[-1]['streaming_url']);self.assertEqual(result['steps'],1)
 def test_cancel_before_start_does_not_spend(self):
  from threading import Event
  from tinyfish_client import ResearchCancelled
  cancel=Event();cancel.set();c=TinyFish('fake-key')
  with patch.object(c,'request') as request:
   with self.assertRaises(ResearchCancelled):c.run('https://housing.com/','goal',cancel=cancel)
   request.assert_not_called()
 def test_confirmed_cancellation_is_not_reported_as_pending(self):
  c=TinyFish('fake-key');events=[]
  with patch.object(c,'request',side_effect=[{'run_id':'abc'},AgentError('offline'),{'status':'CANCELLED'}]):
   with self.assertRaises(AgentError):c.run('https://housing.com/','goal',on_progress=events.append)
  self.assertEqual(events[-1]['status'],'cancellation confirmed')
