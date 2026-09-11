import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_pymongo import PyMongo

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    mongo = PyMongo(app)

    @app.route("/", methods=["GET", "POST"])
    def hello_world():
        if request.method == "POST":
            entry_content = request.form.get("msg")
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
            if mongo.db is not None:
                mongo.db.entries.insert_one(
                    {"content": entry_content, "date": formatted_date}
                )
        entries_with_date = []
        if mongo.db is not None:
            entries_with_date = [
                (
                    entry["_id"],
                    entry["content"],
                    entry["date"],
                )
                for entry in mongo.db.entries.find().sort("_id", -1)
            ]
        return render_template("index.html", entries=entries_with_date)

    return app
