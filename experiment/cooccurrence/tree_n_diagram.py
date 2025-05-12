from cooccurrence import CooccurrenceGraphBuilder, TopicDocumentMapper
from graph_tool.all import minimize_nested_blockmodel_dl
import graph_tool.all as gt

# Step 1: Load and preprocess
with open("data/corpus.txt", "r", encoding="utf-8") as f:
    documents = f.readlines()

builder = CooccurrenceGraphBuilder()
graph = builder.build_from_documents(documents)

# Step 2: Convert to graph-tool
def convert_to_graph_tool(nx_graph):
    g = gt.Graph(directed=False)
    vprop = g.new_vertex_property("string")
    idx_map = {}
    for node in nx_graph.nodes:
        v = g.add_vertex()
        idx_map[node] = v
        vprop[v] = node
    for u, v in nx_graph.edges:
        g.add_edge(idx_map[u], idx_map[v])
    g.vp["name"] = vprop
    return g, vprop

gt_graph, name_prop = convert_to_graph_tool(graph)

# Step 3: Run hSBM
state = minimize_nested_blockmodel_dl(gt_graph)
levels = state.get_levels()
block_levels = []
for lvl in levels:
    blocks = lvl.get_blocks()
    block_levels.append({name_prop[v]: int(blocks[v]) for v in gt_graph.vertices()})
