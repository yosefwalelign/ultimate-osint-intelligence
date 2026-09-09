"""Threat Assessment - Risk scoring and threat level evaluation"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level enumeration"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1
    UNKNOWN = 0


class ThreatAssessor:
    """Assess threat level of target"""

    def __init__(self):
        self.risk_factors = {}
        self.threat_score = 0

    def assess_breach_exposure(self, breach_data: Dict) -> float:
        """Assess risk from breach exposure"""
        if not breach_data or not breach_data.get('found'):
            return 0.0
        
        # High risk if exposed in multiple breaches
        breach_count = breach_data.get('breach_count', 1)
        data_types = breach_data.get('data_types', [])
        
        risk_score = min(breach_count * 0.3, 1.0)  # Cap at 1.0
        
        # Additional risk from data type
        sensitive_types = ['password', 'credit_card', 'ssn', 'passport']
        if any(dt in sensitive_types for dt in data_types):
            risk_score = min(risk_score + 0.4, 1.0)
        
        self.risk_factors['breach_exposure'] = risk_score
        return risk_score

    def assess_infostealer_exposure(self, infostealer_data: Dict) -> float:
        """Assess risk from infostealer malware"""
        if not infostealer_data or not infostealer_data.get('found'):
            return 0.0
        
        # Very high risk if exposed to infostealer
        risk_score = 0.9
        
        malware_types = infostealer_data.get('malware_types', [])
        if malware_types:
            risk_score = min(risk_score + 0.1, 1.0)
        
        self.risk_factors['infostealer_exposure'] = risk_score
        return risk_score

    def assess_activity_pattern(self, activity_data: Dict) -> float:
        """Assess risk from suspicious activity patterns"""
        if not activity_data:
            return 0.0
        
        risk_score = 0.0
        
        # Night-time activity might indicate automation
        if activity_data.get('unusual_hours'):
            risk_score += 0.2
        
        # Rapid location changes
        if activity_data.get('location_changes', 0) > 5:
            risk_score += 0.3
        
        # Suspicious timezone jump
        if activity_data.get('timezone_jumps', 0) > 3:
            risk_score += 0.25
        
        self.risk_factors['suspicious_activity'] = min(risk_score, 1.0)
        return min(risk_score, 1.0)

    def assess_linked_accounts(self, linked_accounts: List[str]) -> float:
        """Assess risk from number of linked accounts"""
        if not linked_accounts:
            return 0.0
        
        # More accounts = more potential exposure
        risk_score = min(len(linked_accounts) * 0.05, 0.5)
        
        self.risk_factors['account_proliferation'] = risk_score
        return risk_score

    def assess_financial_indicators(self, financial_data: Dict) -> float:
        """Assess risk from financial indicators"""
        if not financial_data:
            return 0.0
        
        risk_score = 0.0
        
        # Cryptocurrency involvement
        if financial_data.get('crypto_wallets'):
            risk_score += 0.2
        
        # Recent large transactions
        if financial_data.get('large_transactions'):
            risk_score += 0.15
        
        self.risk_factors['financial_risk'] = min(risk_score, 1.0)
        return min(risk_score, 1.0)

    def calculate_overall_threat_level(self) -> Dict:
        """Calculate overall threat level"""
        if not self.risk_factors:
            threat_score = 0
        else:
            threat_score = sum(self.risk_factors.values()) / len(self.risk_factors)
        
        # Determine threat level
        if threat_score >= 0.8:
            level = ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            level = ThreatLevel.HIGH
        elif threat_score >= 0.4:
            level = ThreatLevel.MEDIUM
        elif threat_score >= 0.2:
            level = ThreatLevel.LOW
        else:
            level = ThreatLevel.MINIMAL
        
        return {
            'threat_level': level.name,
            'threat_score': threat_score,
            'risk_factors': self.risk_factors,
            'confidence': self._calculate_confidence()
        }

    def _calculate_confidence(self) -> float:
        """Calculate confidence in assessment"""
        # More risk factors = higher confidence
        return min(len(self.risk_factors) * 0.15, 0.95)

    def get_recommendations(self) -> List[str]:
        """Get security recommendations"""
        recommendations = []
        
        if self.risk_factors.get('breach_exposure', 0) > 0.5:
            recommendations.append("Check if target was in known breaches and monitor for credential misuse")
        
        if self.risk_factors.get('infostealer_exposure', 0) > 0.5:
            recommendations.append("ALERT: Potential infostealer malware exposure. Recommend full device scan.")
        
        if self.risk_factors.get('suspicious_activity', 0) > 0.5:
            recommendations.append("Suspicious activity patterns detected. May indicate compromise or automation.")
        
        if self.risk_factors.get('account_proliferation', 0) > 0.5:
            recommendations.append("High number of linked accounts. Monitor for coordinated activity.")
        
        if self.risk_factors.get('financial_risk', 0) > 0.3:
            recommendations.append("Financial activity indicators present. Monitor transactions.")
        
        return recommendations


def assess_threat_level(osint_data: Dict) -> Dict:
    """Main threat assessment function"""
    assessor = ThreatAssessor()
    
    if 'breach_data' in osint_data:
        assessor.assess_breach_exposure(osint_data['breach_data'])
    
    if 'infostealer_data' in osint_data:
        assessor.assess_infostealer_exposure(osint_data['infostealer_data'])
    
    if 'activity_data' in osint_data:
        assessor.assess_activity_pattern(osint_data['activity_data'])
    
    if 'linked_accounts' in osint_data:
        assessor.assess_linked_accounts(osint_data['linked_accounts'])
    
    if 'financial_data' in osint_data:
        assessor.assess_financial_indicators(osint_data['financial_data'])
    
    assessment = assessor.calculate_overall_threat_level()
    assessment['recommendations'] = assessor.get_recommendations()
    
    return assessment
