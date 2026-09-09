"""Timezone Detection - Infer timezone from activity patterns"""

import logging
from typing import Dict, Optional, List
import pytz
from datetime import datetime

logger = logging.getLogger(__name__)


class TimezoneDetector:
    """Detect timezone from multiple data points"""

    def __init__(self):
        self.candidates = {}  # timezone -> score
        self.all_timezones = pytz.all_timezones

    def add_timestamp_evidence(self, timestamps: List[datetime]):
        """Add timestamp evidence"""
        if not timestamps:
            return
        
        # Calculate average hour in UTC
        hours = [ts.hour for ts in timestamps if ts]
        if hours:
            avg_hour = sum(hours) / len(hours)
            
            # Score timezones
            for tz_name in self.all_timezones:
                try:
                    tz = pytz.timezone(tz_name)
                    # Convert to this timezone and check if business hours
                    for ts in timestamps:
                        localized = ts.astimezone(tz)
                        hour = localized.hour
                        
                        # Business hours bonus
                        if 8 <= hour <= 18:
                            self.candidates[tz_name] = self.candidates.get(tz_name, 0) + 1
                except:
                    pass
        
        return self.get_best_match()

    def add_location_evidence(self, location: str) -> str:
        """Add location evidence"""
        location_to_tz = {
            'new york': 'America/New_York',
            'los angeles': 'America/Los_Angeles',
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'tokyo': 'Asia/Tokyo',
            'singapore': 'Asia/Singapore',
            'dubai': 'Asia/Dubai',
            'sydney': 'Australia/Sydney',
            'india': 'Asia/Kolkata',
            'germany': 'Europe/Berlin',
        }
        
        location_lower = location.lower()
        for key, tz in location_to_tz.items():
            if key in location_lower:
                self.candidates[tz] = self.candidates.get(tz, 0) + 5
                break
        
        return self.get_best_match()

    def add_ip_geolocation(self, country: str, city: str = None) -> str:
        """Add IP geolocation evidence"""
        country_to_tz = {
            'US': ['America/New_York', 'America/Los_Angeles'],
            'GB': 'Europe/London',
            'FR': 'Europe/Paris',
            'DE': 'Europe/Berlin',
            'JP': 'Asia/Tokyo',
            'SG': 'Asia/Singapore',
            'IN': 'Asia/Kolkata',
            'AU': 'Australia/Sydney',
            'CA': 'America/Toronto',
            'BR': 'America/Sao_Paulo',
        }
        
        tz = country_to_tz.get(country.upper())
        if tz:
            if isinstance(tz, list):
                for t in tz:
                    self.candidates[t] = self.candidates.get(t, 0) + 3
            else:
                self.candidates[tz] = self.candidates.get(tz, 0) + 3
        
        return self.get_best_match()

    def get_best_match(self) -> Optional[str]:
        """Get most likely timezone"""
        if not self.candidates:
            return None
        
        best_tz = max(self.candidates.items(), key=lambda x: x[1])[0]
        return best_tz

    def get_confidence(self) -> float:
        """Get confidence score (0-1)"""
        if not self.candidates:
            return 0.0
        
        scores = list(self.candidates.values())
        max_score = max(scores)
        total_score = sum(scores)
        
        return (max_score / total_score) if total_score > 0 else 0.0

    def get_alternatives(self, top_n: int = 3) -> List[str]:
        """Get alternative timezone possibilities"""
        if not self.candidates:
            return []
        
        sorted_tz = sorted(self.candidates.items(), key=lambda x: x[1], reverse=True)
        return [tz[0] for tz in sorted_tz[:top_n]]


def detect_timezone(evidence: Dict) -> Dict:
    """Main detection function"""
    detector = TimezoneDetector()
    
    if 'timestamps' in evidence:
        detector.add_timestamp_evidence(evidence['timestamps'])
    
    if 'location' in evidence:
        detector.add_location_evidence(evidence['location'])
    
    if 'country' in evidence:
        detector.add_ip_geolocation(evidence['country'], 
                                   evidence.get('city'))
    
    best_tz = detector.get_best_match()
    
    return {
        'timezone': best_tz,
        'confidence': detector.get_confidence(),
        'alternatives': detector.get_alternatives(),
        'utc_offset': _get_utc_offset(best_tz) if best_tz else None
    }


def _get_utc_offset(timezone_name: str) -> str:
    """Get UTC offset for timezone"""
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.now(tz)
        offset = now.strftime('%z')
        return f"UTC{offset[:-2]}:{offset[-2:]}"
    except:
        return None
