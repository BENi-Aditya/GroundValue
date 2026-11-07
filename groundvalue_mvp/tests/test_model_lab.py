"""Synthetic fixtures test code correctness only; never market accuracy."""
import unittest,tempfile,csv,io,math
from pathlib import Path
from datetime import date,timedelta
from unittest.mock import patch
import projects,model_lab

def fixture(count=150,one_building=False):
    buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=model_lab.FIELDS);writer.writeheader()
    for i in range(count):
        area=900+(i%25)*30
        writer.writerow({'transaction_id':str(i),'building_id':'same' if one_building else 'building-'+str(i),
            'sale_date':str(date(2024,1,1)+timedelta(days=i)), 'sale_price_inr':area*7000*(1+(i%7)*.01),
            'area_sqft':area,'bedrooms':2+(i%2),'age_years':i%15,'latitude':12.8+(i%10)*.005,
            'longitude':77.6+(i%9)*.005,'metro_km':1+(i%6),'city':'Bengaluru',
            'property_type':'apartment','area_basis':'Built-up','source_url':'https://example.org/synthetic-test-only'})
    return buf.getvalue()

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        patcher=patch.object(projects,'DB',Path(self.tmp.name)/'test.sqlite');patcher.start();self.addCleanup(patcher.stop)

    def test_train_evaluate_and_prediction_provenance(self):
        dataset=model_lab.ingest(fixture(),'Synthetic fixture, not market data','Tests only')
        model=model_lab.train(dataset['id'])
        self.assertEqual(model['counts']['train'],90);self.assertEqual(model['counts']['test'],30)
        self.assertTrue(math.isfinite(model['test_metrics']['mae_inr']))
        self.assertLessEqual(model['test_interval_coverage'],1)
        pred=model_lab.predict(model['id'],{'area_sqft':1200,'bedrooms':2,'age_years':5,'latitude':12.82,'longitude':77.62,'metro_km':3,'city':'Bengaluru','property_type':'apartment','area_basis':'Built-up'})
        self.assertLessEqual(pred['low'],pred['value']);self.assertGreaterEqual(pred['high'],pred['value'])
        self.assertEqual(pred['model_id'],model['id']);self.assertTrue(pred['factors'])
        self.assertNotIn('sale_price_inr',model['feature_names'])

    def test_prevents_building_leakage(self):
        dataset=model_lab.ingest(fixture(one_building=True),'Synthetic fixture','Tests only')
        with self.assertRaisesRegex(ValueError,'building-overlap'):model_lab.train(dataset['id'])

    def test_requires_sufficient_labels_and_provenance(self):
        with self.assertRaises(ValueError):model_lab.ingest(fixture(),'','')
        dataset=model_lab.ingest(fixture(10),'Synthetic fixture','Tests only')
        with self.assertRaisesRegex(ValueError,'120'):model_lab.train(dataset['id'])

    def test_rejects_out_of_scope_prediction(self):
        dataset=model_lab.ingest(fixture(),'Synthetic fixture','Tests only');model=model_lab.train(dataset['id'])
        with self.assertRaisesRegex(ValueError,'represented'):model_lab.predict(model['id'],{'city':'Mumbai','property_type':'apartment','area_basis':'Built-up'})

    def test_rejects_duplicate_and_bad_numeric_rows(self):
        text=fixture(3);lines=text.splitlines();text+='\n'+lines[1]+'\n'+lines[2].replace(',930,',',nan,')
        dataset=model_lab.ingest(text,'Synthetic fixture','Tests only')
        self.assertEqual(dataset['accepted'],3);self.assertEqual(dataset['rejected_count'],2)
