"""Entity Relationship Graph - GOD-LEVEL Feature #1"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an entity (person, email, username, etc)"""
    id: str
    name: str
    entity_type: str  # 'person', 'email', 'username', 'domain', 'phone', 'ip'
    data: Dict = field(default_factory=dict)
    confidence: float = 1.0
    sources: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.entity_type,
            'data': self.data,
            'confidence': self.confidence,
            'sources': self.sources
        }


@dataclass
class Relationship:
    """Represents a relationship between entities"""
    source_id: str
    target_id: str
    relationship_type: str  # 'same_person', 'knows', 'works_for', 'manages', etc
    strength: float  # 0-1 confidence
    evidence: List[str] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'source': self.source_id,
            'target': self.target_id,
            'type': self.relationship_type,
            'strength': self.strength,
            'evidence': self.evidence,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat()
        }


class EntityRelationshipGraph:
    """Build and analyze entity relationships"""

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, List[Relationship]] = {}
        self.similarity_threshold = 0.7

    def add_entity(self, entity: Entity) -> None:
        """Add entity to graph"""
        if entity.id not in self.entities:
            self.entities[entity.id] = entity
            self.relationships[entity.id] = []
        else:
            # Merge with existing
            existing = self.entities[entity.id]
            existing.data.update(entity.data)
            existing.sources.extend(entity.sources)
            existing.sources = list(set(existing.sources))

    def add_relationship(self, source_id: str, target_id: str,
                        relationship_type: str, strength: float,
                        evidence: List[str] = None) -> None:
        """Add relationship between entities"""
        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            strength=strength,
            evidence=evidence or []
        )
        
        if source_id not in self.relationships:
            self.relationships[source_id] = []
        
        self.relationships[source_id].append(rel)

    def link_identities(self, entity_id1: str, entity_id2: str,
                       similarity_score: float) -> None:
        """Link multiple identities of same person"""
        if similarity_score >= self.similarity_threshold:
            self.add_relationship(
                entity_id1, entity_id2,
                'same_person',
                similarity_score,
                evidence=['OSINT correlation']
            )

    def find_connected_entities(self, entity_id: str, depth: int = 2) -> Dict:
        """Find all entities connected to target"""
        visited = set()
        connections = {}
        
        def traverse(current_id: str, current_depth: int):
            if current_depth == 0 or current_id in visited:
                return
            
            visited.add(current_id)
            
            if current_id in self.relationships:
                for rel in self.relationships[current_id]:
                    if rel.target_id not in visited:
                        if rel.target_id not in connections:
                            connections[rel.target_id] = []
                        
                        connections[rel.target_id].append({
                            'relationship': rel.relationship_type,
                            'strength': rel.strength,
                            'depth': depth - current_depth + 1
                        })
                        
                        traverse(rel.target_id, current_depth - 1)
        
        traverse(entity_id, depth)
        return connections

    def detect_clusters(self) -> List[Set[str]]:
        """Detect entity clusters (groups of connected entities)"""
        visited = set()
        clusters = []
        
        def dfs(entity_id: str, cluster: Set[str]):
            if entity_id in visited:
                return
            
            visited.add(entity_id)
            cluster.add(entity_id)
            
            if entity_id in self.relationships:
                for rel in self.relationships[entity_id]:
                    if rel.target_id not in visited:
                        dfs(rel.target_id, cluster)
        
        for entity_id in self.entities:
            if entity_id not in visited:
                cluster = set()
                dfs(entity_id, cluster)
                if cluster:
                    clusters.append(cluster)
        
        return clusters

    def identify_pivots(self, entity_id: str) -> List[Tuple[str, float]]:
        """Identify pivot points for further investigation"""
        pivots = []
        
        if entity_id in self.relationships:
            for rel in self.relationships[entity_id]:
                target_entity = self.entities.get(rel.target_id)
                if target_entity:
                    # Pivots are highly connected entities
                    connection_count = len(self.relationships.get(rel.target_id, []))
                    pivot_score = connection_count * rel.strength
                    pivots.append((rel.target_id, pivot_score))
        
        return sorted(pivots, key=lambda x: x[1], reverse=True)

    def calculate_degrees_of_separation(self, source_id: str, target_id: str) -> int:
        """Calculate degrees of separation between entities"""
        from collections import deque
        
        queue = deque([(source_id, 0)])
        visited = {source_id}
        
        while queue:
            current_id, distance = queue.popleft()
            
            if current_id == target_id:
                return distance
            
            if current_id in self.relationships:
                for rel in self.relationships[current_id]:
                    if rel.target_id not in visited:
                        visited.add(rel.target_id)
                        queue.append((rel.target_id, distance + 1))
        
        return -1  # Not connected

    def get_graph_visualization_data(self) -> Dict:
        """Get data formatted for visualization (Cytoscape.js, D3.js)"""
        nodes = [
            {
                'data': {
                    'id': entity.id,
                    'label': entity.name,
                    'type': entity.entity_type,
                    'confidence': entity.confidence
                }
            }
            for entity in self.entities.values()
        ]
        
        edges = []
        for source_id, rels in self.relationships.items():
            for rel in rels:
                edges.append({
                    'data': {
                        'id': f"{source_id}_{rel.target_id}",
                        'source': source_id,
                        'target': rel.target_id,
                        'label': rel.relationship_type,
                        'weight': rel.strength
                    }
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_entities': len(self.entities),
                'total_relationships': sum(len(rels) for rels in self.relationships.values()),
                'clusters': len(self.detect_clusters())
            }
        }

    def export_as_json(self) -> str:
        """Export graph as JSON"""
        graph_data = {
            'entities': {eid: e.to_dict() for eid, e in self.entities.items()},
            'relationships': {
                sid: [r.to_dict() for r in rels]
                for sid, rels in self.relationships.items()
            },
            'metadata': {
                'total_entities': len(self.entities),
                'total_relationships': sum(len(rels) for rels in self.relationships.values()),
                'clusters': len(self.detect_clusters())
            }
        }
        return json.dumps(graph_data, indent=2, default=str)

    def export_as_graphml(self) -> str:
        """Export as GraphML for Gephi/Cytoscape"""
        # GraphML format for network analysis tools
        graphml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        graphml += '<graphml xmlns="http://graphml.graphdrawing.org/xmlformat/graphml.xml">\n'
        graphml += '<graph edgedefault="directed">\n'
        
        # Nodes
        for entity in self.entities.values():
            graphml += f'  <node id="{entity.id}" label="{entity.name}">\n'
            graphml += f'    <data key="type">{entity.entity_type}</data>\n'
            graphml += f'    <data key="confidence">{entity.confidence}</data>\n'
            graphml += '  </node>\n'
        
        # Edges
        for source_id, rels in self.relationships.items():
            for rel in rels:
                graphml += f'  <edge source="{source_id}" target="{rel.target_id}" label="{rel.relationship_type}">\n'
                graphml += f'    <data key="strength">{rel.strength}</data>\n'
                graphml += '  </edge>\n'
        
        graphml += '</graph>\n'
        graphml += '</graphml>\n'
        
        return graphml


