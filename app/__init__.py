from flask import Flask

from app import flask_extensions
from app.config import DevConfig


def create_app(config_class=DevConfig):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)
    flask_extensions.mongo.init_app(app)

    from app.microblog import bp as microblog_bp
    from app.habit_tracker import bp as habit_tracker_bp
    app.register_blueprint(microblog_bp, url_prefix="/microblog")
    app.register_blueprint(habit_tracker_bp)
    return app
