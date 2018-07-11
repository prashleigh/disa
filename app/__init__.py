from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models

# CLI
from app.etl import teardown, setup, mongo, users, inferencing
import click

@app.cli.command()
@click.option('--tables','-t', multiple=True)
def empty_tables(tables=[]):
    teardown.clear_data(tables)

@app.cli.command()
def seed():
    setup.load_multivalued_attributes()
    setup.load_many_to_many()

@app.cli.command()
@click.argument('datafile')
def mongo_migration(datafile):
    mongo.load_data(datafile)

@app.cli.command()
def rebuild():
    # teardown.clear_data()
    users.load_existing_users()
    setup.load_multivalued_attributes()
    setup.load_many_to_many()
    mongo.load_data(os.path.join(
        app.config['APP_DIR'], 'data/latest-entries.json') )
    inferencing.extract_information()

# END CLI

# TEMPLATES
@app.template_filter('century')
def get_century_from_year(yearInt):
	return yearInt // 100

@app.template_filter('decade')
def get_decade_from_year(yearInt):
	return yearInt % 100 // 10

@app.template_filter('year')
def get_year_from_datetime(yearInt):
	return yearInt % 10