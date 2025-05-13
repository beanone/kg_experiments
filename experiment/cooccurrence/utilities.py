from typing import Dict, List
from graph_tool.all import minimize_nested_blockmodel_dl
import networkx as nx
import plotly.graph_objects as go
import fitz  # PyMuPDF
from docx import Document
import re
from collections import Counter


HEADER_PATTERNS = [
    r'^neural networks \d+ \d{4}',  # Example: journal header
    r'^\s*page \d+\s*$',            # Page numbers
    r'^\s*doi:',                    # DOI lines
    r'^\s*www\.',                   # URLs
    # Add more as needed
]


def extract_block_levels(nx_graph: nx.Graph) -> List[Dict[str, int]]:
    # Convert to graph-tool format
    import graph_tool.all as gt
    gt_graph = gt.Graph(directed=False)
    vprop = gt_graph.new_vertex_property("string")
    idx_map = {}

    for node in nx_graph.nodes:
        v = gt_graph.add_vertex()
        idx_map[node] = v
        vprop[v] = node

    for u, v in nx_graph.edges:
        if u in idx_map and v in idx_map:
            gt_graph.add_edge(idx_map[u], idx_map[v])

    gt_graph.vp["name"] = vprop

    # Fit nested block model
    state = minimize_nested_blockmodel_dl(gt_graph)
    levels = state.get_levels()  # List of BlockState objects from top to bottom

    # Map node labels to block ids at each level
    name_prop = gt_graph.vp["name"]
    block_levels = []
    for level_state in levels:
        blocks = level_state.get_blocks()
        word_to_block = {name_prop[v]: int(blocks[v]) for v in gt_graph.vertices()}
        block_levels.append(word_to_block)

    return block_levels

def remove_frequent_lines(lines, threshold=0.02):
    line_counts = Counter(lines)
    total = len(lines)
    return [
        line for line in lines
        if line_counts[line] / total < threshold
    ]

def remove_pattern_lines(lines, patterns=HEADER_PATTERNS):
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    return [
        line for line in lines
        if not any(p.match(line) for p in compiled)
    ]

def clean_lines(lines):
    lines = [line.strip() for line in lines if line.strip()]
    lines = remove_frequent_lines(lines, threshold=0.02)
    lines = remove_pattern_lines(lines)
    return lines

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text_blocks = [page.get_text() for page in doc]
    all_lines = []
    for block in text_blocks:
        all_lines.extend(block.splitlines())
    cleaned_lines = clean_lines(all_lines)
    # Optionally, join lines into paragraphs (here, just one big paragraph)
    full_text = ' '.join(cleaned_lines)
    return [full_text] if full_text else []

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return [para.text.strip() for para in doc.paragraphs if len(para.text.strip()) > 40]


def normalize_text(text: str) -> str:
    """
    Normalize text to match the format of corpus.txt:
    - Lowercase
    - Remove punctuation/special characters
    - Replace newlines with spaces
    - Collapse multiple spaces
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def persist_pdf_text_to_corpus(pdf_path: str, corpus_path: str):
    """
    Extracts text from a PDF, normalizes it, and appends it to corpus.txt.
    """
    paragraphs = extract_text_from_pdf(pdf_path)
    with open(corpus_path, 'a', encoding='utf-8') as f:
        for para in paragraphs:
            norm = normalize_text(para)
            if norm:
                f.write(norm + "\n")


def persist_docx_text_to_corpus(docx_path: str, corpus_path: str):
    """
    Extracts text from a DOCX file, normalizes it, and appends it to corpus.txt.
    """
    paragraphs = extract_text_from_docx(docx_path)
    with open(corpus_path, 'a', encoding='utf-8') as f:
        for para in paragraphs:
            norm = normalize_text(para)
            if norm:
                f.write(norm + "\n")
