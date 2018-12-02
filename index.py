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
import tab1
import tab2
import tab3
import tab4

server = app.server


tabs_styles = {
    'height': '44px',
    'border-radius' : "10"
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Rankings / New Score', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Players and Games', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Player Stats', value='tab-3', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Configuration', value='tab-4', style=tab_style, selected_style=tab_selected_style)
    ]),
    html.Div(id='tabs-content',

            style={'padding' : '20px',
                   'outline-color' : 'gray',
                   'margin' : '20px',
                   'border-style' : 'solid',
                   'border-radius' : "10",
                   'border-width' : '1px',
                   'border-color' : 'gray',
                   'textAlign' : "center",
                   'box-shadow' : "5px 5px 6px grey",
                   'background-color' : 'white'}
        ),
    
    ],

    style={'top-padding' : '20px',
           'textAlign' : "center",
           'background' : 'linear-gradient(#119DFF, #FFFFFF)',
           'height' : "100%"}
    )

kfactor_list = pd.read_sql(sql='SELECT * FROM kfactor;', con=conn)['value'].tolist()
kfactor = kfactor_list.pop()

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == "tab-4":
        return(tab4.tab4())


    init_player_df = pd.read_sql(sql='SELECT * FROM player_ids;', 
                                 con=conn)
    init_game_log_df = pd.read_sql(sql='SELECT * FROM game_log;', 
                                   con=conn, 
                                   parse_dates=['created_at'])
    elo_score_df = elo_score.make_elo_scores_df(init_game_log_df, 
                                                init_player_df, 
                                                K=kfactor)
    if tab == 'tab-1':
        player_dict = init_player_df.set_index("player_id").to_dict('index')
        return(tab1.tab1(init_player_df, 
                         elo_score_df, 
                         player_dict))
    elif tab == 'tab-2':
        return(tab2.tab2(init_player_df, 
                         init_game_log_df,
                         elo_score_df))
    elif tab == 'tab-3':
        player_dict = init_player_df.set_index("player_id").to_dict('index')
        return(tab3.tab3(init_player_df,
                         init_game_log_df,
                         elo_score_df,
                         player_dict))

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
