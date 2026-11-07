"""API integration contracts; no paid provider requests."""
import unittest
from unittest.mock import patch, Mock
import api
from core import Property

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = api.app.test_client()

    def test_start_passes_validated_property_and_project_id(self):
        manager = Mock()
        manager.start.return_value = 'job-1'
        with patch.object(api.projects, 'get', return_value={'details': {'area': 1250, 'bedrooms': 3}}), patch.object(api, 'load_key', return_value='test'), patch.object(api, 'get_manager', return_value=manager):
            response = self.client.post('/api/research/start', json={'property_id': 'p1', 'sources': [next(iter(api.SOURCES))]})
        self.assertEqual(response.status_code, 200)
        target = manager.start.call_args.args[0]
        self.assertIsInstance(target, Property)
        self.assertEqual(target.area, 1250)
        self.assertEqual(manager.start.call_args.kwargs, {'project_id': 'p1'})

    def test_invalid_source_rejected_before_provider(self):
        with patch.object(api, 'load_key') as key:
            response = self.client.post('/api/research/start', json={'property_id': 'p1', 'sources': ['unknown']})
        self.assertEqual(response.status_code, 400)
        key.assert_not_called()

    def test_missing_project(self):
        with patch.object(api.projects, 'get', return_value=None):
            response = self.client.post('/api/research/start', json={'property_id': 'missing', 'sources': [next(iter(api.SOURCES))]})
        self.assertEqual(response.status_code, 404)

    def test_property_maps_actual_engine_report(self):
        prop = {'id': 'p1', 'name': 'Home', 'details': {'area': 1200}, 'created': '', 'updated': ''}
        report = {'estimate': {'value': 9000000, 'low': 8000000, 'high': 10000000, 'median_rate': 7500},
                  'records': [{'included': True}, {'included': False}], 'accepted_count': 1}
        run = {'id': 'r1', 'status': 'completed', 'started': '', 'snapshot': {'report': report}}
        with patch.object(api.projects, 'get', return_value=prop), patch.object(api.projects, 'runs', return_value=[run]):
            response = self.client.get('/api/properties/p1')
        self.assertEqual(response.status_code, 200)
        result = response.get_json()['latest_research']
        self.assertEqual(result['estimate']['min_value'], 8000000)
        self.assertEqual(result['estimate']['rate_per_sqft'], 7500)
        self.assertEqual(result['comparisons_count'], 1)

    def test_pending_report_can_be_empty(self):
        run = {'id': 'r1', 'status': 'running', 'started': '', 'snapshot': {'report': None}}
        with patch.object(api.projects, 'runs', return_value=[run]):
            response = self.client.get('/api/properties/p1/runs')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()[0]['estimate'])

    def test_invalid_area_cannot_create_property(self):
        with patch.object(api.projects, 'create') as create:
            response = self.client.post('/api/properties', json={'name': 'Home', 'area': -1})
        self.assertEqual(response.status_code, 400)
        create.assert_not_called()
