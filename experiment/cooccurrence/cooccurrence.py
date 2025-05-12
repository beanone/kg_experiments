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
from graph_tool.all import draw_hierarchy
import plotly.graph_objects as go

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

# Topic Mapping: Assign topics to documents based on graph communities
class TopicDocumentMapper:
    def __init__(self, graph: nx.Graph, documents: List[str], preprocess_fn, block_levels: List[Dict[str, int]] = None):
        self.graph = graph
        self.documents = documents
        self.preprocess_fn = preprocess_fn
        self.block_levels = block_levels  # Optional multilevel block assignments from hSBM

    def map_documents_to_topics(self, threshold: float = 0.3, level: int = -1) -> Dict[int, List[int]]:
        topic_docs = defaultdict(list)

        if self.block_levels and 0 <= level < len(self.block_levels):
            word_to_comm = self.block_levels[level]
        else:
            word_to_comm = {
                word: data["community"]
                for word, data in self.graph.nodes(data=True)
                if "community" in data
            }

        for doc_id, doc in enumerate(self.documents):
            word_counts = Counter(self.preprocess_fn(doc))
            score_by_comm = defaultdict(int)
            total = 0
            for word, count in word_counts.items():
                if word in word_to_comm:
                    comm = word_to_comm[word]
                    score_by_comm[comm] += count
                    total += count

            for comm, score in score_by_comm.items():
                if total > 0 and score / total >= threshold:
                    topic_docs[comm].append(doc_id)

        return dict(topic_docs)

    def get_topic_keywords(self, top_k: int = 5, level: int = -1) -> Dict[int, List[str]]:
        if self.block_levels and 0 <= level < len(self.block_levels):
            word_to_comm = self.block_levels[level]
        else:
            word_to_comm = {
                word: data["community"]
                for word, data in self.graph.nodes(data=True)
                if "community" in data
            }

        grouped = defaultdict(list)
        for word in self.graph.nodes:
            comm = word_to_comm.get(word)
            if comm is not None:
                grouped[comm].append(word)

        summaries = {}
        for comm, terms in grouped.items():
            top_terms = sorted(terms, key=lambda x: self.graph.degree(x), reverse=True)[:top_k]
            summaries[comm] = top_terms
        return summaries

    def render_topic_summaries(self, top_k: int = 1, doc_length: int = 300, level: int = -1):
        topic_docs = self.map_documents_to_topics(level=level)
        topic_terms = self.get_topic_keywords(top_k=5, level=level)

        for comm_id in sorted(topic_docs):
            print(f"\n--- Topic {comm_id} (Level {level}) ---")
            print("Keywords:", ", ".join(topic_terms.get(comm_id, [])))
            for doc_idx in topic_docs[comm_id][:top_k]:
                snippet = re.sub(r"\s+", " ", self.documents[doc_idx]).strip()
                print(f"\n[Doc {doc_idx}]\n", snippet[:doc_length], "...\n")

    def export_topic_summaries_markdown(self, output_path: str = "topic_summaries.md", top_k: int = 1, doc_length: int = 300, level: int = -1):
        topic_docs = self.map_documents_to_topics(level=level)
        topic_terms = self.get_topic_keywords(top_k=5, level=level)

        with open(output_path, "w", encoding="utf-8") as f:
            for comm_id in sorted(topic_docs):
                f.write(f"## Topic {comm_id} (Level {level})\n")
                f.write(f"**Keywords**: {', '.join(topic_terms.get(comm_id, []))}\n\n")
                for doc_idx in topic_docs[comm_id][:top_k]:
                    snippet = re.sub(r"\s+", " ", self.documents[doc_idx]).strip()
                    f.write(f"**Document {doc_idx}**:\n\n{snippet[:doc_length]}...\n\n")

    def draw_cluster_tree(self, state, output_file="topic_tree.pdf"):
        from graph_tool.all import draw_hierarchy, NestedBlockState
        if not isinstance(state, NestedBlockState):
            print("Error: 'state' must be a NestedBlockState with hierarchy.")
            return
        print(f"Rendering topic tree to {output_file}...")
        draw_hierarchy(state, output=output_file)
        from graph_tool.all import draw_hierarchy
        draw_hierarchy(state, output=output_file)

    def draw_sankey_diagram(self):
        import plotly.graph_objects as go
        from collections import Counter
        if not self.block_levels or len(self.block_levels) < 2:
            print("At least two block levels required for Sankey diagram.")
            return

        labels = []
        node_map = {}
        links = {"source": [], "target": [], "value": []}
        node_counter = 0
        transition_counter = Counter()

        for level in range(len(self.block_levels) - 1):
            for term, src in self.block_levels[level].items():
                tgt = self.block_levels[level + 1].get(term)
                if tgt is not None:
                    src_key = f"L{level}:{src}"
                    tgt_key = f"L{level+1}:{tgt}"
                    transition_counter[(src_key, tgt_key)] += 1

        for (src_key, tgt_key), count in transition_counter.items():
            for key in (src_key, tgt_key):
                if key not in node_map:
                    node_map[key] = node_counter
                    labels.append(key)
                    node_counter += 1
            links["source"].append(node_map[src_key])
            links["target"].append(node_map[tgt_key])
            links["value"].append(count)

        fig = go.Figure(go.Sankey(
            node=dict(label=labels),
            link=dict(
                source=links["source"],
                target=links["target"],
                value=links["value"]
            )
        ))
        fig.show()


    def generate_community_labels(self, level: int = -1, method: str = "heuristic", top_k: int = 5, save_path: str = None) -> Dict[int, str]:
        import openai  # Only if using LLM method

        keywords_by_comm = self.get_topic_keywords(top_k=top_k, level=level)
        labels = {}

        for comm_id, keywords in keywords_by_comm.items():
            if method == "heuristic":
                labels[comm_id] = keywords[0] if keywords else f"Topic {comm_id}"
            elif method == "llm":
                prompt = f"What is a concise scientific topic label for the following keywords: {', '.join(keywords)}?"
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    labels[comm_id] = response["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    labels[comm_id] = f"Topic {comm_id}"
                    print(f"LLM error for community {comm_id}: {e}")
            else:
                labels[comm_id] = f"Topic {comm_id}"

        if save_path:
            import csv
            with open(save_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["community_id", "label", "keywords"])
                for comm_id, label in labels.items():
                    writer.writerow([comm_id, label, ", ".join(keywords_by_comm.get(comm_id, []))])

        return labels
