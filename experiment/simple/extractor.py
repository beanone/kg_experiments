import spacy
import networkx as nx
from tqdm import tqdm

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize an empty graph
kg = nx.DiGraph()

# Load the corpus
with open('../data/corpus.txt', 'r', encoding='utf-8') as f:
    documents = f.readlines()

# Process each document
for doc_text in tqdm(documents):
    doc = nlp(doc_text)
    # Extract named entities
    entities = [ent.text for ent in doc.ents]
    # Add entities as nodes
    for ent in entities:
        kg.add_node(ent)
    # Extract relationships (for simplicity, using noun chunks)
    for chunk in doc.noun_chunks:
        if len(chunk.ents) >= 2:
            ent1, ent2 = chunk.ents[0].text, chunk.ents[1].text
            kg.add_edge(ent1, ent2, label="related_to")
