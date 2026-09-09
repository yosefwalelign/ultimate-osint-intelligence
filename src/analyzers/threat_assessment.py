"""Threat Assessment Analyzer - Risk scoring and threat level detection"""

import logging
from typing import Dict, List, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ThreatAssessmentAnalyzer:
    """Analyzes threat level based on collected intelligence"""
    
    def __init__(self):
        """Initialize threat assessment"""
        logger.info("ThreatAssessmentAnalyzer initialized")
    
    def assess_threat_level(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall threat level from intelligence data"""
        
        risk_scores = {}
        
        # Breach risk (0-100)
        breach_risk = self._calculate_breach_risk(intelligence_data.get('breach_data', {}))
        risk_scores['breach'] = breach_risk
        
        # Activity risk (0-100)
        activity_risk = self._calculate_activity_risk(intelligence_data.get('activity_data', {}))
        risk_scores['activity'] = activity_risk
        
        # Exposure risk (0-100)
        exposure_risk = self._calculate_exposure_risk(intelligence_data.get('exposure_data', {}))
        risk_scores['exposure'] = exposure_risk
        
        # Platform risk (0-100)
        platform_risk = self._calculate_platform_risk(intelligence_data.get('platform_data', {}))
        risk_scores['platform'] = platform_risk
        
        # Calculate overall threat score
        overall_score = sum(risk_scores.values()) / len(risk_scores)
        threat_level = self._score_to_threat_level(overall_score)
        
        return {
            'overall_threat_level': threat_level.value,
            'overall_risk_score': overall_score,
            'risk_breakdown': risk_scores,
            'top_risks': self._identify_top_risks(risk_scores),
            'recommendations': self._generate_recommendations(threat_level, risk_scores),
            'timestamp': datetime.now().isoformat(),
            'confidence': 0.88
        }
    
    @staticmethod
    def _calculate_breach_risk(breach_data: Dict[str, Any]) -> float:
        """Calculate breach risk score (0-100)"""
        base_risk = 0
        
        if breach_data.get('breached'):
            base_risk += 40
        
        breach_count = breach_data.get('breach_count', 0)
        base_risk += min(breach_count * 10, 40)
        
        if breach_data.get('credentials_leaked'):
            base_risk += 20
        
        return min(base_risk, 100)
    
    @staticmethod
    def _calculate_activity_risk(activity_data: Dict[str, Any]) -> float:
        """Calculate activity-based risk (0-100)"""
        base_risk = 20  # Base activity risk
        
        if activity_data.get('suspicious_activity'):
            base_risk += 30
        
        if activity_data.get('unusual_timezone_changes'):
            base_risk += 15
        
        if activity_data.get('mass_deletions'):
            base_risk += 20
        
        return min(base_risk, 100)
    
    @staticmethod
    def _calculate_exposure_risk(exposure_data: Dict[str, Any]) -> float:
        """Calculate exposure risk (0-100)"""
        base_risk = 10  # Base exposure
        
        platforms_count = exposure_data.get('platforms_found', 0)
        base_risk += min(platforms_count * 2, 40)
        
        if exposure_data.get('personal_info_exposed'):
            base_risk += 25
        
        if exposure_data.get('financial_info_exposed'):
            base_risk += 25
        
        return min(base_risk, 100)
    
    @staticmethod
    def _calculate_platform_risk(platform_data: Dict[str, Any]) -> float:
        """Calculate platform-based risk (0-100)"""
        base_risk = 0
        
        if platform_data.get('admin_accounts'):
            base_risk += 20
        
        if platform_data.get('verified_accounts'):
            base_risk += 15
        
        high_value_platforms = ['google', 'aws', 'github', 'linkedin']
        for platform in high_value_platforms:
            if platform_data.get(platform):
                base_risk += 15
        
        return min(base_risk, 100)
    
    @staticmethod
    def _score_to_threat_level(score: float) -> ThreatLevel:
        """Convert score to threat level"""
        if score >= 80:
            return ThreatLevel.CRITICAL
        elif score >= 60:
            return ThreatLevel.HIGH
        elif score >= 40:
            return ThreatLevel.MEDIUM
        elif score >= 20:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.MINIMAL
    
    @staticmethod
    def _identify_top_risks(risk_scores: Dict[str, float]) -> List[str]:
        """Identify top 3 risks"""
        sorted_risks = sorted(risk_scores.items(), key=lambda x: x[1], reverse=True)
        return [risk[0] for risk in sorted_risks[:3]]
    
    @staticmethod
    def _generate_recommendations(threat_level: ThreatLevel, risk_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on threat level"""
        recommendations = []
        
        if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
            recommendations.extend([
                'Change all passwords immediately',
                'Enable two-factor authentication on all accounts',
                'Monitor credit reports for fraud',
                'Review account activity logs',
                'Consider password manager for secure credentials'
            ])
        
        if risk_scores.get('breach', 0) > 50:
            recommendations.append('Check if accounts were affected in known breaches')
        
        if risk_scores.get('exposure', 0) > 50:
            recommendations.append('Review privacy settings on all platforms')
        
        return recommendations


def assess_threat_level(intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper function to assess threat"""
    analyzer = ThreatAssessmentAnalyzer()
    return analyzer.assess_threat_level(intelligence_data)
