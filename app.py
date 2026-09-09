"""Main Flask Web Application"""

import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from datetime import datetime, timedelta
import asyncio
import uuid
from functools import wraps

from src.core.engine import OSINTEngine
from src.core.database import DatabaseManager
from src.core.cache import CacheManager
from src.analyzers.entity_relationship import build_entity_graph
from src.analyzers.threat_assessment import assess_threat_level
from src.analyzers.activity_hours import ActivityHoursAnalyzer

logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize components
engine = OSINTEngine()
db = DatabaseManager(os.getenv('DATABASE_URL', 'sqlite:///osint.db'))
cache = CacheManager(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User:
    """User model for authentication"""
    def __init__(self, user_id, username, role='analyst'):
        self.id = user_id
        self.username = username
        self.role = role  # admin, analyst, viewer
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return str(self.id)
    
    def has_permission(self, required_role):
        role_hierarchy = {'admin': 3, 'analyst': 2, 'viewer': 1}
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)


@login_manager.user_loader
def load_user(user_id):
    # This would load from database in production
    return User(user_id, f'user_{user_id}')


def require_role(required_role):
    """Decorator for role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if not current_user.has_permission(required_role):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Routes
@app.route('/')
def index():
    """Dashboard"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # In production, verify against database
        user = User(str(uuid.uuid4()), username, 'analyst')
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('login'))


@app.route('/api/v1/scan', methods=['POST'])
@login_required
@require_role('analyst')
def start_scan():
    """Start OSINT scan"""
    try:
        data = request.json
        target = data.get('target')
        target_type = data.get('type', 'username')  # username, email
        modules = data.get('modules', None)
        cross_scan = data.get('cross_scan', False)
        
        if not target:
            return jsonify({'error': 'Target required'}), 400
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Run scan asynchronously
        if target_type == 'email':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                engine.scan_email(target, modules, cross_scan)
            )
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                engine.scan_username(target, modules, cross_scan)
            )
        
        # Store results
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
            'status': 'completed',
            'results_count': len(results),
            'results': [r.to_dict() for r in results]
        }), 200
    
    except Exception as e:
        logger.error(f"Scan error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/results/<scan_id>')
@login_required
def get_results(scan_id):
    """Get scan results"""
    try:
        results = db.get_results(scan_id)
        
        # Build entity graph
        graph = build_entity_graph(results)
        
        # Assess threat level
        threat_assessment = assess_threat_level({
            'breach_data': {'found': False},
            'activity_data': {}
        })
        
        return jsonify({
            'scan_id': scan_id,
            'results': results,
            'entity_graph': graph.get_graph_visualization_data(),
            'threat_assessment': threat_assessment
        }), 200
    
    except Exception as e:
        logger.error(f"Results error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/activity-analysis', methods=['POST'])
@login_required
@require_role('analyst')
def analyze_activity():
    """Analyze activity patterns"""
    try:
        data = request.json
        
        analyzer = ActivityHoursAnalyzer()
        
        if 'github_commits' in data:
            result = analyzer.analyze_github_commits(data['github_commits'])
            return jsonify(result), 200
        
        if 'twitter_posts' in data:
            result = analyzer.analyze_twitter_posts(data['twitter_posts'])
            return jsonify(result), 200
        
        return jsonify({'error': 'No data provided'}), 400
    
    except Exception as e:
        logger.error(f"Activity analysis error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/graph/<scan_id>')
@login_required
def get_entity_graph(scan_id):
    """Get entity relationship graph"""
    try:
        results = db.get_results(scan_id)
        graph = build_entity_graph(results)
        
        return jsonify({
            'visualization': graph.get_graph_visualization_data(),
            'graphml': graph.export_as_graphml()
        }), 200
    
    except Exception as e:
        logger.error(f"Graph error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/export/<scan_id>/<format>')
@login_required
def export_results(scan_id, format):
    """Export results in various formats"""
    try:
        results = db.get_results(scan_id)
        
        if format == 'json':
            import json
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
        elif format == 'pdf':
            # PDF generation would use reportlab
            return jsonify({'status': 'PDF export coming soon'}), 200
        
        return jsonify({'error': 'Unsupported format'}), 400
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/history')
@login_required
def get_scan_history():
    """Get user's scan history"""
    # This would query from database filtered by user
    return jsonify({'scans': []}), 200


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8000)),
        debug=os.getenv('FLASK_DEBUG', False)
    )
