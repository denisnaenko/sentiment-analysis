from flask import Flask

app = Flask(__name__)

SECRET_KEY = 'qjFq;[0#(y<2tsMx5ch+;J92N@YVr~o&'
app.config['SECRET_KEY'] = SECRET_KEY

from analyser import routes