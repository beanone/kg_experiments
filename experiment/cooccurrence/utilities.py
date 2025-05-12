from typing import Dict, List
from graph_tool.all import minimize_nested_blockmodel_dl
import networkx as nx
import plotly.graph_objects as go


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
