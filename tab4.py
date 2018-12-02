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

def tab4():
    kfactor_list = pd.read_sql(sql='SELECT * FROM kfactor;', con=conn)['value'].tolist()
    kfactor = kfactor_list.pop()
    tab = html.Div(children=[
        html.H1("Configuration Options"),
        html.Div(children=[
            html.H5("Adjust K-Factor", className="four columns"),
            html.Div(
                children=[
                    html.Div('Current K-Factor is: 23', id='k_output'),
                    dcc.Slider(min=1,
                           max=100,
                           step=1,
                            value=kfactor,
                            id="k_slider")],
                className="eight columns")],
            className='row'),

        html.Div(children=[
            html.H5("Delete All Games", className='four columns'),
            html.Div(children=[
                html.Button('Delete', id='delete_games_button'),
                html.Div("", id="delete_games_feedback")],
                className="eight columns")],
            className='row'),

        html.Div(children=[
            html.H5("Delete All Players and Games", className='four columns'),
            html.Div(children=[
                html.Button('Delete', id='delete_players_button'),
                html.Div("", id="delete_players_feedback")],
                className='eight columns')],
            className='row')
        ])
    return(tab)


@app.callback(
    Output(component_id='k_output', component_property='children'),
    [Input('k_slider', 'value')])
def update_k(k_value):
    conn.execute("INSERT INTO kfactor(value) VALUES ({});".format(k_value))
    return("Current K-Factor is: {}".format(k_value))

@app.callback(
    Output('delete_games_feedback', 'children'),
    [Input('delete_games_button', 'n_clicks')])
def del_games(n_clicks):
    if n_clicks == 1:
        return("Are you sure? If so click again")
    try:
        if n_clicks > 1:
            conn.execute("DELETE FROM game_log;")
            return("Players Deleted!")
    except TypeError:
        return("")

@app.callback(
    Output('delete_players_feedback', 'children'),
    [Input('delete_players_button', 'n_clicks')])
def del_players(n_clicks):
    if n_clicks == 1:
        return("Are you sure? If so click again")
    try:
        if n_clicks > 1:
            conn.execute("DELETE FROM game_log;")
            conn.execute("DELETE FROM player_ids;")
            return("Players and Games  Deleted!")
    except TypeError:
        return("")
