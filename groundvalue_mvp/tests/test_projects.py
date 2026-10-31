import unittest,tempfile,json,time
from pathlib import Path
from unittest.mock import patch
from io import BytesIO
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import projects
from excel_export import workbook
from streamlit.testing.v1 import AppTest
class ProjectTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.patch=patch.object(projects,'DB',Path(self.tmp.name)/'test.sqlite');self.patch.start();self.addCleanup(self.patch.stop)
 def test_history_persistence_export_archive(self):
  pid=projects.create('=danger',{'bedrooms':2,'area':1200,'unit':'sq ft'})
  for i in range(2):projects.record(pid,{'id':str(i),'state':'failed','events':[{'message':'=1+1','at':'2026-10-31','source':'test','kind':'status'}],'error':'test failure'}, {'area':1200})
  self.assertEqual(len(projects.runs(pid)),2)
  p=projects.get(pid);data=workbook(p,projects.runs(pid))
  with ZipFile(BytesIO(data)) as z:
   for name in z.namelist():ET.fromstring(z.read(name))
   self.assertEqual(len([n for n in z.namelist() if 'worksheets/' in n]),6)
   self.assertIn(b'=danger',z.read('xl/worksheets/sheet1.xml'))
   self.assertNotIn(b'<f>',z.read('xl/worksheets/sheet1.xml'))
  projects.rename(pid,'Home');self.assertEqual(projects.get(pid)['name'],'Home')
  projects.archive(pid);self.assertEqual(projects.listing(),[]);self.assertEqual(len(projects.runs(pid)),2)
 def test_dashboard_and_form(self):
  app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'))
  app.query_params['view']='app';app.run();self.assertFalse(app.exception)
  self.assertIn('Your Properties',[x.value for x in app.title])
  app.button(key='nav_New Research').click().run();self.assertFalse(app.exception)
  self.assertIn('Add Property Details',[x.value for x in app.title])
  self.assertFalse(any('Sample' in str(x.value) for x in app.radio))
