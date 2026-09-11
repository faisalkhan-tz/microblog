import datetime
from flask import render_template, request, redirect, url_for

from app.flask_extensions import mongo
from app.habit_tracker import bp
from bson import ObjectId


@bp.route("/")
def index():
    date_str = request.args.get("date")
    try:
        selected_date = (
            datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else datetime.date.today()
        )
    except ValueError:
        selected_date = datetime.date.today()

    week = []
    for offset in range(-3, 4):
        day = selected_date + datetime.timedelta(days=offset)
        week.append(
            {
                "iso": day.strftime("%Y-%m-%d"),
                "label": day.strftime("%a"),
                "day_number": day.strftime("%d"),
            }
        )

    habits = []
    if mongo.db is not None:
        selected_iso = selected_date.strftime("%Y-%m-%d")
        for habit in mongo.db.habits.find().sort("_id", 1):
            done = (
                mongo.db.completions.find_one(
                    {"habit_id": habit["_id"], "date": selected_iso}
                )
                is not None
            )
            habits.append({"_id": habit["_id"], "name": habit["name"], "done": done})

    return render_template(
        "habit-tracker/index.html",
        title="Habit Tracker - Home",
        week=week,
        selected_date=selected_date.strftime("%Y-%m-%d"),
        habits=habits,
    )


@bp.route("/add", methods=["GET", "POST"])
def add_habit():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name and mongo.db is not None:
            mongo.db.habits.insert_one({"name": name})
        return redirect(url_for("habit_tracker.index"))
    return render_template(
        "habit-tracker/add_habit.html", title="Habit Tracker - Add Habit"
    )


@bp.route("/toggle/<habit_id>", methods=["POST"])
def toggle_habit(habit_id):
    date_str = request.form.get("date")
    if mongo.db is not None and date_str:
        oid = ObjectId(habit_id)
        existing = mongo.db.completions.find_one({"habit_id": oid, "date": date_str})
        if existing:
            mongo.db.completions.delete_one({"_id": existing["_id"]})
        else:
            mongo.db.completions.insert_one({"habit_id": oid, "date": date_str})
    return redirect(url_for("habit_tracker.index", date=date_str))
