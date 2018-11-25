temp_db_link = "postgres://mzdscoykshzgbv:189b1d7b220b1c4c22fbee4fabb30042e5cca2be6abb00a526e568ca9098c8b8@ec2-54-163-230-178.compute-1.amazonaws.com:5432/dcmbq4go3nl1bs"

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

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
#conn = sqlalchemy.create_engine(os.environ['DATABASE_URL'])
conn = sqlalchemy.create_engine(temp_db_link)
init_player_df = pd.read_sql(sql='SELECT * FROM player_ids;', con=conn)
init_game_log_df = pd.read_sql(sql='SELECT * FROM game_log;', con=conn, parse_dates=['created_at'])
player_dict = init_player_df.set_index("player_id").to_dict('index')
elo_score_df = elo_score.make_elo_scores_df(init_game_log_df, init_player_df, K=20)
app.layout = html.Div(children=[

    html.H1(children="Dart-Tally-Awesome",
            style={'textAlign' : 'center'}),
    html.Div([
        html.Div([html.Div("Player 1"),
                  dcc.Dropdown(options=[{'label' : i['player_name'],
                                         'value' : i['player_id']} 
                                        for i in init_player_df.to_dict("rows")],
                               id="player_2_dropdown"),
                  html.Div("Player 1 Score"),
                  html.Div(dcc.Input(id='player_1_score',
                                     value='', 
                                     type='text'))], 
                className="four columns",
                style={'textAlign' : 'center'}),
        html.H3("-VS-",
                className="four columns"),

        html.Div([html.Div("Player 2"),
                  dcc.Dropdown(options=[{'label' : i['player_name'],
                                         'value' : i['player_id']} 
                                        for i in init_player_df.to_dict("rows")],
                               id="player_1_dropdown"),
                  html.Div("Player 2 Score"),
                  html.Div(dcc.Input(id='player_2_score',
                                     value='', 
                                     type='text'))], 
                className="four columns",
                style={'textAlign' : 'center'}), 
        html.Button("Add Score",
                    id="add_score_button",
                    style={"textAlign" : 'center'})],
        className="row",
        style={"textAlign" : 'center'}),
    html.Div(children=[
        html.H4("Add a player"),
        html.Div(dcc.Input(id='new_player_input_field', 
                           value='', 
                           type='text'),
                           style={"textAlign" : "center"}),
        html.Div([
            html.Button("Submit", 
                        id='add_new_player_button')])],
        style={"textAlign" : "center"}),


    html.Div(children=[
        dcc.Graph(id='timeseries',
            figure=go.Figure(
                data = [go.Scatter(x=elo_score_df.index, 
                                   y=elo_score_df[i],
                                   name=player_dict[i]['player_name']) 
                        for i in list(elo_score_df)],
                
                layout = go.Layout(hovermode='closest')))],
        style={'textAlign' : 'center'}),

    html.Div(children=[
        html.H4("League Table"),
        dash_table.DataTable(id='player_table',
            columns=[{"name" : i, "id" : i} for i in init_player_df.columns],
            data=init_player_df.to_dict("rows"),
            style_cell={'textAlign' : 'center'})],
            style={'textAlign' : 'center'},
            className="twelve columns"),

    html.Div(children=[
        html.H4("Game Table"),
        dash_table.DataTable(id='game_table',
            columns=[{"name" : i, "id" : i} for i in init_game_log_df.columns],
            data=init_game_log_df.to_dict("rows"),
            style_cell={'textAlign' : 'center'})],
            style={'textAlign' : 'center'},
            className="twelve columns"),
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output(component_id='player_table', component_property='data'),
    [Input('add_new_player_button', 'n_clicks')],
    [State('new_player_input_field', 'value')])
def update_league_table(n_clicks, value):
    init_df = pd.read_sql(sql='SELECT * FROM player_ids;', con=conn)
    if value not in ["", None, "enter a new player"] + init_df['player_name'].tolist():
        conn.execute("INSERT INTO player_ids (player_name) VALUES('{}');".format(value))
    df = pd.read_sql(sql='SELECT * FROM player_ids;', con=conn)
    return(df.to_dict("rows"))

@app.callback(
    Output(component_id='game_table', component_property='data'),
    [Input('add_score_button', 'n_clicks_timestamp')],
    [State('player_1_dropdown', 'value'),
    State('player_2_dropdown', 'value'),
    State('player_1_score', 'value'),
    State('player_2_score', 'value')])
def update_games(timestamp, p1_id, p2_id, p1_score, p2_score):
    df = pd.read_sql(sql='SELECT * FROM game_log;', con=conn, parse_dates=['created_at'])
 #  df['created_at'] = df['created_at'].dt.strftime("%D, %r")
    print("p1_id: ", p1_id)
    print("p1_score: ", p1_score)
    try:
        p1_id = int(p1_id)
        p2_id = int(p2_id)
        p1_score = int(p1_score)
        p2_score = int(p2_score)
    except TypeError:
        print("Here")
        return(df.to_dict("rows"))
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

    df = pd.read_sql(sql='SELECT * FROM game_log;', con=conn, parse_dates=['created_at'])
    return(df.to_dict("rows"))

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
