import os
from random import randint
import plotly.plotly as py
from plotly.graph_objs import *
import flask
import dash
import dash_table
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import sqlalchemy
import pandas as pd
from datetime import datetime
import elo_score
from app import app, conn
from collections import Counter

def wld_function(row, target_id):
    if row['winner_score'] == row['looser_score']:
        return("D")
    elif row['winner_id'] == target_id:
        return("W")
    else:
        return("L")


def count_wld(game_log_df, player_id):
    qu = "((winner_id == {}) | (looser_id == {}))".format(player_id, player_id)

    df = game_log_df.query(qu)
    df['wld'] = df.apply(lambda x : wld_function(x, player_id), axis=1)
    WLD_list = df['wld'].tolist()
    WLD = [WLD_list.count('W'), WLD_list.count('L'), WLD_list.count('D')]
    return(WLD)
    

def tab3(init_player_df, init_game_log_df, elo_score_df, player_dict):
    tab = html.Div(children=[
        html.Div([html.H3("Select a Player"),
                  dcc.Dropdown(options=[{'label' : i['player_name'],
                                         'value' : i['player_id']} 
                                        for i in init_player_df.to_dict("rows")],
                               id="player_dropdown",
                               style={"textAlign" : "center",
                                      'box-shadow' : "2px 2px 6px grey"}
                               )]),
        html.Div(children=[
            html.H3("Wins, Losses, Draws"),
            dcc.Graph(id='WLD_pie',
                      config={'displayModeBar': False},
                figure=go.Figure(
                    data = [go.Pie(labels = ["Wins", "Losses", "Draws"], 
                                   values = [1, 2, 3],
                                   marker=dict(colors = ['#00e600', '#ff4d4d','#ffd633']))],
                    
                    layout = go.Layout(hovermode='closest')))

        ],
        style={"margin" : "20px"})])
    return(tab)       



@app.callback(
    Output(component_id='WLD_pie', component_property='figure'),
    [Input('player_dropdown', 'value')])
def update_Pie(value):
    if value == None:
        figure=go.Figure(
            data = [go.Pie(labels = ["Wins", "Losses", "Draws"], 
                           values = [1, 2, 3],
                           marker=dict(colors = ['#00e600', '#ff4d4d','#ffd633']))],
            
            layout = go.Layout(hovermode='closest'))
        return(figure)

    else:

        game_log_df = pd.read_sql(sql='SELECT * FROM game_log;', 
                                       con=conn, 
                                       parse_dates=['created_at'])
        WLD = count_wld(game_log_df, value)
        figure = go.Figure( 
                        data = [go.Pie(labels = ["Wins", "Losses", "Draws"], 
                                       values = WLD,
                                       marker=dict(colors = ['#00e600', '#ff4d4d','#ffd633']))],
                        layout = go.Layout(hovermode='closest'))
        return(figure)

'''
@app.callback(
    Output(component_id='nem_name', component_property='children'),
    [Input('player_dropdown', 'value')])
def update_Nem(value):
    if value == None:
        return("")
    else:
        game_log_df = pd.read_sql(sql='SELECT * FROM game_log;', 
                                       con=conn, 
                                       parse_dates=['created_at'])
        qu = "((winner_id == {}) | (looser_id == {}))".format(value, value)
        df = game_log_df.query(qu)
        ids_list = df["winner_id"].tolist() + df['looser_id'].tolist()
        ids_list = [x for x in ids_list if x != value]
        cnt = Counter(ids_list)
        nem_id = cnt.most_common()[0][0]


        player_df = pd.read_sql(sql='SELECT * FROM player_ids;', 
                                     con=conn)

        player_dict = player_df.set_index("player_id").to_dict('index')
        return(player_dict[nem_id])


'''
