"""Activity Hours Analysis - Detect timezone and active hours"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class ActivityHoursAnalyzer:
    """Analyzes activity patterns to detect timezone and active hours"""
    
    def __init__(self):
        """Initialize activity analyzer"""
        logger.info("ActivityHoursAnalyzer initialized")
    
    def analyze_github_commits(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze GitHub commit timestamps to detect timezone and patterns"""
        if not commits:
            return {'error': 'No commits provided'}
        
        hourly_dist = defaultdict(int)
        daily_dist = defaultdict(int)
        
        for commit in commits:
            try:
                timestamp = datetime.fromisoformat(commit['timestamp'].replace('Z', '+00:00'))
                hourly_dist[timestamp.hour] += 1
                daily_dist[timestamp.weekday()] += 1
            except:
                continue
        
        peak_hours = sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:3]
        low_hours = sorted(hourly_dist.items(), key=lambda x: x[1])[:3]
        
        return {
            'total_commits': len(commits),
            'hourly_distribution': dict(hourly_dist),
            'daily_distribution': dict(daily_dist),
            'peak_active_hours': f"{peak_hours[0][0]:02d}:00 - {(peak_hours[0][0]+2):02d}:00" if peak_hours else 'Unknown',
            'least_active_hours': f"{low_hours[0][0]:02d}:00 - {(low_hours[0][0]+2):02d}:00" if low_hours else 'Unknown',
            'timezone_estimate': self._estimate_timezone(peak_hours),
            'activity_consistency': self._calculate_consistency(hourly_dist),
            'confidence_score': 0.85
        }
    
    def analyze_twitter_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Twitter posting patterns"""
        if not posts:
            return {'error': 'No posts provided'}
        
        hourly_dist = defaultdict(int)
        daily_dist = defaultdict(int)
        
        for post in posts:
            try:
                timestamp = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                hourly_dist[timestamp.hour] += 1
                daily_dist[timestamp.strftime('%A')] += 1
            except:
                continue
        
        peak_hours = sorted(hourly_dist.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_posts': len(posts),
            'posting_frequency': len(posts) / 7 if posts else 0,  # per day
            'peak_posting_times': [h[0] for h in peak_hours],
            'daily_distribution': dict(daily_dist),
            'activity_pattern': 'Regular user' if len(posts) > 50 else 'Casual user',
            'timezone_estimate': self._estimate_timezone(peak_hours),
            'confidence_score': 0.80
        }
    
    @staticmethod
    def _estimate_timezone(peak_hours: List[tuple]) -> str:
        """Estimate timezone based on peak activity hours"""
        if not peak_hours:
            return 'Unknown'
        
        peak_hour = peak_hours[0][0]
        
        timezone_map = {
            (6, 10): 'UTC-8 (Pacific Time)',
            (10, 14): 'UTC-5 (Eastern Time)',
            (14, 18): 'UTC+0 (GMT)',
            (18, 22): 'UTC+4 (Dubai/Moscow)',
            (22, 2): 'UTC+8 (Singapore/China)',
            (2, 6): 'UTC+12 (Sydney/NZ)'
        }
        
        for (start, end), tz in timezone_map.items():
            if start <= peak_hour < end:
                return tz
        return 'UTC-5 (Eastern Time)'
    
    @staticmethod
    def _calculate_consistency(hourly_dist: Dict[int, int]) -> float:
        """Calculate how consistent activity is across hours (0-1)"""
        if not hourly_dist:
            return 0.0
        
        values = list(hourly_dist.values())
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        # Lower std dev = more consistent
        consistency = 1.0 - (std_dev / (mean + 1))
        return max(0.0, min(1.0, consistency))
