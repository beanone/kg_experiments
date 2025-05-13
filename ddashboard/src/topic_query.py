# src/topic_query.py

import networkx as nx
from typing import List, Dict, Any, Optional

class TopicModel:
    def __init__(self, graph_path: str):
        import pickle
        with open(graph_path, "rb") as f:
            self.graph = pickle.load(f)

    def get_levels(self) -> List[int]:
        levels = set()
        for _, data in self.graph.nodes(data=True):
            if 'levels' in data:
                levels.update(data['levels'].keys())
        return sorted(levels)

    def get_topic_list(self, level: Optional[int] = None) -> List[Dict[str, Any]]:
        topics = []
        for node, data in self.graph.nodes(data=True):
            if 'levels' in data:
                # If level is None, include all; else, only include if this node has a community at that level
                if level is None or level in data['levels']:
                    topics.append({
                        'id': node,
                        'community': data['levels'].get(level),
                        'keywords': data.get('keywords', []),
                        'size': self.graph.degree(node),
                        'levels': data['levels']
                    })
        return topics

    def get_topic_details(self, topic_id: str, level: int = None) -> Dict[str, Any]:
        data = self.graph.nodes[topic_id]
        subtopics = []
        if 'subtopics' in data and level is not None:
            subtopics = data['subtopics'].get(level + 1, [])
        return {
            'id': topic_id,
            'keywords': data.get('keywords', []),
            'documents': data.get('documents', []),
            'subtopics': subtopics,
            'levels': data.get('levels', {}),
            'level': level
        }

    def get_subtopics(self, topic_id: str, level: int = None) -> List[str]:
        data = self.graph.nodes[topic_id]
        if 'subtopics' in data and level is not None:
            return data['subtopics'].get(level, [])
        return []

    def get_document_snippets(self, topic_id: str, n: int = 5) -> List[str]:
        """Return up to n document snippets for a topic."""
        docs = self.graph.nodes[topic_id].get('documents', [])
        return docs[:n]

# Example usage (not for Dash, just for testing)
# model = TopicModel('data/topic_graph.gpickle')
# print(model.get_topic_list(level=0))