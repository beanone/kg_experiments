# Environment Setup

This document describes how to setup the development for this.

## Install Conda for WSL

**Download Miniconda Installer:**
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
```

**Run Installer**
```
bash ~/miniconda.sh -b -p $HOME/miniconda
```

**Initialize Conda for shell**
```
$HOME/miniconda/bin/conda init bash
```
**Activate Conda in the Current Session**
```
source ~/.bashrc
```
**Create New Conda Environment**
```
conda env create -f environment.yml
```
**Activate venv**
```
conda activate hsbm_env
```
**Install Additional Dependencies**
```
conda install spacy plotly python-dotenv openai
pip install pymupdf python-docx pyvis dash dash-cytoscape
```
**To Run the Dash Dashboard App under ddashboard/src**
Navigate to ddashboard/src
Make sure that
1. you are in the hsbm_env venv
2. the graph is stored in topic_graph.gpickle
```
conda install dash
pip install dash_bootstrap_components
python app.py
```
