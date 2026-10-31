import unittest,copy,tempfile,sqlite3
from pathlib import Path
from core import Property,analyse,money,area,safe_url,within_locality
from sample import observations
from report import html_report,csv_report
from storage import save

class EvidenceTests(unittest.TestCase):
 def test_prd_example_and_exclusions(self):
  r=analyse(Property(),observations(),'sample')
  self.assertEqual(r['accepted_count'],5)
  self.assertEqual(r['estimate']['value'],7440000)
  self.assertEqual((r['estimate']['low'],r['estimate']['high']),(7200000,7800000))
  self.assertEqual(len([x for x in r['records'] if not x['included']]),3)
 def test_minimum(self):self.assertIsNone(analyse(Property(),observations()[:4],'sample')['estimate'])
 def test_basis(self):self.assertEqual(analyse(Property(area_basis='Carpet'),observations()[:5],'sample')['accepted_count'],0)
 def test_explicit_sublocalities_only(self):
  for place in ['Electronic City Phase I','Kammasandra, Electronic City','Phase II, Electronic City','Electronic City (Neeladri Nagar)']:
   self.assertTrue(within_locality(place,'Electronic City'))
  for place in ['Near Electronic City','Electronic City Phase III','Whitefield','Electronic City Road']:
   self.assertFalse(within_locality(place,'Electronic City'))
 def test_real_source_labels_are_normalized_without_changing_area_basis(self):
  rows=observations()[:5]
  for r in rows:r.update(transaction_type='Resale',property_type='2 BHK Flat',area_basis='Builtup Area',area_raw='1200 Sq.Ft')
  self.assertEqual(analyse(Property(area_basis='Built-up'),rows,'live')['accepted_count'],5)
  self.assertEqual(analyse(Property(area_basis='Super built-up'),rows,'live')['accepted_count'],0)
  rows[0]['transaction_type']='Rent';rows[1]['property_type']='3 BHK Flat'
  self.assertEqual(analyse(Property(area_basis='Built-up'),rows,'live')['accepted_count'],3)
 def test_price_and_units(self):
  self.assertEqual(money('₹75 lakh'),7500000);self.assertEqual(money('INR 1.2 cr'),12000000)
  self.assertAlmostEqual(area('100 m²'),1076.39)
  for x in ['70-80 lakh','75 lakh onwards','price on request','NaN','-5','0','2 lakh + 5 lakh']:
   with self.assertRaises(ValueError):money(x)
 def test_conflicting_duplicate_excludes_both(self):
  rows=observations()[:5];rows.append(dict(rows[0],price_raw='90 lakh'))
  r=analyse(Property(),rows,'sample');self.assertEqual(r['accepted_count'],4);self.assertIsNone(r['estimate'])
 def test_probable_cross_site_duplicate(self):
  rows=observations()[:5];rows.append(dict(rows[0],source_url='https://sample-2.example/elsewhere'))
  self.assertEqual(analyse(Property(),rows,'sample')['accepted_count'],5)
 def test_empty_project_does_not_merge_distinct_homes(self):
  rows=observations()[:5]
  for r in rows:r['project']='';r['price_raw']='75 lakh'
  self.assertEqual(analyse(Property(),rows,'sample')['accepted_count'],5)
 def test_source_rules(self):
  self.assertIsNone(safe_url('javascript:alert(1)'))
  self.assertIsNone(safe_url('https://housing.com.evil.example/a',['housing.com']))
  self.assertIsNone(safe_url('https://user:pass@housing.com/a',['housing.com']))
  self.assertEqual(safe_url('https://housing.com/a/?utm_source=track',['housing.com']),'https://housing.com/a')
 def test_request_validation(self):
  for prop in [Property(area=float('nan')),Property(area=-1),Property(bedrooms=True),Property(locality='Whitefield')]:
   with self.assertRaises(ValueError):prop.validate()
 def test_unknown_and_malformed(self):
  rows=[None,dict(observations()[0],city=None),dict(observations()[1],area_raw='1200')]
  self.assertEqual(analyse(Property(),rows,'sample')['accepted_count'],0)
 def test_output_is_safe(self):
  rows=observations();rows[0]['title']='<script>alert(1)</script>';rows[1]['title']='=HYPERLINK("bad")'
  r=analyse(Property(),rows,'sample');s=html_report(r)
  self.assertNotIn('<script>',s);self.assertIn('&lt;script&gt;',s)
  self.assertIn("'=HYPERLINK",csv_report(r))
  self.assertIn('SAMPLE',s)
 def test_sqlite_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'test.sqlite';r=save(analyse(Property(),observations(),'sample'),path)
   with sqlite3.connect(path) as db:self.assertEqual(db.execute('select mode from reports where id=?',(r['report_id'],)).fetchone()[0],'sample')

if __name__=='__main__':unittest.main()
