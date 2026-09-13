import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from flask_pymongo import PyMongo

load_dotenv(Path(__file__).resolve().parent / ".env")

mongo = PyMongo()


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    mongo.init_app(app)
    from movie_library.routes import pages
    from movie_library.utils import youtube_embed_url

    app.register_blueprint(pages)
    app.jinja_env.filters["youtube_embed_url"] = youtube_embed_url
    return app
