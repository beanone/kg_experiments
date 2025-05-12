import nltk
import matplotlib.pyplot as plt
import networkx as nx
import spacy
from spacy.cli import download
from typing import List, Dict
from collections import Counter, defaultdict
import math
import re
import graph_tool.all as gt

# Download NLTK corpora as needed
for resource in ["stopwords", "punkt"]:
    try:
        nltk.data.find(f"corpora/{resource}" if resource == "stopwords" else f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource)

# Load or download spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


# Word Co-occurrence Graph Module with Statistical Validation
class CooccurrenceGraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()
        self.stop_words = set(nltk.corpus.stopwords.words("english"))
        self.custom_exclude = {
            "also", "however", "therefore", "thus", "meanwhile", "usually",
            "directly", "indirectly", "essentially", "generally", "typically",
            "widely", "broadly", "respectively", "approximately", "overall",
            "mainly", "somewhat", "slightly", "significantly", "specifically"
        }

    def preprocess(self, text: str) -> List[str]:
        doc = nlp(text)
        tokens = []
        for token in doc:
            if (
                token.is_alpha
                and len(token.text) > 2
                and token.pos_ in {"NOUN", "ADJ"}
                and token.lemma_.lower() not in self.stop_words
                and token.lemma_.lower() not in self.custom_exclude
            ):
                tokens.append(token.lemma_.lower())
        return tokens

    def build_from_documents(self, documents: List[str], window_size: int = 10, min_freq: int = 5):
        word_counts = Counter()
        cooccur_counts = defaultdict(int)
        doc_freq = defaultdict(set)

        for doc_id, doc in enumerate(documents):
            words = self.preprocess(doc)
            word_counts.update(words)
            for i in range(len(words)):
                for j in range(i + 1, min(i + window_size, len(words))):
                    w1, w2 = sorted((words[i], words[j]))
                    cooccur_counts[(w1, w2)] += 1
                    doc_freq[w1].add(doc_id)
                    doc_freq[w2].add(doc_id)

        total_docs = len(documents)
        for (w1, w2), count in cooccur_counts.items():
            # Compute statistical threshold (p-value approximation via z-score)
            p1 = len(doc_freq[w1]) / total_docs
            p2 = len(doc_freq[w2]) / total_docs
            expected = p1 * p2 * total_docs
            if expected == 0:
                continue
            z_score = (count - expected) / math.sqrt(expected)
            if z_score > 2:  # Roughly p < 0.05
                self.graph.add_edge(w1, w2, weight=count, z=z_score)

        # Prune rare nodes
        for word in list(self.graph.nodes):
            if word_counts[word] < min_freq:
                self.graph.remove_node(word)

        return self.graph


# Graph Visualization and Interface Module
class GraphVisualizer:
    def __init__(self, nx_graph: nx.Graph):
        self.graph = nx_graph

    def draw_graph(self, with_labels=True, node_color_by_community=True):
        pos = nx.spring_layout(self.graph, seed=42)
        communities = nx.get_node_attributes(self.graph, "community")
        colors = [communities.get(node, 0) for node in self.graph.nodes()] if node_color_by_community else "skyblue"

        plt.figure(figsize=(12, 8))
        nx.draw(self.graph, pos, with_labels=with_labels, node_color=colors, cmap=plt.cm.Set3, edge_color="gray")
        nx.draw_networkx_labels(self.graph, pos)

        # Annotate community group on plot
        if node_color_by_community:
            for node, (x, y) in pos.items():
                community = communities.get(node, 0)
                plt.text(x, y + 0.05, f"C{community}", fontsize=8, color="black", ha="center")

        plt.title("Knowledge Graph Visualization with Communities")
        plt.show()


# Community Detection for Co-occurrence Graphs
class CooccurrenceCommunityDetector:
    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def detect(self):
        from networkx.algorithms.community import greedy_modularity_communities
        communities = list(greedy_modularity_communities(self.graph))
        for i, group in enumerate(communities):
            for node in group:
                self.graph.nodes[node]["community"] = i
        return self.graph


# hSBM Topic Modeling with Graph-Tool
class HSBMCommunityModel:
    def __init__(self, graph: nx.Graph):
        self.graph = graph

    def convert_to_graphtool(self):
        gt_graph = gt.Graph(directed=False)
        node_index = {}
        node_prop = gt_graph.new_vertex_property("string")

        for node in self.graph.nodes:
            v = gt_graph.add_vertex()
            node_index[node] = v
            node_prop[v] = node

        for u, v in self.graph.edges:
            gt_graph.add_edge(node_index[u], node_index[v])

        gt_graph.vertex_properties["name"] = node_prop
        return gt_graph

    def detect(self):
        gt_graph = self.convert_to_graphtool()
        state = gt.minimize_blockmodel_dl(gt_graph)
        blocks = state.get_blocks()
        labels = {gt_graph.vp["name"][v]: int(blocks[v]) for v in gt_graph.vertices()}
        for node in self.graph.nodes:
            self.graph.nodes[node]["community"] = labels[node]
        return self.graph
