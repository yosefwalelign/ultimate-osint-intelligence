"""REST API Endpoints for OSINT Platform"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
import uuid
import asyncio
import logging
from datetime import datetime

from src.core.engine import OSINTEngine
from src.core.database import DatabaseManager
from src.analyzers.activity_hours import ActivityHoursAnalyzer
from src.analyzers.entity_relationship import build_entity_graph
from src.analyzers.threat_assessment import assess_threat_level

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api/v1')

engine = OSINTEngine()
db = DatabaseManager('sqlite:///osint.db')  # Use config value in production


def require_api_key(f):
    """Decorator to check API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        # Verify API key (implement in production)
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@api.route('/scan', methods=['POST'])
@require_api_key
def api_scan():
    """
    Start an OSINT scan
    
    Request body:
    {
        "target": "username or email",
        "type": "username" or "email",
        "modules": ["github", "twitter"],  # optional
        "cross_scan": false,  # optional
        "depth": 1  # optional
    }
    """
    try:
        data = request.json
        target = data.get('target')
        target_type = data.get('type', 'username')
        modules = data.get('modules')
        cross_scan = data.get('cross_scan', False)
        depth = data.get('depth', 1)
        
        if not target:
            return jsonify({'error': 'Target required'}), 400
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Run scan
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if target_type == 'email':
            results = loop.run_until_complete(
                engine.scan_email(target, modules, cross_scan, depth)
            )
        else:
            results = loop.run_until_complete(
                engine.scan_username(target, modules, cross_scan, depth)
            )
        
        # Save results
        for result in results:
            db.save_result({
                'id': f"{scan_id}_{result.module}",
                'scan_id': scan_id,
                'target': result.target,
                'target_type': result.target_type,
                'module': result.module,
                'found': result.found,
                'data': result.data,
                'timestamp': result.timestamp,
                'accuracy_score': result.accuracy_score,
                'confidence': result.confidence,
                'source': result.source,
                'metadata': result.metadata
            })
        
        return jsonify({
            'scan_id': scan_id,
            'target': target,
            'type': target_type,
            'status': 'completed',
            'found_accounts': sum(1 for r in results if r.found),
            'total_checks': len(results),
            'results': [r.to_dict() for r in results]
        }), 201
    
    except Exception as e:
        logger.error(f"API scan error: {e}")
        return jsonify({'error': str(e)}), 500


@api.route('/results/<scan_id>', methods=['GET'])
@require_api_key
def api_get_results(scan_id):
    """Get results for a scan"""
    try:
        results = db.get_results(scan_id)
        
        if not results:
            return jsonify({'error': 'Scan not found'}), 404
        
        return jsonify({
            'scan_id': scan_id,
            'results': results,
            'count': len(results)
        }), 200
    
    except Exception as e:
        logger.error(f"API results error: {e}")
        return jsonify({'error': str(e)}), 500


@api.route('/graph/<scan_id>', methods=['GET'])
@require_api_key
def api_get_graph(scan_id):
    """Get entity relationship graph"""
    try:
        results = db.get_results(scan_id)
        
        if not results:
            return jsonify({'error': 'Scan not found'}), 404
        
        graph = build_entity_graph(results)
        
        return jsonify({
            'scan_id': scan_id,
            'visualization': graph.get_graph_visualization_data(),
            'entities': len(graph.entities),
            'relationships': sum(len(rels) for rels in graph.relationships.values())
        }), 200
    
    except Exception as e:
        logger.error(f"API graph error: {e}")
        return jsonify({'error': str(e)}), 500


@api.route('/threat-assessment/<scan_id>', methods=['GET'])
@require_api_key
def api_threat_assessment(scan_id):
    """Get threat assessment for scan"""
    try:
        results = db.get_results(scan_id)
        
        if not results:
            return jsonify({'error': 'Scan not found'}), 404
        
        # Simple threat assessment
        threat_data = {
            'breach_data': {'found': any('breach' in r.get('module', '') for r in results)},
            'activity_data': {}
        }
        
        assessment = assess_threat_level(threat_data)
        
        return jsonify({
            'scan_id': scan_id,
            'threat_level': assessment['threat_level'],
            'threat_score': assessment['threat_score'],
            'recommendations': assessment['recommendations']
        }), 200
    
    except Exception as e:
        logger.error(f"API threat assessment error: {e}")
        return jsonify({'error': str(e)}), 500


@api.route('/export/<scan_id>', methods=['GET'])
@require_api_key
def api_export(scan_id):
    """Export scan results"""
    try:
        format = request.args.get('format', 'json')
        results = db.get_results(scan_id)
        
        if not results:
            return jsonify({'error': 'Scan not found'}), 404
        
        if format == 'json':
            return jsonify(results), 200
        elif format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            if results:
                fieldnames = results[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            return output.getvalue(), 200, {'Content-Type': 'text/csv'}
        
        return jsonify({'error': 'Unsupported format'}), 400
    
    except Exception as e:
        logger.error(f"API export error: {e}")
        return jsonify({'error': str(e)}), 500


@api.route('/status', methods=['GET'])
def api_status():
    """Get API status"""
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'N/A'
    }), 200


@api.route('/modules', methods=['GET'])
def api_modules():
    """Get available OSINT modules"""
    modules = {
        'username_scan': {'name': 'Username Scanner', 'description': 'Scan 700+ platforms'},
        'email_scan': {'name': 'Email Scanner', 'description': 'Check 175+ email services'},
        'instagram': {'name': 'Instagram OSINT', 'description': 'Deep Instagram reconnaissance'},
        'google_intel': {'name': 'Google Intelligence', 'description': 'Google services analysis'},
        'darkweb': {'name': 'Dark Web Search', 'description': 'Search .onion sites'},
        'github': {'name': 'GitHub Analysis', 'description': 'GitHub activity tracking'},
        'twitter': {'name': 'Twitter/X Analysis', 'description': 'Twitter profile analysis'},
        'telegram': {'name': 'Telegram OSINT', 'description': 'Telegram account analysis'},
        'shadowbroker': {'name': 'Satellite Data', 'description': 'Satellite imagery & tracking'},
        'breach_intel': {'name': 'Breach Intelligence', 'description': 'Breach & infostealer detection'},
    }
    
    return jsonify({
        'total_modules': len(modules),
        'modules': modules
    }), 200