def build_entity_graph(osint_results: List[Dict]) -> EntityRelationshipGraph:
    """Build entity graph from OSINT results"""
    graph = EntityRelationshipGraph()
    
    for result in osint_results:
        # Create entity for target
        target_entity = Entity(
            id=result['target'],
            name=result['target'],
            entity_type=result.get('target_type', 'unknown'),
            data=result.get('data', {}),
            confidence=result.get('accuracy_score', 0.8),
            sources=[result.get('module', 'unknown')]
        )
        graph.add_entity(target_entity)
        
        # Link related entities if found
        if result.get('found'):
            data = result.get('data', {})
            
            # Link to email if available
            if 'email' in data and data['email'] != result['target']:
                email_entity = Entity(
                    id=data['email'],
                    name=data['email'],
                    entity_type='email',
                    sources=[result.get('module', 'unknown')]
                )
                graph.add_entity(email_entity)
                graph.link_identities(result['target'], data['email'], 0.9)
            
            # Link to social profiles
            if 'profile_url' in data:
                url = data['profile_url']
                username = url.split('/')[-1]
                profile_entity = Entity(
                    id=url,
                    name=username,
                    entity_type='profile',
                    data={'url': url},
                    sources=[result.get('module', 'unknown')]
                )
                graph.add_entity(profile_entity)
                graph.link_identities(result['target'], url, 0.95)
    
    return graph
