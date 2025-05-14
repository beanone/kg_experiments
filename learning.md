# Knowledge Graph Learning Journey

This document tracks our progress in learning about knowledge graph concepts and the tools/APIs used in the cooccurrence graph generation utility. As we complete each topic, we will update this file with detailed notes.

## Learning Topics Checklist

- [x] 1. Core Concepts and Components *(Complete)*
    - CooccurrenceGraphBuilder
    - GraphVisualizer
    - CooccurrenceCommunityDetector
    - HSBMCommunityModel
    - TopicDocumentMapper
- [x] 2. Key Technologies and Libraries *(Complete)*
    - NetworkX
    - Graph-Tool
    - spaCy
    - PyMuPDF (fitz)
    - Plotly
    - PyVis
- [x] 3. Text Processing Pipeline *(Complete)*
    - PDF/DOCX extraction
    - Text normalization
    - Stop word and custom filtering
- [x] 4. Graph Analysis Features *(In Progress)*
    - Community detection
    - Hierarchical topic modeling
    - Topic-document mapping
    - Interactive visualizations
    - Sankey diagrams for topic flow

---

## Topic Details

### 1. Core Concepts and Components

#### CooccurrenceGraphBuilder: Graph Building Process

The `CooccurrenceGraphBuilder` class is responsible for constructing a word co-occurrence knowledge graph from a collection of text documents. The process involves several key steps:

1. **Preprocessing**: Each document is processed using spaCy NLP. Words are lemmatized, filtered to include only alphabetic tokens longer than 2 characters, and restricted to nouns and adjectives. Stopwords and a custom exclusion list are removed to focus on meaningful content words.

2. **Co-occurrence Calculation**: For each document, a sliding window (default size 10) is used to count how often pairs of words co-occur within the window. This results in a co-occurrence count for each word pair, as well as document frequency statistics for each word.

3. **Statistical Validation**: For each word pair, a z-score is computed to assess whether the observed co-occurrence is significantly higher than expected by chance (using a simple null model based on document frequencies). Only edges with z-score > 2 (roughly p < 0.05) are retained, ensuring statistical significance.

4. **Pruning**: Words that occur less than a minimum frequency (default 5) are removed from the graph to reduce noise and focus on relevant terms.

The resulting graph is a weighted, undirected NetworkX graph where nodes are lemmatized content words and edges represent statistically significant co-occurrence relationships.

---

#### GraphVisualizer: Visualization of the Knowledge Graph

The `GraphVisualizer` class is responsible for rendering the co-occurrence graph, making it easier to interpret and analyze the structure of the knowledge graph. Key features include:

1. **Spring Layout Visualization**: Uses NetworkX's spring layout to position nodes in a visually appealing way, where related nodes are closer together.
2. **Community Coloring**: Optionally colors nodes by their community assignment, if available, to highlight clusters or topics within the graph.
3. **Labeling**: Supports displaying node labels and annotating community groups directly on the plot.
4. **Matplotlib Integration**: Leverages matplotlib for static, publication-quality visualizations.

This visualization step is crucial for understanding the structure and relationships in the knowledge graph, identifying clusters, and communicating results to others.

---

#### CooccurrenceCommunityDetector: Community Detection

The `CooccurrenceCommunityDetector` class is responsible for identifying communities (clusters of related words) within the co-occurrence graph. Its main features are:

1. **Greedy Modularity Optimization**: Uses NetworkX's `greedy_modularity_communities` algorithm to partition the graph into communities. This method seeks to maximize modularity, a measure of the density of links inside communities compared to links between communities.
2. **Community Annotation**: Assigns a community label (an integer) to each node in the graph, storing it as a node attribute. This enables downstream tasks such as coloring nodes by community or mapping topics to documents.

Community detection is a key step in uncovering the latent topic structure of the knowledge graph, grouping semantically related terms together.

---

#### HSBMCommunityModel: Hierarchical Topic Modeling

The `HSBMCommunityModel` class implements hierarchical stochastic block modeling (hSBM) using the `graph-tool` library. Its main features are:

1. **Graph Conversion**: Converts the NetworkX graph to a `graph-tool` graph, preserving node names as vertex properties.
2. **Hierarchical Community Detection**: Uses `graph-tool`'s `minimize_nested_blockmodel_dl` to fit a nested block model, uncovering multiple levels of community structure (topics and subtopics).
3. **Multi-level Assignment**: Assigns each node a dictionary of community assignments at each hierarchy level, enabling exploration of topics at different granularities.
4. **Integration with Downstream Tasks**: The hierarchical structure supports advanced topic mapping, visualization (e.g., cluster trees), and analysis of topic evolution across levels.

This approach provides a powerful, multi-resolution view of the knowledge graph, revealing both broad and fine-grained topic clusters.

---

#### TopicDocumentMapper: Topic and Document Mapping

The `TopicDocumentMapper` class bridges the gap between the knowledge graph and the original documents. Its main features are:

