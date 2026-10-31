"""UI regressions for the live-only project workflow."""
import unittest,tempfile
from pathlib import Path
from unittest.mock import patch,Mock
from streamlit.testing.v1 import AppTest
import projects
class AppTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  p=patch.object(projects,'DB',Path(self.tmp.name)/'test.sqlite');p.start();self.addCleanup(p.stop)
 def app(self,page='home'):
  a=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'));a.query_params.update({'view':'app','page':page});return a.run()
 def test_light_default_and_dark_toggle(self):
  a=self.app();self.assertFalse(a.session_state.app_dark)
  a.button(key='appearance').click().run();self.assertTrue(a.session_state.app_dark);self.assertFalse(a.exception)
 def test_live_submission_persists_project(self):
  manager=Mock();manager.snapshot.return_value=None
  with patch('application.get_manager',return_value=manager),patch('application.load_key',return_value='test-key'):
   a=self.app('new');a.text_input[0].set_value('Test apartment')
   next(b for b in a.button if b.label=='Start Research').click().run()
   manager.start.assert_called_once();self.assertEqual(len(projects.listing()),1);self.assertFalse(a.exception)
 def test_missing_key_does_not_start(self):
  manager=Mock();manager.snapshot.return_value=None
  with patch('application.get_manager',return_value=manager),patch('application.load_key',return_value=None):
   a=self.app('new');a.text_input[0].set_value('Test apartment');next(b for b in a.button if b.label=='Start Research').click().run()
   manager.start.assert_not_called();self.assertEqual(projects.listing(),[]);self.assertTrue(a.error)
