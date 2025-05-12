# Knowledge Graph Experiments

## Overview

This project provides tools for constructing, analyzing, and visualizing knowledge graphs from scientific text corpora. It includes modules for co-occurrence network analysis with statistical validation, community detection (including hSBM), and entity extraction using NLP. The codebase is designed for reproducible experiments in computational linguistics, chemistry, and physics literature mining.

## Directory Structure

- `experiment/cooccurrence/`
  Co-occurrence graph construction, statistical validation, community detection, hSBM topic modeling, and visualization.
- `experiment/simple/`
  Simple entity and relationship extraction using spaCy and NetworkX.
- `experiment/data/`
  Contains the main corpus (`corpus.txt`) and topic labels (`titles.txt`).
- `experiment/cooccurrence/env_setup.md`
  Environment setup instructions for Conda/WSL.
- `experiment/cooccurrence/environment.yml`
  Conda environment specification.
- `experiment/cooccurrence/paper_comparison.md`
  Comparison to referenced research paper.

## Installation & Environment Setup

### Prerequisites
- Linux (WSL recommended)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### Setup Steps

```bash
# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
$HOME/miniconda/bin/conda init bash
source ~/.bashrc

# Create and activate the environment
cd experiment/cooccurrence
conda env create -f environment.yml
conda activate hsbm_env

# Install additional dependencies
conda install spacy openai
# Download spaCy English model
python -m spacy download en_core_web_sm
```

## Data Format

### `corpus.txt`
- Plain text file, one document per line.
- Example:
  ```
  the nuclear overhauser effect noe is the transfer of nuclear spin polarization from one nuclear spin population to another via cross relaxation ...
  a quantum solvent is essentially a superfluid a quantum liquid used to another chemical species ...
  ```

### `titles.txt`
- Tab-separated file: `<title> <topic>` per line.
- Example:
  ```
  Nuclear_Overhauser_effect Chemical_physics
  Quantum_solvent Chemical_physics
  ...
  ```

## Usage

### Co-occurrence Graph Analysis (`experiment/cooccurrence/cooccurrence.py`)

```python
# Run from the experiment/cooccurrence directory
python cooccurrence.py
```
- Loads `../data/corpus.txt`.
- Builds a word co-occurrence graph with statistical validation (z-score > 2).
- Prunes rare nodes (min frequency = 5).
- Visualizes the graph and communities (using NetworkX and matplotlib).
- Runs hSBM community detection (via graph-tool) and visualizes the result.

#### Output
- Interactive matplotlib plots of the knowledge graph and detected communities.

### Simple Entity Extraction (`experiment/simple/extractor.py`)

```python
# Run from the experiment/simple directory
python extractor.py
```
- Loads `../data/corpus.txt`.
- Extracts named entities and noun chunk relationships using spaCy.
- Builds a directed knowledge graph (NetworkX DiGraph).

#### Output
- In-memory NetworkX graph (can be exported or visualized as needed).

## Features

- **Co-occurrence Graph Construction:**
  - Window-based word co-occurrence counting with stopword and custom exclusion filtering.
  - Statistical edge validation using z-score thresholding.
  - Pruning of rare nodes.
- **Community Detection:**
  - Greedy modularity (NetworkX) and hSBM (graph-tool) algorithms.
  - Community labels stored as node attributes.
- **hSBM Topic Modeling:**
  - Hierarchical stochastic block model (graph-tool) for topic/community discovery.
- **Graph Visualization:**
  - Spring layout, color-coded by community, with matplotlib.
- **Entity Extraction (Simple):**
  - Named entity recognition and noun chunk relationship extraction (spaCy).

## Comparison to Reference Paper

- Implements co-occurrence networks, statistical validation, and community detection as in the referenced paper.
- Uses approximate z-score filtering (vs. formal null model in paper).
- Lowercasing only (no lemmatization or POS filtering; see "Extending" below).
- Flat hSBM output (no hierarchical levels exposed).
- See `experiment/cooccurrence/paper_comparison.md` for a detailed feature table and suggestions for further alignment.

## Testing

- No automated unit or integration tests are currently included.
- Jupyter notebooks (`test.ipynb`) are provided for interactive exploration and validation.

## Extending & Customization

- **Preprocessing:**
  - To add lemmatization or POS filtering, modify `CooccurrenceGraphBuilder.preprocess()` in `cooccurrence.py` (e.g., use spaCy lemmatizer and filter by part-of-speech).
- **Community Detection:**
  - To expose hierarchical hSBM levels, use `graph_tool`'s `get_levels()` or `state.draw()`.
- **Entity Extraction:**
  - Adapt `extractor.py` to extract more complex relationships or use different NLP models.
- **Null Model:**
  - For more rigorous statistical validation, implement a configuration model or permutation-based null model.

## References & Further Reading

- See `experiment/cooccurrence/paper_comparison.md` for a detailed comparison to the reference paper.
- [NetworkX Documentation](https://networkx.org/)
- [graph-tool Documentation](https://graph-tool.skewed.de/)
- [spaCy Documentation](https://spacy.io/)
- [NLTK Documentation](https://www.nltk.org/)

## License

*Add your license information here.*