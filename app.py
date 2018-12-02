temp_db_link = "postgres://mzdscoykshzgbv:189b1d7b220b1c4c22fbee4fabb30042e5cca2be6abb00a526e568ca9098c8b8@ec2-54-163-230-178.compute-1.amazonaws.com:5432/dcmbq4go3nl1bs"

import os
from random import randint
import flask
import dash
import sqlalchemy
import pandas as pd

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
#conn = sqlalchemy.create_engine(os.environ['DATABASE_URL'])
conn = sqlalchemy.create_engine(temp_db_link)

external_css = [

 #  'https://codepen.io/chriddyp/pen/bWLwgP.css',
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
    "//fonts.googleapis.com/css?family=Raleway:400,300,600",
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "/static/style.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

app.config['suppress_callback_exceptions'] = True
