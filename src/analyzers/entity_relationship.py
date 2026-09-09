"""Entity Relationship Graph Builder - Link identities across platforms"""

import logging
from typing import Dict, List, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class EntityRelationshipGraph:
    """Builds and visualizes entity relationships"""
    
    def __init__(self):
        """Initialize entity graph"""
        self.nodes = {}  # Entity ID -> Entity data
        self.edges = []  # Connections between entities
        logger.info("EntityRelationshipGraph initialized")
    
    def add_entity(self, entity_id: str, entity_type: str, attributes: Dict[str, Any]):
        """Add entity to graph"""
        self.nodes[entity_id] = {
            'id': entity_id,
            'type': entity_type,
            'attributes': attributes,
            'discovered_on': datetime.now().isoformat()
        }
    
    def add_edge(self, source_id: str, target_id: str, relationship_type: str, strength: float = 0.8):
        """Add relationship between entities"""
        self.edges.append({
            'source': source_id,
            'target': target_id,
            'type': relationship_type,
            'strength': strength  # 0-1 confidence
        })
    
    def build_from_results(self, results: List[Dict[str, Any]]) -> 'EntityRelationshipGraph':
        """Build graph from scan results"""
        entities_seen = set()
        
        for result in results:
            target = result.get('target')
            module = result.get('module')
            data = result.get('data', {})
            
            # Add target entity if not seen
            if target not in entities_seen:
                self.add_entity(target, 'target', {'target_type': result.get('target_type')})
                entities_seen.add(target)
            
            # Add platform/result entity
            if result.get('found'):
                platform_id = f"{target}_{module}"
                if platform_id not in entities_seen:
                    self.add_entity(platform_id, 'platform_account', data)
                    # Link target to platform
                    self.add_edge(target, platform_id, 'has_account', result.get('confidence', 0.8))
                    entities_seen.add(platform_id)
            
            # Extract and link related entities from data
            related = self._extract_related_entities(data)
            for rel_id, rel_type in related:
                if rel_id not in entities_seen and rel_id:  # Skip empty
                    self.add_entity(rel_id, rel_type, {})
                    self.add_edge(target, rel_id, 'linked_to', 0.75)
                    entities_seen.add(rel_id)
        
        logger.info(f"Built graph with {len(self.nodes)} entities and {len(self.edges)} relationships")
        return self
    
    def get_graph_visualization_data(self) -> Dict[str, Any]:
        """Get graph data formatted for visualization libraries (D3.js, Cytoscape, etc.)"""
        return {
            'nodes': list(self.nodes.values()),
            'edges': self.edges,
            'stats': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'density': self._calculate_density()
            }
        }
    
    def export_as_graphml(self) -> str:
        """Export graph as GraphML for use with Gephi/Cytoscape"""
        graphml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        graphml += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
        graphml += '  <graph edgedefault="directed">\n'
        
        # Add nodes
        for node_id, node_data in self.nodes.items():
            graphml += f'    <node id="{node_id}" label="{node_data["attributes"].get("label", node_id)}"/>\n'
        
        # Add edges
        for i, edge in enumerate(self.edges):
            graphml += f'    <edge id="e{i}" source="{edge["source"]}" target="{edge["target"]}" label="{edge["type"]}"/>\n'
        
        graphml += '  </graph>\n'
        graphml += '</graphml>'
        
        return graphml
    
    def find_clusters(self) -> List[Set[str]]:
        """Find clusters/communities of related entities"""
        # Simple connected components algorithm
        visited = set()
        clusters = []
        
        def dfs(node_id: str, cluster: Set[str]):
            if node_id in visited:
                return
            visited.add(node_id)
            cluster.add(node_id)
            
            # Follow outgoing edges
            for edge in self.edges:
                if edge['source'] == node_id and edge['target'] not in visited:
                    dfs(edge['target'], cluster)
                elif edge['target'] == node_id and edge['source'] not in visited:
                    dfs(edge['source'], cluster)
        
        for node_id in self.nodes:
            if node_id not in visited:
                cluster = set()
                dfs(node_id, cluster)
                clusters.append(cluster)
        
        return clusters
    
    @staticmethod
    def _extract_related_entities(data: Dict[str, Any]) -> List[tuple]:
        """Extract related entity IDs from data"""
        related = []
        
        # Extract email if present
        if 'email' in data and data['email']:
            related.append((data['email'], 'email'))
        
        # Extract linked accounts
        if 'linked_accounts' in data:
            for account in data.get('linked_accounts', []):
                related.append((account, 'account'))
        
        # Extract company if present
        if 'company' in data and data['company']:
            related.append((data['company'], 'company'))
        
        # Extract website if present
        if 'website' in data and data['website']:
            related.append((data['website'], 'website'))
        
        return related
    
    def _calculate_density(self) -> float:
        """Calculate graph density"""
        if len(self.nodes) <= 1:
            return 0.0
        max_edges = len(self.nodes) * (len(self.nodes) - 1)
        return len(self.edges) / max_edges if max_edges > 0 else 0.0


def build_entity_graph(results: List[Dict[str, Any]]) -> EntityRelationshipGraph:
    """Helper function to build entity graph from results"""
    graph = EntityRelationshipGraph()
    return graph.build_from_results(results)
