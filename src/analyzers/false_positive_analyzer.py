"""False Positive Analysis - Detect and score false positive risk"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FalsePositiveAnalyzer:
    """Analyzes results for false positive risk"""
    
    def __init__(self):
        """Initialize false positive analyzer"""
        logger.info("FalsePositiveAnalyzer initialized")
    
    def analyze_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single result for false positive risk"""
        
        fp_risk = 0.0
        fp_indicators = []
        confidence_adjustment = 0.0
        
        # Check confidence score
        confidence = result.get('confidence', 0.5)
        if confidence < 0.70:
            fp_risk += 0.3
            fp_indicators.append('Low confidence score')
        
        # Check accuracy score
        accuracy = result.get('accuracy_score', 0.5)
        if accuracy < 0.75:
            fp_risk += 0.2
            fp_indicators.append('Low accuracy score')
        
        # Check module type
        module = result.get('module', '')
        module_fp_risk = self._get_module_fp_risk(module)
        fp_risk += module_fp_risk
        if module_fp_risk > 0.15:
            fp_indicators.append(f'Module {module} has known false positive rate')
        
        # Check metadata
        metadata = result.get('metadata', {})
        if not metadata or 'verification_method' not in metadata:
            fp_risk += 0.1
            fp_indicators.append('Insufficient metadata for verification')
        
        # Check data quality
        data = result.get('data', {})
        if not data or len(data) == 0:
            fp_risk += 0.2
            fp_indicators.append('Insufficient data returned')
        
        # HTTP status false positives
        if 'http_status' in metadata:
            if metadata['http_status'] in [404, 429, 503]:
                fp_risk += 0.15
                fp_indicators.append(f'HTTP {metadata["http_status"]} may indicate false positive')
        
        # Common false positive patterns
        common_patterns = self._check_common_fp_patterns(result)
        if common_patterns:
            fp_risk += 0.2
            fp_indicators.extend(common_patterns)
        
        # Normalize risk to 0-1 range
        fp_risk = min(fp_risk, 1.0)
        
        # Calculate adjusted confidence
        adjusted_confidence = confidence * (1 - fp_risk)
        
        return {
            'original_result': result,
            'false_positive_risk': round(fp_risk, 3),
            'confidence_score': round(adjusted_confidence, 3),
            'result_classification': self._classify_result(fp_risk, adjusted_confidence),
            'fp_indicators': fp_indicators,
            'recommendation': self._get_recommendation(fp_risk),
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_batch_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze multiple results"""
        analyzed_results = []
        positive_count = 0
        false_positive_count = 0
        negative_count = 0
        unknown_count = 0
        
        for result in results:
            analyzed = self.analyze_result(result)
            analyzed_results.append(analyzed)
            
            classification = analyzed['result_classification']
            if classification == 'True Positive':
                positive_count += 1
            elif classification == 'False Positive':
                false_positive_count += 1
            elif classification == 'Negative':
                negative_count += 1
            else:
                unknown_count += 1
        
        return {
            'total_results': len(results),
            'analyzed_results': analyzed_results,
            'summary': {
                'true_positives': positive_count,
                'false_positives': false_positive_count,
                'negatives': negative_count,
                'unknown': unknown_count
            },
            'false_positive_rate': round(false_positive_count / len(results), 3) if results else 0,
            'confidence_level': 'High' if false_positive_count / len(results) < 0.1 else 'Medium' if false_positive_count / len(results) < 0.25 else 'Low',
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def _get_module_fp_risk(module: str) -> float:
        """Get known false positive risk for a module"""
        module_risks = {
            'email_verification': 0.05,
            'username_scan': 0.15,
            'instagram': 0.10,
            'twitter': 0.08,
            'github': 0.05,
            'breach_intel': 0.02,
            'google_intel': 0.08
        }
        return module_risks.get(module, 0.1)
    
    @staticmethod
    def _check_common_fp_patterns(result: Dict[str, Any]) -> List[str]:
        """Check for common false positive patterns"""
        indicators = []
        data = result.get('data', {})
        metadata = result.get('metadata', {})
        
        # Generic usernames often create false positives
        generic_names = ['admin', 'test', 'user', 'demo', 'guest', 'root']
        target = result.get('target', '').lower()
        if target in generic_names:
            indicators.append('Generic username - high FP risk')
        
        # Very new or very old data
        if metadata.get('account_age_days', 0) < 7:
            indicators.append('Very new account - may be test account')
        
        # Incomplete profile information
        profile_completeness = len([v for v in data.values() if v])
        if profile_completeness < 3:
            indicators.append('Incomplete profile data suggests account placeholder')
        
        return indicators
    
    @staticmethod
    def _classify_result(fp_risk: float, confidence: float) -> str:
        """Classify result as True Positive, False Positive, or Negative"""
        if confidence >= 0.75 and fp_risk < 0.2:
            return 'True Positive'
        elif fp_risk > 0.5:
            return 'False Positive'
        elif confidence < 0.50:
            return 'Negative'
        else:
            return 'Unknown'
    
    @staticmethod
    def _get_recommendation(fp_risk: float) -> str:
        """Get recommendation based on false positive risk"""
        if fp_risk < 0.15:
            return 'TRUST: High confidence result, minimal false positive risk'
        elif fp_risk < 0.35:
            return 'VERIFY: Moderate false positive risk, recommend manual verification'
        elif fp_risk < 0.60:
            return 'CAUTIOUS: Significant false positive risk, treat with skepticism'
        else:
            return 'DISCARD: Very high false positive risk, likely not reliable'