1. **Document-to-Topic Assignment**: For each document, it counts the frequency of topic words (as defined by community assignments) and assigns the document to topics where the proportion of topic words exceeds a threshold.
2. **Topic Keyword Extraction**: Identifies the most representative words (keywords) for each topic/community, typically by node degree or frequency.
3. **Topic Summarization**: Provides summaries of each topic, including keywords and representative document snippets, for interpretation and reporting.
4. **Export and Visualization**: Supports exporting topic summaries to Markdown or CSV, and visualizing topic relationships (e.g., Sankey diagrams, cluster trees).

This component enables practical use of the knowledge graph for topic modeling, document classification, and knowledge discovery.

---

### 2. Key Technologies and Libraries

#### NetworkX
A Python library for the creation, manipulation, and study of complex networks. Used here for building and managing the initial co-occurrence graph.

#### graph-tool
A Python library (with C++ backend) for efficient graph analysis and advanced community detection, including hierarchical stochastic block modeling (hSBM).

#### spaCy
A fast, industrial-strength NLP library for Python. Used for tokenization, lemmatization, part-of-speech tagging, and filtering of text data.

#### PyMuPDF (fitz)
A Python binding for MuPDF, used for extracting text from PDF files as part of the document ingestion pipeline.

#### Plotly
A Python graphing library for creating interactive, web-based visualizations, such as Sankey diagrams and other advanced plots.

#### PyVis
A Python library for interactive network visualization in the browser, used for rendering interactive knowledge graphs.

---

### 3. Text Processing Pipeline

#### PDF/DOCX Extraction
Text is extracted from PDF files using PyMuPDF (fitz) and from DOCX files using python-docx. This step converts documents into raw text for further processing.

#### Text Normalization
Extracted text is normalized by lowercasing, removing punctuation and special characters, replacing newlines with spaces, and collapsing multiple spaces. This ensures consistency and reduces noise in the data.

#### Stop Word and Custom Filtering
During preprocessing, common stop words (using NLTK's stopword list) and a custom exclusion list are removed. This focuses the analysis on meaningful content words, improving the quality of the resulting knowledge graph.

These steps are essential for preparing clean, relevant data for graph construction and downstream analysis.

---

### 4. Graph Analysis Features

#### Community Detection
Identifies clusters of related words or concepts in the knowledge graph, revealing latent topic structure. Methods include modularity-based detection and hierarchical stochastic block modeling (hSBM).

#### Hierarchical Topic Modeling
Discovers multi-level topic structures using hSBM, allowing exploration of both broad and fine-grained topics within the graph.

#### Topic-Document Mapping
Associates documents with topics based on the presence and frequency of topic words, enabling document classification and topic summarization.

#### Interactive Visualizations
Provides tools for visualizing the knowledge graph and its communities, including static plots, interactive network diagrams, and cluster trees for hierarchical exploration.

#### Sankey Diagrams for Topic Flow
Visualizes the flow and transitions of topics across different levels of the hierarchy, helping to interpret how topics split and merge at various resolutions.

#### Typical Patterns in Hierarchical Sankey Diagrams

Hierarchical Sankey diagrams (and hSBM block structures) can reveal different patterns depending on the structure of your data. These patterns often correspond to the type and diversity of the document collection:

- **Bushy Hierarchy (Many Splits at Each Level):**
  - Encyclopedic or survey-like collections (e.g., Wikipedia, textbooks)
  - Large, diverse corpora with many distinct topics and subtopics
  - Indicates high diversity at all levels

- **Narrowing Hierarchy (Many Splits → Few Splits):**
  - Collections with surface diversity but a common core (e.g., news articles about different events but all related to politics)
  - Diversity at first, but deeper analysis reveals underlying similarity

- **Expanding Hierarchy (Few Splits → Many Splits):**
  - Technical or scientific corpora with a few broad fields, each containing many specialized subfields (e.g., scientific journals by discipline)
  - Broad categories with rich internal structure

- **Flat Hierarchy (One or Few Levels, Little Splitting):**
  - Homogeneous collections (e.g., a set of articles all on the same topic)
  - Lacks significant internal structure

- **Unbalanced or Lopsided Hierarchy:**
  - Collections with a dominant topic and several minor ones (e.g., company internal documents where most are about one department)
  - One or a few topics dominate

**Summary Table:**

| Pattern         | Typical Data Type                | Interpretation                        |
|-----------------|----------------------------------|---------------------------------------|
| Bushy           | Encyclopedic, diverse corpora    | High diversity at all levels          |
| Narrowing       | News, event-based                | Surface diversity, deep similarity    |
| Expanding       | Academic, technical              | Broad fields, many subfields          |
| Flat            | Homogeneous, focused             | Little internal structure             |
| Unbalanced      | Corporate, domain-dominated      | One/few dominant topics               |

These patterns provide insight into the diversity and organization of your data, and can help guide exploration, analysis, and quality checks of your knowledge graph and topic models.

---
