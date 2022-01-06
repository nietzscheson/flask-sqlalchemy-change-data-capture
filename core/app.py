import os
from flask import Flask, escape, request, g
from models import db
from flask_migrate import Migrate
from uuid import uuid4

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
migrate = Migrate(app, db)

@app.before_request
def before_request_handler():
    g.request_id = uuid4()

@app.route('/')
def index():
    name = request.args.get("name", os.environ['NAME'])
    return f'Hello, {escape(name)}!'
