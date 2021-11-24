import pandas as pd
import numpy as np
import networkx as nx
from itertools import cycle
from fa2 import ForceAtlas2

import plotly.graph_objects as go
import plotly.express as px


def graph_preprocessing(network, attribute):
    """
    network:    unpickled network graph
    attribute:  string

    """

    palette = cycle(px.colors.qualitative.Alphabet)

    attribute_group = np.unique([*list(dict(nx.get_node_attributes(network, attribute)).values())]).tolist()
    attribute_to_number = dict(zip(attribute_group, np.arange(len(attribute_group))))
    culture_colors = [attribute_to_number[attributes[attribute]] for n, attributes in network.nodes(data = True)]

    palette = cycle(px.colors.qualitative.Alphabet)
    attribute_color_lst = [next(iter(palette)) for i in range(len(attribute_group))]
    attribute_color_dict = dict(zip(attribute_group,attribute_color_lst))

    node_sizes = [int(network.degree(n)) for n in network.nodes()]
    max_node_size = np.max(node_sizes)
    min_node_size = np.min(node_sizes)  
    degree_dict_plotly = dict(zip(list(network.nodes()),[(50-10)/(max_node_size-min_node_size)*(node_size-max_node_size)+50 for node_size in node_sizes]))

    node_dict = network.nodes(data=True)
    attribute_edge_colors = []

    for edge in network.edges():
        attribute_edge_colors.append(attribute_to_number[node_dict[edge[0]][attribute]])

    forceatlas2 = ForceAtlas2(
                        # Behavior alternatives
                        outboundAttractionDistribution=True,  # Dissuade hubs
                        edgeWeightInfluence=1,

                        # Performance
                        jitterTolerance=0.2,  # Tolerance
                        barnesHutOptimize=True,
                        barnesHutTheta=0.5,
                        multiThreaded=False,  # NOT IMPLEMENTED

                        # Tuning
                        scalingRatio=10.0,
                        strongGravityMode=False,
                        gravity=0.01,

                        # Log
                        verbose=True)

    positions = forceatlas2.forceatlas2_networkx_layout(G= network, pos=None, iterations=2000)

    return attribute_group, positions, attribute_color_dict, degree_dict_plotly

def make_edge(x, y, text, width, opacity):
    return  go.Scatter(x         = x,
                       y         = y,
                       line      = dict(width = width,
                                   color = 'cornflowerblue'),
                       hoverinfo = 'text',
                       text      = ([text]),
                       mode      = 'lines',
                       showlegend=False,
                       opacity=opacity)

def make_figure(network, attribute):

    attribute_group, positions, attribute_color_dict, degree_dict_plotly = graph_preprocessing(network, attribute)
    node_dict = network.nodes(data=True)

    edge_widths = nx.get_edge_attributes(network, 'weight')
    alphas = (list(edge_widths.values()) - np.min(list(edge_widths.values()))) / (np.max(list(edge_widths.values()))-np.min(list(edge_widths.values())))
    opacity_dict = dict(zip(list(edge_widths.keys()),alphas))

    # Create edge traces
    edge_traces = []
    for edge in network.edges():
        
        if network.edges()[edge]['weight'] > 0:
            char_1 = edge[0]
            char_2 = edge[1]
            x0, y0 = positions[char_1]
            x1, y1 = positions[char_2]
            text   = char_1 + '--' + char_2 + ': ' + str(network.edges()[edge]['weight'])
            opacity = opacity_dict[edge]
            
            trace  = make_edge([x0, x1, None], [y0, y1, None], text, 
                            width = network.edges()[edge]['weight'],
                            opacity = opacity)
            
            edge_traces.append(trace)

    # Create node traces
    node_traces = []
    for group in attribute_group:
        node_trace = go.Scatter(
                    x         = [],
                    y         = [],
                    text      = [],
                    textposition = "top center",
                    textfont_size = 10,
                    mode      = 'markers+text',
                    showlegend=True,
                    hoverinfo = 'text',
                    name = group,
                    hovertext = [],
                    marker = dict(color = [],
                                        size  = [],
                                        line  = None))
        
        for node, attributes in network.nodes(data=True):
            if attributes[attribute] == group:
                x, y = positions[node]
                node_trace['x'] += tuple([x])
                node_trace['y'] += tuple([y])  
                color_key = node_dict[node][attribute]
                node_trace['marker']['color'] += tuple([attribute_color_dict[color_key]])
                node_trace['marker']['size'] += tuple([degree_dict_plotly[node]])
                node_trace['text'] += tuple(['<b>' + node.replace('_',' ') + '</b>'])
                node_trace['hovertext'] += tuple(['<b>' + node.replace('_',' ') + '</b>'])
        print(node_trace['marker']['size'])
        node_traces.append(node_trace)   

    return edge_traces, node_traces



    



