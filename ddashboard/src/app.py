# src/app.py

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from topic_query import TopicModel
from dash.dependencies import ALL
import dash_cytoscape as cyto

# Initialize model (adjust path as needed)
model = TopicModel('topic_graph.gpickle')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def topic_dropdown(level):
    topics = model.get_topic_list(level)
    options = []
    for t in topics:
        keywords = t.get('keywords', {})
        # If keywords is a list, use it directly; if dict, get by level
        if isinstance(keywords, dict):
            kws = keywords.get(level, [])
        elif isinstance(keywords, list):
            kws = keywords
        else:
            kws = []
        options.append({
            'label': f"Topic {t['id']}",
            'value': t['id']
        })
    return options

# Define a color palette for up to 10 communities
COMMUNITY_COLORS = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

def get_community_color(comm):
    try:
        return COMMUNITY_COLORS[int(comm) % len(COMMUNITY_COLORS)]
    except Exception:
        return '#cccccc'

app.layout = dbc.Container([
    html.H1("Topic Graph Explorer"),
    html.Label("Select Level:"),
    dcc.Dropdown(
        id='level-dropdown',
        options=[{'label': f"Level {lvl}", 'value': lvl} for lvl in model.get_levels()],
        value=model.get_levels()[0] if model.get_levels() else None
    ),
    html.Br(),
    html.Label("Select Topic:"),
    dcc.Dropdown(id='topic-dropdown'),
    html.Br(),
    html.Div(id='topic-details'),
    html.Hr(),
    html.H4("Subtopics"),
    html.Ul(id='subtopic-list'),
    html.Hr(),
    html.H4("Graph View"),
    cyto.Cytoscape(
        id='topic-graph',
        layout={'name': 'cose'},
        style={'width': '100%', 'height': '500px'},
        elements=[],
        stylesheet=[
            {'selector': 'node', 'style': {'content': 'data(label)', 'font-size': 10}},
            # Color nodes by community (up to 10)
            *[
                {'selector': f'.comm-{i}', 'style': {'background-color': color}}
                for i, color in enumerate(COMMUNITY_COLORS)
            ],
            {'selector': 'node', 'style': {'text-wrap': 'wrap', 'text-max-width': 80}},
            {'selector': 'edge', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
        ]
    ),
    html.Div(
        [html.H5("Community Legend:")] +
        [
            html.Div([
                html.Span(
                    style={
                        'display': 'inline-block',
                        'width': '16px',
                        'height': '16px',
                        'backgroundColor': color,
                        'marginRight': '8px',
                        'verticalAlign': 'middle',
                        'border': '1px solid #888'
                    }
                ),
                html.Span(f"Community {i}", style={'marginRight': '16px'})
            ], style={'display': 'inline-block', 'marginRight': '16px'})
            for i, color in enumerate(COMMUNITY_COLORS)
        ],
        style={'marginTop': '16px'})
], fluid=True)

@app.callback(
    Output('topic-dropdown', 'options'),
    Output('topic-dropdown', 'value'),
    Input('level-dropdown', 'value'),
    Input({'type': 'subtopic-link', 'index': ALL}, 'n_clicks'),
    Input('topic-graph', 'tapNodeData'),
    State({'type': 'subtopic-link', 'index': ALL}, 'id'),
    State('topic-dropdown', 'value'),
)
def update_topic_dropdown_and_navigate(level, n_clicks_list, node_data, ids, current_value):
    ctx = dash.callback_context
    options = topic_dropdown(level)
    value = current_value  # Default: keep current selection

    # If a node in the graph was clicked
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'topic-graph.tapNodeData':
        if node_data and 'id' in node_data:
            value = node_data['id']
    # If a subtopic link was clicked, set value to that subtopic
    elif ctx.triggered and ctx.triggered[0]['prop_id'].startswith('{"type":"subtopic-link"'):
        for n_clicks, id_dict in zip(n_clicks_list, ids):
            if n_clicks:
                value = id_dict['index']
                break
    # If the level dropdown was changed, set value to the first topic (if any)
    elif ctx.triggered and ctx.triggered[0]['prop_id'] == 'level-dropdown.value':
        value = options[0]['value'] if options else None

    return options, value

@app.callback(
    Output('topic-details', 'children'),
    Output('subtopic-list', 'children'),
    Input('topic-dropdown', 'value'),
    Input('level-dropdown', 'value')
)
def display_topic_details(topic_id, level):
    if not topic_id or level is None:
        return "Select a topic to see details.", []
    details = model.get_topic_details(topic_id, level=level)
    # Handle keywords as dict or list
    keywords = details.get('keywords', {})
    if isinstance(keywords, dict):
        kws = keywords.get(level, [])
    elif isinstance(keywords, list):
        kws = keywords
    else:
        kws = []
    # Handle documents as dict or list
    documents = details.get('documents', {})
    if isinstance(documents, dict):
        docs = documents.get(level, [])
    elif isinstance(documents, list):
        docs = documents
    else:
        docs = []
    snippets = docs[:5]
    # Handle subtopics as dict or list
    subtopics = details.get('subtopics', {})
    if isinstance(subtopics, dict):
        subs = subtopics.get(level + 1, [])
    elif isinstance(subtopics, list):
        subs = subtopics
    else:
        subs = []
    return (
        html.Div([
            html.H3(f"Topic {details['id']} (Level {details['level']})"),
            html.P(f"Keywords: {', '.join(kws)}"),
            html.P(f"Documents: {len(docs)}"),
            html.H5("Sample Documents:"),
            html.Ul([html.Li(snip) for snip in snippets])
        ]),
        [html.Li(
            html.Button(
                sub,
                n_clicks=0,
                id={'type': 'subtopic-link', 'index': sub},
                style={'background': 'none', 'border': 'none', 'color': 'blue', 'textDecoration': 'underline', 'cursor': 'pointer'}
            )
        ) for sub in subs]
    )

@app.callback(
    Output('topic-graph', 'elements'),
    Input('level-dropdown', 'value')
)
def update_graph_elements(level):
    topics = model.get_topic_list(level)
    nodes = []
    for t in topics:
        # Get keywords for this level
        if isinstance(t['keywords'], dict):
            kws = t['keywords'].get(level, [])
        elif isinstance(t['keywords'], list):
            kws = t['keywords']
        else:
            kws = []
        label = f"{t['id']}\n{', '.join(kws[:3])}"  # Show up to 3 keywords
        comm = t.get('community', 0)
        nodes.append({
            'data': {
                'id': t['id'],
                'label': label,
                'community': comm,
                'tooltip': ', '.join(kws)
            },
            'classes': f"comm-{comm}"
        })
    # Create edges based on subtopics
    edges = []
    for t in topics:
        subtopics = t.get('subtopics', [])
        if isinstance(subtopics, dict):
            subs = subtopics.get(level, [])
        else:
            subs = subtopics
        for sub in subs:
            edges.append({'data': {'source': t['id'], 'target': sub}})
    return nodes + edges



if __name__ == '__main__':
    app.run(debug=True)