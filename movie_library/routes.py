from dataclasses import asdict
from datetime import datetime
import functools

from werkzeug.security import check_password_hash, generate_password_hash

from flask import (
    Blueprint,
    abort,
    flash,
    render_template,
    session,
    redirect,
    request,
    url_for,
)
from movie_library import mongo
from movie_library.forms import MovieForm, ExtendedMovieForm, RegisterForm, LoginForm
from uuid import uuid4 as uuid

from movie_library.models import Movie, User

pages = Blueprint(
    "movie_library", __name__, static_folder="static", template_folder="templates"
)


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        return route(*args, **kwargs)

    return route_wrapper


@pages.route("/")
@login_required
def index():
    assert mongo.db is not None
    movie_data = mongo.db.movies.find({})
    movies = [Movie(**movie) for movie in movie_data]
    return render_template("index.html", title="Movies WatchList", movies=movies)


@pages.route("/movie/<string:_id>")
def movie(_id: str):
    assert mongo.db is not None
    movie_data = mongo.db.movies.find_one({"_id": _id})
    if not movie_data:
        abort(404)
    movie = Movie(**movie_data)
    return render_template(
        "movie.html", title=f"Movies WatchList - {movie.title}", movie=movie
    )


@pages.route("/movie/<string:_id>/rate", methods=["POST"])
@login_required
def rate_movie(_id: str):
    rating = int(request.form.get("rating") or 0)
    assert mongo.db is not None
    mongo.db.movies.update_one({"_id": _id}, {"$set": {"rating": rating}})
    return redirect(url_for(".movie", _id=_id))


@pages.route("/movie/<string:_id>/watch")
@login_required
def watch_today(_id: str):
    assert mongo.db is not None
    mongo.db.movies.update_one(
        {"_id": _id}, {"$set": {"last_watched": datetime.today()}}
    )
    return redirect(url_for(".movie", _id=_id))


@pages.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie(
            _id=uuid().hex,
            title=form.title.data,  # type: ignore
            director=form.director.data,  # type: ignore
            year=form.year.data,  # type: ignore
            user=session.get("user_id"),
        )
        assert mongo.db is not None
        mongo.db.movies.insert_one(asdict(movie))
        mongo.db.users.update_one({"_id": movie.user}, {"$push": {"movies": movie._id}})
        return redirect(url_for("movie_library.index"))
    return render_template(
        "new_movie.html", title="Movies WatchList - Add Movie", form=form
    )


@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
@login_required
def update_movie(_id: str):
    assert mongo.db is not None
    movie_data = mongo.db.movies.find_one({"_id": _id})
    if not movie_data:
        abort(404)
    movie = Movie(**movie_data)
    if movie.user != session.get("user_id"):
        abort(403)
    form = ExtendedMovieForm(obj=movie)
    if form.validate_on_submit():
        movie.title = form.title.data  # type: ignore
        movie.director = form.director.data  # type: ignore
        movie.description = form.description.data
        movie.year = form.year.data  # type: ignore
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.video_link = form.video_link.data
        movie.user = session.get("user_id")

        mongo.db.movies.update_one({"_id": _id}, {"$set": asdict(movie)})
        return redirect(url_for(".movie", _id=_id))

    return render_template(
        "edit_movie.html", title="Movies WatchList - Update Movie", form=form
    )


@pages.route("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page") or url_for("movie_library.index"))


@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()
    if form.validate_on_submit():
        assert mongo.db is not None
        existing_user = mongo.db.users.find_one({"email": form.email.data})

        if existing_user:
            form.email.errors = [*form.email.errors, "This email is already in use."]
        else:
            user = User(
                _id=uuid().hex,
                email=form.email.data,  # type: ignore
                password=generate_password_hash(form.password.data),  # type: ignore
            )
            mongo.db.users.insert_one(asdict(user))

            flash("User Registered Successfully.", "success")
            return redirect(url_for(".login"))

    return render_template(
        "register.html", title="Movies WatchList - Register", form=form
    )


@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))
    form = LoginForm()
    if form.validate_on_submit():
        assert mongo.db is not None
        existing_user = mongo.db.users.find_one({"email": form.email.data})

        if not existing_user or not check_password_hash(
            existing_user["password"], form.password.data  # type: ignore
        ):
            flash("Invalid email or password.", "error")
        else:
            session["email"] = existing_user["email"]
            session["user_id"] = existing_user["_id"]
            flash("Logged in successfully.", "success")
            return redirect(url_for(".index"))

    return render_template("login.html", title="Movies WatchList - Login", form=form)


@pages.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".login"))
