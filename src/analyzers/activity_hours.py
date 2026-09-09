"""Activity Hours Analysis - Detect user active hours from multiple platforms"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

logger = logging.getLogger(__name__)


class ActivityHoursAnalyzer:
    """Analyze activity patterns to detect active hours and timezone"""

    def __init__(self):
        self.activity_data = defaultdict(list)  # hour -> count
        self.day_activity = defaultdict(int)  # day -> count
        self.detected_timezone = None
        self.confidence = 0.0

    def add_activity(self, timestamp: datetime, platform: str = 'unknown'):
        """Add an activity data point"""
        hour = timestamp.hour
        day = timestamp.strftime('%A')
        
        self.activity_data[hour].append({
            'timestamp': timestamp,
            'platform': platform
        })
        self.day_activity[day] += 1

    def analyze_github_commits(self, commits: List[Dict]) -> Dict:
        """Analyze GitHub commit timestamps"""
        for commit in commits:
            try:
                timestamp_str = commit.get('timestamp') or commit.get('committed_date')
                if timestamp_str:
                    # Parse ISO format
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    self.add_activity(timestamp, 'github')
            except Exception as e:
                logger.warning(f"Error parsing commit timestamp: {e}")
        
        return self._analyze_pattern()

    def analyze_twitter_posts(self, posts: List[Dict]) -> Dict:
        """Analyze Twitter/X post timestamps"""
        for post in posts:
            try:
                timestamp = post.get('created_at')
                if timestamp:
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    self.add_activity(timestamp, 'twitter')
            except Exception as e:
                logger.warning(f"Error parsing tweet timestamp: {e}")
        
        return self._analyze_pattern()

    def analyze_instagram_posts(self, posts: List[Dict]) -> Dict:
        """Analyze Instagram post timestamps"""
        for post in posts:
            try:
                timestamp = post.get('timestamp') or post.get('taken_at')
                if timestamp:
                    if isinstance(timestamp, int):
                        timestamp = datetime.fromtimestamp(timestamp)
                    self.add_activity(timestamp, 'instagram')
            except Exception as e:
                logger.warning(f"Error parsing Instagram timestamp: {e}")
        
        return self._analyze_pattern()

    def _analyze_pattern(self) -> Dict:
        """Analyze activity patterns"""
        if not self.activity_data:
            return {'error': 'No activity data'}
        
        # Find peak hours
        hours_sorted = sorted(self.activity_data.items(), 
                            key=lambda x: len(x[1]), reverse=True)
        
        peak_hours = [h[0] for h in hours_sorted[:3]]
        low_hours = [h[0] for h in hours_sorted[-3:]]
        
        # Calculate activity window
        all_hours = [item['timestamp'].hour for hour_data in self.activity_data.values() 
                     for item in hour_data]
        
        if all_hours:
            min_hour = min(all_hours)
            max_hour = max(all_hours)
            activity_window = (min_hour, max_hour)
        else:
            activity_window = None
        
        # Most active day
        most_active_day = max(self.day_activity.items(), key=lambda x: x[1])[0] \
                         if self.day_activity else None
        
        return {
            'peak_hours': peak_hours,
            'low_hours': low_hours,
            'activity_window': activity_window,
            'most_active_day': most_active_day,
            'total_activities': sum(len(v) for v in self.activity_data.values()),
            'days_active': len(self.day_activity),
            'activity_by_hour': {h: len(d) for h, d in self.activity_data.items()}
        }

    def detect_timezone(self, peak_hour: int, reference_timezone: str = 'UTC') -> str:
        """Detect likely timezone based on activity"""
        # Peak activity is typically 9 AM - 5 PM
        ideal_peak = 14  # 2 PM is mid-workday
        
        offset = peak_hour - ideal_peak
        
        # Map to common timezones
        timezone_map = {
            -8: 'America/Los_Angeles',
            -7: 'America/Denver',
            -6: 'America/Chicago',
            -5: 'America/New_York',
            0: 'UTC',
            1: 'Europe/London',
            2: 'Europe/Paris',
            5: 'Asia/Kolkata',
            8: 'Asia/Singapore',
            9: 'Asia/Tokyo',
        }
        
        self.detected_timezone = timezone_map.get(offset, 'Unknown')
        self.confidence = 0.7  # Moderate confidence
        
        return self.detected_timezone

    def get_summary(self) -> Dict:
        """Get analysis summary"""
        pattern = self._analyze_pattern()
        
        peak_hour = pattern['peak_hours'][0] if pattern['peak_hours'] else None
        timezone = self.detect_timezone(peak_hour) if peak_hour else 'Unknown'
        
        return {
            'timezone': timezone,
            'timezone_confidence': self.confidence,
            'peak_hours': pattern['peak_hours'],
            'active_window': pattern['activity_window'],
            'most_active_day': pattern['most_active_day'],
            'total_data_points': pattern['total_activities'],
            'interpretation': self._interpret_pattern(pattern)
        }

    def _interpret_pattern(self, pattern: Dict) -> str:
        """Generate human-readable interpretation"""
        peak_hours = pattern['peak_hours']
        window = pattern['activity_window']
        
        if not peak_hours:
            return "Insufficient data for analysis"
        
        interpretation = []
        
        # Business hours activity
        business_hours = [h for h in peak_hours if 9 <= h <= 17]
        if len(business_hours) >= 2:
            interpretation.append("Active during typical business hours (9 AM - 5 PM)")
        
        # Night activity
        night_hours = [h for h in peak_hours if h < 6 or h > 22]
        if night_hours:
            interpretation.append("Significant night-time activity")
        
        # Weekend activity
        if pattern['most_active_day'] in ['Saturday', 'Sunday']:
            interpretation.append("Prefers weekends")
        
        if interpretation:
            return " | ".join(interpretation)
        else:
            return f"Active mainly between {window[0]}:00 and {window[1]}:00"


def analyze_activity_hours(data: Dict) -> Dict:
    """Main analysis function"""
    analyzer = ActivityHoursAnalyzer()
    
    # Process different data sources
    if 'github_commits' in data:
        analyzer.analyze_github_commits(data['github_commits'])
    
    if 'twitter_posts' in data:
        analyzer.analyze_twitter_posts(data['twitter_posts'])
    
    if 'instagram_posts' in data:
        analyzer.analyze_instagram_posts(data['instagram_posts'])
    
    return analyzer.get_summary()
