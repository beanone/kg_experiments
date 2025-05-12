# 🧠 TopicDocumentMapper: Knowledge Graph–Driven Topic Mapping and Analysis

This module is part of a comprehensive pipeline for extracting, validating, and organizing **semantic knowledge** and **topics** from unstructured text using statistically validated co-occurrence graphs and hierarchical community detection.

## 📋 Summary

- **Statistical validation** of co-occurrence edges using z-scores
- **Multilevel topic modeling** via hSBM (hierarchical Stochastic Block Model)
- **Document-to-topic assignment** based on graph-level community inference
- **Topic summarization**, **label generation** (heuristic or LLM-powered)
- **Visualization** via cluster trees and Sankey diagrams
- **Markdown and CSV exports** for analysis and reporting

## ✅ Features

### 1. Co-occurrence Graph
Constructs a statistically grounded co-occurrence graph from documents using:
- Stopword + custom filtering
- Lemmatization and POS-tag filtering (nouns and adjectives)
- Edge validation using z-score-based significance

### 2. hSBM Topic Detection
Uses `graph-tool`’s nested blockmodel to infer multilevel topic structure:
- `block_levels` stores multiple resolution levels
- Each node is assigned a community per level

### 3. TopicDocumentMapper

Main operations:
- `map_documents_to_topics(threshold=0.3, level=1)`
- `get_topic_keywords(level=1)`
- `render_topic_summaries()` and `export_topic_summaries_markdown()`
- `generate_community_labels(method='heuristic'|'llm', save_path='labels.csv')`
- `draw_sankey_diagram()`
- `draw_cluster_tree(state)`

### 4. Outputs

#### CSV (Community Labels):
| community_id | label           | keywords                             |
|--------------|------------------|--------------------------------------|
| 0            | Quantum Physics | quantum, relativity, mechanics, ... |

#### Markdown:
- Keywords and representative documents per topic

#### Visualizations:
- `topic_tree.pdf`: cluster tree
- `plotly.Sankey`: topic transitions across levels

## 🛠 Requirements

- Python 3.10
- `networkx`, `nltk`, `spacy`, `graph-tool`, `plotly`
- Optional: `openai` (for LLM labeling)

## 📚 Reference

Based on:  
*Statistically validated network for analysing textual data* (2025)  
DOI: 10.1007/s41109-025-00693-z
