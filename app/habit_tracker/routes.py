import datetime
from flask import render_template, request, redirect, url_for

from app.flask_extensions import mongo
from app.habit_tracker import bp
from bson import ObjectId


@bp.context_processor
def add_calc_date_range():
    def build_week(selected_date):
        if isinstance(selected_date, str):
            selected_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
        week_days = []
        for offset in range(-3, 4):
            day = selected_date + datetime.timedelta(days=offset)
            week_days.append(
                {
                    "iso": day.strftime("%Y-%m-%d"),
                    "label": day.strftime("%a"),
                    "day_number": day.strftime("%d"),
                }
            )
        return week_days

    return {"week": build_week}


def _parse_selected_date(date_str):
    try:
        return (
            datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_str
            else datetime.date.today()
        )
    except ValueError:
        return datetime.date.today()


@bp.route("/")
def index():
    date_str = request.args.get("date")
    selected_date = _parse_selected_date(date_str)

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
        "index.html",
        title="Habit Tracker - Home",
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

    selected_date = _parse_selected_date(request.args.get("date")) or datetime.datetime.today() 
    return render_template(
        "add_habit.html",
        title="Habit Tracker - Add Habit",
        selected_date=selected_date.strftime("%Y-%m-%d"),
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
