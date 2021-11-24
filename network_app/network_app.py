import json
import networkx as nx
import pandas as pd

import dash
from dash import dcc 
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

from data_methods import make_figure
from fa2 import ForceAtlas2

from skimage import io
import random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

network = nx.read_gpickle("got_G_s1.gpickle")

def compute_positions(network):

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
    return positions

random.seed(1)
positions = compute_positions(network)
attribute = 'religion'

edge_traces, node_traces = make_figure(network, attribute, positions)

layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)', # transparent background
    plot_bgcolor='rgba(0,0,0,0)', # transparent 2nd background
    xaxis =  {'showgrid': False, 'zeroline': False}, # no gridlines
    yaxis = {'showgrid': False, 'zeroline': False}, # no gridlines
)

#Create figure
fig = go.Figure(layout = layout)
thumbnail = go.Figure(layout = layout)

# Add all edge traces
for trace in edge_traces:
    fig.add_trace(trace)# Add node trace
for trace in node_traces:
    fig.add_trace(trace)

fig.update_xaxes(showticklabels = False)
fig.update_yaxes(showticklabels = False)
fig.update_layout(clickmode='event+select')




app.layout = html.Div([
    dcc.Graph(
        id='computed_figure',
        figure=fig,
        style={'height':'70vh'}
    ),

    html.Div(className='row', children=[
        html.Div([
            dcc.Markdown("""
                **Season selection**

                Select a season to view the corresponding network or select overall to view the built network for all seasons combined.
            """),
            dcc.Dropdown(
                id="season_dropdown_menu",
                options =[
                    {'label': 'All seasons', 'value': 'got_G'},
                    {'label': 'Season 1','value': 's1'},
                    {'label': 'Season 2', 'value': 's2'},
                    {'label': 'Season 3', 'value': 's3'},
                    {'label': 'Season 4', 'value': 's4'},
                    {'label': 'Season 5', 'value': 's5'},
                    {'label': 'Season 6', 'value': 's6'},
                    {'label': 'Season 7', 'value': 's7'},
                    {'label': 'Season 8', 'value': 's8'}
                ],
                value = 's1'
            ),
            html.Pre(id='season_dropdown', style=styles['pre'])
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Graph attribute overlay**

                Select attribute overlay of the graph.
            """),
            dcc.Dropdown(
                id="attribute_dropdown_menu",
                options =[
                    {'label': 'Allegiance','value': 'allegiance'},
                    {'label': 'Religion', 'value': 'religion'},
                    {'label': 'Culture', 'value': 'culture'}
                ],
                value = 'religion'
            ),
            html.Pre(id='attribute_dropdown', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Click Data**

                Click on points in the graph to show meta data and the characters most frequently used words according to Term Frequency Inverse Document Count.
            """),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.

                Note that if `layout.clickmode = 'event+select'`, selection data also
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """),
            dcc.Graph(
                id='selected-data',
                figure=thumbnail,
                style={'height':'70vh'}
            ),
            #html.Pre(id='selected-data', style=styles['pre']),
        ], className='three columns'),

    ])
])

@app.callback(
    Output('computed_figure', 'figure'),
    [Input('season_dropdown_menu', 'value'),
    Input('attribute_dropdown_menu', 'value')]
)
def display_figure(season_dropdown_menu,attribute_dropdown_menu):
    base_path = 'got_G_'
    end_path = '.gpickle'
    complete_path = base_path + season_dropdown_menu + end_path

    if season_dropdown_menu == 'got_G':
        complete_path = season_dropdown_menu + end_path

    network = nx.read_gpickle(complete_path)
    attribute = attribute_dropdown_menu
    random.seed(1)
    positions = compute_positions(network)

    edge_traces, node_traces = make_figure(network, attribute, positions)

    # Create figure
    fig = go.Figure(layout = layout)

    # Add all edge traces
    for trace in edge_traces:
        fig.add_trace(trace)# Add node trace
    for trace in node_traces:
        fig.add_trace(trace)

    fig.update_xaxes(showticklabels = False)
    fig.update_yaxes(showticklabels = False)
    fig.update_layout(clickmode='event+select')

    return fig


@app.callback(
    [Output('click-data', 'children'),
    Output('selected-data', 'figure')],
    Input('computed_figure', 'clickData'))
def display_click_data(clickData):
    if clickData is not None:
        path = clickData['points'][0]['meta']
        img = io.imread(path)
        thumbnail = px.imshow(img)

        return clickData['points'][0]['customdata'],thumbnail

    path = "https://static.wikia.nocookie.net/gameofthrones/images/c/c8/Iron_throne.jpg/revision/latest/scale-to-width-down/334?cb=20131005175755"
    img = io.imread(path)
    thumbnail = px.imshow(img)
    return json.dumps(clickData, indent=2),thumbnail


# @app.callback(
#     Output('selected-data', 'children'),
#     [Input('computed_figure', 'clickData'),
#     Input('computed_figure', 'selectedData')]
#     )
# def display_selected_data(clickData,selectedData):
#     print(clickData)

#     if clickData is not None:
#         print(clickData)
#         path = clickData['points'][0]['meta']
#         img = io.imread(path)
#         thumbnail = px.imshow(img)
#         return thumbnail
#     else:
#         return json.dumps(selectedData, indent = 2)

   
   
     





if __name__ == '__main__':
    app.run_server(debug=True)
