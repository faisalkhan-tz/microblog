import datetime

from flask import render_template, request

from app.flask_extensions import mongo
from app.microblog import bp


@bp.route("/", methods=["GET", "POST"])
def index():
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
            (entry["_id"], entry["content"], entry["date"])
            for entry in mongo.db.entries.find().sort("_id", -1)
        ]

    return render_template("microblog.html", entries=entries_with_date)
