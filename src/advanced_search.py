"""Advanced Search Engine with Boolean operators and saved queries"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class SearchQuery:
    """Represents a complex search query"""
    id: str
    name: str
    query: str  # Boolean query string
    filters: Dict = None
    created_at: datetime = None
    saved_by: str = None
    is_public: bool = False


class AdvancedSearchEngine:
    """Advanced search with Boolean operators, filters, and saved queries"""

    def __init__(self):
        self.saved_queries: Dict[str, SearchQuery] = {}
        self.query_templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """Load search query templates"""
        return {
            'breach_check': '(breach:true OR exposed:true) AND (type:email OR type:username)',
            'high_activity': 'activity_level:high AND posts_per_day:>5',
            'crypto_trader': 'wallet:bitcoin OR wallet:ethereum AND transactions:>10',
            'security_researcher': 'github:repos>20 AND stackoverflow:reputation>1000',
            'dormant_account': 'last_activity:<90days AND created_at:>2years',
            'suspicious_behavior': 'location_changes:>5 AND timezone_jumps:>3 AND vpn:true',
        }

    def parse_boolean_query(self, query_string: str) -> Dict:
        """
        Parse Boolean query string
        
        Examples:
        - (username:johndoe OR username:john_doe) AND platform:twitter
        - breach:true NOT region:us
        - activity:high AND (risk_score:>75 OR infostealer:true)
        """
        # Parse query into tokens
        tokens = self._tokenize(query_string)
        
        # Convert to search criteria
        criteria = self._build_criteria(tokens)
        
        return criteria

    def _tokenize(self, query: str) -> List[str]:
        """Tokenize query string"""
        # Replace operators with spaced versions
        query = query.replace(' AND ', ' __AND__ ')
        query = query.replace(' OR ', ' __OR__ ')
        query = query.replace(' NOT ', ' __NOT__ ')
        
        return query.split()

    def _build_criteria(self, tokens: List[str]) -> Dict:
        """Build search criteria from tokens"""
        criteria = {
            'and_conditions': [],
            'or_conditions': [],
            'not_conditions': [],
            'field_filters': {}
        }
        
        current_operator = 'AND'
        
        for token in tokens:
            if token == '__AND__':
                current_operator = 'AND'
            elif token == '__OR__':
                current_operator = 'OR'
            elif token == '__NOT__':
                current_operator = 'NOT'
            elif ':' in token:
                # Field filter
                field, value = token.split(':', 1)
                criteria['field_filters'][field] = value
            else:
                # Condition
                if current_operator == 'AND':
                    criteria['and_conditions'].append(token)
                elif current_operator == 'OR':
                    criteria['or_conditions'].append(token)
                elif current_operator == 'NOT':
                    criteria['not_conditions'].append(token)
        
        return criteria

    def search_with_filters(self, target: str, filters: Dict) -> List[Dict]:
        """
        Search with advanced filters
        
        Filters:
        {
            'date_range': {'from': '2024-01-01', 'to': '2024-12-31'},
            'breach_severity': 'critical',  # low, medium, high, critical
            'confidence_min': 0.8,
            'platforms': ['github', 'twitter', 'instagram'],
            'risk_level': 'high',  # low, medium, high, critical
        }
        """
        results = []
        
        logger.info(f"Advanced search for {target} with filters: {filters}")
        
        # Apply filters to results
        # This would integrate with actual search backend
        
        return results

    def save_query(self, query_name: str, query_string: str, 
                  saved_by: str, is_public: bool = False) -> str:
        """Save a search query"""
        import uuid
        
        query_id = str(uuid.uuid4())
        query = SearchQuery(
            id=query_id,
            name=query_name,
            query=query_string,
            created_at=datetime.now(),
            saved_by=saved_by,
            is_public=is_public
        )
        
        self.saved_queries[query_id] = query
        logger.info(f"Saved query: {query_name}")
        
        return query_id

    def get_saved_query(self, query_id: str) -> Optional[SearchQuery]:
        """Retrieve saved query"""
        return self.saved_queries.get(query_id)

    def get_public_queries(self) -> List[SearchQuery]:
        """Get all public queries"""
        return [
            q for q in self.saved_queries.values()
            if q.is_public
        ]

    def get_user_queries(self, username: str) -> List[SearchQuery]:
        """Get queries saved by user"""
        return [
            q for q in self.saved_queries.values()
            if q.saved_by == username
        ]

    def get_template_query(self, template_name: str) -> Optional[str]:
        """Get template query"""
        return self.query_templates.get(template_name)

    def list_templates(self) -> Dict:
        """List available query templates"""
        return self.query_templates


class SearchAggregator:
    """Aggregate results from multiple sources"""

    def aggregate_by_source(self, results: List[Dict]) -> Dict:
        """Group results by source"""
        aggregated = {}
        
        for result in results:
            source = result.get('source', 'unknown')
            if source not in aggregated:
                aggregated[source] = []
            aggregated[source].append(result)
        
        return aggregated

    def aggregate_by_confidence(self, results: List[Dict]) -> Dict:
        """Group results by confidence level"""
        confidence_groups = {
            'critical': [],  # 0.9-1.0
            'high': [],      # 0.7-0.9
            'medium': [],    # 0.5-0.7
            'low': []        # <0.5
        }
        
        for result in results:
            conf = result.get('confidence', 0)
            if conf >= 0.9:
                confidence_groups['critical'].append(result)
            elif conf >= 0.7:
                confidence_groups['high'].append(result)
            elif conf >= 0.5:
                confidence_groups['medium'].append(result)
            else:
                confidence_groups['low'].append(result)
        
        return confidence_groups

    def score_and_rank(self, results: List[Dict]) -> List[Dict]:
        """Score and rank results by intelligence value"""
        scored = []
        
        for result in results:
            score = 0
            
            # Confidence score
            score += result.get('accuracy_score', 0) * 40
            
            # Source reliability
            source_weights = {
                'github': 1.0,
                'twitter': 0.9,
                'instagram': 0.85,
                'breach_db': 1.0,
                'default': 0.7
            }
            weight = source_weights.get(result.get('source'), 0.7)
            score += weight * 30
            
            # Data richness
            if result.get('data'):
                data_size = len(str(result['data']))
                score += min(data_size / 1000 * 20, 20)
            
            # Recency bonus
            if result.get('timestamp'):
                from datetime import datetime
                try:
                    ts = datetime.fromisoformat(result['timestamp'])
                    days_old = (datetime.now() - ts).days
                    if days_old < 7:
                        score += 10
                except:
                    pass
            
            scored.append({
                **result,
                'intelligence_score': score
            })
        
        return sorted(scored, key=lambda x: x['intelligence_score'], reverse=True)
