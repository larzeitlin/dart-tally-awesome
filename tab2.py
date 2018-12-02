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
from app import app, conn
import elo_score


def make_score_table(init_player_df, elo_score_df):
    if elo_score_df.shape[0] == 0:
        return(pd.DataFrame())
    last_scores = elo_score_df.tail(1)
    last_scores = last_scores.reset_index(drop=True)
    last_scores = last_scores.T
    last_scores_dict = last_scores.to_dict()[0]
    for index, row in init_player_df.iterrows():
        init_player_df.at[index, 'Score'] = last_scores_dict[row['player_id']]
    init_player_df = init_player_df[["player_name", "Score"]]
    init_player_df['Score'] = init_player_df['Score'].round(2)
    init_player_df = init_player_df.sort_values(by='Score', ascending=False)
    init_player_df = init_player_df.rename(columns = {"player_name" : "Player Name"})
    return(init_player_df)

def tab2(init_player_df, init_game_log_df, elo_score_df):
    result = init_game_log_df.merge(init_player_df.rename(columns={"player_name" : "winner"}), 
                                    how='left', 
                                    left_on="winner_id", 
                                    right_on="player_id", 
                                    suffixes=("", "_winner"))

    result_df = result.merge(init_player_df.rename(columns={'player_name' : "looser"}), 
                             how='left', 
                             left_on="looser_id", 
                             right_on="player_id", 
                             suffixes=("", "_looser"))


    
    result_df = result_df[['winner', 'winner_score', 'looser', 'looser_score', 'created_at']]
    result_df = result_df.rename(columns={'winner' : "P1", 
                                          "winner_score" : "P1 Score",
                                          "looser" : "P2",
                                          "looser_score" : "P2 Score",
                                          "created_at" : "Created At"
                                          }).tail(20)

    init_player_df = make_score_table(init_player_df, elo_score_df)

    tab = html.Div(children=[

        html.Div(children=[
            html.H4("Add a player"),
            html.Div(dcc.Input(id='new_player_input_field', 
                               value='', 
                               type='text',
                               
                                style={"background-color" : "white",
                                       "box-shadow" : "2px 2px 3px grey"}
                               )),
            html.Div([
                html.Button("Submit", 
                            id='add_new_player_button',
                            style={"background-color" : "white",
                                   "box-shadow" : "2px 2px 3px grey"}
                            )]),],
                
                style={
                   'padding' : '40px',
                   'margin' : '20px',
                   'border-style' : 'solid',
                   'border-radius' : "10",
                   'border-width' : '1px',
                   'border-color' : 'gray',
                   'textAlign' : "center",
                   'box-shadow' : "5px 5px 6px grey",
                   'background-color' : '#d9d9d9'},

            ),

        html.Div(children=[
            html.H4("League Table"),
            dash_table.DataTable(id='player_table',
                columns=[{"name" : i, "id" : i} for i in init_player_df.columns],
                data=init_player_df.to_dict("rows"),
                style_cell={'textAlign' : 'center'})]),

        html.Div(children=[
            html.H4("Game Table"),
            dash_table.DataTable(id='game_table',
                columns=[{"name" : i, "id" : i} for i in result_df.columns],
                data=result_df.to_dict("rows"),
                style_cell={'textAlign' : 'center'})])
        ])
    return(tab)
    
@app.callback(
    Output(component_id='player_table', component_property='data'),
    [Input('add_new_player_button', 'n_clicks')],
    [State('new_player_input_field', 'value')])
def update_league_table(n_clicks, value):
    init_df = pd.read_sql(sql='SELECT * FROM player_ids;', con=conn)
    if value not in ["", None, "enter a new player"] + init_df['player_name'].tolist():
        conn.execute("INSERT INTO player_ids (player_name) VALUES('{}');".format(value))


    kfactor_list = pd.read_sql(sql='SELECT * FROM kfactor;', con=conn)['value'].tolist()
    kfactor = kfactor_list.pop()

    game_log_df = pd.read_sql(sql='SELECT * FROM game_log;', con=conn)
    player_df = pd.read_sql(sql='SELECT * FROM player_ids;', con=conn)
    elo_score_df = elo_score.make_elo_scores_df(game_log_df, 
                                                player_df,                                                    
                                                K=kfactor)

    df = make_score_table(player_df, elo_score_df)
    return(df.to_dict("rows"))
