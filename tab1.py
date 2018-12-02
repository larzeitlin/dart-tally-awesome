import os
from random import randint
import plotly.plotly as py
from plotly.graph_objs import *
import dash
import dash_table
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from app import app, conn
from datetime import datetime
import elo_score

def tab1(init_player_df, elo_score_df, player_dict):
    tab = html.Div(children=[
        html.H1(children="Dart-Tally-Awesome",
                style={'textAlign' : 'center'}),
        html.Div(
            
            style={'padding' : '40px',
                   'margin' : '20px',
                   'border-style' : 'solid',
                   'border-radius' : "10",
                   'border-width' : '1px',
                   'border-color' : 'gray',
                   'textAlign' : "center",
                   'box-shadow' : "5px 5px 6px grey",
                   'background-color' : '#d9d9d9'},
            children=[
            html.Div([html.Div("Player 1"),
                      dcc.Dropdown(options=[{'label' : i['player_name'],
                                             'value' : i['player_id']} 
                                            for i in init_player_df.to_dict("rows")],
                                   id="player_1_dropdown",
                                   style={"textAlign" : "center",
                                          'box-shadow' : "2px 2px 6px grey"}
                                   ),
                      html.Div("Player 1 Score"),
                      html.Div(dcc.Input(id='player_1_score',
                                         value='', 
                                         type='number',
                                         style={"textAlign" : "center",
                                                "width" : "100px",
                                                'box-shadow' : "2px 2px 6px grey",
                                                }))], 
                    className="four columns",
                    style={'textAlign' : 'center'}),
            html.H3("-VS-",
                    className="four columns"),

            html.Div([html.Div("Player 2"),
                      dcc.Dropdown(options=[{'label' : i['player_name'],
                                             'value' : i['player_id']} 
                                            for i in init_player_df.to_dict("rows")],
                                   id="player_2_dropdown",
                                   style={"textAlign" : "center",
                                          'box-shadow' : "2px 2px 6px grey"}
                                   ),
                      html.Div("Player 2 Score"),
                      html.Div(dcc.Input(id='player_2_score',
                                         value='', 
                                         type='number',
                                         style={"textAlign" : "center",
                                                "width" : "100px",
                                                'box-shadow' : "2px 2px 6px grey"}))], 
                    className="four columns",
                    style={'textAlign' : 'center'}), 
            html.Button("Add Score",
                        id="add_score_button",
                        style={"textAlign" : 'center',
                               'box-shadow' : "2px 2px 6px grey",
                               "background-color" : "white"}
                        )],
            className="row"),
            dcc.Graph(id='timeseries',
                      config={'displayModeBar': False},
                figure=go.Figure(
                    data = [go.Scatter(x=elo_score_df.index, 
                                       y=elo_score_df[i],
                                       name=player_dict[i]['player_name']) 
                            for i in list(elo_score_df)],
                    
                    layout = go.Layout(hovermode='closest'))
                ),
            html.Div(children=[
                html.H3("The Elo Rating System"),
                html.P("This web app is uses the Elo Rating System to rate players through time."\
                       " The previous rankings of the two players, and the outcome of the game all"\
                       " contribute to the new scores of each player. The Elo Rating System was"\
                       " originally divised by Arpad Elo for rating chess players. It has since"\
                       " been used for all sorts of zero-sum games. For more about this, head over"\
                       " to the Wikipedia Article:"),
                html.A("The Elo Rating System - Wikipedia.org", 
                       href="https://en.wikipedia.org/wiki/Elo_rating_system")
                ],

            style={'padding' : '40px',
                   'margin' : '20px',
                   'border-style' : 'solid',
                   'border-radius' : "10",
                   'border-width' : '1px',
                   'border-color' : 'gray',
                   'textAlign' : "left",
                   'box-shadow' : "5px 5px 6px grey",
                   'background-color' : '#d9d9d9'},
            )
            ])


    return(tab)

@app.callback(
    Output(component_id='timeseries', component_property='figure'),
    [Input('add_score_button', 'n_clicks_timestamp')],
    [State('player_1_dropdown', 'value'),
    State('player_2_dropdown', 'value'),
    State('player_1_score', 'value'),
    State('player_2_score', 'value')])
def update_games(timestamp, p1_id, p2_id, p1_score, p2_score):

    df = pd.read_sql(sql='SELECT * FROM game_log;', con=conn, parse_dates=['created_at'])
    try:
        p1_id = int(p1_id)
        p2_id = int(p2_id)
        p1_score = int(p1_score)
        p2_score = int(p2_score)
    except TypeError:
        pass
    else:
        if p1_score >= p2_score:
            winner_id = p1_id
            winner_score = p1_score
            looser_id = p2_id
            looser_score=p2_score
        else:
            winner_id = p2_id
            winner_score = p2_score
            looser_id = p1_id
            looser_score=p1_score
        utc_stamp = str(datetime.utcfromtimestamp(int(timestamp / 1000)))

        conn.execute("INSERT INTO game_log "\
        "(winner_id, winner_score, looser_id, looser_score, created_at) "\
        "VALUES({}, {}, {}, {}, '{}');".format(winner_id,
                                               winner_score,
                                               looser_id,
                                               looser_score,
                                               utc_stamp))
    finally:

        kfactor_list = pd.read_sql(sql='SELECT * FROM kfactor;', con=conn)['value'].tolist()
        kfactor = kfactor_list.pop()

        init_player_df = pd.read_sql(sql='SELECT * FROM player_ids;', 
                                     con=conn)
        init_game_log_df = pd.read_sql(sql='SELECT * FROM game_log;', 
                                       con=conn, 
                                       parse_dates=['created_at'])
        elo_score_df = elo_score.make_elo_scores_df(init_game_log_df, 
                                                    init_player_df, 
                                                    K=kfactor)

        player_dict = init_player_df.set_index("player_id").to_dict('index')

        figure = go.Figure(
            data = [go.Scatter(x=elo_score_df.index, 
                               y=elo_score_df[i],
                               name=player_dict[i]['player_name']) 
                    for i in list(elo_score_df)],
            
            layout = go.Layout(hovermode='closest'))
        
        return(figure)
    
