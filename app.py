"""
I keep app.py very thin.
"""
from flask import Flask

# Peewee database wrapper. It can handle different types of db.
from playhouse.flask_utils import FlaskDB
from micawber import bootstrap_basic
from micawber.cache import Cache as OEmbedCache

# Config class
import config


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


# FlaskDB is a wrapper for a peewee database that sets up pre/post-request
# hooks for managing database connections.
flask_db = FlaskDB(app)

# The 'database' is the actual peewee database, as opposed to flask_db which is
# the wrapper.
db = flask_db.database

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())

# Here I would set up the cache, a task queue, etc.