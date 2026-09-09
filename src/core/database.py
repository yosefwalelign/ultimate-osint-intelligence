"""Database Management System for OSINT Results"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class ScanRecord:
    """Database record for scan results"""
    id: str
    scan_id: str
    target: str
    target_type: str
    module: str
    found: bool
    data: Dict[str, Any]
    timestamp: str
    accuracy_score: float
    confidence: float
    source: str
    metadata: Dict[str, Any]
    false_positive_risk: float = 0.0
    status: str = "completed"
    error: Optional[str] = None


class DatabaseManager:
    """Manages database operations for OSINT scans"""
    
    def __init__(self, connection_string: str):
        """Initialize database manager"""
        self.connection_string = connection_string
        self.results_store = {}  # In-memory store (replace with actual DB)
        self.initialized = False
        logger.info(f"Database initialized: {connection_string}")
    
    def save_result(self, result: Dict[str, Any]) -> bool:
        """Save scan result to database"""
        try:
            result_id = result.get('id')
            if not result_id:
                logger.error("Result ID required")
                return False
            
            self.results_store[result_id] = result
            logger.info(f"Result saved: {result_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            return False
    
    def get_results(self, scan_id: str) -> List[Dict[str, Any]]:
        """Retrieve scan results"""
        try:
            results = [
                result for result in self.results_store.values()
                if result.get('scan_id') == scan_id
            ]
            logger.info(f"Retrieved {len(results)} results for scan {scan_id}")
            return results
        except Exception as e:
            logger.error(f"Error retrieving results: {e}")
            return []
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get single result by ID"""
        return self.results_store.get(result_id)
    
    def delete_results(self, scan_id: str) -> bool:
        """Delete results for a scan"""
        try:
            keys_to_delete = [
                key for key, result in self.results_store.items()
                if result.get('scan_id') == scan_id
            ]
            for key in keys_to_delete:
                del self.results_store[key]
            logger.info(f"Deleted {len(keys_to_delete)} results for scan {scan_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting results: {e}")
            return False
    
    def get_scan_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get scan history"""
        try:
            scans = {}
            for result in self.results_store.values():
                scan_id = result.get('scan_id')
                if scan_id not in scans:
                    scans[scan_id] = {
                        'scan_id': scan_id,
                        'target': result.get('target'),
                        'target_type': result.get('target_type'),
                        'timestamp': result.get('timestamp'),
                        'result_count': 0,
                        'modules': []
                    }
                scans[scan_id]['result_count'] += 1
                if result.get('module') not in scans[scan_id]['modules']:
                    scans[scan_id]['modules'].append(result.get('module'))
            
            return sorted(list(scans.values()), key=lambda x: x['timestamp'], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Error retrieving scan history: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            'total_results': len(self.results_store),
            'total_scans': len(set(r.get('scan_id') for r in self.results_store.values())),
            'modules_used': list(set(r.get('module') for r in self.results_store.values())),
            'status': 'connected'
        }
