# Import required libraries
temp_db_link = "postgres://mzdscoykshzgbv:189b1d7b220b1c4c22fbee4fabb30042e5cca2be6abb00a526e568ca9098c8b8@ec2-54-163-230-178.compute-1.amazonaws.com:5432/dcmbq4go3nl1bs"

import os
from random import randint

import plotly.plotly as py
from plotly.graph_objs import *

import flask
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html


# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)


# Put your Dash code here

import sqlalchemy
import pandas as pd
#conn = sqlalchemy.create_engine(os.environ['DATABASE_URL'])
#   conn = sqlalchemy.create_engine(temp_db_link)
#   x = conn.execute('SELECT * FROM player_ids')

#   conn.execute("DELETE FROM player_ids WHERE player_ids.player_id=1;" )
#   conn.execute("INSERT INTO player_ids (player_name) VALUES('test2');")
#   df = pd.read_sql(sql='SELECT * FROM player_ids;', 
#                    con=conn)
#   print(df)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Input(
        placeholder='Enter a value...',
        type='text',
        value='')
])

# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
