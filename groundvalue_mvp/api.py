"""
Flask API endpoints to serve data to React frontend.
Wraps existing Streamlit backend functionality.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import projects
from tinyfish_client import load_key
from jobs import get_manager
from core import BASES
from research import SOURCES
from report import rupees

app = Flask(__name__)
CORS(app)

# Initialize legacy data
projects.import_legacy()


@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all properties."""
    items = projects.listing()
    result = []

    for prop in items:
        history = projects.runs(prop['id'])
        details = json.loads(prop['details'])

        # Get latest valuation
        estimate = None
        if history and history[0]['snapshot'].get('report'):
            estimate_data = history[0]['snapshot']['report'].get('estimate')
            if estimate_data:
                estimate = {
                    'value': estimate_data['value'],
                    'formatted': rupees(estimate_data['value'])
                }

        # Get status
        status = history[0]['status'] if history else 'draft'

        result.append({
            'id': prop['id'],
            'name': prop['name'],
            'location': 'Electronic City, Bengaluru, Karnataka',
            'details': details,
            'estimate': estimate,
            'status': status,
            'runs_count': len(history),
            'created': prop['created'],
            'updated': prop['updated']
        })

    return jsonify(result)


@app.route('/api/properties/<pid>', methods=['GET'])
def get_property(pid):
    """Get single property details."""
    prop = projects.get(pid)
    if not prop:
        return jsonify({'error': 'Property not found'}), 404

    history = projects.runs(pid)
    details = json.loads(prop['details'])

    # Get latest research data
    latest_research = None
    if history:
        latest = history[0]
        snapshot = latest['snapshot']
        report = snapshot.get('report', {})

        estimate = None
        if report.get('estimate'):
            est = report['estimate']
            estimate = {
                'value': est['value'],
                'formatted': rupees(est['value']),
                'min_value': est.get('min_value'),
                'max_value': est.get('max_value'),
                'rate_per_sqft': est.get('rate_per_sqft')
            }

        comparisons = report.get('comparisons', [])

        latest_research = {
            'id': latest['id'],
            'status': latest['status'],
            'started': latest['started'],
            'finished': latest.get('finished'),
            'estimate': estimate,
            'comparisons_count': len(comparisons),
            'comparisons': comparisons[:10]  # Limit to 10 for API
        }

    return jsonify({
        'id': prop['id'],
        'name': prop['name'],
        'location': 'Electronic City, Bengaluru, Karnataka',
        'details': details,
        'latest_research': latest_research,
        'runs_count': len(history),
        'created': prop['created'],
        'updated': prop['updated']
    })


@app.route('/api/properties/<pid>/runs', methods=['GET'])
def get_property_runs(pid):
    """Get all research runs for a property."""
    history = projects.runs(pid)

    result = []
    for run in history:
        snapshot = run['snapshot']
        report = snapshot.get('report', {})

        estimate = None
        if report.get('estimate'):
            est = report['estimate']
            estimate = {
                'value': est['value'],
                'formatted': rupees(est['value'])
            }

        result.append({
            'id': run['id'],
            'status': run['status'],
            'started': run['started'],
            'finished': run.get('finished'),
            'estimate': estimate,
            'sources': list(snapshot.get('sources', {}).keys()),
            'comparisons_count': len(report.get('comparisons', []))
        })

    return jsonify(result)


@app.route('/api/properties', methods=['POST'])
def create_property():
    """Create new property."""
    data = request.json

    if not data.get('name'):
        return jsonify({'error': 'Property name required'}), 400

    details = {
        'bedrooms': data.get('bedrooms', 2),
        'area': data.get('area', 1200),
        'unit': data.get('unit', 'sq ft'),
        'area_basis': data.get('area_basis', 'Built-up'),
        'notes': data.get('notes', '')
    }

    pid = projects.create(data['name'], details)

    return jsonify({
        'id': pid,
        'message': 'Property created successfully'
    }), 201


@app.route('/api/research/start', methods=['POST'])
def start_research():
    """Start research for a property."""
    data = request.json

    pid = data.get('property_id')
    sources = data.get('sources', [])

    if not pid:
        return jsonify({'error': 'Property ID required'}), 400

    if not sources:
        return jsonify({'error': 'At least one source required'}), 400

    key = load_key()
    if not key:
        return jsonify({'error': 'TinyFish API key not configured'}), 500

    manager = get_manager()
    job_id = manager.start(pid, sources, key)

    return jsonify({
        'job_id': job_id,
        'message': 'Research started successfully'
    }), 200


@app.route('/api/research/status/<job_id>', methods=['GET'])
def get_research_status(job_id):
    """Get research job status."""
    manager = get_manager()
    job = manager.snapshot()

    if not job or job.get('id') != job_id:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'id': job['id'],
        'state': job['state'],
        'events': job['events'][-20:],  # Last 20 events
        'sources': job['sources'],
        'project_id': job.get('project_id')
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration options."""
    return jsonify({
        'sources': list(SOURCES.keys()),
        'area_bases': BASES,
        'units': ['sq ft', 'sq m'],
        'location': 'Electronic City, Bengaluru'
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
