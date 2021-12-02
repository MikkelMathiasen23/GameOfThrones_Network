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
from data_methods import create_thumbnail
from fa2 import ForceAtlas2

from skimage import io
import random
import os
import gunicorn
from whitenoise import WhiteNoise

from PIL import Image
import requests
from io import BytesIO

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
config_thumbnail = {'staticPlot': True}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowY': 'scroll'
    }
}

os.chdir('network_app/')
network = nx.read_gpickle("got_G_s1.gpickle")

with open('positions_all_seasons.json') as f:
    positions = json.load(f)


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
                **Character Image**
            """),
            dcc.Graph(
                id='selected-data',
                figure=thumbnail                
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

    base_path_pos = 'positions_'
    end_path_pos = '.json'
    complete_path_pos = base_path_pos + season_dropdown_menu + end_path_pos

    if season_dropdown_menu == 'got_G':
        complete_path = season_dropdown_menu + end_path
        complete_path_pos = base_path_pos + 'all_seasons' + end_path_pos

    network = nx.read_gpickle(complete_path)
    attribute = attribute_dropdown_menu

    with open('positions_all_seasons.json') as f:
        positions = json.load(f)

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
        response = requests.get(path)
        img = Image.open(BytesIO(response.content))
        thumbnail = create_thumbnail(img)

        return clickData['points'][0]['customdata'],thumbnail

    path = "https://static.wikia.nocookie.net/gameofthrones/images/c/c8/Iron_throne.jpg/revision/latest/scale-to-width-down/334?cb=20131005175755"
    response = requests.get(path)
    img = Image.open(BytesIO(response.content))
    thumbnail = create_thumbnail(img)
    return json.dumps(clickData, indent=2),thumbnail


server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')


